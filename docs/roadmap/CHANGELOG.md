# Changelog

All notable changes to this project are documented in this file.

The project follows a sprint-based release model.

---

# v0.2.0 – Enterprise MCP Framework

Released: July 2026

## Added

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

- Ruff
- mypy (strict)
- pytest
- 37 automated tests
- 91.13% code coverage

### Documentation

- Updated README
- Updated architecture overview
- Project roadmap
- Project state
- Sprint documentation updates

---

# v0.1.0 – Platform Foundation

Released: July 2026

## Added

### Platform

- FastAPI application
- Environment configuration
- Structured logging
- OpenAPI
- Health endpoints

### Engineering

- Docker
- Docker Compose
- Ruff
- mypy
- pytest
- GitHub workflow
- Pull Request workflow
- Initial architecture documentation

# Unreleased – v0.3.0 Agent Runtime

## Added

## Planned Sprint 3 capabilities

- Agent Runtime
- Execution Context
- Task/run lifecycle
- Deterministic Planning
- Retry Policy
- Timeout Handling
- Cancellation
- Runtime Unit and Integration Tests

### Sprint 3 Increment 1 – Agent Runtime Contracts

- AgentTask contract
- AgentRun contract
- AgentStep contract
- AgentExecutionContext
- CancellationToken
- Agent run and step state machines
- Runtime exception hierarchy
- Bounded step execution model
- ADR-007 Agent Runtime Architecture
- ADR-008 Explicit Agent Runtime State Machine
- ADR-009 Bounded Agent Execution

### Sprint 3 Increment 2 – Runtime Execution ✅

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

### Sprint 3 Increment 3 – Bounded Tool Retry Policy ✅

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

### Sprint 3 Increment 4 – Deterministic Plan Execution 🚧

Status: 🚧 In Progress

Implemented scope:

- Immutable `ToolPlanStep` and `AgentPlan` planning contracts
- `DeterministicPlanner` protocol
- Sequential `PlannedAgent` adapter over the existing `ToolExecutor`
- Deterministic two-step reference planned agent
- Logical plan-step versus physical `AgentStep` attempt separation
- Existing retry attempts continue to consume the single `max_steps` budget
- Existing cooperative cancellation and run-level timeout span plan execution
- Tool invocation remains exclusively through `ToolInvocationService`
- ADR-010 Deterministic Agent Planning

Explicitly deferred:

- LLM planning and provider SDKs
- branching, loops, parallel plans, and dynamic replanning
- memory and conversation persistence
- multi-agent orchestration
- observability and production security work
