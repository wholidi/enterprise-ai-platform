import asyncio

import pytest
from enterprise_ai_api.agents.context import (
    MAX_AGENT_STEPS,
    AgentExecutionContext,
    CancellationToken,
)


def test_execution_context_accepts_bounded_step_budget() -> None:
    context = AgentExecutionContext(run_id="run-1", max_steps=10, timeout_seconds=30.0)

    assert context.remaining_steps(3) == 7
    assert context.cancellation.is_cancelled is False


@pytest.mark.parametrize("max_steps", [0, -1, MAX_AGENT_STEPS + 1])
def test_execution_context_rejects_invalid_step_budget(max_steps: int) -> None:
    with pytest.raises(ValueError, match="max_steps"):
        AgentExecutionContext(run_id="run-1", max_steps=max_steps)


def test_execution_context_rejects_empty_run_id() -> None:
    with pytest.raises(ValueError, match="run_id"):
        AgentExecutionContext(run_id="", max_steps=1)


def test_execution_context_rejects_non_positive_timeout() -> None:
    with pytest.raises(ValueError, match="timeout_seconds"):
        AgentExecutionContext(run_id="run-1", max_steps=1, timeout_seconds=0)


def test_remaining_steps_never_goes_below_zero() -> None:
    context = AgentExecutionContext(run_id="run-1", max_steps=2)

    assert context.remaining_steps(5) == 0


def test_remaining_steps_rejects_negative_completed_count() -> None:
    context = AgentExecutionContext(run_id="run-1", max_steps=2)

    with pytest.raises(ValueError, match="completed_steps"):
        context.remaining_steps(-1)


def test_cancellation_token_can_be_cancelled() -> None:
    token = CancellationToken()

    token.cancel()

    assert token.is_cancelled is True


def test_cancellation_token_wait_completes_after_cancel() -> None:
    async def scenario() -> None:
        token = CancellationToken()
        token.cancel()
        await token.wait()

    asyncio.run(scenario())
