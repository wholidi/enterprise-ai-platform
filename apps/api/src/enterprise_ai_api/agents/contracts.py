from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from enterprise_ai_api.agents.states import AgentRunState, AgentStepKind, AgentStepState


class AgentError(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    code: str = Field(min_length=1)
    message: str = Field(min_length=1)


class AgentTask(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    task_id: str = Field(min_length=1)
    agent_name: str = Field(min_length=1)
    input: dict[str, object] = Field(default_factory=dict)


class AgentStep(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    step_id: str = Field(min_length=1)
    run_id: str = Field(min_length=1)
    sequence: int = Field(ge=1)
    kind: AgentStepKind
    state: AgentStepState = AgentStepState.PENDING
    started_at: datetime | None = None
    completed_at: datetime | None = None
    output: dict[str, object] | None = None
    error: AgentError | None = None


class AgentRun(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    run_id: str = Field(min_length=1)
    task_id: str = Field(min_length=1)
    state: AgentRunState = AgentRunState.PENDING
    steps: tuple[AgentStep, ...] = ()
    started_at: datetime | None = None
    completed_at: datetime | None = None
    output: dict[str, object] | None = None
    error: AgentError | None = None
