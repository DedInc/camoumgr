import logging

from ..interfaces.protocols import IBrowserLauncher, IProfileManager, IProxyService
from .config import LOG_DIR, LOG_LEVEL
from .events import EventBus
from .logging import setup_logging


class Container:
    def __init__(self) -> None:
        setup_logging(LOG_DIR, getattr(logging, LOG_LEVEL, logging.INFO))
        self._instances: dict = {}

    @property
    def event_bus(self) -> EventBus:
        if "eb" not in self._instances:
            self._instances["eb"] = EventBus()
        return self._instances["eb"]

    @property
    def profile_manager(self) -> IProfileManager:
        if "pm" not in self._instances:
            from ..services.profile.manager import ProfileManager

            self._instances["pm"] = ProfileManager()
        return self._instances["pm"]

    @property
    def browser_launcher(self) -> IBrowserLauncher:
        if "bl" not in self._instances:
            from ..services.browser.launcher import BrowserLauncher

            self._instances["bl"] = BrowserLauncher()
        return self._instances["bl"]

    @property
    def proxy_service(self) -> IProxyService:
        if "ps" not in self._instances:
            from ..services.proxy.service import ProxyService

            self._instances["ps"] = ProxyService()
        return self._instances["ps"]
