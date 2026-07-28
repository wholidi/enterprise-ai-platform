# ADR-005: Pydantic-Based Tool Contracts

## Status

Accepted

## Context

Each enterprise tool requires typed input and output validation
together with MCP-compatible JSON Schema.

## Decision

Pydantic models are the authoritative source for tool input and
output contracts.

JSON Schema is generated from those models and exposed through MCP.

## Consequences

### Positive

- One source of truth.
- Runtime validation.
- JSON Schema generation.
- Strong typing.
- Reduced schema drift.

### Negative

- Tool contracts depend on Pydantic.
- Non-Python tools require equivalent schemas or adapters.