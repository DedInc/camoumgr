import threading
import time

ITEMS_PER_PAGE = 8


class AppState:
    def __init__(self) -> None:
        self.current_page: int = 1
        self.log_collapsed: bool = False

        self._log_lines: list[str] = []
        self._loading_profiles: set[str] = set()
        self._loading_lock = threading.Lock()
        self._log_lock = threading.Lock()
        self._last_log_ui_update: float = 0.0
        self._pending_log_flush: bool = False
        self._refresh_requested = threading.Event()
        self._last_running_snapshot: set[str] = set()
        self._ui_update_lock = threading.Lock()
        self._selected_profiles: set[str] = set()
        self._selection_lock = threading.Lock()

    def is_loading(self, name: str) -> bool:
        with self._loading_lock:
            return name in self._loading_profiles

    def set_loading(self, name: str, value: bool) -> None:
        with self._loading_lock:
            if value:
                self._loading_profiles.add(name)
            else:
                self._loading_profiles.discard(name)

    def schedule_refresh(self) -> None:
        self._refresh_requested.set()

    def consume_refresh(self) -> bool:
        if self._refresh_requested.is_set():
            self._refresh_requested.clear()
            return True
        return False

    def add_log(self, message: str) -> bool:
        force = (
            message == "Browser started!"
            or message.startswith("Session ended:")
            or "LAUNCH_FAILED:" in message
            or "Error" in message
        )
        now = time.monotonic()
        with self._log_lock:
            self._log_lines.append(f"> {message}")
            if force or now - self._last_log_ui_update >= 0.15:
                self._last_log_ui_update = now
                self._pending_log_flush = True
                return True
        return False

    def flush_log(self) -> str | None:
        with self._log_lock:
            if not self._pending_log_flush:
                return None
            self._pending_log_flush = False
            return "\n".join(self._log_lines[-50:])

    def get_all_log_lines(self) -> list[str]:
        with self._log_lock:
            return list(self._log_lines)

    def toggle_selection(self, name: str) -> None:
        with self._selection_lock:
            if name in self._selected_profiles:
                self._selected_profiles.discard(name)
            else:
                self._selected_profiles.add(name)

    def is_selected(self, name: str) -> bool:
        with self._selection_lock:
            return name in self._selected_profiles

    def selected_names(self) -> set[str]:
        with self._selection_lock:
            return set(self._selected_profiles)

    def clear_selection(self) -> None:
        with self._selection_lock:
            self._selected_profiles.clear()

    def select_all(self, names: list[str]) -> None:
        with self._selection_lock:
            self._selected_profiles = set(names)
