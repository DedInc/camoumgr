import asyncio

import flet as ft

from ..core.container import Container
from ..core.logging import get_logger
from ..core.strings import get_string
from ..interfaces.protocols import IBrowserLauncher, IProfileManager, IProxyService
from .components import (
    build_content_area,
    build_empty_state,
    build_profile_card,
    build_sidebar,
    build_ui_refs,
    rebuild_bulk_bar,
)
from .handlers import AppHandlers
from .refs import UIRefs
from .state import ITEMS_PER_PAGE, AppState
from .theme import COLORS, configure_page

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
        c.event_bus.subscribe(self.state.schedule_refresh)
        self.h = AppHandlers(
            pm=self.pm,
            bl=self.bl,
            ps=self.ps,
            state=self.state,
            get_page=lambda: self.page,
            get_refs=lambda: self.refs,
            log_fn=self._log,
            refresh_fn=self._refresh_profiles,
            get_page_profiles=self._get_page_profiles,
        )

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
            on_new_profile=lambda _: self.h.open_add_dialog(),
            on_import=self.h.on_import,
            on_export=lambda _: self.h.on_export_open(),
            on_toggle_log=lambda _: self.h.toggle_log(),
            on_fullscreen_log=lambda _: self.h.open_log_fullscreen(),
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

    def _get_page_profiles(self) -> tuple[list, list, int]:
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
                    self.h.on_launch,
                    self.h.on_edit,
                    self.h.on_delete,
                    is_selected=self.state.is_selected(p.name),
                    on_select=self.h.on_toggle_select,
                )
                for p in page_profiles
            ]
            if page_profiles
            else [build_empty_state(lambda _: self.h.open_add_dialog())]
        )
        rebuild_bulk_bar(
            r.bulk_bar,
            self.state,
            page_profiles,
            {
                "launch": self.h.on_bulk_launch,
                "stop": self.h.on_bulk_stop,
                "delete": self.h.on_bulk_delete,
                "select_page": self.h.on_select_all_page,
                "deselect_page": self.h.on_deselect_page,
                "clear": self.h.on_clear_selection,
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
