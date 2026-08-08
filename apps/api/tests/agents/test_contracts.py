from datetime import UTC, datetime

import pytest
from enterprise_ai_api.agents.contracts import AgentError, AgentRun, AgentStep, AgentTask
from enterprise_ai_api.agents.states import AgentRunState, AgentStepKind, AgentStepState
from pydantic import ValidationError


def test_agent_task_defaults_to_empty_input() -> None:
    task = AgentTask(task_id="task-1", agent_name="reference.ping")

    assert task.input == {}


def test_agent_task_rejects_extra_fields() -> None:
    with pytest.raises(ValidationError):
        AgentTask(task_id="task-1", agent_name="reference.ping", unexpected=True)


def test_agent_task_is_immutable() -> None:
    task = AgentTask(task_id="task-1", agent_name="reference.ping")

    with pytest.raises(ValidationError):
        task.task_id = "task-2"  # type: ignore[misc]


def test_agent_step_defaults_to_pending() -> None:
    step = AgentStep(
        step_id="step-1",
        run_id="run-1",
        sequence=1,
        kind=AgentStepKind.TOOL,
    )

    assert step.state is AgentStepState.PENDING


def test_agent_step_rejects_non_positive_sequence() -> None:
    with pytest.raises(ValidationError):
        AgentStep(
            step_id="step-1",
            run_id="run-1",
            sequence=0,
            kind=AgentStepKind.TOOL,
        )


def test_agent_run_defaults_to_pending_with_no_steps() -> None:
    run = AgentRun(run_id="run-1", task_id="task-1")

    assert run.state is AgentRunState.PENDING
    assert run.steps == ()


def test_agent_run_accepts_step_snapshot_and_error_contract() -> None:
    now = datetime.now(UTC)
    error = AgentError(code="TOOL_INVOCATION_FAILED", message="Tool failed")
    step = AgentStep(
        step_id="step-1",
        run_id="run-1",
        sequence=1,
        kind=AgentStepKind.TOOL,
        state=AgentStepState.FAILED,
        started_at=now,
        completed_at=now,
        error=error,
    )
    run = AgentRun(
        run_id="run-1",
        task_id="task-1",
        state=AgentRunState.FAILED,
        steps=(step,),
        started_at=now,
        completed_at=now,
        error=error,
    )

    assert run.steps == (step,)
    assert run.error == error
