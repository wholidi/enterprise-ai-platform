"""Tests for enterprise tool contracts."""

from typing import Literal

from enterprise_ai_api.tools.contracts import ToolDefinition
from pydantic import BaseModel, Field


class ExampleInput(BaseModel):
    message: str = Field(min_length=1)


class ExampleOutput(BaseModel):
    response: Literal["pong"]


async def example_handler(arguments: BaseModel) -> BaseModel:
    del arguments
    return ExampleOutput(response="pong")


def test_tool_definition_generates_input_schema() -> None:
    tool = ToolDefinition(
        name="platform.ping",
        description="Returns a deterministic ping response.",
        input_model=ExampleInput,
        output_model=ExampleOutput,
        handler=example_handler,
    )

    schema = tool.input_schema

    assert schema["type"] == "object"
    assert "message" in schema["properties"]


def test_tool_definition_generates_output_schema() -> None:
    tool = ToolDefinition(
        name="platform.ping",
        description="Returns a deterministic ping response.",
        input_model=ExampleInput,
        output_model=ExampleOutput,
        handler=example_handler,
    )

    schema = tool.output_schema

    assert schema["type"] == "object"
    assert "response" in schema["properties"]
