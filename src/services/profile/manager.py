import json
import os
import pathlib
import shutil

from ...core.config import DATA_DIR, PROFILES_FILE
from ...core.logging import get_logger
from ...models.profile import Profile
from .transfer import export_to_zip, import_from_zip

logger = get_logger("profile.manager")


class ProfileManager:
    def __init__(self) -> None:
        self.profiles: dict[str, Profile] = {}
        self._load_profiles()
        pathlib.Path(DATA_DIR).mkdir(exist_ok=True, parents=True)

    def _data_path(self, name: str) -> str:
        return os.path.join(DATA_DIR, name)

    def _load_profiles(self) -> None:
        if pathlib.Path(PROFILES_FILE).exists():
            try:
                with pathlib.Path(PROFILES_FILE).open(encoding="utf-8") as f:
                    data = json.load(f)
                    for name, p_data in data.items():
                        clean_data = {
                            "name": p_data.get("name"),
                            "proxy": p_data.get("proxy"),
                            "os_type": p_data.get(
                                "os_type",
                                p_data.get("config", {}).get("os", "windows"),
                            ),
                        }
                        self.profiles[name] = Profile(**clean_data)
                logger.info("Loaded %d profiles", len(self.profiles))
            except Exception as e:
                logger.exception("Error loading profiles: %s", e)

    def save_profiles(self) -> None:
        try:
            with pathlib.Path(PROFILES_FILE).open("w", encoding="utf-8") as f:
                json.dump(
                    {name: p.to_dict() for name, p in self.profiles.items()},
                    f,
                    indent=4,
                )
            logger.debug("Profiles saved")
        except Exception as e:
            logger.exception("Error saving profiles: %s", e)

    def add_profile(self, name: str, proxy: str, os_type: str) -> bool:
        if name in self.profiles:
            return False
        self.profiles[name] = Profile(
            name=name,
            proxy=proxy or None,
            os_type=os_type,
        )
        self.save_profiles()
        pathlib.Path(self._data_path(name)).mkdir(exist_ok=True, parents=True)
        logger.info("Created profile: %s", name)
        return True

    def update_profile(
        self,
        original_name: str,
        new_name: str,
        new_proxy: str,
        new_os: str,
    ) -> bool:
        if original_name not in self.profiles:
            return False

        if new_name != original_name and new_name in self.profiles:
            return False

        profile = self.profiles[original_name]
        profile.name = new_name
        profile.proxy = new_proxy or None
        profile.os_type = new_os

        if new_name != original_name:
            del self.profiles[original_name]
            self.profiles[new_name] = profile

            old_dir = self._data_path(original_name)
            if pathlib.Path(old_dir).exists():
                pathlib.Path(old_dir).rename(self._data_path(new_name))

        self.save_profiles()
        logger.info("Updated profile: %s -> %s", original_name, new_name)
        return True

    def delete_profile(self, name: str) -> bool:
        if name in self.profiles:
            del self.profiles[name]
            self.save_profiles()
            shutil.rmtree(self._data_path(name), ignore_errors=True)
            logger.info("Deleted profile: %s", name)
            return True
        return False

    def list_profiles(self) -> list[Profile]:
        return list(self.profiles.values())

    def export_profile(
        self,
        name: str,
        export_path: str,
        include_data: bool = True,
    ) -> tuple[bool, str]:
        if name not in self.profiles:
            return False, "Profile not found"
        return export_to_zip(
            self.profiles[name],
            self._data_path(name),
            export_path,
            include_data,
        )

    def import_profile(
        self,
        zip_path: str,
        overwrite: bool = False,
    ) -> tuple[bool, str]:
        success, result = import_from_zip(zip_path, DATA_DIR)
        if not success:
            return False, result

        profile = result
        if profile.name in self.profiles and not overwrite:
            return False, f"Profile '{profile.name}' already exists"

        self.profiles[profile.name] = profile
        self.save_profiles()
        logger.info("Registered imported profile: %s", profile.name)
        return True, profile.name
