from collections.abc import Callable

import flet as ft

from ..config import COLORS
from ..strings import get_string
from .theme import ACCENT_STYLE, OUTLINE_STYLE


def build_sidebar(
    stats_text: ft.Text,
    running_text: ft.Text,
    log_text: ft.Text,
    log_column: ft.Container,
    log_toggle_btn: ft.TextButton,
    on_new_profile: Callable,
    on_import: Callable,
    on_export: Callable,
    on_toggle_log: Callable,
    on_fullscreen_log: Callable,
) -> ft.Container:
    log_toggle_btn.on_click = on_toggle_log
    return ft.Container(
        width=310,
        bgcolor=COLORS["sidebar"],
        padding=ft.Padding.symmetric(horizontal=20, vertical=28),
        content=ft.Column(
            spacing=0,
            expand=True,
            controls=[
                ft.Text(
                    get_string("app_name"),
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    color=COLORS["accent"],
                ),
                ft.Text(
                    get_string("app_subtitle"),
                    size=10,
                    color=COLORS["text_dim"],
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Divider(height=28, color=COLORS["border"]),
                ft.Button(
                    "New Profile",
                    icon=ft.Icons.ADD,
                    width=270,
                    height=44,
                    style=ACCENT_STYLE,
                    on_click=on_new_profile,
                ),
                ft.Container(height=14),
                ft.Row(
                    spacing=10,
                    controls=[
                        ft.OutlinedButton(
                            "Import",
                            icon=ft.Icons.DOWNLOAD,
                            width=116,
                            height=40,
                            style=OUTLINE_STYLE,
                            on_click=on_import,
                        ),
                        ft.OutlinedButton(
                            "Export",
                            icon=ft.Icons.UPLOAD,
                            width=116,
                            height=40,
                            style=OUTLINE_STYLE,
                            on_click=on_export,
                        ),
                    ],
                ),
                ft.Divider(height=24, color=COLORS["border"]),
                stats_text,
                ft.Container(height=6),
                running_text,
                ft.Container(height=16),
                ft.Divider(height=1, color=COLORS["border"]),
                ft.Container(height=10),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        log_toggle_btn,
                        ft.IconButton(
                            icon=ft.Icons.OPEN_IN_FULL,
                            icon_size=16,
                            icon_color=COLORS["text_sub"],
                            on_click=on_fullscreen_log,
                        ),
                    ],
                ),
                ft.Container(height=4),
                log_column,
            ],
        ),
    )
