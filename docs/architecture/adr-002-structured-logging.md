# ADR-002: Emit structured JSON logs

- Status: Accepted
- Date: 2026-07-25

## Context

Agentic systems require traceable execution across requests, tool calls, model calls, and errors. Plain-text logs are difficult to query and correlate.

## Decision

Use structlog to emit JSON logs from the first development week.

## Consequences

Positive:
- Compatible with centralized logging platforms.
- Future correlation IDs and trace IDs can be added without redesign.
- Logs are easier to filter and analyze.

Trade-offs:
- Local logs are less visually friendly without a formatter.
