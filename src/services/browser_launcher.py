import atexit
import contextlib
import os
import pathlib
import subprocess
import sys
import threading
from collections.abc import Callable

from ..logging_config import get_logger
from ..models.profile import Profile

logger = get_logger("browser_launcher")

_NOISY_PREFIXES = (
    "- [pid=",
    "console.error:",
    "Crash Annotation",
    "JavaScript error:",
    "WARNING: At least one completion condition",
)


class BrowserLauncher:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._active_sessions: dict[str, subprocess.Popen] = {}
        self._stop_notifiers: dict[str, threading.Event] = {}
        atexit.register(self.shutdown_all)

    def shutdown_all(self) -> None:
        with self._lock:
            for name, proc in list(self._active_sessions.items()):
                notifier = self._stop_notifiers.pop(name, None)
                if notifier:
                    notifier.set()
                _terminate(proc, name)
            self._active_sessions.clear()
        logger.info("All browser sessions terminated")

    def start_thread(
        self,
        profile: Profile,
        log_callback: Callable[[str], None],
        on_start: Callable[[], None] | None = None,
        on_ready: Callable[[], None] | None = None,
        on_stop: Callable[[], None] | None = None,
    ) -> None:
        with self._lock:
            if profile.name in self._active_sessions:
                return

        log_callback(f"Starting {profile.name} ({profile.os_type})...")
        logger.info(f"Starting browser for profile: {profile.name}")
        if on_start:
            on_start()

        stop_event = threading.Event()
        notify_lock = threading.Lock()

        def notify_stopped() -> None:
            with notify_lock:
                if stop_event.is_set():
                    return
                stop_event.set()
                with self._lock:
                    self._active_sessions.pop(profile.name, None)
                    self._stop_notifiers.pop(profile.name, None)
                log_callback(f"Session ended: {profile.name}")
                logger.info(f"Session ended for profile: {profile.name}")
                if on_stop:
                    on_stop()

        try:
            proc = _spawn_process(profile)
            with self._lock:
                self._active_sessions[profile.name] = proc
                self._stop_notifiers[profile.name] = stop_event

            threading.Thread(
                target=self._monitor_process,
                args=(proc, profile.name, log_callback, on_ready, notify_stopped),
                daemon=True,
            ).start()
            threading.Thread(
                target=_wait_for_exit,
                args=(proc, profile.name, notify_stopped),
                daemon=True,
            ).start()
        except Exception as e:
            logger.exception(f"Error starting browser for {profile.name}: {e}")
            log_callback(f"Error starting process: {e}")
            if on_stop:
                on_stop()

    def stop_profile(self, profile_name: str, timeout: int = 2) -> bool:
        with self._lock:
            if profile_name not in self._active_sessions:
                return False
            proc = self._active_sessions.pop(profile_name)
            notifier = self._stop_notifiers.pop(profile_name, None)
        if notifier:
            notifier.set()
        _terminate(proc, profile_name, timeout)
        logger.info("Stopped browser for profile: %s", profile_name)
        return True

    def running_profile_names(self) -> set[str]:
        with self._lock:
            stale = [
                n for n, p in self._active_sessions.items() if p.poll() is not None
            ]
            for n in stale:
                self._active_sessions.pop(n, None)
                self._stop_notifiers.pop(n, None)
            return set(self._active_sessions.keys())

    def running_count(self) -> int:
        return len(self.running_profile_names())

    def is_running(self, profile_name: str) -> bool:
        with self._lock:
            if profile_name not in self._active_sessions:
                return False
            if self._active_sessions[profile_name].poll() is None:
                return True
            del self._active_sessions[profile_name]
            self._stop_notifiers.pop(profile_name, None)
            return False

    def _monitor_process(
        self,
        proc: subprocess.Popen,
        name: str,
        log_callback: Callable[[str], None],
        on_ready: Callable[[], None] | None,
        notify_stopped: Callable[[], None],
    ) -> None:
        ready_notified = False
        try:
            if proc.stdout is None:
                return
            for line in iter(proc.stdout.readline, ""):
                msg = line.strip()
                if not msg:
                    continue
                if msg == "BROWSER_STARTED":
                    if not ready_notified:
                        ready_notified = True
                        if on_ready:
                            on_ready()
                    log_callback("Browser started!")
                    logger.info("Browser started for profile: %s", name)
                    continue
                if msg == "BROWSER_CLOSED":
                    logger.info("Browser close detected for profile: %s", name)
                    notify_stopped()
                    _terminate(proc, name, timeout=1)
                    continue
                if msg.startswith("LAUNCH_FAILED:") or msg == "LAUNCH_CANCELLED":
                    log_callback(f"[{name}] {msg}")
                    logger.warning("Launch failed for profile %s: %s", name, msg)
                    notify_stopped()
                    _terminate(proc, name, timeout=1)
                    break
                if msg.startswith(_NOISY_PREFIXES):
                    logger.debug("[%s] %s", name, msg)
                    continue
                if len(msg) > 400:
                    msg = msg[:400] + "..."
                log_callback(f"[{name}] {msg}")
                logger.debug("[%s] %s", name, msg)
        except Exception as e:
            logger.exception("Monitor error for profile %s: %s", name, e)
            log_callback(f"[{name}] Monitor error: {e}")
        finally:
            if proc.stdout is not None:
                with contextlib.suppress(Exception):
                    proc.stdout.close()


def _spawn_process(profile: Profile) -> subprocess.Popen:
    script = os.path.join(pathlib.Path(__file__).parent, "run_browser.py")
    return subprocess.Popen(
        [sys.executable, script, profile.name, str(profile.proxy), profile.os_type],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        cwd=pathlib.Path.cwd(),
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1,
    )


def _terminate(proc: subprocess.Popen, name: str, timeout: int = 5) -> None:
    if proc.poll() is not None:
        return
    try:
        proc.terminate()
        try:
            proc.wait(timeout=timeout)
            logger.info("Browser %s terminated gracefully", name)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=1)
            logger.warning("Browser %s force killed after timeout", name)
    except Exception as e:
        logger.exception("Error terminating browser %s: %s", name, e)


def _wait_for_exit(
    proc: subprocess.Popen,
    name: str,
    notify_stopped: Callable[[], None],
) -> None:
    try:
        proc.wait()
    except Exception as e:
        logger.exception("Wait error for profile %s: %s", name, e)
    finally:
        notify_stopped()
