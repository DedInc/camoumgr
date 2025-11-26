import json
import os
import shutil
import zipfile
from typing import Dict, Tuple
from datetime import datetime

from ..models.profile import Profile
from ..config import PROFILES_FILE, DATA_DIR
from ..logging_config import get_logger

logger = get_logger("profile_manager")


class ProfileManager:
    def __init__(self):
        self.profiles: Dict[str, Profile] = {}
        self.load_profiles()
        os.makedirs(DATA_DIR, exist_ok=True)

    def load_profiles(self):
        if os.path.exists(PROFILES_FILE):
            try:
                with open(PROFILES_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for name, p_data in data.items():
                        clean_data = {
                            "name": p_data.get("name"),
                            "proxy": p_data.get("proxy"),
                            "os_type": p_data.get("os_type", p_data.get("config", {}).get("os", "windows"))
                        }
                        self.profiles[name] = Profile(**clean_data)
                logger.info(f"Loaded {len(self.profiles)} profiles")
            except Exception as e:
                logger.error(f"Error loading profiles: {e}")

    def save_profiles(self):
        try:
            with open(PROFILES_FILE, 'w', encoding='utf-8') as f:
                json.dump({name: p.to_dict() for name, p in self.profiles.items()}, f, indent=4)
            logger.debug("Profiles saved")
        except Exception as e:
            logger.error(f"Error saving profiles: {e}")

    def add_profile(self, name: str, proxy: str, os_type: str) -> bool:
        if name in self.profiles:
            return False
        self.profiles[name] = Profile(name=name, proxy=proxy if proxy else None, os_type=os_type)
        self.save_profiles()
        os.makedirs(os.path.join(DATA_DIR, name), exist_ok=True)
        logger.info(f"Created profile: {name}")
        return True

    def update_profile(self, original_name: str, new_name: str, new_proxy: str, new_os: str) -> bool:
        if original_name not in self.profiles:
            return False
        
        if new_name != original_name and new_name in self.profiles:
            return False

        profile = self.profiles[original_name]
        profile.name = new_name
        profile.proxy = new_proxy if new_proxy else None
        profile.os_type = new_os
        
        if new_name != original_name:
            del self.profiles[original_name]
            self.profiles[new_name] = profile
            
            old_dir = os.path.join(DATA_DIR, original_name)
            new_dir = os.path.join(DATA_DIR, new_name)
            if os.path.exists(old_dir):
                os.rename(old_dir, new_dir)
        
        self.save_profiles()
        logger.info(f"Updated profile: {original_name} -> {new_name}")
        return True

    def delete_profile(self, name: str) -> bool:
        if name in self.profiles:
            del self.profiles[name]
            self.save_profiles()
            shutil.rmtree(os.path.join(DATA_DIR, name), ignore_errors=True)
            logger.info(f"Deleted profile: {name}")
            return True
        return False

    def list_profiles(self):
        return list(self.profiles.values())

    def export_profile(self, name: str, export_path: str, include_data: bool = True) -> Tuple[bool, str]:
        if name not in self.profiles:
            return False, "Profile not found"
        
        try:
            profile = self.profiles[name]
            profile_data_dir = os.path.join(DATA_DIR, name)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            zip_filename = f"{name}_{timestamp}.zip"
            zip_path = os.path.join(export_path, zip_filename)
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                profile_json = json.dumps(profile.to_dict(), indent=2)
                zipf.writestr("profile.json", profile_json)
                
                if include_data and os.path.exists(profile_data_dir):
                    for root, dirs, files in os.walk(profile_data_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.join("data", os.path.relpath(file_path, profile_data_dir))
                            zipf.write(file_path, arcname)
            
            logger.info(f"Exported profile {name} to {zip_path}")
            return True, zip_path
        except Exception as e:
            logger.error(f"Error exporting profile {name}: {e}")
            return False, str(e)

    def import_profile(self, zip_path: str, overwrite: bool = False) -> Tuple[bool, str]:
        try:
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                if "profile.json" not in zipf.namelist():
                    return False, "Invalid profile archive (missing profile.json)"
                
                profile_data = json.loads(zipf.read("profile.json"))
                name = profile_data.get("name")
                
                if not name:
                    return False, "Invalid profile data (missing name)"
                
                if name in self.profiles and not overwrite:
                    return False, f"Profile '{name}' already exists"
                
                self.profiles[name] = Profile(
                    name=name,
                    proxy=profile_data.get("proxy"),
                    os_type=profile_data.get("os_type", "windows")
                )
                
                data_files = [f for f in zipf.namelist() if f.startswith("data/")]
                if data_files:
                    profile_data_dir = os.path.join(DATA_DIR, name)
                    os.makedirs(profile_data_dir, exist_ok=True)
                    
                    for file in data_files:
                        target_path = os.path.join(profile_data_dir, os.path.relpath(file, "data"))
                        os.makedirs(os.path.dirname(target_path), exist_ok=True)
                        
                        if not file.endswith('/'):
                            with zipf.open(file) as src, open(target_path, 'wb') as dst:
                                dst.write(src.read())
                
                self.save_profiles()
                logger.info(f"Imported profile: {name}")
                return True, name
        except zipfile.BadZipFile:
            return False, "Invalid zip file"
        except Exception as e:
            logger.error(f"Error importing profile: {e}")
            return False, str(e)
