from collections.abc import Callable

import flet as ft

from ...core.strings import get_string
from ...interfaces.protocols import IBrowserLauncher, IProfileManager, IProxyService
from ..dialogs import open_confirm_dialog, open_profile_dialog


def delete_profile(
    page: ft.Page,
    name: str,
    pm: IProfileManager,
    log: Callable[[str], None],
    refresh: Callable[[], None],
) -> None:
    def do_delete() -> None:
        pm.delete_profile(name)
        log(get_string("deleted_profile", name=name))
        refresh()

    open_confirm_dialog(page, name, do_delete)


def edit_profile(
    page: ft.Page,
    name: str,
    pm: IProfileManager,
    bl: IBrowserLauncher,
    ps: IProxyService,
    log: Callable[[str], None],
    refresh: Callable[[], None],
) -> None:
    profile = pm.profiles.get(name)
    if not profile:
        return
    original = profile.name

    def on_save(new_name: str, new_proxy: str, new_os: str) -> str | None:
        if new_name != original and bl.is_running(original):
            return "Stop the browser before renaming"
        if pm.update_profile(original, new_name, new_proxy, new_os):
            log(get_string("updated_profile", old=original, new=new_name))
            refresh()
            return None
        return get_string("update_failed")

    open_profile_dialog(page, ps, on_save, profile)


def add_profile(
    page: ft.Page,
    pm: IProfileManager,
    ps: IProxyService,
    log: Callable[[str], None],
    refresh: Callable[[], None],
) -> None:
    def on_save(name: str, proxy: str, os_type: str) -> str | None:
        if pm.add_profile(name, proxy, os_type):
            log(get_string("created_profile", name=name))
            refresh()
            return None
        return get_string("profile_exists")

    open_profile_dialog(page, ps, on_save)
