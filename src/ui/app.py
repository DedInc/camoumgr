import asyncio

import flet as ft

from ..config import COLORS
from ..container import Container
from ..interfaces.protocols import IBrowserLauncher, IProfileManager, IProxyService
from ..logging_config import get_logger
from ..strings import get_string
from .actions import (
    add_profile,
    bulk_delete_profiles,
    bulk_launch_profiles,
    bulk_stop_profiles,
    delete_profile,
    edit_profile,
    export_profile,
    import_profile,
    launch_or_stop,
)
from .bulk_bar import rebuild_bulk_bar
from .dialogs import open_log_dialog
from .profile_list import build_content_area, build_empty_state, build_profile_card
from .refs import UIRefs
from .sidebar import build_sidebar
from .state import ITEMS_PER_PAGE, AppState
from .theme import configure_page
from .ui_factory import build_ui_refs

logger = get_logger("app")


class App:
    def __init__(self, container: Container | None = None) -> None:
        c = container or Container()
        self.pm: IProfileManager = c.profile_manager
        self.bl: IBrowserLauncher = c.browser_launcher
        self.ps: IProxyService = c.proxy_service
        self.state = AppState()
        self.page: ft.Page | None = None
        self._reconcile_started = False
        self.refs: UIRefs | None = None

    def run(self) -> None:
        ft.run(self._main)

    def _main(self, page: ft.Page) -> None:
        self.page = page
        configure_page(page)
        fp = ft.FilePicker()
        page.services.append(fp)
        self.refs = build_ui_refs(
            pm=self.pm,
            on_change_page=self._change_page,
            on_select=self._on_toggle_select,
            file_picker=fp,
        )
        page.add(self._build_root_layout(self.refs))
        self._refresh_profiles()
        self.state._last_running_snapshot = self.bl.running_profile_names()
        if not self._reconcile_started:
            self._reconcile_started = True
            page.run_task(self._ui_reconcile_loop)

    def _build_root_layout(self, r: UIRefs) -> ft.Row:
        sidebar = build_sidebar(
            r.stats_text,
            r.running_text,
            r.log_text,
            r.log_column,
            r.log_toggle_btn,
            on_new_profile=lambda _: self._open_add_dialog(),
            on_import=self._on_import,
            on_export=lambda _: self._on_export_open(),
            on_toggle_log=lambda _: self._toggle_log(),
            on_fullscreen_log=lambda _: self._open_log_fullscreen(),
        )
        content = build_content_area(
            r.content_subtitle,
            r.profile_list_area,
            r.prev_btn,
            r.next_btn,
            r.page_label,
            r.bulk_bar,
        )
        return ft.Row(
            expand=True,
            spacing=0,
            controls=[
                sidebar,
                ft.VerticalDivider(width=1, color=COLORS["border"]),
                content,
            ],
        )

    def _get_page_profiles(self):
        all_profiles = self.pm.list_profiles()
        total = max(1, (len(all_profiles) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE)
        self.state.current_page = min(self.state.current_page, total)
        start = (self.state.current_page - 1) * ITEMS_PER_PAGE
        return all_profiles, all_profiles[start : start + ITEMS_PER_PAGE], total

    def _refresh_profiles(self) -> None:
        r = self.refs
        assert r is not None
        self._update_stats()
        self._flush_log()
        all_profiles, page_profiles, total_pages = self._get_page_profiles()

        all_names = {p.name for p in all_profiles}
        for stale in self.state.selected_names() - all_names:
            self.state.toggle_selection(stale)

        r.profile_list_area.controls = (
            [
                build_profile_card(
                    p,
                    self.state.is_loading(p.name),
                    self.bl.is_running(p.name),
                    self._on_launch,
                    self._on_edit,
                    self._on_delete,
                    is_selected=self.state.is_selected(p.name),
                    on_select=self._on_toggle_select,
                )
                for p in page_profiles
            ]
            if page_profiles
            else [build_empty_state(lambda _: self._open_add_dialog())]
        )
        rebuild_bulk_bar(
            r.bulk_bar,
            self.state,
            page_profiles,
            {
                "launch": self._on_bulk_launch,
                "stop": self._on_bulk_stop,
                "delete": self._on_bulk_delete,
                "select_page": self._on_select_all_page,
                "deselect_page": self._on_deselect_page,
                "clear": self._on_clear_selection,
            },
        )
        r.content_subtitle.value = self._profiles_subtitle()
        r.page_label.value = get_string(
            "page_of",
            current=self.state.current_page,
            total=total_pages,
        )
        r.prev_btn.disabled = self.state.current_page <= 1
        r.next_btn.disabled = self.state.current_page >= total_pages
        self._safe_update()

    def _change_page(self, delta: int) -> None:
        self.state.current_page += delta
        self._refresh_profiles()

    def _profiles_subtitle(self) -> str:
        c, r = len(self.pm.profiles), self.bl.running_count()
        suffix = f"  \u2014  \u25cf {r} running" if r else ""
        return f"{c} profile{'s' if c != 1 else ''} configured{suffix}"

    def _update_stats(self) -> None:
        r = self.refs
        if r:
            cnt = self.bl.running_count()
            r.stats_text.value = get_string(
                "total_profiles",
                count=len(self.pm.profiles),
            )
            r.running_text.value = (
                f"\u25cf  {cnt} browser{'s' if cnt != 1 else ''} running"
                if cnt
                else "\u25cb  No active sessions"
            )

    def _log(self, message: str) -> None:
        logger.info(message)
        if self.state.add_log(message):
            self.state.schedule_refresh()

    def _flush_log(self) -> None:
        text = self.state.flush_log()
        if text is not None and self.refs:
            lines = text.split("\n")
            sidebar_lines = lines[-6:]
            self.refs.log_text.value = "\n".join(sidebar_lines)
            self.refs.log_column.height = max(72, len(sidebar_lines) * 18 + 20)
            self.refs.log_column.visible = (
                bool(sidebar_lines) and not self.state.log_collapsed
            )

    def _toggle_log(self) -> None:
        assert self.refs is not None and self.page is not None
        self.state.log_collapsed = not self.state.log_collapsed
        has_content = bool(self.refs.log_text.value)
        self.refs.log_column.visible = has_content and not self.state.log_collapsed
        self.refs.log_toggle_btn.icon = (
            ft.Icons.KEYBOARD_ARROW_RIGHT
            if self.state.log_collapsed
            else ft.Icons.KEYBOARD_ARROW_DOWN
        )
        self.page.update()

    def _open_log_fullscreen(self) -> None:
        assert self.page is not None
        open_log_dialog(self.page, self.state.get_all_log_lines())

    def _safe_update(self) -> None:
        if not self.page:
            return
        try:
            with self.state._ui_update_lock:
                self.page.update()
        except Exception as e:
            logger.error("Error updating UI: %s", e)

    async def _ui_reconcile_loop(self) -> None:
        while self.page:
            try:
                running_now = self.bl.running_profile_names()
                changed = running_now != self.state._last_running_snapshot
                if changed:
                    self.state._last_running_snapshot = running_now
                if changed or self.state.consume_refresh():
                    self._refresh_profiles()
            except Exception as e:
                logger.error("Error in UI reconcile loop: %s", e)
            await asyncio.sleep(0.12)

    def _on_launch(self, name: str) -> None:
        launch_or_stop(name, self.pm, self.bl, self.state, self._log)

    def _on_delete(self, name: str) -> None:
        assert self.page is not None
        delete_profile(self.page, name, self.pm, self._log, self._refresh_profiles)

    def _on_edit(self, name: str) -> None:
        assert self.page is not None
        edit_profile(
            self.page,
            name,
            self.pm,
            self.bl,
            self.ps,
            self._log,
            self._refresh_profiles,
        )

    def _open_add_dialog(self) -> None:
        assert self.page is not None
        add_profile(self.page, self.pm, self.ps, self._log, self._refresh_profiles)

    async def _on_import(self, _=None) -> None:
        assert self.refs is not None
        await import_profile(
            self.refs.file_picker,
            self.pm,
            self._log,
            self._refresh_profiles,
        )

    def _on_export_open(self) -> None:
        assert self.page is not None and self.refs is not None
        export_profile(self.page, self.refs.file_picker, self.pm, self._log)

    def _on_toggle_select(self, name: str) -> None:
        self.state.toggle_selection(name)
        self.state.schedule_refresh()

    def _on_select_all_page(self) -> None:
        _, page_profiles, _ = self._get_page_profiles()
        self.state.select_all([p.name for p in page_profiles])
        self.state.schedule_refresh()

    def _on_deselect_page(self) -> None:
        _, page_profiles, _ = self._get_page_profiles()
        for p in page_profiles:
            if self.state.is_selected(p.name):
                self.state.toggle_selection(p.name)
        self.state.schedule_refresh()

    def _on_clear_selection(self) -> None:
        self.state.clear_selection()
        self.state.schedule_refresh()

    def _on_bulk_delete(self) -> None:
        assert self.page is not None
        if names := list(self.state.selected_names()):
            bulk_delete_profiles(
                self.page,
                names,
                self.pm,
                self._log,
                self._refresh_profiles,
                on_done=self.state.clear_selection,
            )

    def _on_bulk_launch(self) -> None:
        if names := list(self.state.selected_names()):
            bulk_launch_profiles(names, self.pm, self.bl, self.state, self._log)

    def _on_bulk_stop(self) -> None:
        if names := list(self.state.selected_names()):
            bulk_stop_profiles(names, self.pm, self.bl, self.state, self._log)
