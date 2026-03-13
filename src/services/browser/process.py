import os
import pathlib
import subprocess
import sys
from collections.abc import Callable

from ...core.logging import get_logger
from ...models.profile import Profile

logger = get_logger("browser.process")


_PROJECT_ROOT = str(pathlib.Path(__file__).parents[3])


def spawn_browser(profile: Profile) -> subprocess.Popen:
    """Spawn a Camoufox browser subprocess for the given profile."""
    script = os.path.join(pathlib.Path(__file__).parent, "runner.py")
    env = os.environ.copy()
    existing_pythonpath = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = _PROJECT_ROOT + (
        os.pathsep + existing_pythonpath if existing_pythonpath else ""
    )
    return subprocess.Popen(
        [sys.executable, script, profile.name, str(profile.proxy), profile.os_type],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        cwd=pathlib.Path.cwd(),
        env=env,
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1,
    )


def terminate(proc: subprocess.Popen, name: str, timeout: int = 5) -> None:
    """Gracefully terminate a browser process, force-kill on timeout."""
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


def wait_for_exit(
    proc: subprocess.Popen,
    name: str,
    notify_stopped: Callable[[], None],
) -> None:
    """Block until the process exits, then fire the callback."""
    try:
        proc.wait()
    except Exception as e:
        logger.exception("Wait error for profile %s: %s", name, e)
    finally:
        notify_stopped()
