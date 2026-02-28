import threading
from collections.abc import Callable

import flet as ft

from ..interfaces.protocols import IBrowserLauncher, IProfileManager, IProxyService
from ..strings import get_string
from .dialogs import open_confirm_dialog, open_export_dialog, open_profile_dialog
from .state import AppState


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

        def do_stop():
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


def delete_profile(
    page: ft.Page,
    name: str,
    pm: IProfileManager,
    log: Callable[[str], None],
    refresh: Callable[[], None],
) -> None:
    def do_delete():
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


async def import_profile(
    file_picker: ft.FilePicker,
    pm: IProfileManager,
    log: Callable[[str], None],
    refresh: Callable[[], None],
) -> None:
    files = await file_picker.pick_files(
        allow_multiple=True,
        allowed_extensions=["zip"],
        dialog_title="Import Profile",
    )
    if not files:
        return
    ok_count = 0
    for f in files:
        if f.path:
            success, result = pm.import_profile(f.path)
            if success:
                ok_count += 1
                log(get_string("import_success") + f": {result}")
            else:
                log(get_string("import_error", error=result))
    if ok_count:
        refresh()


def export_profile(
    page: ft.Page,
    file_picker: ft.FilePicker,
    pm: IProfileManager,
    log: Callable[[str], None],
) -> None:
    profiles = pm.list_profiles()
    if not profiles:
        return

    def on_complete(names: list[str], dir_path: str, include_data: bool) -> None:
        for name in names:
            success, result = pm.export_profile(name, dir_path, include_data)
            if success:
                log(get_string("export_success") + f": {result}")
            else:
                log(get_string("export_error", error=result))

    open_export_dialog(page, file_picker, profiles, on_complete)


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
