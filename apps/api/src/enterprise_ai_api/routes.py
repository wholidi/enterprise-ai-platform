"""API route modules."""

from fastapi import APIRouter

health = APIRouter()


@health.get("/live", summary="Liveness probe")
def liveness() -> dict[str, str]:
    """Confirm the process is running."""

    return {"status": "alive"}


@health.get("/ready", summary="Readiness probe")
def readiness() -> dict[str, str]:
    """Confirm the service is ready to accept requests."""

    return {"status": "ready"}
