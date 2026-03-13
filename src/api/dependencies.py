from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import Depends, Request

if TYPE_CHECKING:
    from ..core.container import Container
    from ..core.events import EventBus
    from ..interfaces import IBrowserLauncher, IProfileManager, IProxyService


def _container(request: Request) -> Container:
    return request.app.state.container


def get_profile_manager(
    container: Container = Depends(_container),
) -> IProfileManager:
    return container.profile_manager


def get_browser_launcher(
    container: Container = Depends(_container),
) -> IBrowserLauncher:
    return container.browser_launcher


def get_proxy_service(
    container: Container = Depends(_container),
) -> IProxyService:
    return container.proxy_service


def get_event_bus(
    container: Container = Depends(_container),
) -> EventBus:
    return container.event_bus
