import customtkinter as ctk
from ...config import COLORS

class OSBadge(ctk.CTkFrame):
    def __init__(self, parent, os_type):
        color_map = {
            "windows": "#0078D7",  # Windows Blue
            "macos": "#999999",    # Apple Grey
            "linux": "#E95420"     # Ubuntu Orange
        }
        text_map = {
            "windows": "WIN",
            "macos": "MAC",
            "linux": "LIN"
        }
        
        color = color_map.get(os_type, COLORS["accent"])
        text = text_map.get(os_type, "OS")
        
        super().__init__(parent, fg_color=color, corner_radius=6, width=50, height=24)
        
        self.label = ctk.CTkLabel(self, text=text, font=("Roboto", 11, "bold"), text_color="white")
        self.label.place(relx=0.5, rely=0.5, anchor="center")
