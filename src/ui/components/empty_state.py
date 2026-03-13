from collections.abc import Callable

import flet as ft

from ...core.strings import get_string
from ..theme.colors import COLORS
from ..theme.styles import ACCENT_STYLE


def build_empty_state(on_create: Callable) -> ft.Container:
    """Placeholder shown when no profiles exist."""
    return ft.Container(
        alignment=ft.Alignment(0, 0),
        expand=True,
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10,
            controls=[
                ft.Container(height=60),
                ft.Icon(ft.Icons.PERSON_OUTLINE, size=64, color=COLORS["text_dim"]),
                ft.Text(
                    get_string("no_profiles_yet"),
                    size=22,
                    weight=ft.FontWeight.BOLD,
                    color=COLORS["text_main"],
                ),
                ft.Text(
                    get_string("create_profile_hint"),
                    size=14,
                    color=COLORS["text_sub"],
                ),
                ft.Container(height=12),
                ft.Button(
                    "Create Profile",
                    icon=ft.Icons.ADD,
                    height=44,
                    style=ACCENT_STYLE,
                    on_click=on_create,
                ),
            ],
        ),
    )
