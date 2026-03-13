"""Event handlers extracted from App for Single Responsibility compliance."""

from collections.abc import Callable

import flet as ft

from ..interfaces.protocols import IBrowserLauncher, IProfileManager, IProxyService
from .actions.browser import launch_or_stop
from .actions.bulk import bulk_delete_profiles, bulk_launch_profiles, bulk_stop_profiles
from .actions.profile import add_profile, delete_profile, edit_profile
from .actions.transfer import export_profile, import_profile
from .dialogs import open_log_dialog
from .refs import UIRefs
from .state import AppState


class AppHandlers:
    """Decoupled event-handler object wired to the App's dependencies."""

    def __init__(
        self,
        pm: IProfileManager,
        bl: IBrowserLauncher,
        ps: IProxyService,
        state: AppState,
        get_page: Callable[[], ft.Page | None],
        get_refs: Callable[[], UIRefs | None],
        log_fn: Callable[[str], None],
        refresh_fn: Callable[[], None],
        get_page_profiles: Callable[[], tuple],
    ) -> None:
        self._pm = pm
        self._bl = bl
        self._ps = ps
        self._state = state
        self._get_page = get_page
        self._get_refs = get_refs
        self._log = log_fn
        self._refresh = refresh_fn
        self._get_page_profiles = get_page_profiles

    def on_launch(self, name: str) -> None:
        launch_or_stop(name, self._pm, self._bl, self._state, self._log)

    def on_delete(self, name: str) -> None:
        page = self._get_page()
        assert page is not None
        delete_profile(page, name, self._pm, self._log, self._refresh)

    def on_edit(self, name: str) -> None:
        page = self._get_page()
        assert page is not None
        edit_profile(
            page,
            name,
            self._pm,
            self._bl,
            self._ps,
            self._log,
            self._refresh,
        )

    def open_add_dialog(self) -> None:
        page = self._get_page()
        assert page is not None
        add_profile(page, self._pm, self._ps, self._log, self._refresh)

    async def on_import(self, _: ft.ControlEvent | None = None) -> None:
        refs = self._get_refs()
        assert refs is not None
        await import_profile(refs.file_picker, self._pm, self._log, self._refresh)

    def on_export_open(self) -> None:
        page = self._get_page()
        refs = self._get_refs()
        assert page is not None and refs is not None
        export_profile(page, refs.file_picker, self._pm, self._log)

    # --- Selection handlers ---

    def on_toggle_select(self, name: str) -> None:
        self._state.toggle_selection(name)
        self._state.schedule_refresh()

    def on_select_all_page(self) -> None:
        _, page_profiles, _ = self._get_page_profiles()
        self._state.select_all([p.name for p in page_profiles])
        self._state.schedule_refresh()

    def on_deselect_page(self) -> None:
        _, page_profiles, _ = self._get_page_profiles()
        for p in page_profiles:
            if self._state.is_selected(p.name):
                self._state.toggle_selection(p.name)
        self._state.schedule_refresh()

    def on_clear_selection(self) -> None:
        self._state.clear_selection()
        self._state.schedule_refresh()

    # --- Bulk action handlers ---

    def on_bulk_delete(self) -> None:
        page = self._get_page()
        assert page is not None
        if names := list(self._state.selected_names()):
            bulk_delete_profiles(
                page,
                names,
                self._pm,
                self._log,
                self._refresh,
                on_done=self._state.clear_selection,
            )

    def on_bulk_launch(self) -> None:
        if names := list(self._state.selected_names()):
            bulk_launch_profiles(names, self._pm, self._bl, self._state, self._log)

    def on_bulk_stop(self) -> None:
        if names := list(self._state.selected_names()):
            bulk_stop_profiles(names, self._pm, self._bl, self._state, self._log)

    # --- Log handlers ---

    def toggle_log(self) -> None:
        page = self._get_page()
        refs = self._get_refs()
        assert refs is not None and page is not None
        self._state.log_collapsed = not self._state.log_collapsed
        has_content = bool(refs.log_text.value)
        refs.log_column.visible = has_content and not self._state.log_collapsed
        refs.log_toggle_btn.icon = (
            ft.Icons.KEYBOARD_ARROW_RIGHT
            if self._state.log_collapsed
            else ft.Icons.KEYBOARD_ARROW_DOWN
        )
        page.update()

    def open_log_fullscreen(self) -> None:
        page = self._get_page()
        assert page is not None
        open_log_dialog(page, self._state.get_all_log_lines())
