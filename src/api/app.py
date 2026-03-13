from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import FastAPI

from ..core.logging import get_logger
from .routes import browser_router, profiles_router, proxy_router
from .schemas.common import SuccessResponse

if TYPE_CHECKING:
    from ..container import Container

logger = get_logger("api")

API_PREFIX = "/api/v1"


def create_app(container: Container) -> FastAPI:
    """Build and return the FastAPI application."""
    app = FastAPI(
        title="CamouMgr API",
        description="Local REST API for CamouMgr profile management",
        version="1.0.0",
    )
    app.state.container = container

    app.include_router(profiles_router, prefix=API_PREFIX)
    app.include_router(browser_router, prefix=API_PREFIX)
    app.include_router(proxy_router, prefix=API_PREFIX)

    @app.get("/api/v1/health", response_model=SuccessResponse, tags=["health"])
    def health_check() -> SuccessResponse:
        return SuccessResponse(message="CamouMgr API is running")

    logger.info("FastAPI application created")
    return app
