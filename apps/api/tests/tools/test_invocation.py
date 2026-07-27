"""Tests for protocol-independent tool invocation."""

import pytest
from enterprise_ai_api.tools.builtins.ping import create_ping_tool
from enterprise_ai_api.tools.contracts import ToolDefinition
from enterprise_ai_api.tools.exceptions import (
    ToolExecutionError,
    ToolInputValidationError,
    ToolOutputValidationError,
)
from enterprise_ai_api.tools.invocation import ToolInvocationService
from enterprise_ai_api.tools.registry import ToolRegistry
from pydantic import BaseModel


@pytest.fixture
def invocation_service() -> ToolInvocationService:
    registry = ToolRegistry()
    registry.register(create_ping_tool())
    return ToolInvocationService(registry)


@pytest.mark.asyncio
async def test_invoke_ping_tool(
    invocation_service: ToolInvocationService,
) -> None:
    result = await invocation_service.invoke(
        "platform.ping",
        {"message": "hello"},
    )

    assert result == {
        "message": "hello",
        "response": "pong",
        "service": "enterprise-ai-platform",
        "version": "0.2.0",
    }


@pytest.mark.asyncio
async def test_invalid_input_is_rejected(
    invocation_service: ToolInvocationService,
) -> None:
    with pytest.raises(ToolInputValidationError):
        await invocation_service.invoke(
            "platform.ping",
            {"message": ""},
        )


class EmptyInput(BaseModel):
    pass


class ExpectedOutput(BaseModel):
    value: str


class InvalidOutput(BaseModel):
    unexpected: str


async def failing_handler(arguments: BaseModel) -> BaseModel:
    del arguments
    raise RuntimeError("unexpected failure")


async def invalid_output_handler(arguments: BaseModel) -> BaseModel:
    del arguments
    return InvalidOutput(unexpected="value")


@pytest.mark.asyncio
async def test_handler_failure_is_normalized() -> None:
    registry = ToolRegistry()
    registry.register(
        ToolDefinition(
            name="platform.failure",
            description="Always fails.",
            input_model=EmptyInput,
            output_model=ExpectedOutput,
            handler=failing_handler,
        )
    )

    service = ToolInvocationService(registry)

    with pytest.raises(ToolExecutionError):
        await service.invoke("platform.failure", {})


@pytest.mark.asyncio
async def test_invalid_output_is_rejected() -> None:
    registry = ToolRegistry()
    registry.register(
        ToolDefinition(
            name="platform.invalid_output",
            description="Returns invalid output.",
            input_model=EmptyInput,
            output_model=ExpectedOutput,
            handler=invalid_output_handler,
        )
    )

    service = ToolInvocationService(registry)

    with pytest.raises(ToolOutputValidationError):
        await service.invoke("platform.invalid_output", {})
