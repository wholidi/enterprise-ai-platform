from __future__ import annotations

from typing import Any

from enterprise_ai_api.agents.contracts import AgentTask
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
