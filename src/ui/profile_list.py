from collections.abc import Callable

import flet as ft

from ..config import COLORS
from ..models.profile import Profile
from ..strings import get_string
from .theme import ACCENT_STYLE, ERROR_STYLE

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
    badge_color = _OS_COLORS.get(profile.os_type, COLORS["accent"])
    status_icon, status_text, status_color = _resolve_status(profile, is_running)
    launch_btn = _build_launch_button(profile.name, is_loading, is_running, on_launch)

    edit_btn = ft.IconButton(
        icon=ft.Icons.EDIT,
        icon_size=20,
        icon_color=COLORS["text_sub"],
        tooltip="Edit profile",
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
        on_click=lambda _, n=profile.name: on_edit(n),
    )
    delete_btn = ft.IconButton(
        icon=ft.Icons.CLOSE,
        icon_size=20,
        icon_color=COLORS["text_dim"],
        tooltip="Delete profile",
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10),
            overlay_color=ft.Colors.with_opacity(0.1, COLORS["error"]),
        ),
        on_click=lambda _, n=profile.name: on_delete(n),
    )

    check_box = ft.Container(
        width=22,
        height=22,
        border_radius=11,
        border=ft.Border.all(
            2,
            COLORS["accent"] if is_selected else COLORS["card_border"],
        ),
        bgcolor=COLORS["accent"] if is_selected else "transparent",
        alignment=ft.Alignment(0, 0),
        on_click=lambda _, n=profile.name: on_select(n) if on_select else None,
        ink=True,
        tooltip="Select profile",
        content=ft.Icon(ft.Icons.CHECK, size=13, color="#FFFFFF")
        if is_selected
        else None,
    )
    if is_running:
        border_color, card_bg = COLORS["accent"], COLORS["card_hover"]
    elif is_selected:
        border_color, card_bg = "#9D5EF7", "#171732"
    else:
        border_color, card_bg = COLORS["card_border"], COLORS["card_bg"]

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
                ft.Row(
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
                                        ft.Icon(
                                            status_icon,
                                            size=10,
                                            color=status_color,
                                        ),
                                        ft.Text(
                                            status_text,
                                            size=12,
                                            color=status_color,
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),
                ft.Row(
                    spacing=8,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[launch_btn, edit_btn, delete_btn],
                ),
            ],
        ),
    )


def build_empty_state(on_create: Callable) -> ft.Container:
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


def build_content_area(
    subtitle: ft.Text,
    profile_list: ft.Column,
    prev_btn: ft.IconButton,
    next_btn: ft.IconButton,
    page_label: ft.Text,
    bulk_bar: ft.Control | None = None,
) -> ft.Container:
    return ft.Container(
        expand=True,
        bgcolor=COLORS["bg"],
        padding=ft.Padding.all(40),
        content=ft.Column(
            spacing=0,
            expand=True,
            controls=[
                ft.Text(
                    get_string("your_profiles"),
                    size=26,
                    weight=ft.FontWeight.BOLD,
                    color=COLORS["text_main"],
                ),
                ft.Container(height=6),
                subtitle,
                ft.Container(height=24),
                *([] if bulk_bar is None else [bulk_bar, ft.Container(height=8)]),
                profile_list,
                ft.Container(height=16),
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        prev_btn,
                        ft.Container(width=12),
                        page_label,
                        ft.Container(width=12),
                        next_btn,
                    ],
                ),
            ],
        ),
    )


def _resolve_status(profile: Profile, is_running: bool):
    if is_running:
        return ft.Icons.CIRCLE, "RUNNING", COLORS["success"]
    if profile.proxy:
        return ft.Icons.CIRCLE, get_string("proxy_active"), COLORS["success"]
    return ft.Icons.CIRCLE_OUTLINED, get_string("direct_connection"), COLORS["text_dim"]


def _build_launch_button(
    name: str,
    is_loading: bool,
    is_running: bool,
    on_launch: Callable,
) -> ft.Button:
    if is_loading:
        return ft.Button(
            "Loading...",
            icon=ft.Icons.HOURGLASS_TOP,
            width=130,
            height=44,
            disabled=True,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                bgcolor=COLORS["text_dim"],
                color="#FFFFFF",
            ),
        )
    if is_running:
        return ft.Button(
            "Stop",
            icon=ft.Icons.STOP,
            width=120,
            height=44,
            style=ERROR_STYLE,
            on_click=lambda _, n=name: on_launch(n),
        )
    return ft.Button(
        "Launch",
        icon=ft.Icons.PLAY_ARROW,
        width=120,
        height=44,
        style=ACCENT_STYLE,
        on_click=lambda _, n=name: on_launch(n),
    )
