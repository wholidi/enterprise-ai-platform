# Enterprise AI Platform

> A public reference implementation demonstrating how to build production-oriented Enterprise AI applications using the Model Context Protocol (MCP), agent architecture, and enterprise software engineering practices.

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green)
![MCP](https://img.shields.io/badge/MCP-v1-orange)
![License](https://img.shields.io/badge/License-MIT-blue)

---

## Current Status

**Current Release**

**v0.2.0 – Enterprise MCP Framework**

### Completed

- ✅ Sprint 1 – Platform Foundation
- ✅ Sprint 2 – Enterprise MCP Framework
- ✅ Sprint 3 – Agent Runtime

---

# Overview

Enterprise AI Platform is a production-oriented reference implementation that demonstrates how modern enterprise AI systems can be designed from first principles.

The project is built incrementally over multiple sprints and emphasizes:

- Enterprise software architecture
- Model Context Protocol (MCP)
- Agent runtime design
- Strong typing
- JSON Schema contracts
- Testing and quality gates
- Production engineering practices

All implementations use **synthetic data only**.

---

# Vision

The long-term vision is to build an enterprise-grade AI platform capable of supporting:

- Enterprise Tool Registry
- MCP Server
- Agent Runtime
- Planning Engine
- Memory
- Evaluation Framework
- Observability
- Production Deployment

---

# Current Architecture

```text
                     Enterprise AI Platform

                         MCP Clients
                              │
                              ▼
                       MCP Server (Sprint 2)
                              │
                              ▼
                        MCP Tool Adapter
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
      ToolDiscoveryService          ToolInvocationService
              │                               │
              └───────────────┬───────────────┘
                              ▼
                       Enterprise Registry
                              │
                              ▼
                       Enterprise Tools
```
 
 # Enterprise AI Platform

                    ┌──────── MCP Clients ────────┐
                    │                              │
                    ▼                              │
                MCP Server                         │
                    │                              │
                    ▼                              │
              MCP Tool Adapter                     │
                    │                              │
                    └──────────────┐               │
                                   ▼
                            Tool Platform
                       ┌────────────────────┐
                       │ ToolDiscoveryService
                       │ ToolInvocationService
                       └────────────────────┘
                                   ▲
                                   │
                              ToolExecutor
                                   ▲
                                   │
                              AgentRuntime
                                   ▲
                                   │
                         Planned / Executable Agent
                                   ▲
                                   │
                         DeterministicPlanner
                                   │
                                   ▼
                              AgentPlan

---

# Features

## Sprint 1 – Platform Foundation

- FastAPI application
- Docker support
- Structured logging
- OpenAPI documentation
- Environment configuration
- Health endpoints
- Ruff
- mypy (strict) apps/api/src
- pytest
- Coverage reporting

---

## Sprint 2 – Enterprise MCP Framework

- Enterprise Tool Registry
- Tool Contracts
- Tool Discovery
- Tool Invocation
- JSON Schema validation
- Built-in `platform.ping` tool
- MCP Server
- MCP Adapter
- MCP Inspector validation

---

## Sprint 3 – Agent Runtime

Sprint 3 capabilities:
- AgentTask / AgentRun / AgentStep
- AgentExecutionContext
- Explicit run and step state machines
- Bounded max_steps execution
- RetryPolicy
- Cancellation
- Run-level timeout
- AgentRuntime
- ToolExecutor boundary
- DeterministicPlanner
- AgentPlan / ToolPlanStep
- PlannedAgent
- deterministic multi-step reference plan
- ADR-007 through ADR-010

Quality:
- Ruff passed
- pytest: 109 passed
- mypy --strict apps/api/src: passed on 25 source files
- Coverage: 93.89% last reported in Increment 3

---

# Repository Structure

```text
enterprise-ai-platform/

├── apps/
│   └── api/
│       ├── src/
│       └── tests/
│
├── docs/
│   ├── architecture/
│   └── roadmap/
│
├── deployment/
│
├── scripts/
│
├── docker-compose.yml
└── pyproject.toml
```

---

# Quick Start

Clone the repository.

```bash
git clone https://github.com/wholidi/enterprise-ai-platform.git

cd enterprise-ai-platform
```

Create a virtual environment.

```bash
python -m venv .venv
```

Activate it.

Windows PowerShell

```powershell
.venv\Scripts\Activate.ps1
```

Linux / macOS

```bash
source .venv/bin/activate
```

Install dependencies.

```bash
pip install -e ".[dev]"
```

Start the API.

```bash
uvicorn enterprise_ai_api.main:app --app-dir apps/api/src --reload
```

Open:

```
http://localhost:8000/docs
```

---

# Running the MCP Server

```bash
python -m enterprise_ai_api.mcp.server
```

or

```bash
enterprise-ai-mcp
```

Validate with MCP Inspector.

```bash
npx @modelcontextprotocol/inspector \
    python \
    -m enterprise_ai_api.mcp.server
```

---

# Engineering Quality

Run all quality gates.

```bash
ruff check .

mypy --strict apps/api/src

pytest --cov
```

Current quality metrics:

- Ruff ✔
- mypy (strict) ✔
- pytest ✔
- 37 unit tests
- 91% code coverage

---

# Roadmap

| Sprint | Description | Status |
|---------|-------------|--------|
| Sprint 1 | Platform Foundation | ✅ |
| Sprint 2 | Enterprise MCP Framework | ✅ |
| Sprint 3 | Agent Runtime | ✅ |
| Sprint 4 | Memory & Context | Planned |
| Sprint 5 | Evaluation Framework | Planned |
| Sprint 6 | Observability | Planned |
| Sprint 7 | Production Platform | Planned |
| Sprint 8 | Enterprise AI Platform | Planned |

---

# Releases

| Version | Description |
|----------|-------------|
| v0.1.0 | Platform Foundation |
| v0.2.0 | Enterprise MCP Framework |
| v0.3.0 | Agent Run Timw |
---

# Documentation

Architecture documentation:

```
docs/architecture/
```

Project roadmap:

```
docs/roadmap/PROJECT_STATE.md
```

---

# Contributing

Contributions, suggestions, and discussions are welcome.

Please open an Issue or Pull Request before submitting significant architectural changes.

---

# License

MIT License

---

# Author

**William Hartono**

Enterprise AI Platform Reference Implementation
