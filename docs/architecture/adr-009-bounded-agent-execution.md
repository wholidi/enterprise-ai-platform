# ADR-009: Bounded Agent Execution

## Status

Accepted for Sprint 3 Increment 1.

## Context

An enterprise Agent Runtime must not allow unbounded execution. Sprint 3 requires bounded steps,
timeout handling, and cancellation while intentionally deferring autonomous multi-agent behavior and
persistent memory.

## Decision

Every run receives an ephemeral `AgentExecutionContext` containing:

- `run_id`
- `max_steps`
- optional runtime timeout
- a cooperative cancellation token

The runtime owns enforcement of step budgets and run-level timeout/cancellation. Agents cannot opt
out of these controls.

Sprint 3 Increment 1 caps configured step budgets at `MAX_AGENT_STEPS = 100`. This is an internal
platform guardrail and can later move to configuration without changing the execution-context
contract.

Tool-specific timeout policy is not introduced in this increment. Tool execution continues through
`ToolInvocationService`; the Agent Runtime will later bound the awaited orchestration operation using
its remaining runtime budget.

## Consequences

- Infinite or accidentally unbounded agent loops are structurally prevented.
- Cancellation is run-scoped and ephemeral rather than persisted as memory.
- Tool timeout policy remains separate from run-level orchestration timeout policy.
- Sprint 4 can add memory/context capabilities without redefining the basic execution-control model.
