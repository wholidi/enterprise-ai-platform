# ADR-001: Use Python and FastAPI for the service baseline

- Status: Accepted
- Date: 2026-07-25

## Context

The future platform needs Python-native integration with AI frameworks, data tooling, MCP libraries, and statistical/report-generation packages. It also needs strongly typed HTTP interfaces and generated API documentation.

## Decision

Use Python 3.11+ and FastAPI as the application service baseline.

## Consequences

Positive:
- Strong compatibility with AI and data ecosystems.
- OpenAPI documentation is generated automatically.
- Async support is available when tool execution becomes concurrent.
- Pydantic provides schema validation.

Trade-offs:
- CPU-intensive work must later be isolated in workers or external services.
- Dependency governance will be required before internal production use.
