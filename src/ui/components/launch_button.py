from collections.abc import Callable

import flet as ft

from ...models.profile import Profile
from ..theme.colors import COLORS
from ..theme.styles import ACCENT_STYLE, ERROR_STYLE


def resolve_status(profile: Profile, is_running: bool) -> tuple[str, str, str]:
    """Return (icon, label, color) based on the profile's current state."""
    if is_running:
        return ft.Icons.CIRCLE, "RUNNING", COLORS["success"]
    if profile.proxy:
        return ft.Icons.CIRCLE, "PROXY ACTIVE", COLORS["success"]
    return ft.Icons.CIRCLE_OUTLINED, "DIRECT CONNECTION", COLORS["text_dim"]


def build_launch_button(
    name: str,
    is_loading: bool,
    is_running: bool,
    on_launch: Callable,
) -> ft.Button:
    """Create the context-aware Launch / Stop / Loading button."""
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
