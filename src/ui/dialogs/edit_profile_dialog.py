import customtkinter as ctk
from ...config import COLORS

class EditProfileDialog(ctk.CTkToplevel):
    def __init__(self, parent, profile, on_save):
        super().__init__(parent)
        self.profile = profile
        self.on_save = on_save
        
        self.title("Edit Profile")
        self.geometry("400x450")
        self.configure(fg_color=COLORS["bg"])
        self.attributes("-topmost", True)
        
        # Center window
        self.update_idletasks()
        width = 400
        height = 450
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
        
        self.transient(parent)
        self.grab_set()
        self.focus_force()
        
        # UI Elements
        ctk.CTkLabel(self, text="Edit Profile", font=("Roboto", 20, "bold"), text_color=COLORS["text_main"]).pack(pady=20)
        
        self.name_entry = ctk.CTkEntry(self, placeholder_text="Profile Name", width=300, height=40)
        self.name_entry.pack(pady=10)
        self.name_entry.insert(0, profile.name)
        
        self.proxy_entry = ctk.CTkEntry(self, placeholder_text="Proxy (user:pass@ip:port)", width=300, height=40)
        self.proxy_entry.pack(pady=10)
        if profile.proxy:
            self.proxy_entry.insert(0, profile.proxy)
        
        self.os_var = ctk.StringVar(value=profile.os_type)
        self.os_menu = ctk.CTkOptionMenu(self, variable=self.os_var, values=["windows", "macos", "linux"],
                                         width=300, height=40, fg_color=COLORS["sidebar"], button_color=COLORS["accent"])
        self.os_menu.pack(pady=10)
        
        ctk.CTkButton(self, text="Save Changes", width=300, height=45, 
                      fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
                      font=("Roboto Medium", 14), command=self.save).pack(pady=20)
        
    def save(self):
        name = self.name_entry.get().strip()
        proxy = self.proxy_entry.get().strip()
        os_type = self.os_var.get()
        
        if not name:
            return
        
        self.on_save(self.profile.name, name, proxy, os_type)
        self.destroy()
