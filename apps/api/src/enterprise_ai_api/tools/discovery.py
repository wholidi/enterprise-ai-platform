"""Protocol-independent tool discovery services."""

from dataclasses import dataclass

from enterprise_ai_api.tools.registry import ToolRegistry


@dataclass(frozen=True, slots=True)
class ToolDescriptor:
    """Public description of a registered tool."""

    name: str
    description: str
    input_schema: dict[str, object]
    output_schema: dict[str, object]


class ToolDiscoveryService:
    """Exposes registered tool contracts without execution handlers."""

    def __init__(self, registry: ToolRegistry) -> None:
        self._registry = registry

    def list_tools(self) -> tuple[ToolDescriptor, ...]:
        """Return all discoverable tools in deterministic order."""

        return tuple(
            ToolDescriptor(
                name=tool.name,
                description=tool.description,
                input_schema=tool.input_schema,
                output_schema=tool.output_schema,
            )
            for tool in self._registry.list_tools()
        )
