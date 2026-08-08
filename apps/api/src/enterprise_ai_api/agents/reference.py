from __future__ import annotations

from typing import Any

from enterprise_ai_api.agents.contracts import AgentTask
from enterprise_ai_api.agents.planning import AgentPlan, PlannedAgent, ToolPlanStep
from enterprise_ai_api.agents.runtime import ToolExecutor


class ReferencePingAgent:
    """Deterministic reference agent that executes exactly one platform.ping step."""

    @property
    def name(self) -> str:
        return "reference.ping"

    async def execute(
        self,
        task: AgentTask,
        execute_tool: ToolExecutor,
    ) -> dict[str, Any]:
        arguments: dict[str, Any] = {}
        if "message" in task.input:
            arguments["message"] = task.input["message"]
        return await execute_tool("platform.ping", arguments)


class ReferencePingPlan:
    """Build a fixed two-step platform.ping plan from task input."""

    def plan(self, task: AgentTask) -> AgentPlan:
        first_arguments: dict[str, object] = {}
        if "message" in task.input:
            first_arguments["message"] = task.input["message"]

        return AgentPlan(
            steps=(
                ToolPlanStep(
                    step_id="ping-1",
                    tool_name="platform.ping",
                    arguments=first_arguments,
                ),
                ToolPlanStep(
                    step_id="ping-2",
                    tool_name="platform.ping",
                    arguments={},
                ),
            )
        )


class ReferencePlannedPingAgent(PlannedAgent):
    """Reference deterministic planned agent with two ordered ping operations."""

    def __init__(self) -> None:
        super().__init__(name="reference.planned-ping", planner=ReferencePingPlan())
