from __future__ import annotations

import asyncio
from typing import Any

from enterprise_ai_api.agents.context import AgentExecutionContext, CancellationToken
from enterprise_ai_api.agents.contracts import AgentTask
from enterprise_ai_api.agents.reference import ReferencePingAgent
from enterprise_ai_api.agents.retry import RetryPolicy
from enterprise_ai_api.agents.runtime import AgentRuntime, ToolExecutor
from enterprise_ai_api.agents.states import AgentRunState, AgentStepState
from enterprise_ai_api.tools.exceptions import (
    ToolExecutionError,
    ToolInputValidationError,
)
from enterprise_ai_api.tools.invocation import ToolInvocationService


class StubInvocationService(ToolInvocationService):
    def __init__(
        self,
        *,
        result: dict[str, Any] | None = None,
        error: Exception | None = None,
        delay: float = 0.0,
    ) -> None:
        self.result = result or {"response": "pong"}
        self.error = error
        self.delay = delay
        self.calls: list[tuple[str, dict[str, Any]]] = []

    async def invoke(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        self.calls.append((tool_name, arguments))
        if self.delay:
            await asyncio.sleep(self.delay)
        if self.error is not None:
            raise self.error
        return self.result


class TwoStepAgent:
    @property
    def name(self) -> str:
        return "test.two-step"

    async def execute(
        self,
        task: AgentTask,
        execute_tool: ToolExecutor,
    ) -> dict[str, Any]:
        del task
        await execute_tool("platform.ping", {})
        return await execute_tool("platform.ping", {})


async def test_runtime_executes_reference_agent_successfully() -> None:
    service = StubInvocationService(
        result={
            "message": "hello",
            "response": "pong",
            "service": "enterprise-ai-platform",
            "version": "0.2.0",
        }
    )
    runtime = AgentRuntime(service)

    run = await runtime.execute(
        AgentTask(
            task_id="task-1",
            agent_name="reference.ping",
            input={"message": "hello"},
        ),
        AgentExecutionContext(run_id="run-1", max_steps=1),
        ReferencePingAgent(),
    )

    assert run.state is AgentRunState.SUCCEEDED
    assert run.started_at is not None
    assert run.completed_at is not None
    assert run.error is None
    assert run.output == service.result
    assert len(run.steps) == 1
    step = run.steps[0]
    assert step.state is AgentStepState.SUCCEEDED
    assert step.sequence == 1
    assert step.output == service.result
    assert step.started_at is not None
    assert step.completed_at is not None
    assert service.calls == [("platform.ping", {"message": "hello"})]


async def test_runtime_cancels_before_run_starts() -> None:
    token = CancellationToken()
    token.cancel()
    service = StubInvocationService()

    run = await AgentRuntime(service).execute(
        AgentTask(task_id="task-1", agent_name="reference.ping"),
        AgentExecutionContext(run_id="run-1", max_steps=1, cancellation=token),
        ReferencePingAgent(),
    )

    assert run.state is AgentRunState.CANCELLED
    assert run.started_at is None
    assert run.completed_at is not None
    assert run.error is not None
    assert run.error.code == "RUN_CANCELLED"
    assert run.steps == ()
    assert service.calls == []


async def test_runtime_cancels_running_tool_step() -> None:
    token = CancellationToken()
    service = StubInvocationService(delay=10.0)
    runtime = AgentRuntime(service)

    execution = asyncio.create_task(
        runtime.execute(
            AgentTask(task_id="task-1", agent_name="reference.ping"),
            AgentExecutionContext(run_id="run-1", max_steps=1, cancellation=token),
            ReferencePingAgent(),
        )
    )
    await asyncio.sleep(0)
    token.cancel()
    run = await execution

    assert run.state is AgentRunState.CANCELLED
    assert run.error is not None
    assert run.error.code == "RUN_CANCELLED"
    assert len(run.steps) == 1
    assert run.steps[0].state is AgentStepState.CANCELLED


async def test_runtime_times_out_running_tool_step() -> None:
    service = StubInvocationService(delay=10.0)

    run = await AgentRuntime(service).execute(
        AgentTask(task_id="task-1", agent_name="reference.ping"),
        AgentExecutionContext(run_id="run-1", max_steps=1, timeout_seconds=0.01),
        ReferencePingAgent(),
    )

    assert run.state is AgentRunState.TIMED_OUT
    assert run.error is not None
    assert run.error.code == "RUN_TIMED_OUT"
    assert len(run.steps) == 1
    assert run.steps[0].state is AgentStepState.TIMED_OUT


async def test_runtime_enforces_step_budget() -> None:
    service = StubInvocationService()

    run = await AgentRuntime(service).execute(
        AgentTask(task_id="task-1", agent_name="test.two-step"),
        AgentExecutionContext(run_id="run-1", max_steps=1),
        TwoStepAgent(),
    )

    assert run.state is AgentRunState.FAILED
    assert run.error is not None
    assert run.error.code == "STEP_LIMIT_EXCEEDED"
    assert len(run.steps) == 1
    assert run.steps[0].state is AgentStepState.SUCCEEDED
    assert len(service.calls) == 1


async def test_runtime_normalizes_tool_platform_failure() -> None:
    service = StubInvocationService(error=ToolExecutionError("boom"))

    run = await AgentRuntime(service).execute(
        AgentTask(task_id="task-1", agent_name="reference.ping"),
        AgentExecutionContext(run_id="run-1", max_steps=1),
        ReferencePingAgent(),
    )

    assert run.state is AgentRunState.FAILED
    assert run.error is not None
    assert run.error.code == "AGENT_EXECUTION_FAILED"
    assert run.error.message == "Tool invocation failed."
    assert len(run.steps) == 1
    assert run.steps[0].state is AgentStepState.FAILED
    assert run.steps[0].error is not None
    assert run.steps[0].error.code == "TOOL_INVOCATION_FAILED"


async def test_runtime_rejects_agent_name_mismatch_without_tool_call() -> None:
    service = StubInvocationService()

    run = await AgentRuntime(service).execute(
        AgentTask(task_id="task-1", agent_name="wrong.agent"),
        AgentExecutionContext(run_id="run-1", max_steps=1),
        ReferencePingAgent(),
    )

    assert run.state is AgentRunState.FAILED
    assert run.error is not None
    assert run.error.code == "AGENT_EXECUTION_FAILED"
    assert run.steps == ()
    assert service.calls == []


class SequencedInvocationService(ToolInvocationService):
    def __init__(self, outcomes: list[dict[str, Any] | Exception]) -> None:
        self.outcomes = outcomes
        self.calls: list[tuple[str, dict[str, Any]]] = []

    async def invoke(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        self.calls.append((tool_name, arguments))
        outcome = self.outcomes[len(self.calls) - 1]
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


async def test_runtime_retries_tool_execution_error_and_succeeds() -> None:
    result = {"response": "pong"}
    service = SequencedInvocationService([ToolExecutionError("transient"), result])

    run = await AgentRuntime(service).execute(
        AgentTask(task_id="task-1", agent_name="reference.ping"),
        AgentExecutionContext(
            run_id="run-1",
            max_steps=2,
            retry_policy=RetryPolicy(max_attempts=2),
        ),
        ReferencePingAgent(),
    )

    assert run.state is AgentRunState.SUCCEEDED
    assert run.output == result
    assert [step.state for step in run.steps] == [
        AgentStepState.FAILED,
        AgentStepState.SUCCEEDED,
    ]
    assert [step.sequence for step in run.steps] == [1, 2]
    assert len(service.calls) == 2


async def test_runtime_exhausts_retry_attempts() -> None:
    service = SequencedInvocationService(
        [ToolExecutionError("first"), ToolExecutionError("second")]
    )

    run = await AgentRuntime(service).execute(
        AgentTask(task_id="task-1", agent_name="reference.ping"),
        AgentExecutionContext(
            run_id="run-1",
            max_steps=2,
            retry_policy=RetryPolicy(max_attempts=2),
        ),
        ReferencePingAgent(),
    )

    assert run.state is AgentRunState.FAILED
    assert run.error is not None
    assert run.error.code == "AGENT_EXECUTION_FAILED"
    assert [step.state for step in run.steps] == [
        AgentStepState.FAILED,
        AgentStepState.FAILED,
    ]
    assert len(service.calls) == 2


async def test_runtime_retry_cannot_exceed_step_budget() -> None:
    service = SequencedInvocationService([ToolExecutionError("first"), {"response": "pong"}])

    run = await AgentRuntime(service).execute(
        AgentTask(task_id="task-1", agent_name="reference.ping"),
        AgentExecutionContext(
            run_id="run-1",
            max_steps=1,
            retry_policy=RetryPolicy(max_attempts=2),
        ),
        ReferencePingAgent(),
    )

    assert run.state is AgentRunState.FAILED
    assert run.error is not None
    assert run.error.code == "STEP_LIMIT_EXCEEDED"
    assert len(run.steps) == 1
    assert run.steps[0].state is AgentStepState.FAILED
    assert len(service.calls) == 1


async def test_runtime_does_not_retry_non_execution_tool_platform_error() -> None:

    service = SequencedInvocationService(
        [ToolInputValidationError("invalid"), {"response": "pong"}]
    )

    run = await AgentRuntime(service).execute(
        AgentTask(task_id="task-1", agent_name="reference.ping"),
        AgentExecutionContext(
            run_id="run-1",
            max_steps=2,
            retry_policy=RetryPolicy(max_attempts=2),
        ),
        ReferencePingAgent(),
    )

    assert run.state is AgentRunState.FAILED
    assert len(run.steps) == 1
    assert run.steps[0].state is AgentStepState.FAILED
    assert len(service.calls) == 1


async def test_runtime_cancellation_prevents_retry_attempt() -> None:
    token = CancellationToken()

    class CancellingFailureService(ToolInvocationService):
        def __init__(self) -> None:
            self.calls = 0

        async def invoke(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
            del tool_name, arguments
            self.calls += 1
            token.cancel()
            raise ToolExecutionError("transient")

    service = CancellingFailureService()
    run = await AgentRuntime(service).execute(
        AgentTask(task_id="task-1", agent_name="reference.ping"),
        AgentExecutionContext(
            run_id="run-1",
            max_steps=2,
            cancellation=token,
            retry_policy=RetryPolicy(max_attempts=2),
        ),
        ReferencePingAgent(),
    )

    assert run.state is AgentRunState.CANCELLED
    assert run.error is not None
    assert run.error.code == "RUN_CANCELLED"
    assert len(run.steps) == 1
    assert run.steps[0].state is AgentStepState.CANCELLED
    assert service.calls == 1


async def test_runtime_timeout_stops_retry_sequence() -> None:
    class RetryThenDelayService(ToolInvocationService):
        def __init__(self) -> None:
            self.calls = 0

        async def invoke(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
            del tool_name, arguments
            self.calls += 1
            if self.calls == 1:
                raise ToolExecutionError("transient")
            await asyncio.sleep(10.0)
            return {"response": "pong"}

    service = RetryThenDelayService()
    run = await AgentRuntime(service).execute(
        AgentTask(task_id="task-1", agent_name="reference.ping"),
        AgentExecutionContext(
            run_id="run-1",
            max_steps=2,
            timeout_seconds=0.25,
            retry_policy=RetryPolicy(max_attempts=2),
        ),
        ReferencePingAgent(),
    )

    assert run.state is AgentRunState.TIMED_OUT
    assert run.error is not None
    assert run.error.code == "RUN_TIMED_OUT"
    assert [step.state for step in run.steps] == [
        AgentStepState.FAILED,
        AgentStepState.TIMED_OUT,
    ]
    assert service.calls == 2
