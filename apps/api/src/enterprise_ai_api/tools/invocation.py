"""Protocol-independent tool invocation services."""

from typing import Any

from pydantic import ValidationError

from enterprise_ai_api.tools.exceptions import (
    ToolExecutionError,
    ToolInputValidationError,
    ToolOutputValidationError,
    ToolPlatformError,
)
from enterprise_ai_api.tools.registry import ToolRegistry


class ToolInvocationService:
    """Validate and execute registered enterprise tools."""

    def __init__(self, registry: ToolRegistry) -> None:
        self._registry = registry

    async def invoke(
        self,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> dict[str, Any]:
        """Invoke a tool using validated input and output contracts."""

        tool = self._registry.get(tool_name)

        try:
            validated_input = tool.input_model.model_validate(arguments)
        except ValidationError as exc:
            raise ToolInputValidationError(
                f"Input validation failed for tool '{tool_name}'."
            ) from exc

        try:
            raw_output = await tool.handler(validated_input)
        except ToolPlatformError:
            raise
        except Exception as exc:
            raise ToolExecutionError(f"Execution failed for tool '{tool_name}'.") from exc

        try:
            validated_output = tool.output_model.model_validate(raw_output)
        except ValidationError as exc:
            raise ToolOutputValidationError(
                f"Output validation failed for tool '{tool_name}'."
            ) from exc

        return validated_output.model_dump()
