"""Enterprise AI Platform MCP server."""

import asyncio
from typing import Any

import mcp.server.stdio
import mcp.types as types
from mcp.server.lowlevel import NotificationOptions, Server
from mcp.server.models import InitializationOptions

from enterprise_ai_api.mcp.adapter import MCPToolAdapter
from enterprise_ai_api.tools.builtins import create_ping_tool
from enterprise_ai_api.tools.discovery import ToolDiscoveryService
from enterprise_ai_api.tools.invocation import ToolInvocationService
from enterprise_ai_api.tools.registry import ToolRegistry

SERVER_NAME = "enterprise-ai-platform"
SERVER_VERSION = "0.2.0"


def build_registry() -> ToolRegistry:
    """Build the application tool registry."""

    registry = ToolRegistry()
    registry.register(create_ping_tool())
    return registry


def build_adapter(
    registry: ToolRegistry | None = None,
) -> MCPToolAdapter:
    """Build the MCP adapter and its application services."""

    active_registry = registry or build_registry()

    return MCPToolAdapter(
        discovery_service=ToolDiscoveryService(active_registry),
        invocation_service=ToolInvocationService(active_registry),
    )


def build_server(
    adapter: MCPToolAdapter | None = None,
) -> Server:
    """Create and configure the MCP server."""

    active_adapter = adapter or build_adapter()
    server = Server(SERVER_NAME)

    @server.list_tools()  # type: ignore[no-untyped-call, untyped-decorator]
    async def list_tools() -> list[types.Tool]:
        tools: list[types.Tool] = await active_adapter.list_tools()
        return tools

    @server.call_tool()  # type: ignore[untyped-decorator]
    async def call_tool(
        name: str,
        arguments: dict[str, Any],
    ) -> types.CallToolResult:
        result: types.CallToolResult = await active_adapter.call_tool(
            name,
            arguments,
        )
        return result

    return server


async def run() -> None:
    """Run the MCP server using the stdio transport."""

    server = build_server()

    async with mcp.server.stdio.stdio_server() as (
        read_stream,
        write_stream,
    ):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name=SERVER_NAME,
                server_version=SERVER_VERSION,
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


def main() -> None:
    """Start the MCP server."""

    asyncio.run(run())


if __name__ == "__main__":
    main()
