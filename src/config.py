import os
import customtkinter as ctk

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

PROFILES_FILE = os.getenv("CAMOUMGR_PROFILES_FILE", "profiles.json")
DATA_DIR = os.getenv("CAMOUMGR_DATA_DIR", "camoufox_data")
LOG_DIR = os.getenv("CAMOUMGR_LOG_DIR", "logs")
LOG_LEVEL = os.getenv("CAMOUMGR_LOG_LEVEL", "INFO")
PROXY_CHECK_TIMEOUT = int(os.getenv("CAMOUMGR_PROXY_TIMEOUT", "10"))


def setup_theme():
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("dark-blue")


COLORS = {
    "bg": "#121212",
    "sidebar": "#1E1E1E",
    "card_bg": "#252525",
    "card_hover": "#2F2F2F",
    "accent": "#7C4DFF",
    "accent_hover": "#651FFF",
    "text_main": "#FFFFFF",
    "text_sub": "#B0B0B0",
    "success": "#00E676",
    "error": "#FF5252",
    "delete_hover": "#FF1744",
    "warning": "#FFD740",
}
