import flet as ft

from ...config import COLORS


def open_log_dialog(page: ft.Page, log_lines: list[str]) -> None:
    content = "\n".join(log_lines) if log_lines else "No activity yet."

    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text("Activity Log", size=22, weight=ft.FontWeight.BOLD),
        content=ft.Container(
            width=800,
            height=400,
            border_radius=10,
            bgcolor=COLORS["log_bg"],
            padding=14,
            content=ft.Column(
                scroll=ft.ScrollMode.AUTO,
                controls=[
                    ft.Text(
                        f"{len(log_lines)} entries",
                        size=12,
                        color=COLORS["text_dim"],
                    ),
                    ft.Container(height=8),
                    ft.Text(
                        content,
                        size=12,
                        color=COLORS["text_sub"],
                        selectable=True,
                    ),
                ],
            ),
        ),
        actions=[
            ft.TextButton("Close", on_click=lambda e: page.pop_dialog()),
        ],
    )
    page.show_dialog(dlg)
