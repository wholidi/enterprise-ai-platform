"""MCP protocol adapter for the enterprise tool platform."""

import json
from typing import Any

import mcp.types as types

from enterprise_ai_api.tools.discovery import ToolDiscoveryService
from enterprise_ai_api.tools.exceptions import (
    ToolExecutionError,
    ToolInputValidationError,
    ToolNotFoundError,
    ToolOutputValidationError,
)
from enterprise_ai_api.tools.invocation import ToolInvocationService


class MCPToolAdapter:
    """Translate MCP tool operations into platform services."""

    def __init__(
        self,
        discovery_service: ToolDiscoveryService,
        invocation_service: ToolInvocationService,
    ) -> None:
        self._discovery_service = discovery_service
        self._invocation_service = invocation_service

    async def list_tools(self) -> list[types.Tool]:
        """Return registered platform tools as MCP tool definitions."""

        return [
            types.Tool(
                name=descriptor.name,
                description=descriptor.description,
                inputSchema=descriptor.input_schema,
                outputSchema=descriptor.output_schema,
            )
            for descriptor in self._discovery_service.list_tools()
        ]

    async def call_tool(
        self,
        name: str,
        arguments: dict[str, Any] | None,
    ) -> types.CallToolResult:
        """Invoke a platform tool and convert its result to MCP."""

        try:
            result = await self._invocation_service.invoke(
                tool_name=name,
                arguments=arguments or {},
            )
        except ToolNotFoundError as exc:
            return self._error_result("TOOL_NOT_FOUND", str(exc))
        except ToolInputValidationError as exc:
            return self._error_result("TOOL_INPUT_INVALID", str(exc))
        except ToolOutputValidationError as exc:
            return self._error_result("TOOL_OUTPUT_INVALID", str(exc))
        except ToolExecutionError as exc:
            return self._error_result("TOOL_EXECUTION_FAILED", str(exc))

        return types.CallToolResult(
            content=[
                types.TextContent(
                    type="text",
                    text=json.dumps(result, sort_keys=True),
                )
            ],
            structuredContent=result,
            isError=False,
        )

    @staticmethod
    def _error_result(
        code: str,
        message: str,
    ) -> types.CallToolResult:
        """Create a predictable MCP tool error result."""

        error = {
            "code": code,
            "message": message,
        }

        return types.CallToolResult(
            content=[
                types.TextContent(
                    type="text",
                    text=json.dumps(error, sort_keys=True),
                )
            ],
            structuredContent={"error": error},
            isError=True,
        )
