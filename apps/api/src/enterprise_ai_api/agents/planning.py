from __future__ import annotations

from typing import Any, Protocol

from pydantic import BaseModel, ConfigDict, Field

from enterprise_ai_api.agents.contracts import AgentTask
from enterprise_ai_api.agents.runtime import ToolExecutor


class ToolPlanStep(BaseModel):
    """One logical tool operation in a deterministic agent plan."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    step_id: str = Field(min_length=1)
    tool_name: str = Field(min_length=1)
    arguments: dict[str, object] = Field(default_factory=dict)


class AgentPlan(BaseModel):
    """Immutable ordered tool plan produced before deterministic execution."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    steps: tuple[ToolPlanStep, ...] = Field(min_length=1)


class DeterministicPlanner(Protocol):
    """Produce a deterministic, side-effect-free plan for one agent task."""

    def plan(self, task: AgentTask) -> AgentPlan: ...


class PlannedAgent:
    """Execute an immutable deterministic plan through the runtime ToolExecutor."""

    def __init__(self, name: str, planner: DeterministicPlanner) -> None:
        if not name:
            raise ValueError("name must not be empty")
        self._name = name
        self._planner = planner

    @property
    def name(self) -> str:
        return self._name

    async def execute(
        self,
        task: AgentTask,
        execute_tool: ToolExecutor,
    ) -> dict[str, Any]:
        plan = self._planner.plan(task)
        results: list[dict[str, Any]] = []

        for plan_step in plan.steps:
            result = await execute_tool(plan_step.tool_name, dict(plan_step.arguments))
            results.append(result)

        return {"results": results}
