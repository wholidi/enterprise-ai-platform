"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

import structlog
from fastapi import FastAPI

from enterprise_ai_api.core.config import get_settings
from enterprise_ai_api.core.logging import configure_logging
from enterprise_ai_api.routes import health

settings = get_settings()
configure_logging(settings.log_level)
logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Log application startup and shutdown lifecycle events."""

    logger.info(
        "application_started",
        application=settings.app_name,
        environment=settings.environment,
        version=settings.version,
    )
    yield
    logger.info("application_stopped", application=settings.app_name)


app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    lifespan=lifespan,
)
app.include_router(health.router, prefix="/health", tags=["health"])


@app.get("/", summary="Service metadata")
def root() -> dict[str, str]:
    """Return basic service information."""

    return {
        "service": settings.app_name,
        "environment": settings.environment,
        "version": settings.version,
        "status": "running",
    }
