"""In-memory registry for enterprise tool definitions."""

import re

from pydantic import BaseModel

from enterprise_ai_api.tools.contracts import ToolDefinition
from enterprise_ai_api.tools.exceptions import (
    InvalidToolDefinitionError,
    ToolAlreadyRegisteredError,
    ToolNotFoundError,
)

_TOOL_NAME_PATTERN = re.compile(r"^[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)+$")


class ToolRegistry:
    """Stores and retrieves immutable enterprise tool definitions."""

    def __init__(self) -> None:
        self._tools: dict[str, ToolDefinition] = {}

    def register(self, tool: ToolDefinition) -> None:
        """Register a tool definition.

        Raises:
            InvalidToolDefinitionError: If the definition is invalid.
            ToolAlreadyRegisteredError: If its name already exists.
        """

        self._validate_definition(tool)

        if tool.name in self._tools:
            raise ToolAlreadyRegisteredError(f"Tool '{tool.name}' is already registered.")

        self._tools[tool.name] = tool

    def get(self, name: str) -> ToolDefinition:
        """Return a tool by name.

        Raises:
            ToolNotFoundError: If no tool exists under the requested name.
        """

        try:
            return self._tools[name]
        except KeyError as exc:
            raise ToolNotFoundError(f"Tool '{name}' is not registered.") from exc

    def list_tools(self) -> tuple[ToolDefinition, ...]:
        """Return registered tools in deterministic name order."""

        return tuple(self._tools[name] for name in sorted(self._tools))

    def contains(self, name: str) -> bool:
        """Return whether a tool name is registered."""

        return name in self._tools

    @staticmethod
    def _validate_definition(tool: ToolDefinition) -> None:
        if not _TOOL_NAME_PATTERN.fullmatch(tool.name):
            raise InvalidToolDefinitionError(
                "Tool names must use a lowercase namespace and name, for example 'platform.ping'."
            )

        if not tool.description.strip():
            raise InvalidToolDefinitionError("Tool descriptions must not be empty.")

        if not issubclass(tool.input_model, BaseModel):
            raise InvalidToolDefinitionError("input_model must inherit from BaseModel.")

        if not issubclass(tool.output_model, BaseModel):
            raise InvalidToolDefinitionError("output_model must inherit from BaseModel.")
