from __future__ import annotations

from collections.abc import Mapping
from enum import StrEnum
from types import MappingProxyType

from enterprise_ai_api.agents.exceptions import AgentStateTransitionError


class AgentRunState(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    TIMED_OUT = "timed_out"
    CANCELLED = "cancelled"


class AgentStepState(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    TIMED_OUT = "timed_out"
    CANCELLED = "cancelled"


class AgentStepKind(StrEnum):
    TOOL = "tool"


_RUN_TRANSITIONS: Mapping[AgentRunState, frozenset[AgentRunState]] = MappingProxyType(
    {
        AgentRunState.PENDING: frozenset(
            {AgentRunState.RUNNING, AgentRunState.CANCELLED}
        ),
        AgentRunState.RUNNING: frozenset(
            {
                AgentRunState.SUCCEEDED,
                AgentRunState.FAILED,
                AgentRunState.TIMED_OUT,
                AgentRunState.CANCELLED,
            }
        ),
        AgentRunState.SUCCEEDED: frozenset(),
        AgentRunState.FAILED: frozenset(),
        AgentRunState.TIMED_OUT: frozenset(),
        AgentRunState.CANCELLED: frozenset(),
    }
)

_STEP_TRANSITIONS: Mapping[AgentStepState, frozenset[AgentStepState]] = MappingProxyType(
    {
        AgentStepState.PENDING: frozenset(
            {AgentStepState.RUNNING, AgentStepState.CANCELLED}
        ),
        AgentStepState.RUNNING: frozenset(
            {
                AgentStepState.SUCCEEDED,
                AgentStepState.FAILED,
                AgentStepState.TIMED_OUT,
                AgentStepState.CANCELLED,
            }
        ),
        AgentStepState.SUCCEEDED: frozenset(),
        AgentStepState.FAILED: frozenset(),
        AgentStepState.TIMED_OUT: frozenset(),
        AgentStepState.CANCELLED: frozenset(),
    }
)


def validate_run_transition(current: AgentRunState, target: AgentRunState) -> None:
    if target not in _RUN_TRANSITIONS[current]:
        raise AgentStateTransitionError("agent run", current.value, target.value)


def validate_step_transition(current: AgentStepState, target: AgentStepState) -> None:
    if target not in _STEP_TRANSITIONS[current]:
        raise AgentStateTransitionError("agent step", current.value, target.value)
