import asyncio
import os
import signal
import sys

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
)

from camoufox.async_api import AsyncCamoufox

from src.config import DATA_DIR
from src.utils.proxy_parser import parse_proxy

_shutdown = asyncio.Event()


def _configure_stdio():
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


def _safe_print(message: str):
    try:
        print(message, flush=True)
    except UnicodeEncodeError:
        fallback = (message + "\n").encode("utf-8", errors="replace")
        sys.stdout.buffer.write(fallback)
        sys.stdout.flush()


def _compact_error(exc: Exception, limit: int = 700) -> str:
    text = " ".join(str(exc).split())
    if "Call log:" in text:
        text = text.split("Call log:", 1)[0].strip()
    if len(text) > limit:
        return text[:limit] + "..."
    return text


def _setup_signals(loop):
    try:
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(sig, _shutdown.set)
    except NotImplementedError:
        pass


async def run_browser(profile_name, proxy_str, os_type):
    profile_dir = os.path.join(os.getcwd(), DATA_DIR, profile_name)

    launch_config = {
        "headless": False,
        "os": os_type,
        "humanize": True,
        "geoip": True,
        "block_images": False,
        "user_data_dir": profile_dir,
        "persistent_context": True,
    }

    proxy_config = parse_proxy(proxy_str)
    if proxy_config:
        launch_config["proxy"] = proxy_config

    _safe_print(f"Starting browser for {profile_name}...")

    try:
        async with AsyncCamoufox(**launch_config) as context:
            _safe_print("BROWSER_STARTED")

            page = context.pages[0] if context.pages else await context.new_page()

            close_event = asyncio.Event()
            context.on("close", lambda: close_event.set())
            page.on("close", lambda: close_event.set())

            close_task = asyncio.create_task(close_event.wait())
            shutdown_task = asyncio.create_task(_shutdown.wait())

            done, pending = await asyncio.wait(
                [close_task, shutdown_task],
                return_when=asyncio.FIRST_COMPLETED,
            )

            if close_task in done:
                _safe_print("BROWSER_CLOSED")

            for task in pending:
                task.cancel()
            if pending:
                await asyncio.gather(*pending, return_exceptions=True)

            return 0

    except asyncio.CancelledError:
        _safe_print("LAUNCH_CANCELLED")
        return 1
    except Exception as e:
        _safe_print(f"LAUNCH_FAILED: {type(e).__name__}: {_compact_error(e, 220)}")
        return 1


async def _async_main() -> int:
    loop = asyncio.get_running_loop()
    _setup_signals(loop)
    return await run_browser(sys.argv[1], sys.argv[2], sys.argv[3])


if __name__ == "__main__":
    _configure_stdio()

    if len(sys.argv) < 4:
        _safe_print("Usage: python run_browser.py <name> <proxy> <os>")
        sys.exit(1)

    exit_code = 1
    try:
        exit_code = asyncio.run(_async_main())
    except KeyboardInterrupt:
        _safe_print("Interrupted by user")
        exit_code = 130

    sys.exit(exit_code)
