# ADR-008: Explicit Agent Runtime State Machine

## Status

Accepted for Sprint 3 Increment 1.

## Context

Agent execution requires deterministic lifecycle semantics for successful completion, failure,
timeout, and cancellation. Implicit state changes make retries and later observability difficult to
reason about.

## Decision

Both `AgentRun` and `AgentStep` use explicit lifecycle states:

```text
PENDING
RUNNING
SUCCEEDED
FAILED
TIMED_OUT
CANCELLED
```

Legal run and step transitions are:

```text
PENDING -> RUNNING
PENDING -> CANCELLED
RUNNING -> SUCCEEDED
RUNNING -> FAILED
RUNNING -> TIMED_OUT
RUNNING -> CANCELLED
```

`SUCCEEDED`, `FAILED`, `TIMED_OUT`, and `CANCELLED` are terminal states.

Transition rules are centralized and invalid transitions raise `AgentStateTransitionError`.

Failure reasons such as `STEP_LIMIT_EXCEEDED` are error codes associated with `FAILED`; they are not
additional lifecycle states.

## Consequences

- Lifecycle behavior is deterministic and testable.
- Terminal state mutation is prohibited by the transition model.
- Retry behavior can later create new attempts without reopening a terminal step.
- Observability and persistence can consume stable runtime states in later sprints.
