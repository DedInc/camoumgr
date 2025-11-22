import json
import os
import shutil
from typing import Dict
from ..models.profile import Profile
from ..config import PROFILES_FILE, DATA_DIR

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
            except Exception:
                pass

    def save_profiles(self):
        with open(PROFILES_FILE, 'w', encoding='utf-8') as f:
            json.dump({name: p.to_dict() for name, p in self.profiles.items()}, f, indent=4)

    def add_profile(self, name: str, proxy: str, os_type: str):
        if name in self.profiles:
            return False
        self.profiles[name] = Profile(name=name, proxy=proxy if proxy else None, os_type=os_type)
        self.save_profiles()
        os.makedirs(os.path.join(DATA_DIR, name), exist_ok=True)
        return True

    def update_profile(self, original_name: str, new_name: str, new_proxy: str, new_os: str):
        if original_name not in self.profiles:
            return False
        
        # If renaming, check if new name exists
        if new_name != original_name and new_name in self.profiles:
            return False

        # Update data
        profile = self.profiles[original_name]
        profile.name = new_name
        profile.proxy = new_proxy if new_proxy else None
        profile.os_type = new_os
        
        # Handle rename in dictionary and filesystem
        if new_name != original_name:
            del self.profiles[original_name]
            self.profiles[new_name] = profile
            
            old_dir = os.path.join(DATA_DIR, original_name)
            new_dir = os.path.join(DATA_DIR, new_name)
            if os.path.exists(old_dir):
                os.rename(old_dir, new_dir)
        
        self.save_profiles()
        return True

    def delete_profile(self, name: str):
        if name in self.profiles:
            del self.profiles[name]
            self.save_profiles()
            shutil.rmtree(os.path.join(DATA_DIR, name), ignore_errors=True)
            return True
        return False

    def list_profiles(self):
        return list(self.profiles.values())
