from collections.abc import Callable

import flet as ft

from ...config import COLORS
from ...models.profile import Profile
from ..theme import ACCENT_STYLE


def open_export_dialog(
    page: ft.Page,
    file_picker: ft.FilePicker,
    profiles: list[Profile],
    on_complete: Callable[[list[str], str, bool], None],
) -> None:
    if not profiles:
        return

    names = [p.name for p in profiles]
    checkboxes = [
        ft.Checkbox(label=n, value=False, shape=ft.CircleBorder()) for n in names
    ]
    include_data_cb = ft.Checkbox(label="Include browser data", value=True)

    async def on_export(_):
        selected = [cb.label for cb in checkboxes if cb.value]
        if not selected:
            return
        include_data = include_data_cb.value
        page.pop_dialog()
        dir_path = await file_picker.get_directory_path(
            dialog_title="Select export directory",
        )
        if dir_path:
            on_complete(selected, dir_path, include_data)

    def sync_select_all() -> None:
        select_all_cb.value = all(cb.value for cb in checkboxes)
        select_all_cb.tristate = any(cb.value for cb in checkboxes) and not all(
            cb.value for cb in checkboxes
        )

    def on_profile_change(_):
        sync_select_all()
        page.update()

    for cb in checkboxes:
        cb.on_change = on_profile_change

    def toggle_all(e):
        target = e.control.value
        if target is None:
            target = True
        for cb in checkboxes:
            cb.value = target
        select_all_cb.value = target
        select_all_cb.tristate = False
        page.update()

    select_all_cb = ft.Checkbox(
        label="Select all",
        value=False,
        tristate=False,
        shape=ft.CircleBorder(),
        on_change=toggle_all,
    )

    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text("Export Profiles", size=20, weight=ft.FontWeight.BOLD),
        content=ft.Container(
            width=350,
            content=ft.Column(
                tight=True,
                spacing=8,
                scroll=ft.ScrollMode.AUTO,
                controls=[
                    ft.Text(
                        "Choose profiles to export",
                        size=12,
                        color=COLORS["text_dim"],
                    ),
                    ft.Container(height=4),
                    select_all_cb,
                    ft.Divider(height=1),
                    *checkboxes,
                    ft.Container(height=8),
                    include_data_cb,
                ],
            ),
        ),
        actions=[
            ft.TextButton("Cancel", on_click=lambda e: page.pop_dialog()),
            ft.Button(
                "Export",
                icon=ft.Icons.UPLOAD,
                style=ACCENT_STYLE,
                on_click=on_export,
            ),
        ],
    )
    page.show_dialog(dlg)
