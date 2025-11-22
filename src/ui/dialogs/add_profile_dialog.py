import customtkinter as ctk
from ...config import COLORS

class AddProfileDialog(ctk.CTkToplevel):
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.callback = callback
        self.title("Add Profile")
        self.geometry("400x480")
        self.resizable(False, False)
        self.configure(fg_color=COLORS["bg"])
        self.attributes("-topmost", True)
        
        # Center window
        self.update_idletasks()
        width = 400
        height = 480
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        self.focus_force()
        
        self.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(self, text="Create New Profile", font=("Roboto", 24, "bold"), text_color=COLORS["text_main"]).grid(row=0, column=0, pady=(30, 20))
        
        self.name_entry = ctk.CTkEntry(self, placeholder_text="Profile Name", height=45, 
                                       fg_color=COLORS["card_bg"], border_color=COLORS["sidebar"], text_color=COLORS["text_main"])
        self.name_entry.grid(row=1, column=0, padx=30, pady=10, sticky="ew")
        
        self.proxy_entry = ctk.CTkEntry(self, placeholder_text="Proxy (user:pass@ip:port) [Optional]", height=45,
                                        fg_color=COLORS["card_bg"], border_color=COLORS["sidebar"], text_color=COLORS["text_main"])
        self.proxy_entry.grid(row=2, column=0, padx=30, pady=10, sticky="ew")
        
        ctk.CTkLabel(self, text="Operating System", font=("Roboto", 12), text_color=COLORS["text_sub"]).grid(row=3, column=0, padx=30, pady=(10, 5), sticky="w")
        self.os_var = ctk.StringVar(value="windows")
        self.os_menu = ctk.CTkOptionMenu(self, variable=self.os_var, values=["windows", "macos", "linux"], 
                                         fg_color=COLORS["card_bg"], button_color=COLORS["accent"], button_hover_color=COLORS["accent_hover"],
                                         text_color=COLORS["text_main"], height=40)
        self.os_menu.grid(row=4, column=0, padx=30, pady=(0, 30), sticky="ew")
        
        self.save_btn = ctk.CTkButton(self, text="Create Profile", fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"], 
                                      height=45, font=("Roboto Medium", 14), corner_radius=8, command=self.on_save)
        self.save_btn.grid(row=5, column=0, padx=30, pady=10, sticky="ew")

    def on_save(self):
        name = self.name_entry.get().strip()
        proxy = self.proxy_entry.get().strip()
        os_type = self.os_var.get()
        
        if not name:
            return
            
        self.callback(name, proxy, os_type)
        self.destroy()
