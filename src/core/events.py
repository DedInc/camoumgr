import threading
from collections.abc import Callable

from .logging import get_logger

logger = get_logger("events")


class EventBus:
    """Simple thread-safe pub/sub for cross-layer notifications."""

    def __init__(self) -> None:
        self._subscribers: list[Callable[[], None]] = []
        self._lock = threading.Lock()

    def subscribe(self, callback: Callable[[], None]) -> None:
        with self._lock:
            self._subscribers.append(callback)

    def unsubscribe(self, callback: Callable[[], None]) -> None:
        with self._lock:
            self._subscribers = [s for s in self._subscribers if s is not callback]

    def emit(self) -> None:
        with self._lock:
            subscribers = list(self._subscribers)
        for cb in subscribers:
            try:
                cb()
            except Exception as exc:
                logger.error("EventBus subscriber error: %s", exc)
