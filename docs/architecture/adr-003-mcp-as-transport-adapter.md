# ADR-003: MCP as a Transport Adapter

## Status

Accepted

## Context

The platform must expose tools through MCP while allowing future
clients such as REST APIs, agents, CLIs, evaluation runners, and
scheduled processes to use the same tool platform.

## Decision

MCP will be implemented as an adapter over protocol-independent
tool discovery and invocation services.

The core tool platform must not depend on MCP types or MCP sessions.

## Consequences

### Positive

- Tools can be reused outside MCP.
- Agent Runtime can invoke tools directly.
- Testing is simpler.
- MCP SDK changes are isolated.

### Negative

- Additional adapter code is required.
- Internal and MCP result models must be mapped explicitly.