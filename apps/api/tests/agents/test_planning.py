from __future__ import annotations

import asyncio
from typing import Any

import pytest
from enterprise_ai_api.agents.context import AgentExecutionContext, CancellationToken
from enterprise_ai_api.agents.contracts import AgentTask
from enterprise_ai_api.agents.planning import AgentPlan, PlannedAgent, ToolPlanStep
from enterprise_ai_api.agents.reference import ReferencePlannedPingAgent
from enterprise_ai_api.agents.retry import RetryPolicy
from enterprise_ai_api.agents.runtime import AgentRuntime, ToolExecutor
from enterprise_ai_api.agents.states import AgentRunState, AgentStepKind, AgentStepState
from enterprise_ai_api.tools.exceptions import ToolExecutionError, ToolInputValidationError
from enterprise_ai_api.tools.invocation import ToolInvocationService
from pydantic import ValidationError


class RecordingPlanner:
    def __init__(self, plan: AgentPlan) -> None:
        self.plan_value = plan
        self.tasks: list[AgentTask] = []

    def plan(self, task: AgentTask) -> AgentPlan:
        self.tasks.append(task)
        return self.plan_value


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


def two_step_plan() -> AgentPlan:
    return AgentPlan(
        steps=(
            ToolPlanStep(step_id="one", tool_name="tool.one", arguments={"value": 1}),
            ToolPlanStep(step_id="two", tool_name="tool.two", arguments={"value": 2}),
        )
    )


def test_tool_plan_step_contract_is_frozen_and_validated() -> None:
    step = ToolPlanStep(step_id="one", tool_name="tool.one")
    assert step.arguments == {}

    with pytest.raises(ValidationError):
        ToolPlanStep(step_id="", tool_name="tool.one")
    with pytest.raises(ValidationError):
        ToolPlanStep(step_id="one", tool_name="")
    with pytest.raises(ValidationError):
        step.tool_name = "other"


def test_agent_plan_requires_ordered_non_empty_steps_and_is_frozen() -> None:
    plan = two_step_plan()
    assert [step.step_id for step in plan.steps] == ["one", "two"]

    with pytest.raises(ValidationError):
        AgentPlan(steps=())
    with pytest.raises(ValidationError):
        plan.steps = ()


