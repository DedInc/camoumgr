from collections.abc import Callable

import flet as ft

from ...models.profile import Profile
from ..theme.colors import COLORS
from .launch_button import build_launch_button, resolve_status

_OS_COLORS = {"windows": "#0078D7", "macos": "#A0A0AA", "linux": "#E95420"}
_OS_LABELS = {"windows": "WIN", "macos": "MAC", "linux": "LIN"}


def build_profile_card(
    profile: Profile,
    is_loading: bool,
    is_running: bool,
    on_launch: Callable[[str], None],
    on_edit: Callable[[str], None],
    on_delete: Callable[[str], None],
    is_selected: bool = False,
    on_select: Callable[[str], None] | None = None,
) -> ft.Container:
    """Build a single profile row card with status, actions, and selection."""
    badge_color = _OS_COLORS.get(profile.os_type, COLORS["accent"])
    status_icon, status_text, status_color = resolve_status(profile, is_running)
    launch_btn = build_launch_button(profile.name, is_loading, is_running, on_launch)

    action_buttons = _build_action_buttons(profile.name, on_edit, on_delete)
    check_box = _build_checkbox(profile.name, is_selected, on_select)

    if is_running:
        border_color, card_bg = COLORS["accent"], COLORS["card_hover"]
    elif is_selected:
        border_color, card_bg = "#9D5EF7", "#171732"
    else:
        border_color, card_bg = COLORS["card_border"], COLORS["card_bg"]

    left_side = _build_left_section(
        check_box,
        badge_color,
        profile,
        status_icon,
        status_text,
        status_color,
    )

    return ft.Container(
        height=100,
        border_radius=16,
        border=ft.Border.all(1, border_color),
        bgcolor=card_bg,
        padding=ft.Padding.symmetric(horizontal=30, vertical=20),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                left_side,
                ft.Row(
                    spacing=8,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[launch_btn, *action_buttons],
                ),
            ],
        ),
    )


def _build_action_buttons(
    name: str,
    on_edit: Callable[[str], None],
    on_delete: Callable[[str], None],
) -> list[ft.IconButton]:
    return [
        ft.IconButton(
            icon=ft.Icons.EDIT,
            icon_size=20,
            icon_color=COLORS["text_sub"],
            tooltip="Edit profile",
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
            on_click=lambda _, n=name: on_edit(n),
        ),
        ft.IconButton(
            icon=ft.Icons.CLOSE,
            icon_size=20,
            icon_color=COLORS["text_dim"],
            tooltip="Delete profile",
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                overlay_color=ft.Colors.with_opacity(0.1, COLORS["error"]),
            ),
            on_click=lambda _, n=name: on_delete(n),
        ),
    ]


def _build_checkbox(
    name: str,
    is_selected: bool,
    on_select: Callable[[str], None] | None,
) -> ft.Container:
    return ft.Container(
        width=22,
        height=22,
        border_radius=11,
        border=ft.Border.all(
            2,
            COLORS["accent"] if is_selected else COLORS["card_border"],
        ),
        bgcolor=COLORS["accent"] if is_selected else "transparent",
        alignment=ft.Alignment(0, 0),
        on_click=lambda _, n=name: on_select(n) if on_select else None,
        ink=True,
        tooltip="Select profile",
        content=ft.Icon(ft.Icons.CHECK, size=13, color="#FFFFFF")
        if is_selected
        else None,
    )


def _build_left_section(
    check_box: ft.Container,
    badge_color: str,
    profile: Profile,
    status_icon: str,
    status_text: str,
    status_color: str,
) -> ft.Row:
    return ft.Row(
        spacing=16,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            check_box,
            ft.Container(
                width=52,
                height=52,
                border_radius=8,
                bgcolor=badge_color,
                alignment=ft.Alignment(0, 0),
                content=ft.Text(
                    _OS_LABELS.get(profile.os_type, "OS"),
                    size=12,
                    weight=ft.FontWeight.BOLD,
                    color="#FFFFFF",
                ),
            ),
            ft.Column(
                spacing=4,
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Text(
                        profile.name,
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=COLORS["text_main"],
                    ),
                    ft.Row(
                        spacing=6,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Icon(status_icon, size=10, color=status_color),
                            ft.Text(status_text, size=12, color=status_color),
                        ],
                    ),
                ],
            ),
        ],
    )
