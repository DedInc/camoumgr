from collections.abc import Callable

import flet as ft

from ...config import COLORS
from ...strings import get_string
from ..theme import ERROR_STYLE


def open_confirm_dialog(
    page: ft.Page,
    profile_name: str,
    on_confirm: Callable[[], None],
    *,
    title: str | None = None,
    body: str | None = None,
) -> None:

    def _on_confirm(_):
        on_confirm()
        page.pop_dialog()

    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text(
            title
            if title is not None
            else get_string("confirm_delete_msg", name=profile_name),
            size=18,
            weight=ft.FontWeight.BOLD,
        ),
        content=ft.Text(
            body if body is not None else "This action cannot be undone.",
            size=13,
            color=COLORS["text_dim"],
        ),
        actions=[
            ft.TextButton("Cancel", on_click=lambda e: page.pop_dialog()),
            ft.Button(
                "Delete",
                icon=ft.Icons.DELETE,
                style=ERROR_STYLE,
                on_click=_on_confirm,
            ),
        ],
    )
    page.show_dialog(dlg)
