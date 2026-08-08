from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from typing import Any, Protocol

from enterprise_ai_api.agents.context import AgentExecutionContext
from enterprise_ai_api.agents.contracts import AgentError, AgentRun, AgentStep, AgentTask
from enterprise_ai_api.agents.exceptions import (
    AgentCancelledError,
    AgentExecutionError,
    AgentStepLimitExceededError,
    AgentTimeoutError,
)
from enterprise_ai_api.agents.states import (
    AgentRunState,
    AgentStepKind,
    AgentStepState,
    validate_run_transition,
    validate_step_transition,
)
from enterprise_ai_api.tools.exceptions import ToolPlatformError
from enterprise_ai_api.tools.invocation import ToolInvocationService

ToolExecutor = Callable[[str, dict[str, Any]], Awaitable[dict[str, Any]]]


class ExecutableAgent(Protocol):
    """Smallest agent contract required by the runtime execution path."""

    @property
    def name(self) -> str: ...

    async def execute(self, task: AgentTask, execute_tool: ToolExecutor) -> dict[str, Any]: ...


class AgentRuntime:
    """Execute bounded agents exclusively through ToolInvocationService."""

    def __init__(self, invocation_service: ToolInvocationService) -> None:
        self._invocation_service = invocation_service

    async def execute(
        self,
        task: AgentTask,
        context: AgentExecutionContext,
        agent: ExecutableAgent,
    ) -> AgentRun:
        run = AgentRun(run_id=context.run_id, task_id=task.task_id)
        steps: list[AgentStep] = []

        if context.cancellation.is_cancelled:
            return self._finish_run(
                run,
                AgentRunState.CANCELLED,
                error=AgentError(code="RUN_CANCELLED", message="Agent run was cancelled."),
            )

        run = self._start_run(run)

        async def execute_tool(tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
            if context.cancellation.is_cancelled:
                raise AgentCancelledError("Agent run was cancelled.")
            if len(steps) >= context.max_steps:
                raise AgentStepLimitExceededError(
                    f"Agent run exceeded max_steps={context.max_steps}."
                )

            step = AgentStep(
                step_id=f"{context.run_id}:step:{len(steps) + 1}",
                run_id=context.run_id,
                sequence=len(steps) + 1,
                kind=AgentStepKind.TOOL,
            )
            step = self._start_step(step)
            steps.append(step)

            invocation_task = asyncio.create_task(
                self._invocation_service.invoke(tool_name, arguments)
            )
            cancellation_task = asyncio.create_task(context.cancellation.wait())

            try:
                done, _ = await asyncio.wait(
                    {invocation_task, cancellation_task},
                    return_when=asyncio.FIRST_COMPLETED,
                )
                if cancellation_task in done:
                    invocation_task.cancel()
                    await asyncio.gather(invocation_task, return_exceptions=True)
                    steps[-1] = self._finish_step(
                        steps[-1],
                        AgentStepState.CANCELLED,
                        error=AgentError(
                            code="RUN_CANCELLED",
                            message="Agent run was cancelled.",
                        ),
                    )
                    raise AgentCancelledError("Agent run was cancelled.")

                cancellation_task.cancel()
                await asyncio.gather(cancellation_task, return_exceptions=True)
                result = await invocation_task
            except ToolPlatformError as exc:
                steps[-1] = self._finish_step(
                    steps[-1],
                    AgentStepState.FAILED,
                    error=AgentError(
                        code="TOOL_INVOCATION_FAILED",
                        message="Tool invocation failed.",
                    ),
                )
                raise AgentExecutionError("Tool invocation failed.") from exc
            except asyncio.CancelledError:
                if not invocation_task.done():
                    invocation_task.cancel()
                cancellation_task.cancel()
                await asyncio.gather(
                    invocation_task,
                    cancellation_task,
                    return_exceptions=True,
                )
                if steps[-1].state is AgentStepState.RUNNING:
                    steps[-1] = self._finish_step(
                        steps[-1],
                        AgentStepState.TIMED_OUT,
                        error=AgentError(
                            code="RUN_TIMED_OUT",
                            message="Agent run timed out.",
                        ),
                    )
                raise
            finally:
                if not cancellation_task.done():
                    cancellation_task.cancel()

            steps[-1] = self._finish_step(
                steps[-1],
                AgentStepState.SUCCEEDED,
                output=result,
            )
            return result

        try:
            if task.agent_name != agent.name:
                raise AgentExecutionError(
                    f"Task agent_name '{task.agent_name}' does not match agent '{agent.name}'."
                )

            if context.timeout_seconds is None:
                output = await agent.execute(task, execute_tool)
            else:
                try:
                    output = await asyncio.wait_for(
                        agent.execute(task, execute_tool),
                        timeout=context.timeout_seconds,
                    )
                except TimeoutError as exc:
                    raise AgentTimeoutError("Agent run timed out.") from exc
        except AgentCancelledError:
            return self._finish_run(
                run,
                AgentRunState.CANCELLED,
                steps=steps,
                error=AgentError(code="RUN_CANCELLED", message="Agent run was cancelled."),
            )
        except AgentTimeoutError:
            return self._finish_run(
                run,
                AgentRunState.TIMED_OUT,
                steps=steps,
                error=AgentError(code="RUN_TIMED_OUT", message="Agent run timed out."),
            )
        except AgentStepLimitExceededError:
            return self._finish_run(
                run,
                AgentRunState.FAILED,
                steps=steps,
                error=AgentError(
                    code="STEP_LIMIT_EXCEEDED",
                    message="Agent run exceeded its configured step budget.",
                ),
            )
        except AgentExecutionError as exc:
            return self._finish_run(
                run,
                AgentRunState.FAILED,
                steps=steps,
                error=AgentError(code="AGENT_EXECUTION_FAILED", message=str(exc)),
            )
        except Exception:
            return self._finish_run(
                run,
                AgentRunState.FAILED,
                steps=steps,
                error=AgentError(
                    code="AGENT_EXECUTION_FAILED",
                    message="Agent execution failed.",
                ),
            )

        if context.cancellation.is_cancelled:
            return self._finish_run(
                run,
                AgentRunState.CANCELLED,
                steps=steps,
                error=AgentError(code="RUN_CANCELLED", message="Agent run was cancelled."),
            )

        return self._finish_run(
            run,
            AgentRunState.SUCCEEDED,
            steps=steps,
            output=output,
        )

    @staticmethod
    def _start_run(run: AgentRun) -> AgentRun:
        validate_run_transition(run.state, AgentRunState.RUNNING)
        return run.model_copy(
            update={"state": AgentRunState.RUNNING, "started_at": datetime.now(UTC)}
        )

    @staticmethod
    def _finish_run(
        run: AgentRun,
        state: AgentRunState,
        *,
        steps: list[AgentStep] | None = None,
        output: dict[str, Any] | None = None,
        error: AgentError | None = None,
    ) -> AgentRun:
        validate_run_transition(run.state, state)
        return run.model_copy(
            update={
                "state": state,
                "steps": tuple(steps or ()),
                "completed_at": datetime.now(UTC),
                "output": output,
                "error": error,
            }
        )

    @staticmethod
    def _start_step(step: AgentStep) -> AgentStep:
        validate_step_transition(step.state, AgentStepState.RUNNING)
        return step.model_copy(
            update={"state": AgentStepState.RUNNING, "started_at": datetime.now(UTC)}
        )

    @staticmethod
    def _finish_step(
        step: AgentStep,
        state: AgentStepState,
        *,
        output: dict[str, Any] | None = None,
        error: AgentError | None = None,
    ) -> AgentStep:
        validate_step_transition(step.state, state)
        return step.model_copy(
            update={
                "state": state,
                "completed_at": datetime.now(UTC),
                "output": output,
                "error": error,
            }
        )
