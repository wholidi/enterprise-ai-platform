# Enterprise AI Platform

## Project

Enterprise AI Platform Reference Implementation

---

## Repository

https://github.com/wholidi/enterprise-ai-platform

---

## Current Release

**v0.2.0-mcp-tools**

Release Date: July 2026

---

## Current Sprint

**Sprint 3 – Agent Runtime**

---

# Mission

Build a production-oriented Enterprise AI Platform demonstrating:

- Enterprise Tool Registry
- Model Context Protocol (MCP)
- Agent Runtime
- Planning Engine
- Memory
- Evaluation Framework
- Observability
- Production Engineering Practices

using synthetic data only.

---

# Sprint Status

| Sprint | Name | Status |
|---------|------|--------|
| Sprint 1 | Platform Foundation | ✅ Complete |
| Sprint 2 | Enterprise MCP Framework | ✅ Complete |
| Sprint 3 | Agent Runtime | 🚧 In Progress |
| Sprint 4 | Memory & Context | ⬜ Planned |
| Sprint 5 | Evaluation Framework | ⬜ Planned |
| Sprint 6 | Observability | ⬜ Planned |
| Sprint 7 | Production Platform | ⬜ Planned |
| Sprint 8 | Enterprise AI Platform | ⬜ Planned |

---

# Completed

## Sprint 1

- FastAPI platform
- Docker
- Structured logging
- OpenAPI
- Ruff
- mypy
- pytest
- GitHub workflow
- Pull Request workflow
- Release process

---

## Sprint 2

### Enterprise Tool Platform

- Enterprise Tool Registry
- Tool Contracts
- Tool Discovery
- Tool Invocation
- JSON Schema generation
- JSON Schema validation

### Built-in Tools

- platform.ping

### MCP

- MCP Server
- MCP Adapter
- MCP Inspector validation

### Engineering

- 37 unit tests
- 91.13% coverage
- Ruff
- mypy (strict)
- pytest

---

# Current Goal

Sprint 3

Build the Enterprise Agent Runtime.

---

# Sprint 3 Deliverables

- Agent Runtime
- Execution Context
- Task Lifecycle
- Planning Engine
- Conversation State (Sprint 4 – Memory & Context)
- Retry Policy
- Timeout Handling
- Cancellation
- Runtime Unit Tests

---

# Architecture Decisions

## Completed

- ADR-001 Python + FastAPI
- ADR-002 Structured Logging
- ADR-003 MCP as Transport Adapter
- ADR-004 In-Memory Tool Registry
- ADR-005 Pydantic Tool Contracts
- ADR-006 Async Tool Execution
- ADR-007 Agent Runtime Architecture
- ADR-008 Explicit Agent Runtime State Machine
- ADR-009 Bounded Agent Execution
- ADR-010 Deterministic Agent Planning

---

# Current Repository Health

| Metric | Status |
|---------|--------|
| Ruff | ✅ |
| mypy | ✅ |
| pytest | ✅ |
| Automated Tests | ✅ 96 passed |
| Coverage | ✅ 93.89% |
| MCP Inspector | ✅ |
| GitHub Releases | ✅ |
| Release Tag | ✅ v0.2.0-mcp-tools |

---

# Risks

Current risks:

- Agent Runtime execution layer not yet complete
- No persistence layer
- No evaluation framework
- No observability pipeline

All are planned in future sprints.

---

# Long-Term Vision

```
Enterprise AI Platform
        │
        ▼
Enterprise Agent Platform
        │
        ▼
Enterprise AI Operating System
```

---

# Latest Release

**v0.2.0 – Enterprise MCP Framework**

Highlights

- Enterprise Tool Registry
- Tool Contracts
- Tool Discovery
- Tool Invocation
- MCP Server
- MCP Adapter
- JSON Schema Validation
- MCP Inspector Validation
- 37 Tests
- 91.13% Code Coverage

---

**Sprint 3 – Agent Runtime**
Status: In Progress

Target Outcome:

```
Agent
      │
      ▼
Planning Engine
      │
      ▼
Enterprise Tool Platform
      │
      ▼
Enterprise Tools

Increment 1 – Contracts and Lifecycle Foundation ✅
- AgentTask
- AgentRun
- AgentStep
- AgentExecutionContext
- CancellationToken
- AgentRunState
- AgentStepState
- AgentStepKind
- Explicit state-transition validation
- Runtime exception hierarchy
- ADR-007 Agent Runtime Architecture
- ADR-008 Explicit Agent Runtime State Machine
- ADR-009 Bounded Agent Execution
- 76 tests passing
- 94.01% coverage

Current branch:
feat/agent-runtime-contracts

Latest commit:
6518471 feat(agent-runtime): add contracts and lifecycle foundation

 Increment 2 – Runtime Execution ✅

Status: ✅ Complete

Completed:

- AgentRuntime execution service
- Deterministic ReferencePingAgent
- Tool invocation exclusively through ToolInvocationService
- AgentRun lifecycle execution
- AgentStep lifecycle execution
- Step-budget enforcement
- Run timeout handling
- Cancellation handling
- Runtime failure normalization
- Integration test using platform.ping

### Engineering

- 86 automated tests
- 93.59% code coverage
- Ruff passing
- mypy strict passing

Current branch:
`feat/agent-runtime-execution`

Latest implementation commit:
`429e34c feat(agent-runtime): add bounded reference execution path`

 Increment 3 – Bounded Tool Retry Policy ✅

Status: ✅ Complete

Completed:

- RetryPolicy with bounded max_attempts
- MAX_TOOL_ATTEMPTS platform guardrail
- ToolExecutionError-only retry eligibility
- New AgentStep for each retry attempt
- Retry attempts consume max_steps
- Step-budget precedence over retry preference
- Cancellation prevents additional attempts
- Run-level timeout across retry sequences
- Non-retryable ToolPlatformError failures remain single-attempt
- ReferencePingAgent remains retry-unaware
- Tool invocation remains exclusively through ToolInvocationService

### Engineering

- 96 automated tests
- 93.89% code coverage
- Ruff passing
- mypy strict passing

Current branch:
`feat/agent-runtime-execution`

Latest implementation commit:
532c14b (HEAD -> feat/agent-runtime-execution) feat(agent-runtime): add bounded tool retry policy

## Increment 4 – Deterministic Plan Execution 🚧

Status: 🚧 In Progress

Scope:

- Immutable `ToolPlanStep` and `AgentPlan` contracts
- `DeterministicPlanner` protocol
- Sequential `PlannedAgent` execution through the existing `ToolExecutor`
- Deterministic multi-step reference plan
- Logical plan operations remain separate from physical runtime `AgentStep` attempts
- Existing retry, `max_steps`, cancellation, and timeout semantics remain unchanged
- Tool invocation remains exclusively through `ToolInvocationService`
- ADR-010 Deterministic Agent Planning

Out of scope: LLMs, prompt frameworks, memory, conversation persistence, dynamic replanning, branching, parallel execution, and multi-agent orchestration.
