from enterprise_ai_api.agents.context import AgentExecutionContext
from enterprise_ai_api.agents.contracts import AgentTask
from enterprise_ai_api.agents.reference import ReferencePingAgent
from enterprise_ai_api.agents.runtime import AgentRuntime
from enterprise_ai_api.agents.states import AgentRunState, AgentStepState
from enterprise_ai_api.tools.builtins.ping import create_ping_tool
from enterprise_ai_api.tools.invocation import ToolInvocationService
from enterprise_ai_api.tools.registry import ToolRegistry


async def test_reference_ping_agent_executes_through_tool_invocation_service() -> None:
    registry = ToolRegistry()
    registry.register(create_ping_tool())
    runtime = AgentRuntime(ToolInvocationService(registry))

    run = await runtime.execute(
        AgentTask(
            task_id="task-integration",
            agent_name="reference.ping",
            input={"message": "Sprint 3 Increment 2"},
        ),
        AgentExecutionContext(run_id="run-integration", max_steps=1),
        ReferencePingAgent(),
    )

    assert run.state is AgentRunState.SUCCEEDED
    assert run.output == {
        "message": "Sprint 3 Increment 2",
        "response": "pong",
        "service": "enterprise-ai-platform",
        "version": "0.2.0",
    }
    assert len(run.steps) == 1
    assert run.steps[0].state is AgentStepState.SUCCEEDED
    assert run.steps[0].output == run.output
