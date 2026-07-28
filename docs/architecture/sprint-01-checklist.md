# Sprint 1 Checklist

## Day 1 - Repository and standards
- [ ] Create a private Git repository.
- [ ] Copy this baseline into the repository.
- [ ] Protect the default branch.
- [ ] Add a short project description and owner.
- [ ] Confirm no confidential Seagate data is committed.

## Day 2 - Local runtime
- [ ] Create `.venv`.
- [ ] Install `.[dev]` dependencies.
- [ ] Start the FastAPI service.
- [ ] Verify root, liveness, readiness, and OpenAPI endpoints.

## Day 3 - Engineering quality
- [ ] Run Ruff linting.
- [ ] Run formatting check.
- [ ] Run mypy.
- [ ] Run tests with coverage.
- [ ] Correct all failures before committing.

## Day 4 - Container baseline
- [ ] Copy `.env.example` to `.env`.
- [ ] Build the Docker image.
- [ ] Start with Docker Compose.
- [ ] Verify the container health status.
- [ ] Confirm the container runs as a non-root user.

## Day 5 - CI and documentation
- [ ] Push to the private Git repository.
- [ ] Confirm the GitLab pipeline passes.
- [ ] Review the architecture overview and ADRs.
- [ ] Tag the baseline as `v0.1.0-week1`.
- [ ] Record a two-minute demonstration.

## Sprint 1 acceptance criteria
- Service starts locally and in Docker.
- `/health/live` returns HTTP 200.
- `/health/ready` returns HTTP 200.
- CI lint, typing, unit-test, coverage, and image-build jobs pass.
- No secrets or internal production data exist in the repository.
