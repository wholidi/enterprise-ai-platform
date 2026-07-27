# Enterprise AI Platform

A private reference implementation for building secure, observable, agentic AI applications.

## Sprint 1 scope

- FastAPI application baseline
- Environment-based configuration
- Structured JSON logging
- Health and readiness endpoints
- Docker image and Docker Compose
- Unit tests and coverage gate
- GitLab CI quality pipeline
- Architecture and engineering documentation

## Quick start

```bash
cp .env.example .env
python -m venv .venv
source .venv/bin/activate  # Windows PowerShell: .venv\\Scripts\\Activate.ps1
pip install -e ".[dev]"
uvicorn enterprise_ai_api.main:app --app-dir apps/api/src --reload
```

Open:

- API root: http://localhost:8000/
- Health: http://localhost:8000/health/live
- Readiness: http://localhost:8000/health/ready
- OpenAPI: http://localhost:8000/docs

## Docker

```bash
docker compose up --build
```

## Quality checks

```bash
ruff check .
ruff format --check .
mypy
pytest --cov
```

## Repository layout

```text
enterprise-ai-platform/
├── apps/api/                # FastAPI application and tests
├── docs/architecture/       # Architecture baseline and ADRs
├── deployment/docker/       # Container assets
├── scripts/                 # Local engineering scripts
├── .gitlab-ci.yml           # CI pipeline
├── docker-compose.yml
└── pyproject.toml
```

## Sprint 1 definition of done

The service starts locally and in Docker, emits structured logs, passes lint/type/test checks, and exposes liveness/readiness endpoints.
