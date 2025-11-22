import customtkinter as ctk
from ...config import COLORS

class Sidebar(ctk.CTkFrame):
    def __init__(self, master, profile_manager, on_add_profile):
        super().__init__(master, width=240, corner_radius=0, fg_color=COLORS["sidebar"])
        self.pm = profile_manager
        self.on_add_profile = on_add_profile
        
        self.expanded_log_window = None
        
        self.grid(row=0, column=0, sticky="nsew")
        self.grid_rowconfigure(4, weight=1)
        
        self._create_widgets()
        
    def _create_widgets(self):
        # Logo Area
        ctk.CTkLabel(self, text="Camou Manager", font=("Roboto Black", 32), text_color=COLORS["accent"]).grid(row=0, column=0, padx=25, pady=(40, 5), sticky="w")
        ctk.CTkLabel(self, text="PREMIUM EDITION", font=("Roboto Medium", 10), text_color=COLORS["text_sub"]).grid(row=1, column=0, padx=25, pady=(0, 40), sticky="w")
        
        # Main Action
        self.add_btn = ctk.CTkButton(self, text="+ NEW PROFILE", fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
                                     height=50, font=("Roboto Medium", 14), corner_radius=8, command=self.on_add_profile)
        self.add_btn.grid(row=2, column=0, padx=25, pady=10, sticky="ew")
        
        # Stats or Info
        self.stats_lbl = ctk.CTkLabel(self, text=f"Total Profiles: {len(self.pm.profiles)}", font=("Roboto", 12), text_color=COLORS["text_sub"])
        self.stats_lbl.grid(row=3, column=0, padx=25, pady=10, sticky="w")
        
        # Log Area
        self.log_header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.log_header_frame.grid(row=5, column=0, padx=25, pady=(10, 5), sticky="ew")
        self.log_header_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.log_header_frame, text="ACTIVITY LOG", font=("Roboto Medium", 11), text_color=COLORS["text_sub"]).grid(row=0, column=0, sticky="w")
        
        self.toggle_btn = ctk.CTkButton(self.log_header_frame, text="Expand", width=40, height=20, 
                                        font=("Roboto", 10), fg_color="transparent", text_color=COLORS["accent"], 
                                        hover_color=COLORS["sidebar"], command=self.toggle_log)
        self.toggle_btn.grid(row=0, column=1, sticky="e")

        self.log_box = ctk.CTkTextbox(self, height=150, font=("Consolas", 11), fg_color="#151515", text_color="#888888", corner_radius=8)
        self.log_box.grid(row=6, column=0, padx=20, pady=(0, 25), sticky="ew")
        self.log_box.configure(state="disabled")

    def update_stats(self):
        self.stats_lbl.configure(text=f"Total Profiles: {len(self.pm.profiles)}")

    def log(self, message):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", f"> {message}\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")
        
        if self.expanded_log_window and self.expanded_log_window.winfo_exists():
            try:
                self.expanded_log_box.configure(state="normal")
                self.expanded_log_box.insert("end", f"> {message}\n")
                self.expanded_log_box.see("end")
                self.expanded_log_box.configure(state="disabled")
            except Exception:
                pass

    def toggle_log(self):
        if self.expanded_log_window is None or not self.expanded_log_window.winfo_exists():
            self.open_expanded_log()
        else:
            self.close_expanded_log()

    def open_expanded_log(self):
        self.expanded_log_window = ctk.CTkToplevel(self)
        self.expanded_log_window.title("Activity Log - Full Screen")
        self.expanded_log_window.geometry("800x600")
        self.expanded_log_window.configure(fg_color=COLORS["bg"])
        self.expanded_log_window.attributes("-topmost", True)
        
        # Center window
        self.expanded_log_window.update_idletasks()
        width = 800
        height = 600
        x = (self.expanded_log_window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.expanded_log_window.winfo_screenheight() // 2) - (height // 2)
        self.expanded_log_window.geometry(f"{width}x{height}+{x}+{y}")
        self.expanded_log_window.focus_force()
        
        # Handle window close via 'X'
        self.expanded_log_window.protocol("WM_DELETE_WINDOW", self.close_expanded_log)
        
        # Content
        self.expanded_log_box = ctk.CTkTextbox(self.expanded_log_window, font=("Consolas", 12), fg_color="#151515", text_color="#888888")
        self.expanded_log_box.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Copy existing logs
        current_logs = self.log_box.get("1.0", "end")
        self.expanded_log_box.insert("1.0", current_logs)
        self.expanded_log_box.configure(state="disabled")
        self.expanded_log_box.see("end")
        
        self.toggle_btn.configure(text="Minimize")

    def close_expanded_log(self):
        if self.expanded_log_window and self.expanded_log_window.winfo_exists():
            self.expanded_log_window.destroy()
        self.expanded_log_window = None
        self.toggle_btn.configure(text="Expand")
