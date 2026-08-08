# ADR-010: Deterministic Agent Planning

## Status

Accepted for Sprint 3 Increment 4.

## Context

Sprint 3 Increment 2 established `AgentRuntime` and an agent-facing `ToolExecutor`. Increment 3 added bounded tool retries while preserving the rule that every physical tool attempt becomes a distinct `AgentStep` and consumes the run-level `max_steps` budget.

The runtime can already execute multiple ordered tool calls because an `ExecutableAgent` may invoke `ToolExecutor` repeatedly. Sprint 3 still needs a minimal planning abstraction that makes this intended sequence explicit without introducing an LLM, persistence, dynamic orchestration, or a second tool-execution path.

## Decision

Introduce immutable deterministic planning contracts above the existing `ToolExecutor` boundary:

```text
AgentTask
    |
    v
AgentRuntime
    |
    v
Executable planned agent
    |
    v
DeterministicPlanner
    |
    v
AgentPlan
    |
    v
ToolPlanStep
    |
    v
ToolExecutor
    |
    v
AgentRuntime execution controls
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

`ToolPlanStep` represents one logical requested tool operation. `AgentPlan` is a non-empty ordered tuple of those operations. `DeterministicPlanner.plan(task)` is synchronous and side-effect-free for this increment.

A planned agent executes plan steps sequentially and fail-fast by calling only the supplied `ToolExecutor`. Planning does not receive `ToolInvocationService`, `ToolRegistry`, `ToolDefinition`, tool handlers, cancellation controls, timeout controls, or retry controls.

`AgentStep` retains its existing meaning: one physical runtime execution attempt. It is not a logical plan-step record. Therefore one `ToolPlanStep` may produce multiple `AgentStep` records when retry policy allows another attempt.

The existing run-level controls remain authoritative:

- retries create new `AgentStep` records;
- retry attempts consume `max_steps`;
- `max_steps` remains the single hard run-level attempt budget;
- cooperative cancellation prevents later attempts and later logical plan operations;
- the existing run-level timeout spans planning plus sequential plan execution;
- terminal `AgentStep` states are never reopened;
- tool execution remains exclusively `ToolExecutor` -> `ToolInvocationService`.

No new `AgentStepKind`, planning lifecycle state, plan-specific timeout, plan-specific retry policy, or secondary execution budget is introduced.

## Consequences

- Sprint 3 gains an explicit planning vocabulary without changing `AgentRuntime` execution mechanics.
- Logical intent (`ToolPlanStep`) is separated from physical execution attempts (`AgentStep`).
- Future LLM-based planning can target the same `AgentPlan` shape without changing Tool Platform boundaries.
- Retry, cancellation, timeout, and step-budget semantics remain centralized in `AgentRuntime`.
- Branching, loops, DAG execution, parallel execution, dynamic replanning, memory, and persistence remain deferred.
