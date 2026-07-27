"""Built-in platform ping tool."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from enterprise_ai_api.tools.contracts import ToolDefinition


class PingInput(BaseModel):
    """Input contract for the platform ping tool."""

    model_config = ConfigDict(extra="forbid")

    message: str = Field(
        default="ping",
        min_length=1,
        max_length=100,
        description="Message echoed in the ping response.",
    )


class PingOutput(BaseModel):
    """Output contract for the platform ping tool."""

    model_config = ConfigDict(extra="forbid")

    message: str
    response: Literal["pong"]
    service: Literal["enterprise-ai-platform"]
    version: str


async def ping_handler(arguments: BaseModel) -> BaseModel:
    """Return a deterministic connectivity response."""

    ping_input = PingInput.model_validate(arguments)

    return PingOutput(
        message=ping_input.message,
        response="pong",
        service="enterprise-ai-platform",
        version="0.2.0",
    )


def create_ping_tool() -> ToolDefinition:
    """Create the built-in platform ping definition."""

    return ToolDefinition(
        name="platform.ping",
        description="Returns a deterministic platform connectivity response.",
        input_model=PingInput,
        output_model=PingOutput,
        handler=ping_handler,
    )
