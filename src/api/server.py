from __future__ import annotations

import threading
from typing import TYPE_CHECKING

import uvicorn

from ..core.config import API_HOST, API_PORT
from ..core.logging import get_logger

if TYPE_CHECKING:
    from fastapi import FastAPI

logger = get_logger("api.server")


class APIServer:
    """Runs the FastAPI app in a background daemon thread."""

    def __init__(self, app: FastAPI) -> None:
        self._app = app
        self._server: uvicorn.Server | None = None
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        config = uvicorn.Config(
            app=self._app,
            host=API_HOST,
            port=API_PORT,
            log_level="warning",
            access_log=False,
        )
        self._server = uvicorn.Server(config)

        self._thread = threading.Thread(
            target=self._server.run,
            daemon=True,
            name="camoumgr-api",
        )
        self._thread.start()
        logger.info("API server started on http://%s:%s", API_HOST, API_PORT)

    def stop(self) -> None:
        if self._server:
            self._server.should_exit = True
            logger.info("API server shutdown requested")

    @property
    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()
