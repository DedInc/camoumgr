import threading
from collections.abc import Callable

from ...core.strings import get_string
from ...interfaces.protocols import IBrowserLauncher, IProfileManager
from ..state import AppState


def launch_or_stop(
    name: str,
    pm: IProfileManager,
    bl: IBrowserLauncher,
    state: AppState,
    log: Callable[[str], None],
) -> None:
    profile = pm.profiles.get(name)
    if not profile:
        return

    if bl.is_running(name):
        log(get_string("stopping_profile", name=name))
        state.set_loading(name, True)
        state.schedule_refresh()

        def do_stop() -> None:
            try:
                bl.stop_profile(name)
            finally:
                state.set_loading(name, False)
                state.schedule_refresh()

        threading.Thread(target=do_stop, daemon=True).start()
        return

    state.set_loading(name, True)
    log(get_string("launching_profile", name=name))
    state.schedule_refresh()

    def _on_ready() -> None:
        state.set_loading(name, False)
        state.schedule_refresh()

    def _on_stop() -> None:
        state.set_loading(name, False)
        state.schedule_refresh()

    bl.start_thread(
        profile,
        log,
        None,
        on_ready=_on_ready,
        on_stop=_on_stop,
    )
