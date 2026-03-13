"""Shared helpers for API routes (DRY)."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

from fastapi import HTTPException

from ..core.config import DATA_DIR
from .schemas.profiles import ProfileResponse

if TYPE_CHECKING:
    from ..interfaces import IBrowserLauncher, IProfileManager


def require_profile(name: str, pm: IProfileManager) -> None:
    """Raise 404 if the profile does not exist."""
    if name not in pm.profiles:
        raise HTTPException(status_code=404, detail=f"Profile '{name}' not found")


def build_profile_response(
    name: str,
    pm: IProfileManager,
    bl: IBrowserLauncher,
) -> ProfileResponse:
    """Build a ProfileResponse DTO for the given profile name."""
    profile = pm.profiles[name]
    data_dir = os.path.join(os.getcwd(), DATA_DIR, name)
    return ProfileResponse(
        name=profile.name,
        proxy=profile.proxy,
        os_type=profile.os_type,
        data_dir=data_dir,
        is_running=bl.is_running(name),
    )
