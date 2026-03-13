from collections.abc import Callable

import flet as ft

from ...core.strings import get_string
from ...interfaces.protocols import IProfileManager
from ..dialogs import open_export_dialog


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
