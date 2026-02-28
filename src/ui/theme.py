import os
from typing import Any

import flet as ft

from ..config import COLORS

ACCENT_STYLE = ft.ButtonStyle(
    shape=ft.RoundedRectangleBorder(radius=10),
    bgcolor=COLORS["accent"],
    color="#FFFFFF",
)

ERROR_STYLE = ft.ButtonStyle(
    shape=ft.RoundedRectangleBorder(radius=10),
    bgcolor=COLORS["error"],
    color="#FFFFFF",
)

OUTLINE_STYLE = ft.ButtonStyle(
    shape=ft.RoundedRectangleBorder(radius=8),
    side=ft.BorderSide(1, COLORS["card_border"]),
    color=COLORS["text_sub"],
)


DLG_FIELD_KWARGS: dict[str, Any] = dict(
    border_radius=10,
    bgcolor="#13132A",
    color=COLORS["text_main"],
    border_color=COLORS["card_border"],
    focused_border_color=COLORS["accent"],
    label_style=ft.TextStyle(color=COLORS["text_sub"]),
    cursor_color=COLORS["accent"],
)


def build_page_theme() -> ft.Theme:
    return ft.Theme(
        color_scheme_seed="#7C3AED",
        color_scheme=ft.ColorScheme(
            primary="#7C3AED",
            on_primary="#FFFFFF",
            surface=COLORS["card_bg"],
            on_surface=COLORS["text_main"],
            on_surface_variant=COLORS["text_sub"],
            surface_container=COLORS["sidebar"],
            outline=COLORS["border"],
            error="#EF4444",
        ),
    )


def build_os_dropdown(value: str = "windows") -> ft.Dropdown:
    return ft.Dropdown(
        label="Operating System",
        value=value,
        bgcolor="#13132A",
        color=COLORS["text_main"],
        border_color=COLORS["card_border"],
        focused_border_color=COLORS["accent"],
        label_style=ft.TextStyle(color=COLORS["text_sub"]),
        border_radius=10,
        options=[
            ft.dropdown.Option("windows"),
            ft.dropdown.Option("macos"),
            ft.dropdown.Option("linux"),
        ],
    )


def configure_page(page: ft.Page) -> None:
    page.title = "Camoufox Manager"
    page.window.width, page.window.height = 1280, 820
    page.window.min_width, page.window.min_height = 1024, 680

    icon_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "assets", "icon.png")
    )
    if os.path.exists(icon_path):
        page.window.icon = icon_path

    page.padding = page.spacing = 0
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = COLORS["bg"]
    page.theme = build_page_theme()
