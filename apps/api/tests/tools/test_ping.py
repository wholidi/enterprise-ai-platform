"""Tests for the built-in platform ping tool."""

import pytest
from enterprise_ai_api.tools.builtins.ping import (
    PingInput,
    PingOutput,
    create_ping_tool,
    ping_handler,
)
from pydantic import ValidationError


def test_create_ping_tool_returns_expected_contract() -> None:
    tool = create_ping_tool()

    assert tool.name == "platform.ping"
    assert tool.input_model is PingInput
    assert tool.output_model is PingOutput


@pytest.mark.asyncio
async def test_ping_handler_returns_pong() -> None:
    result = await ping_handler(PingInput(message="hello"))

    assert isinstance(result, PingOutput)
    assert result.message == "hello"
    assert result.response == "pong"
    assert result.service == "enterprise-ai-platform"
    assert result.version == "0.2.0"


def test_ping_input_rejects_empty_message() -> None:
    with pytest.raises(ValidationError):
        PingInput(message="")


def test_ping_input_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        PingInput.model_validate(
            {
                "message": "hello",
                "unexpected": "value",
            }
        )
