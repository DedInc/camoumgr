from collections.abc import Callable

import flet as ft

from ..config import COLORS
from ..interfaces.protocols import IProfileManager
from ..strings import get_string
from .refs import UIRefs


def build_ui_refs(
    pm: IProfileManager,
    on_change_page: Callable[[int], None],
    on_select: Callable[[str], None],
    file_picker: ft.FilePicker,
) -> UIRefs:
    log_text = ft.Text(
        "",
        size=11,
        color=COLORS["text_dim"],
        selectable=True,
        no_wrap=False,
    )
    log_toggle_btn = ft.TextButton(
        "Activity Log",
        icon=ft.Icons.KEYBOARD_ARROW_DOWN,
        style=ft.ButtonStyle(color=COLORS["text_sub"]),
    )
    return UIRefs(
        stats_text=ft.Text(
            get_string("total_profiles", count=len(pm.profiles)),
            size=12,
            color=COLORS["text_sub"],
        ),
        running_text=ft.Text("", size=12, color=COLORS["text_dim"]),
        log_text=log_text,
        log_column=ft.Container(
            content=ft.Column(
                controls=[log_text],
                spacing=0,
            ),
            visible=False,
            padding=ft.Padding.symmetric(horizontal=12, vertical=10),
            margin=ft.Margin.symmetric(horizontal=0, vertical=4),
            border_radius=10,
            bgcolor=COLORS["log_bg"],
        ),
        log_toggle_btn=log_toggle_btn,
        content_subtitle=ft.Text("", size=13, color=COLORS["text_sub"]),
        profile_list_area=ft.Column(
            spacing=10,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        ),
        prev_btn=ft.IconButton(
            icon=ft.Icons.CHEVRON_LEFT,
            icon_color=COLORS["text_sub"],
            disabled=True,
            on_click=lambda _: on_change_page(-1),
        ),
        next_btn=ft.IconButton(
            icon=ft.Icons.CHEVRON_RIGHT,
            icon_color=COLORS["text_sub"],
            disabled=True,
            on_click=lambda _: on_change_page(1),
        ),
        page_label=ft.Text(
            get_string("page_of", current=1, total=1),
            size=13,
            color=COLORS["text_sub"],
        ),
        bulk_bar=ft.Row(visible=False, spacing=0, controls=[]),
        file_picker=file_picker,
    )
