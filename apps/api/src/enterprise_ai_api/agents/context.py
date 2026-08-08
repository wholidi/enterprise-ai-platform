from __future__ import annotations

import asyncio
from dataclasses import dataclass, field

from enterprise_ai_api.agents.retry import RetryPolicy

MAX_AGENT_STEPS = 100


@dataclass(slots=True)
class CancellationToken:
    """Ephemeral cooperative cancellation primitive for a single agent run."""

    _event: asyncio.Event = field(default_factory=asyncio.Event)

    @property
    def is_cancelled(self) -> bool:
        return self._event.is_set()

    def cancel(self) -> None:
        self._event.set()

    async def wait(self) -> None:
        await self._event.wait()


@dataclass(frozen=True, slots=True)
class AgentExecutionContext:
    """Ephemeral execution controls for one agent run."""

    run_id: str
    max_steps: int
    timeout_seconds: float | None = None
    cancellation: CancellationToken = field(default_factory=CancellationToken)
    retry_policy: RetryPolicy = field(default_factory=RetryPolicy)

    def __post_init__(self) -> None:
        if not self.run_id:
            raise ValueError("run_id must not be empty")
        if not 1 <= self.max_steps <= MAX_AGENT_STEPS:
            raise ValueError(f"max_steps must be between 1 and {MAX_AGENT_STEPS}")
        if self.timeout_seconds is not None and self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be greater than zero")

    def remaining_steps(self, completed_steps: int) -> int:
        if completed_steps < 0:
            raise ValueError("completed_steps must not be negative")
        return max(self.max_steps - completed_steps, 0)
