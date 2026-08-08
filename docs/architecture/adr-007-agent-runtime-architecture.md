# ADR-007: Agent Runtime Architecture

## Status

Accepted for Sprint 3 Increment 1.

## Context

Sprint 2 established a protocol-independent enterprise tool platform. Tool lookup, input validation,
handler execution, output validation, and exception normalization are centralized in
`ToolInvocationService`. MCP is a transport adapter over that platform.

Sprint 3 introduces an Agent Runtime without coupling the tool platform to agents or MCP.

## Decision

The Agent Runtime is a protocol-independent orchestration layer above `ToolInvocationService`.

Dependency direction:

```text
Agent Runtime
    |
    v
ToolInvocationService
    |
    v
ToolRegistry
    |
    v
Enterprise Tools
```

The Agent Runtime must not resolve tools from `ToolRegistry`, inspect `ToolDefinition.handler`, or
invoke handlers directly. All tool execution must cross the existing `ToolInvocationService`
boundary.

MCP and Agent Runtime are sibling consumers of the protocol-independent tool platform.

## Consequences

- Tool validation and execution semantics remain centralized.
- Agent orchestration can evolve independently of MCP.
- Tool handlers remain independently testable.
- Agent tests can substitute or mock `ToolInvocationService` without exposing registry internals.
- A future LLM or planning engine can be added above the same runtime boundary without changing the
  tool platform.
