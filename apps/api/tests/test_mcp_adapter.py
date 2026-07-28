"""Tests for the MCP tool adapter."""

import json

import pytest
from enterprise_ai_api.mcp.adapter import MCPToolAdapter
from enterprise_ai_api.mcp.server import (
    SERVER_NAME,
    SERVER_VERSION,
    build_adapter,
    build_registry,
    build_server,
)
from enterprise_ai_api.tools.discovery import ToolDiscoveryService
from enterprise_ai_api.tools.invocation import ToolInvocationService
from enterprise_ai_api.tools.registry import ToolRegistry


@pytest.fixture
def adapter() -> MCPToolAdapter:
    registry = build_registry()
    return build_adapter(registry)


@pytest.mark.asyncio
async def test_list_tools_exposes_ping_contract(
    adapter: MCPToolAdapter,
) -> None:
    tools = await adapter.list_tools()

    assert len(tools) == 1

    ping_tool = tools[0]

    assert ping_tool.name == "platform.ping"
    assert ping_tool.description
    assert ping_tool.inputSchema["type"] == "object"
    assert ping_tool.outputSchema is not None
    assert ping_tool.outputSchema["type"] == "object"


@pytest.mark.asyncio
async def test_call_ping_returns_structured_result(
    adapter: MCPToolAdapter,
) -> None:
    result = await adapter.call_tool(
        "platform.ping",
        {"message": "MCP test"},
    )

    assert result.isError is False
    assert result.structuredContent == {
        "message": "MCP test",
        "response": "pong",
        "service": "enterprise-ai-platform",
        "version": "0.2.0",
    }

    text_content = result.content[0]
    assert text_content.type == "text"

    payload = json.loads(text_content.text)
    assert payload == result.structuredContent


@pytest.mark.asyncio
async def test_call_ping_uses_default_arguments(
    adapter: MCPToolAdapter,
) -> None:
    result = await adapter.call_tool("platform.ping", None)

    assert result.isError is False
    assert result.structuredContent is not None
    assert result.structuredContent["message"] == "ping"


@pytest.mark.asyncio
async def test_invalid_input_returns_mcp_tool_error(
    adapter: MCPToolAdapter,
) -> None:
    result = await adapter.call_tool(
        "platform.ping",
        {"message": ""},
    )

    assert result.isError is True
    assert result.structuredContent is not None
    assert result.structuredContent["error"]["code"] == "TOOL_INPUT_INVALID"


@pytest.mark.asyncio
async def test_unknown_tool_returns_mcp_tool_error(
    adapter: MCPToolAdapter,
) -> None:
    result = await adapter.call_tool(
        "platform.missing",
        {},
    )

    assert result.isError is True
    assert result.structuredContent is not None
    assert result.structuredContent["error"]["code"] == "TOOL_NOT_FOUND"


def test_build_registry_registers_ping_tool() -> None:
    registry = build_registry()

    assert registry.contains("platform.ping")


def test_build_adapter_accepts_existing_registry() -> None:
    registry = ToolRegistry()

    adapter = build_adapter(registry)

    assert isinstance(adapter, MCPToolAdapter)


def test_server_metadata() -> None:
    assert SERVER_NAME == "enterprise-ai-platform"
    assert SERVER_VERSION == "0.2.0"


def test_build_server_returns_configured_server() -> None:
    registry = ToolRegistry()
    adapter = MCPToolAdapter(
        discovery_service=ToolDiscoveryService(registry),
        invocation_service=ToolInvocationService(registry),
    )

    server = build_server(adapter)

    assert server.name == SERVER_NAME
