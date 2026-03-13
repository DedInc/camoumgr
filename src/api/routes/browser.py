from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, HTTPException

from ...core.logging import get_logger
from ..dependencies import get_browser_launcher, get_event_bus, get_profile_manager
from ..helpers import require_profile
from ..schemas.browser import (
    BrowserStatusResponse,
    LaunchResponse,
    RunningBrowsersResponse,
)
from ..schemas.common import ErrorResponse, SuccessResponse

if TYPE_CHECKING:
    from ...core.events import EventBus
    from ...interfaces import IBrowserLauncher, IProfileManager

logger = get_logger("api.browser")

router = APIRouter(prefix="/browser", tags=["browser"])


def _api_log(msg: str) -> None:
    logger.info("[browser] %s", msg)


@router.get("", response_model=RunningBrowsersResponse)
def list_running(
    bl: IBrowserLauncher = Depends(get_browser_launcher),
) -> RunningBrowsersResponse:
    names = sorted(bl.running_profile_names())
    return RunningBrowsersResponse(running=names, count=len(names))


@router.get(
    "/{name}/status",
    response_model=BrowserStatusResponse,
    responses={404: {"model": ErrorResponse}},
)
def browser_status(
    name: str,
    pm: IProfileManager = Depends(get_profile_manager),
    bl: IBrowserLauncher = Depends(get_browser_launcher),
) -> BrowserStatusResponse:
    require_profile(name, pm)
    return BrowserStatusResponse(name=name, is_running=bl.is_running(name))


@router.post(
    "/{name}/launch",
    response_model=LaunchResponse,
    status_code=202,
    responses={404: {"model": ErrorResponse}, 409: {"model": ErrorResponse}},
)
def launch_browser(
    name: str,
    pm: IProfileManager = Depends(get_profile_manager),
    bl: IBrowserLauncher = Depends(get_browser_launcher),
    bus: EventBus = Depends(get_event_bus),
) -> LaunchResponse:
    require_profile(name, pm)
    if bl.is_running(name):
        raise HTTPException(status_code=409, detail="Browser already running")

    profile = pm.profiles[name]

    def _on_ready() -> None:
        bus.emit()

    def _on_stop() -> None:
        bus.emit()

    bl.start_thread(profile, _api_log, on_ready=_on_ready, on_stop=_on_stop)
    logger.info("API launched browser for: %s", name)
    bus.emit()
    return LaunchResponse(success=True, message=f"Browser launching for '{name}'")


@router.post(
    "/{name}/stop",
    response_model=SuccessResponse,
    responses={404: {"model": ErrorResponse}, 409: {"model": ErrorResponse}},
)
def stop_browser(
    name: str,
    pm: IProfileManager = Depends(get_profile_manager),
    bl: IBrowserLauncher = Depends(get_browser_launcher),
    bus: EventBus = Depends(get_event_bus),
) -> SuccessResponse:
    require_profile(name, pm)
    if not bl.is_running(name):
        raise HTTPException(status_code=409, detail="Browser is not running")

    bl.stop_profile(name)
    logger.info("API stopped browser for: %s", name)
    bus.emit()
    return SuccessResponse(message=f"Browser stopped for '{name}'")
