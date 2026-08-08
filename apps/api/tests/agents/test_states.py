import pytest
from enterprise_ai_api.agents.exceptions import AgentStateTransitionError
from enterprise_ai_api.agents.states import (
    AgentRunState,
    AgentStepState,
    validate_run_transition,
    validate_step_transition,
)


@pytest.mark.parametrize(
    ("current", "target"),
    [
        (AgentRunState.PENDING, AgentRunState.RUNNING),
        (AgentRunState.PENDING, AgentRunState.CANCELLED),
        (AgentRunState.RUNNING, AgentRunState.SUCCEEDED),
        (AgentRunState.RUNNING, AgentRunState.FAILED),
        (AgentRunState.RUNNING, AgentRunState.TIMED_OUT),
        (AgentRunState.RUNNING, AgentRunState.CANCELLED),
    ],
)
def test_valid_run_transitions(current: AgentRunState, target: AgentRunState) -> None:
    validate_run_transition(current, target)


@pytest.mark.parametrize(
    ("current", "target"),
    [
        (AgentRunState.PENDING, AgentRunState.SUCCEEDED),
        (AgentRunState.FAILED, AgentRunState.RUNNING),
        (AgentRunState.SUCCEEDED, AgentRunState.CANCELLED),
        (AgentRunState.TIMED_OUT, AgentRunState.RUNNING),
        (AgentRunState.CANCELLED, AgentRunState.RUNNING),
    ],
)
def test_invalid_run_transitions(current: AgentRunState, target: AgentRunState) -> None:
    with pytest.raises(AgentStateTransitionError):
        validate_run_transition(current, target)


@pytest.mark.parametrize(
    ("current", "target"),
    [
        (AgentStepState.PENDING, AgentStepState.RUNNING),
        (AgentStepState.PENDING, AgentStepState.CANCELLED),
        (AgentStepState.RUNNING, AgentStepState.SUCCEEDED),
        (AgentStepState.RUNNING, AgentStepState.FAILED),
        (AgentStepState.RUNNING, AgentStepState.TIMED_OUT),
        (AgentStepState.RUNNING, AgentStepState.CANCELLED),
    ],
)
def test_valid_step_transitions(current: AgentStepState, target: AgentStepState) -> None:
    validate_step_transition(current, target)


@pytest.mark.parametrize(
    ("current", "target"),
    [
        (AgentStepState.PENDING, AgentStepState.SUCCEEDED),
        (AgentStepState.FAILED, AgentStepState.RUNNING),
        (AgentStepState.SUCCEEDED, AgentStepState.CANCELLED),
        (AgentStepState.TIMED_OUT, AgentStepState.RUNNING),
        (AgentStepState.CANCELLED, AgentStepState.RUNNING),
    ],
)
def test_invalid_step_transitions(current: AgentStepState, target: AgentStepState) -> None:
    with pytest.raises(AgentStateTransitionError):
        validate_step_transition(current, target)
