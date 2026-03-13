import flet as ft

from ...core.strings import get_string
from ..theme.colors import COLORS


def build_content_area(
    subtitle: ft.Text,
    profile_list: ft.Column,
    prev_btn: ft.IconButton,
    next_btn: ft.IconButton,
    page_label: ft.Text,
    bulk_bar: ft.Control | None = None,
) -> ft.Container:
    """Main content area with profile list, pagination, and bulk-action bar."""
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
