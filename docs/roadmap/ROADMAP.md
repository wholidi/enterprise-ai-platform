# Enterprise AI Platform Roadmap

## Vision

Build a production-oriented Enterprise AI Platform demonstrating modern enterprise AI engineering practices.

The project is developed incrementally over eight sprints.

---

# Long-Term Objectives

- Enterprise Tool Registry
- Model Context Protocol (MCP)
- Agent Runtime
- Planning Engine
- Memory
- Evaluation Framework
- Observability
- Production Engineering Practices

All implementations use synthetic data only.

---

# Sprint Roadmap

| Sprint | Name | Goal | Status |
|---------|------|------|--------|
| Sprint 1 | Platform Foundation | FastAPI, Docker, quality gates, engineering baseline | ✅ Complete |
| Sprint 2 | Enterprise MCP Framework | Tool Registry, Tool Contracts, MCP Server | ✅ Complete |
| Sprint 3 | Agent Runtime | Execute enterprise agents using registered tools | 🚧 In Progress |
| Sprint 4 | Memory & Context | Conversation state, memory interfaces, execution context | ⬜ Planned |
| Sprint 5 | Evaluation Framework | Quality evaluation, benchmarking, regression testing | ⬜ Planned |
| Sprint 6 | Observability | Tracing, metrics, structured events, monitoring | ⬜ Planned |
| Sprint 7 | Production Platform | Security, authentication, deployment, scalability | ⬜ Planned |
| Sprint 8 | Enterprise AI Platform | End-to-end production reference implementation | ⬜ Planned |

---

# Sprint 3 Progress

## Increment 1 – Contracts and Lifecycle Foundation ✅

Completed:

- AgentTask
- AgentRun
- AgentStep
- AgentExecutionContext
- CancellationToken
- Agent run and step lifecycle states
- Explicit state-transition validation
- Runtime exception hierarchy
- Bounded execution model
- ADR-007 Agent Runtime Architecture
- ADR-008 Explicit Agent Runtime State Machine
- ADR-009 Bounded Agent Execution
- 76 automated tests passing
- 94.01% code coverage

## Increment 2 – Runtime Execution ✅

Status: ✅ Complete

- AgentRuntime execution service
- Deterministic ReferencePingAgent
- Tool execution through ToolInvocationService
- AgentRun lifecycle execution
- AgentStep lifecycle execution
- Step-budget enforcement
- Run timeout handling
- Cancellation handling
- Runtime failure normalization
- Integration with platform.ping

Target flow:

```text
AgentTask
    ↓
AgentRuntime
    ↓
ReferencePingAgent
    ↓
ToolInvocationService
    ↓
platform.ping
    ↓
AgentStep.SUCCEEDED
    ↓
AgentRun.SUCCEEDED
```

## Increment 3 – Bounded Tool Retry Policy ✅

Status: ✅ Complete

Completed:

- RetryPolicy with bounded max_attempts
- MAX_TOOL_ATTEMPTS platform guardrail
- ToolExecutionError-only retry eligibility
- New AgentStep for every retry attempt
- Retry attempts consume the existing max_steps budget
- Step-budget precedence over retry preference
- Cancellation prevents additional attempts
- Run-level timeout across retry sequences
- Non-retryable tool-platform failures remain single-attempt
- ReferencePingAgent remains retry-unaware
- Tool execution remains exclusively through ToolInvocationService

Validated lifecycle:

```text
Tool attempt 1
    ↓
AgentStep.FAILED
    ↓
bounded retry
    ↓
Tool attempt 2
    ↓
AgentStep.SUCCEEDED or TIMED_OUT
    ↓
AgentRun terminal state
```


## Increment 4 – Deterministic Plan Execution 🚧

Scope:

- Immutable `ToolPlanStep` and `AgentPlan` contracts
- `DeterministicPlanner` protocol
- Reusable sequential `PlannedAgent` adapter
- Deterministic two-step reference planned agent
- Logical plan steps remain distinct from runtime `AgentStep` attempts
- Retries continue to create new `AgentStep` records and consume `max_steps`
- Cancellation and run-level timeout continue to be owned by `AgentRuntime`
- Tool execution remains exclusively `ToolExecutor` -> `ToolInvocationService`
- ADR-010 Deterministic Agent Planning

Explicitly deferred: LLM planning, branching, loops, parallel plans, replanning, memory, conversation persistence, and observability.


---

# Platform Evolution

```text
Sprint 1
Platform Foundation
        │
        ▼
Sprint 2
Enterprise MCP Framework
        │
        ▼
Sprint 3
Agent Runtime
        │
        ▼
Sprint 4
Memory & Context
        │
        ▼
Sprint 5
Evaluation
        │
        ▼
Sprint 6
Observability
        │
        ▼
Sprint 7
Production Platform
        │
        ▼
Sprint 8
Enterprise AI Platform
```

---

# Guiding Principles

The project follows several engineering principles:

- Layered Architecture
- Protocol Independence
- Strong Typing
- Test-Driven Engineering
- Modular Design
- Production-Oriented Engineering
- Open Standards (MCP)
- Synthetic Data Only

---

# Success Criteria

At the completion of Sprint 8 the repository will demonstrate:

- Enterprise-grade AI architecture
- Agent runtime
- MCP ecosystem
- Evaluation framework
- Observability
- Production engineering practices
- High code quality
- Complete technical documentation

## Engineering

- 96 automated tests
- 93.89% code coverage
- Ruff passing
- mypy strict passing

Current branch:
`feat/agent-runtime-execution`

Latest implementation commit:
`429e34c feat(agent-runtime): add bounded reference execution path`
532c14b (HEAD -> feat/agent-runtime-execution) feat(agent-runtime): add bounded tool retry policy