async def test_planned_agent_executes_declared_steps_in_order() -> None:
    task = AgentTask(task_id="task-1", agent_name="test.planned")
    planner = RecordingPlanner(two_step_plan())
    agent = PlannedAgent("test.planned", planner)
    calls: list[tuple[str, dict[str, Any]]] = []

    async def execute_tool(tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        calls.append((tool_name, arguments))
        return {"tool": tool_name}

    output = await agent.execute(task, execute_tool)

    assert planner.tasks == [task]
    assert calls == [("tool.one", {"value": 1}), ("tool.two", {"value": 2})]
    assert output == {"results": [{"tool": "tool.one"}, {"tool": "tool.two"}]}


async def test_reference_planned_agent_executes_two_runtime_steps() -> None:
    first = {"response": "pong-1"}
    second = {"response": "pong-2"}
    service = SequencedInvocationService([first, second])

    run = await AgentRuntime(service).execute(
        AgentTask(
            task_id="task-1",
            agent_name="reference.planned-ping",
            input={"message": "hello"},
        ),
        AgentExecutionContext(run_id="run-1", max_steps=2),
        ReferencePlannedPingAgent(),
    )

    assert run.state is AgentRunState.SUCCEEDED
    assert run.output == {"results": [first, second]}
    assert [step.sequence for step in run.steps] == [1, 2]
    assert [step.kind for step in run.steps] == [AgentStepKind.TOOL, AgentStepKind.TOOL]
    assert [step.state for step in run.steps] == [
        AgentStepState.SUCCEEDED,
        AgentStepState.SUCCEEDED,
    ]
    assert service.calls == [
        ("platform.ping", {"message": "hello"}),
        ("platform.ping", {}),
    ]


async def test_retry_creates_new_runtime_step_then_plan_advances() -> None:
    service = SequencedInvocationService(
        [ToolExecutionError("transient"), {"response": "one"}, {"response": "two"}]
    )
    agent = PlannedAgent("test.planned", RecordingPlanner(two_step_plan()))

    run = await AgentRuntime(service).execute(
        AgentTask(task_id="task-1", agent_name="test.planned"),
        AgentExecutionContext(
            run_id="run-1",
            max_steps=3,
            retry_policy=RetryPolicy(max_attempts=2),
        ),
        agent,
    )

    assert run.state is AgentRunState.SUCCEEDED
    assert [step.state for step in run.steps] == [
        AgentStepState.FAILED,
        AgentStepState.SUCCEEDED,
        AgentStepState.SUCCEEDED,
    ]
    assert [step.sequence for step in run.steps] == [1, 2, 3]
    assert len(service.calls) == 3


async def test_retry_exhaustion_prevents_later_plan_step() -> None:
    service = SequencedInvocationService(
        [ToolExecutionError("first"), ToolExecutionError("second")]
    )
    agent = PlannedAgent("test.planned", RecordingPlanner(two_step_plan()))

    run = await AgentRuntime(service).execute(
        AgentTask(task_id="task-1", agent_name="test.planned"),
        AgentExecutionContext(
            run_id="run-1",
            max_steps=3,
            retry_policy=RetryPolicy(max_attempts=2),
        ),
        agent,
    )

    assert run.state is AgentRunState.FAILED
    assert [step.state for step in run.steps] == [AgentStepState.FAILED, AgentStepState.FAILED]
    assert service.calls == [("tool.one", {"value": 1}), ("tool.one", {"value": 1})]


async def test_non_retryable_failure_prevents_later_plan_step() -> None:
    service = SequencedInvocationService(
        [ToolInputValidationError("invalid"), {"response": "unused"}]
    )
    agent = PlannedAgent("test.planned", RecordingPlanner(two_step_plan()))

    run = await AgentRuntime(service).execute(
        AgentTask(task_id="task-1", agent_name="test.planned"),
        AgentExecutionContext(
            run_id="run-1",
            max_steps=3,
            retry_policy=RetryPolicy(max_attempts=2),
        ),
        agent,
    )

    assert run.state is AgentRunState.FAILED
    assert len(run.steps) == 1
    assert run.steps[0].state is AgentStepState.FAILED
    assert service.calls == [("tool.one", {"value": 1})]


async def test_retry_consumption_can_exhaust_budget_before_next_plan_step() -> None:
    service = SequencedInvocationService(
        [ToolExecutionError("transient"), {"response": "one"}]
    )
    agent = PlannedAgent("test.planned", RecordingPlanner(two_step_plan()))

    run = await AgentRuntime(service).execute(
        AgentTask(task_id="task-1", agent_name="test.planned"),
        AgentExecutionContext(
            run_id="run-1",
            max_steps=2,
            retry_policy=RetryPolicy(max_attempts=2),
        ),
        agent,
    )

    assert run.state is AgentRunState.FAILED
    assert run.error is not None
    assert run.error.code == "STEP_LIMIT_EXCEEDED"
    assert [step.state for step in run.steps] == [AgentStepState.FAILED, AgentStepState.SUCCEEDED]
    assert len(service.calls) == 2


async def test_cancellation_during_plan_prevents_later_plan_step() -> None:
    token = CancellationToken()

    class CancellingService(ToolInvocationService):
        def __init__(self) -> None:
            self.calls = 0

        async def invoke(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
            del tool_name, arguments
            self.calls += 1
            token.cancel()
            await asyncio.sleep(0)
            return {"response": "unused"}

    service = CancellingService()
    agent = PlannedAgent("test.planned", RecordingPlanner(two_step_plan()))

    run = await AgentRuntime(service).execute(
        AgentTask(task_id="task-1", agent_name="test.planned"),
        AgentExecutionContext(run_id="run-1", max_steps=2, cancellation=token),
        agent,
    )

    assert run.state is AgentRunState.CANCELLED
    assert len(run.steps) == 1
    assert run.steps[0].state is AgentStepState.CANCELLED
    assert service.calls == 1


async def test_timeout_on_later_plan_step_preserves_earlier_terminal_step() -> None:
    class DelaySecondService(ToolInvocationService):
        def __init__(self) -> None:
            self.calls = 0

        async def invoke(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
            del tool_name, arguments
            self.calls += 1
            if self.calls == 1:
                return {"response": "one"}
            await asyncio.sleep(10.0)
            return {"response": "two"}

    service = DelaySecondService()
    agent = PlannedAgent("test.planned", RecordingPlanner(two_step_plan()))

    run = await AgentRuntime(service).execute(
        AgentTask(task_id="task-1", agent_name="test.planned"),
        AgentExecutionContext(run_id="run-1", max_steps=2, timeout_seconds=0.25),
        agent,
    )

    assert run.state is AgentRunState.TIMED_OUT
    assert [step.state for step in run.steps] == [
        AgentStepState.SUCCEEDED,
        AgentStepState.TIMED_OUT,
    ]
    assert service.calls == 2


async def test_planner_failure_is_normalized_without_tool_steps() -> None:
    class FailingPlanner:
        def plan(self, task: AgentTask) -> AgentPlan:
            del task
            raise RuntimeError("boom")

    service = SequencedInvocationService([])
    agent = PlannedAgent("test.planned", FailingPlanner())

    run = await AgentRuntime(service).execute(
        AgentTask(task_id="task-1", agent_name="test.planned"),
        AgentExecutionContext(run_id="run-1", max_steps=2),
        agent,
    )

    assert run.state is AgentRunState.FAILED
    assert run.error is not None
    assert run.error.code == "AGENT_EXECUTION_FAILED"
    assert run.steps == ()
    assert service.calls == []


async def test_agent_name_mismatch_skips_planner_and_tools() -> None:
    planner = RecordingPlanner(two_step_plan())
    service = SequencedInvocationService([])
    agent = PlannedAgent("test.planned", planner)

    run = await AgentRuntime(service).execute(
        AgentTask(task_id="task-1", agent_name="wrong.agent"),
        AgentExecutionContext(run_id="run-1", max_steps=2),
        agent,
    )

    assert run.state is AgentRunState.FAILED
    assert planner.tasks == []
    assert service.calls == []


async def test_planned_agent_depends_only_on_supplied_tool_executor() -> None:
    planner = RecordingPlanner(two_step_plan())
    agent = PlannedAgent("test.planned", planner)
    calls: list[str] = []

    async def execute_tool(tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        del arguments
        calls.append(tool_name)
        return {"ok": True}

    executor: ToolExecutor = execute_tool
    await agent.execute(AgentTask(task_id="task-1", agent_name="test.planned"), executor)

    assert calls == ["tool.one", "tool.two"]
