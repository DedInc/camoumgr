from typing import Any

import flet as ft

from .colors import COLORS

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
