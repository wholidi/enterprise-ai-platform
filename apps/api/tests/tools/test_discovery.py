"""Tests for protocol-independent tool discovery."""

from enterprise_ai_api.tools.builtins.ping import create_ping_tool
from enterprise_ai_api.tools.discovery import ToolDiscoveryService
from enterprise_ai_api.tools.registry import ToolRegistry


def test_discovery_returns_registered_tool() -> None:
    registry = ToolRegistry()
    registry.register(create_ping_tool())

    descriptors = ToolDiscoveryService(registry).list_tools()

    assert len(descriptors) == 1
    assert descriptors[0].name == "platform.ping"
    assert descriptors[0].input_schema["type"] == "object"
    assert descriptors[0].output_schema["type"] == "object"


def test_discovery_does_not_expose_handler() -> None:
    registry = ToolRegistry()
    registry.register(create_ping_tool())

    descriptor = ToolDiscoveryService(registry).list_tools()[0]

    assert not hasattr(descriptor, "handler")
