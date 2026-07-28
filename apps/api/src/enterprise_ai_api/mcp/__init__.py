"""Model Context Protocol integration."""

from enterprise_ai_api.mcp.adapter import MCPToolAdapter
from enterprise_ai_api.mcp.server import (
    SERVER_NAME,
    SERVER_VERSION,
    build_adapter,
    build_registry,
    build_server,
)

__all__ = [
    "MCPToolAdapter",
    "SERVER_NAME",
    "SERVER_VERSION",
    "build_adapter",
    "build_registry",
    "build_server",
]
