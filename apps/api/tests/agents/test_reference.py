from typing import Any

from enterprise_ai_api.agents.contracts import AgentTask
from enterprise_ai_api.agents.reference import ReferencePingAgent


async def test_reference_ping_agent_requests_platform_ping() -> None:
    calls: list[tuple[str, dict[str, Any]]] = []

    async def execute_tool(tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        calls.append((tool_name, arguments))
        return {"response": "pong"}

    agent = ReferencePingAgent()
    result = await agent.execute(
        AgentTask(
            task_id="task-1",
            agent_name="reference.ping",
            input={"message": "hello"},
        ),
        execute_tool,
    )

    assert agent.name == "reference.ping"
    assert calls == [("platform.ping", {"message": "hello"})]
    assert result == {"response": "pong"}


async def test_reference_ping_agent_uses_ping_default_arguments() -> None:
    captured_arguments: dict[str, Any] | None = None

    async def execute_tool(tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        nonlocal captured_arguments
        assert tool_name == "platform.ping"
        captured_arguments = arguments
        return {"response": "pong"}

    await ReferencePingAgent().execute(
        AgentTask(task_id="task-1", agent_name="reference.ping"),
        execute_tool,
    )

    assert captured_arguments == {}
