# ADR-004: In-Memory Tool Registry

## Status

Accepted

## Context

Sprint 2 requires deterministic registration, discovery, and lookup
without introducing database or configuration persistence.

## Decision

Use an in-memory registry initialized during application startup.

Duplicate names are rejected, and tool listing is deterministic.

## Consequences

### Positive

- Simple and testable.
- No external infrastructure.
- Fast startup.
- Appropriate for the reference implementation.

### Negative

- Registry changes require restart.
- No administrative UI.
- No persistent runtime registration.

## Future Evolution

Possible future implementations:

- YAML-backed registry
- Database-backed registry
- Plugin discovery
- Environment-specific registration