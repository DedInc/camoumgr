import os

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


COLORS = {
    "bg": "#0B0B14",
    "sidebar": "#0F0F1A",
    "card_bg": "#161628",
    "card_hover": "#1E1E38",
    "card_border": "#252548",
    "accent": "#7C3AED",
    "accent_hover": "#6D28D9",
    "text_main": "#ECEDF5",
    "text_sub": "#A3A3C2",
    "text_dim": "#70708C",
    "success": "#10B981",
    "error": "#EF4444",
    "delete_hover": "#DC2626",
    "warning": "#F59E0B",
    "input_bg": "#111125",
    "border": "#1E1E3A",
    "scrollbar_bg": "#0B0B14",
    "scrollbar_grab": "#252548",
    "log_bg": "#0D0D1A",
}
