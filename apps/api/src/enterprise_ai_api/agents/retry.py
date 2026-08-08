from __future__ import annotations

from dataclasses import dataclass

MAX_TOOL_ATTEMPTS = 3


@dataclass(frozen=True, slots=True)
class RetryPolicy:
    """Bounded retry controls for tool execution within one agent run."""

    max_attempts: int = 1

    def __post_init__(self) -> None:
        if not 1 <= self.max_attempts <= MAX_TOOL_ATTEMPTS:
            raise ValueError(f"max_attempts must be between 1 and {MAX_TOOL_ATTEMPTS}")
