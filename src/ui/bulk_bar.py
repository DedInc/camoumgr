from collections.abc import Callable

import flet as ft

from ..config import COLORS
from ..models.profile import Profile
from .state import AppState

BulkCallbacks = dict[str, Callable[[], None]]


def rebuild_bulk_bar(
    bulk_bar: ft.Row,
    state: AppState,
    page_profiles: list[Profile],
    cbs: BulkCallbacks,
) -> None:
    count = len(state.selected_names())
    if count == 0:
        bulk_bar.visible = False
        bulk_bar.controls = []
        return
    all_page_selected = bool(page_profiles) and all(
        state.is_selected(p.name) for p in page_profiles
    )
    bulk_bar.visible = True
    bulk_bar.controls = [_build_container(count, all_page_selected, cbs)]


def _build_container(
    count: int,
    all_page_selected: bool,
    cbs: BulkCallbacks,
) -> ft.Container:
    return ft.Container(
        bgcolor=COLORS["card_bg"],
        border=ft.border.all(1, COLORS["accent"]),
        border_radius=12,
        padding=ft.padding.symmetric(horizontal=16, vertical=8),
        content=ft.Row(
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Icon(ft.Icons.CHECK_BOX, size=16, color=COLORS["accent"]),
                ft.Text(
                    f"{count} selected",
                    size=13,
                    weight=ft.FontWeight.BOLD,
                    color=COLORS["text_main"],
                ),
                ft.VerticalDivider(width=1, color=COLORS["card_border"]),
                *_build_action_buttons(all_page_selected, cbs),
            ],
        ),
    )


def _build_action_buttons(
    all_page_selected: bool,
    cbs: BulkCallbacks,
) -> list[ft.Control]:
    return [
        ft.TextButton(
            "Launch",
            icon=ft.Icons.PLAY_ARROW,
            on_click=lambda _: cbs["launch"](),
            style=ft.ButtonStyle(color=COLORS["success"]),
        ),
        ft.TextButton(
            "Stop",
            icon=ft.Icons.STOP,
            on_click=lambda _: cbs["stop"](),
            style=ft.ButtonStyle(color=COLORS["text_sub"]),
        ),
        ft.TextButton(
            "Delete",
            icon=ft.Icons.DELETE,
            on_click=lambda _: cbs["delete"](),
            style=ft.ButtonStyle(color=COLORS["error"]),
        ),
        ft.VerticalDivider(width=1, color=COLORS["card_border"]),
        ft.TextButton(
            "Deselect Page" if all_page_selected else "Select Page",
            icon=ft.Icons.DESELECT if all_page_selected else ft.Icons.SELECT_ALL,
            on_click=lambda _, v=all_page_selected: (
                cbs["deselect_page"]() if v else cbs["select_page"]()
            ),
            style=ft.ButtonStyle(color=COLORS["text_sub"]),
        ),
        ft.TextButton(
            "Clear",
            icon=ft.Icons.CLOSE,
            on_click=lambda _: cbs["clear"](),
            style=ft.ButtonStyle(color=COLORS["text_dim"]),
        ),
    ]
