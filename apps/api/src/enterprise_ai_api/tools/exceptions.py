"""Exceptions raised by the enterprise tool platform."""


class ToolPlatformError(Exception):
    """Base exception for tool-platform failures."""


class InvalidToolDefinitionError(ToolPlatformError):
    """Raised when a tool definition violates registry requirements."""


class ToolAlreadyRegisteredError(ToolPlatformError):
    """Raised when a tool name is registered more than once."""


class ToolNotFoundError(ToolPlatformError):
    """Raised when a requested tool does not exist in the registry."""


class ToolInputValidationError(ToolPlatformError):
    """Raised when supplied tool input violates its contract."""


class ToolOutputValidationError(ToolPlatformError):
    """Raised when tool output violates its declared contract."""


class ToolExecutionError(ToolPlatformError):
    """Raised when a tool handler fails unexpectedly."""
