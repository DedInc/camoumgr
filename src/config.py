import customtkinter as ctk

# --- CONFIG ---
PROFILES_FILE = "profiles.json"
DATA_DIR = "camoufox_data"

# --- THEME CONFIG ---
def setup_theme():
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("dark-blue")

# Premium Color Palette
COLORS = {
    "bg": "#121212",            # Very dark background
    "sidebar": "#1E1E1E",       # Slightly lighter sidebar
    "card_bg": "#252525",       # Card background
    "card_hover": "#2F2F2F",    # Card hover state
    "accent": "#7C4DFF",        # Deep Purple Accent
    "accent_hover": "#651FFF",  # Brighter Purple Hover
    "text_main": "#FFFFFF",     # High emphasis text
    "text_sub": "#B0B0B0",      # Medium emphasis text
    "success": "#00E676",       # Green for active/proxy
    "error": "#FF5252",         # Red for no proxy/delete
    "delete_hover": "#FF1744"   # Bright red for delete hover
}
