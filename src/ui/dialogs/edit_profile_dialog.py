import customtkinter as ctk
import threading
from ...config import COLORS
from ...strings import get_string
from ...utils.validation import validate_profile_name, validate_proxy_format
from ...utils.proxy_checker import check_proxy_sync


class EditProfileDialog(ctk.CTkToplevel):
    def __init__(self, parent, profile, on_save):
        super().__init__(parent)
        self.profile = profile
        self.on_save = on_save
        
        self.title(get_string("edit_profile"))
        self.geometry("400x520")
        self.configure(fg_color=COLORS["bg"])
        self.attributes("-topmost", True)
        
        self.update_idletasks()
        width = 400
        height = 520
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
        
        self.transient(parent)
        self.grab_set()
        self.focus_force()
        
        self.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(self, text=get_string("edit_profile"), font=("Roboto", 20, "bold"), 
                     text_color=COLORS["text_main"]).grid(row=0, column=0, pady=(30, 20))
        
        self.name_entry = ctk.CTkEntry(self, placeholder_text=get_string("profile_name"), width=300, height=40,
                                       fg_color=COLORS["card_bg"], border_color=COLORS["sidebar"],
                                       text_color=COLORS["text_main"])
        self.name_entry.grid(row=1, column=0, padx=30, pady=10, sticky="ew")
        self.name_entry.insert(0, profile.name)
        
        self.name_error_lbl = ctk.CTkLabel(self, text="", font=("Roboto", 11), text_color=COLORS["error"])
        self.name_error_lbl.grid(row=2, column=0, padx=30, sticky="w")
        
        self.proxy_entry = ctk.CTkEntry(self, placeholder_text=get_string("proxy_placeholder"), width=300, height=40,
                                        fg_color=COLORS["card_bg"], border_color=COLORS["sidebar"],
                                        text_color=COLORS["text_main"])
        self.proxy_entry.grid(row=3, column=0, padx=30, pady=10, sticky="ew")
        if profile.proxy:
            self.proxy_entry.insert(0, profile.proxy)
        
        self.proxy_error_lbl = ctk.CTkLabel(self, text="", font=("Roboto", 11), text_color=COLORS["error"])
        self.proxy_error_lbl.grid(row=4, column=0, padx=30, sticky="w")
        
        self.check_proxy_btn = ctk.CTkButton(self, text=get_string("check_proxy"), height=35,
                                              fg_color=COLORS["sidebar"], hover_color=COLORS["card_hover"],
                                              font=("Roboto", 12), corner_radius=6, command=self.on_check_proxy)
        self.check_proxy_btn.grid(row=5, column=0, padx=30, pady=(0, 10), sticky="ew")
        
        ctk.CTkLabel(self, text=get_string("operating_system"), font=("Roboto", 12),
                     text_color=COLORS["text_sub"]).grid(row=6, column=0, padx=30, pady=(10, 5), sticky="w")
        
        self.os_var = ctk.StringVar(value=profile.os_type)
        self.os_menu = ctk.CTkOptionMenu(self, variable=self.os_var, values=["windows", "macos", "linux"],
                                         width=300, height=40, fg_color=COLORS["sidebar"], 
                                         button_color=COLORS["accent"])
        self.os_menu.grid(row=7, column=0, padx=30, pady=(0, 20), sticky="ew")
        
        ctk.CTkButton(self, text=get_string("save_changes"), width=300, height=45, 
                      fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
                      font=("Roboto Medium", 14), command=self.save).grid(row=8, column=0, padx=30, pady=10, sticky="ew")

    def on_check_proxy(self):
        proxy = self.proxy_entry.get().strip()
        if not proxy:
            self.proxy_error_lbl.configure(text="Enter a proxy to check", text_color=COLORS["warning"])
            return
        
        self.check_proxy_btn.configure(text=get_string("proxy_checking"), state="disabled")
        self.proxy_error_lbl.configure(text="")
        
        def check():
            success, message = check_proxy_sync(proxy)
            self.after(0, lambda: self.show_proxy_result(success, message))
        
        threading.Thread(target=check, daemon=True).start()
    
    def show_proxy_result(self, success, message):
        self.check_proxy_btn.configure(text=get_string("check_proxy"), state="normal")
        color = COLORS["success"] if success else COLORS["error"]
        self.proxy_error_lbl.configure(text=message, text_color=color)
        
    def save(self):
        name = self.name_entry.get().strip()
        proxy = self.proxy_entry.get().strip()
        os_type = self.os_var.get()
        
        self.name_error_lbl.configure(text="")
        self.proxy_error_lbl.configure(text="")
        
        valid_name, name_error = validate_profile_name(name)
        if not valid_name:
            self.name_error_lbl.configure(text=name_error)
            return
        
        valid_proxy, proxy_error = validate_proxy_format(proxy)
        if not valid_proxy:
            self.proxy_error_lbl.configure(text=proxy_error)
            return
        
        self.on_save(self.profile.name, name, proxy, os_type)
        self.destroy()
