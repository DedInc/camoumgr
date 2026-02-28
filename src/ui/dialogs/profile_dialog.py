import threading
from collections.abc import Callable

import flet as ft

from ...config import COLORS
from ...interfaces.protocols import IProxyService
from ...models.profile import Profile
from ...strings import get_string
from ...utils.validation import validate_profile_name, validate_proxy_format
from ..theme import ACCENT_STYLE, DLG_FIELD_KWARGS, OUTLINE_STYLE, build_os_dropdown


def open_profile_dialog(
    page: ft.Page,
    proxy_service: IProxyService,
    on_save: Callable[[str, str, str], str | None],
    profile: Profile | None = None,
) -> None:
    is_edit = profile is not None
    title = "Edit Profile" if is_edit else get_string("create_new_profile")
    subtitle = (
        f"Editing: {profile.name}"
        if profile is not None
        else "Configure your browser identity"
    )
    save_label = "Save Changes" if is_edit else "Create Profile"
    save_icon = ft.Icons.SAVE if is_edit else ft.Icons.ADD

    name_field = ft.TextField(
        label=get_string("profile_name"),
        value=profile.name if profile is not None else "",
        hint_text="" if profile is not None else "Enter a profile name",
        **DLG_FIELD_KWARGS,
    )
    proxy_field = ft.TextField(
        label="Proxy (optional)",
        value=(profile.proxy or "") if profile is not None else "",
        hint_text="user:pass@ip:port",
        **DLG_FIELD_KWARGS,
    )
    os_dropdown = build_os_dropdown(
        profile.os_type if profile is not None else "windows",
    )
    name_error = ft.Text("", size=12, color=COLORS["error"], visible=False)
    proxy_error = ft.Text("", size=12, color=COLORS["error"], visible=False)
    check_btn = ft.OutlinedButton(
        "Check Proxy",
        icon=ft.Icons.WIFI_FIND,
        height=38,
        style=OUTLINE_STYLE,
    )

    check_btn.on_click = lambda _: _do_proxy_check(
        page,
        proxy_field,
        proxy_error,
        check_btn,
        proxy_service,
    )

    def on_submit(_):
        name = (name_field.value or "").strip()
        proxy = (proxy_field.value or "").strip()
        os_type = os_dropdown.value or "windows"
        name_error.visible = proxy_error.visible = False

        valid_name, name_err = validate_profile_name(name)
        if not valid_name:
            name_error.value = name_err
            name_error.visible = True
            page.update()
            return

        valid_proxy, proxy_err = validate_proxy_format(proxy)
        if not valid_proxy:
            proxy_error.value = proxy_err
            proxy_error.visible = True
            page.update()
            return

        error = on_save(name, proxy, os_type)
        if error:
            name_error.value = error
            name_error.visible = True
            page.update()
        else:
            page.pop_dialog()

    dlg = ft.AlertDialog(
        modal=True,
        bgcolor=COLORS["card_bg"],
        title=ft.Text(
            title,
            size=22,
            weight=ft.FontWeight.BOLD,
            color=COLORS["text_main"],
        ),
        content=ft.Container(
            width=420,
            content=ft.Column(
                tight=True,
                spacing=10,
                controls=[
                    ft.Text(subtitle, size=13, color=COLORS["text_sub"]),
                    ft.Container(height=14),
                    name_field,
                    name_error,
                    ft.Container(height=6),
                    proxy_field,
                    proxy_error,
                    check_btn,
                    ft.Container(height=6),
                    os_dropdown,
                    ft.Container(height=14),
                ],
            ),
        ),
        actions=[
            ft.TextButton(
                "Cancel",
                style=ft.ButtonStyle(color=COLORS["text_sub"]),
                on_click=lambda e: page.pop_dialog(),
            ),
            ft.Button(
                save_label,
                icon=save_icon,
                style=ACCENT_STYLE,
                on_click=on_submit,
            ),
        ],
    )
    page.show_dialog(dlg)


def _do_proxy_check(
    page: ft.Page,
    proxy_field: ft.TextField,
    proxy_error: ft.Text,
    check_btn: ft.OutlinedButton,
    proxy_service: IProxyService,
) -> None:
    proxy = (proxy_field.value or "").strip()
    if not proxy:
        proxy_error.value = "Enter a proxy to check"
        proxy_error.color = COLORS["warning"]
        proxy_error.visible = True
        page.update()
        return

    check_btn.content = ft.Text(get_string("proxy_checking"))
    check_btn.disabled = True
    proxy_error.visible = False
    page.update()

    def do_check():
        success, message = proxy_service.check_proxy_sync(proxy)
        check_btn.content = ft.Text("Check Proxy")
        check_btn.disabled = False
        proxy_error.value = message
        proxy_error.color = COLORS["success"] if success else COLORS["error"]
        proxy_error.visible = True
        page.update()

    threading.Thread(target=do_check, daemon=True).start()
