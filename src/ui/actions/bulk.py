from collections.abc import Callable

import flet as ft

from ...core.strings import get_string
from ...interfaces.protocols import IBrowserLauncher, IProfileManager
from ..dialogs import open_confirm_dialog
from ..state import AppState
from .browser import launch_or_stop


def bulk_delete_profiles(
    page: ft.Page,
    names: list[str],
    pm: IProfileManager,
    log: Callable[[str], None],
    refresh: Callable[[], None],
    on_done: Callable[[], None],
) -> None:
    if not names:
        return

    def do_bulk_delete() -> None:
        for name in names:
            pm.delete_profile(name)
            log(get_string("deleted_profile", name=name))
        on_done()
        refresh()

    count = len(names)
    open_confirm_dialog(
        page,
        "",
        do_bulk_delete,
        title=f"Delete {count} profile{'s' if count != 1 else ''}?",
        body="This action cannot be undone.",
    )


def bulk_launch_profiles(
    names: list[str],
    pm: IProfileManager,
    bl: IBrowserLauncher,
    state: AppState,
    log: Callable[[str], None],
) -> None:
    for name in names:
        if not bl.is_running(name) and not state.is_loading(name):
            launch_or_stop(name, pm, bl, state, log)


def bulk_stop_profiles(
    names: list[str],
    pm: IProfileManager,
    bl: IBrowserLauncher,
    state: AppState,
    log: Callable[[str], None],
) -> None:
    for name in names:
        if bl.is_running(name):
            launch_or_stop(name, pm, bl, state, log)
