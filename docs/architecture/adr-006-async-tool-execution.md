# ADR-006: Asynchronous Tool Execution

## Status

Accepted

## Context

Future tools may call databases, APIs, model services, storage,
or long-running analytical services.

## Decision

All tool handlers use an asynchronous execution contract.

Even simple built-in tools such as `platform.ping` implement the
same async interface.

## Consequences

### Positive

- Supports I/O-bound enterprise tools.
- Fits FastAPI and MCP execution models.
- Consistent handler interface.
- Enables future timeout and cancellation support.

### Negative

- Async testing requires plugin support.
- Simple synchronous tools need async wrappers.