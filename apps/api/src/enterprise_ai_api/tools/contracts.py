"""Core contracts for enterprise tools."""

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import TypeAlias

from pydantic import BaseModel

ToolHandler: TypeAlias = Callable[[BaseModel], Awaitable[BaseModel]]


@dataclass(frozen=True, slots=True)
class ToolDefinition:
    """Describes a tool that can be discovered and invoked.

    The input and output models are the authoritative tool contracts.
    Their JSON schemas can later be exposed through MCP.
    """

    name: str
    description: str
    input_model: type[BaseModel]
    output_model: type[BaseModel]
    handler: ToolHandler

    @property
    def input_schema(self) -> dict[str, object]:
        """Return the JSON Schema for the tool input."""

        return self.input_model.model_json_schema()

    @property
    def output_schema(self) -> dict[str, object]:
        """Return the JSON Schema for the tool output."""

        return self.output_model.model_json_schema()
