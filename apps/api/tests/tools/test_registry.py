"""Tests for the in-memory enterprise tool registry."""

from typing import Literal

import pytest
from enterprise_ai_api.tools.contracts import ToolDefinition
from enterprise_ai_api.tools.exceptions import (
    InvalidToolDefinitionError,
    ToolAlreadyRegisteredError,
    ToolNotFoundError,
)
from enterprise_ai_api.tools.registry import ToolRegistry
from pydantic import BaseModel


class EmptyInput(BaseModel):
    pass


class PingOutput(BaseModel):
    response: Literal["pong"]


async def ping_handler(arguments: BaseModel) -> BaseModel:
    del arguments
    return PingOutput(response="pong")


def build_tool(
    name: str = "platform.ping",
    description: str = "Returns pong.",
) -> ToolDefinition:
    return ToolDefinition(
        name=name,
        description=description,
        input_model=EmptyInput,
        output_model=PingOutput,
        handler=ping_handler,
    )


def test_register_and_get_tool() -> None:
    registry = ToolRegistry()
    tool = build_tool()

    registry.register(tool)

    assert registry.get("platform.ping") is tool
    assert registry.contains("platform.ping")


def test_duplicate_tool_registration_is_rejected() -> None:
    registry = ToolRegistry()
    registry.register(build_tool())

    with pytest.raises(
        ToolAlreadyRegisteredError,
        match="already registered",
    ):
        registry.register(build_tool())


def test_unknown_tool_raises_tool_not_found() -> None:
    registry = ToolRegistry()

    with pytest.raises(
        ToolNotFoundError,
        match="not registered",
    ):
        registry.get("platform.missing")


@pytest.mark.parametrize(
    "invalid_name",
    [
        "",
        "ping",
        "Platform.Ping",
        "platform-ping",
        "platform.",
        ".ping",
        "platform.PING",
    ],
)
def test_invalid_tool_name_is_rejected(
    invalid_name: str,
) -> None:
    registry = ToolRegistry()

    with pytest.raises(InvalidToolDefinitionError):
        registry.register(build_tool(name=invalid_name))


def test_empty_description_is_rejected() -> None:
    registry = ToolRegistry()

    with pytest.raises(
        InvalidToolDefinitionError,
        match="descriptions must not be empty",
    ):
        registry.register(build_tool(description="   "))


def test_list_tools_is_sorted_by_name() -> None:
    registry = ToolRegistry()
    registry.register(build_tool(name="planning.get_demand"))
    registry.register(build_tool(name="platform.ping"))
    registry.register(build_tool(name="inventory.get_stock"))

    names = [tool.name for tool in registry.list_tools()]

    assert names == [
        "inventory.get_stock",
        "planning.get_demand",
        "platform.ping",
    ]


def test_list_tools_returns_immutable_tuple() -> None:
    registry = ToolRegistry()
    registry.register(build_tool())

    tools = registry.list_tools()

    assert isinstance(tools, tuple)
