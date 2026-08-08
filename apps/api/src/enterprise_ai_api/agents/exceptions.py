from __future__ import annotations


class AgentRuntimeError(Exception):
    """Base exception for agent runtime failures."""


class AgentStateTransitionError(AgentRuntimeError):
    """Raised when a run or step attempts an illegal lifecycle transition."""

    def __init__(self, subject: str, current: str, target: str) -> None:
        super().__init__(
            f"Invalid {subject} state transition from '{current}' to '{target}'."
        )


class AgentStepLimitExceededError(AgentRuntimeError):
    """Raised when a run attempts to exceed its configured step budget."""


class AgentTimeoutError(AgentRuntimeError):
    """Raised when execution exceeds its runtime deadline."""


class AgentCancelledError(AgentRuntimeError):
    """Raised when execution is cancelled."""


class AgentExecutionError(AgentRuntimeError):
    """Raised when agent execution fails for a normalized runtime reason."""
