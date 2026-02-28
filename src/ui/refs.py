from dataclasses import dataclass

import flet as ft


@dataclass
class UIRefs:
    stats_text: ft.Text
    running_text: ft.Text
    log_text: ft.Text
    log_column: ft.Container
    log_toggle_btn: ft.TextButton
    content_subtitle: ft.Text
    profile_list_area: ft.Column
    prev_btn: ft.IconButton
    next_btn: ft.IconButton
    page_label: ft.Text
    bulk_bar: ft.Row
    file_picker: ft.FilePicker
