import customtkinter as ctk
from tkinter import filedialog, messagebox
from ...config import COLORS
from ...strings import get_string


class Sidebar(ctk.CTkFrame):
    def __init__(self, master, profile_manager, on_add_profile, on_refresh=None):
        super().__init__(master, width=240, corner_radius=0, fg_color=COLORS["sidebar"])
        self.pm = profile_manager
        self.on_add_profile = on_add_profile
        self.on_refresh = on_refresh
        
        self.expanded_log_window = None
        
        self.grid(row=0, column=0, sticky="nsew")
        self.grid_rowconfigure(6, weight=1)
        
        self._create_widgets()
        
    def _create_widgets(self):
        ctk.CTkLabel(self, text=get_string("app_name"), font=("Roboto Black", 32), 
                     text_color=COLORS["accent"]).grid(row=0, column=0, padx=25, pady=(40, 5), sticky="w")
        ctk.CTkLabel(self, text=get_string("app_subtitle"), font=("Roboto Medium", 10), 
                     text_color=COLORS["text_sub"]).grid(row=1, column=0, padx=25, pady=(0, 40), sticky="w")
        
        self.add_btn = ctk.CTkButton(self, text=get_string("new_profile"), fg_color=COLORS["accent"], 
                                     hover_color=COLORS["accent_hover"], height=50, font=("Roboto Medium", 14), 
                                     corner_radius=8, command=self.on_add_profile)
        self.add_btn.grid(row=2, column=0, padx=25, pady=10, sticky="ew")
        
        import_export_frame = ctk.CTkFrame(self, fg_color="transparent")
        import_export_frame.grid(row=3, column=0, padx=25, pady=5, sticky="ew")
        import_export_frame.grid_columnconfigure((0, 1), weight=1)
        
        self.import_btn = ctk.CTkButton(import_export_frame, text=get_string("import_profile"), 
                                        fg_color=COLORS["card_bg"], hover_color=COLORS["card_hover"],
                                        height=35, font=("Roboto", 11), corner_radius=6,
                                        command=self.on_import)
        self.import_btn.grid(row=0, column=0, padx=(0, 5), sticky="ew")
        
        self.export_btn = ctk.CTkButton(import_export_frame, text=get_string("export_profile"),
                                        fg_color=COLORS["card_bg"], hover_color=COLORS["card_hover"],
                                        height=35, font=("Roboto", 11), corner_radius=6,
                                        command=self.on_export)
        self.export_btn.grid(row=0, column=1, padx=(5, 0), sticky="ew")
        
        self.stats_lbl = ctk.CTkLabel(self, text=get_string("total_profiles", count=len(self.pm.profiles)), 
                                      font=("Roboto", 12), text_color=COLORS["text_sub"])
        self.stats_lbl.grid(row=4, column=0, padx=25, pady=10, sticky="w")
        
        self.log_header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.log_header_frame.grid(row=7, column=0, padx=25, pady=(10, 5), sticky="ew")
        self.log_header_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.log_header_frame, text=get_string("activity_log"), font=("Roboto Medium", 11), 
                     text_color=COLORS["text_sub"]).grid(row=0, column=0, sticky="w")
        
        self.toggle_btn = ctk.CTkButton(self.log_header_frame, text=get_string("expand"), width=40, height=20, 
                                        font=("Roboto", 10), fg_color="transparent", text_color=COLORS["accent"], 
                                        hover_color=COLORS["sidebar"], command=self.toggle_log)
        self.toggle_btn.grid(row=0, column=1, sticky="e")

        self.log_box = ctk.CTkTextbox(self, height=150, font=("Consolas", 11), fg_color="#151515", 
                                      text_color="#888888", corner_radius=8)
        self.log_box.grid(row=8, column=0, padx=20, pady=(0, 25), sticky="ew")
        self.log_box.configure(state="disabled")

    def on_import(self):
        file_path = filedialog.askopenfilename(
            title="Import Profile",
            filetypes=[("ZIP files", "*.zip"), ("All files", "*.*")]
        )
        if file_path:
            success, result = self.pm.import_profile(file_path)
            if success:
                self.log(get_string("import_success") + f": {result}")
                self.update_stats()
                if self.on_refresh:
                    self.on_refresh()
            else:
                messagebox.showerror(get_string("error"), get_string("import_error", error=result))
    
    def on_export(self):
        profiles = self.pm.list_profiles()
        if not profiles:
            messagebox.showinfo("Info", "No profiles to export")
            return
        
        export_window = ctk.CTkToplevel(self)
        export_window.title("Export Profile")
        export_window.geometry("300x400")
        export_window.configure(fg_color=COLORS["bg"])
        export_window.attributes("-topmost", True)
        
        export_window.update_idletasks()
        x = (export_window.winfo_screenwidth() // 2) - 150
        y = (export_window.winfo_screenheight() // 2) - 200
        export_window.geometry(f"300x400+{x}+{y}")
        
        ctk.CTkLabel(export_window, text="Select Profile to Export", font=("Roboto", 16, "bold"),
                     text_color=COLORS["text_main"]).pack(pady=20)
        
        selected_var = ctk.StringVar(value=profiles[0].name if profiles else "")
        
        scroll_frame = ctk.CTkScrollableFrame(export_window, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        for profile in profiles:
            ctk.CTkRadioButton(scroll_frame, text=profile.name, variable=selected_var, 
                              value=profile.name, fg_color=COLORS["accent"]).pack(anchor="w", pady=5)
        
        include_data_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(export_window, text="Include browser data", variable=include_data_var,
                       fg_color=COLORS["accent"]).pack(pady=10)
        
        def do_export():
            name = selected_var.get()
            if not name:
                return
            
            export_dir = filedialog.askdirectory(title="Select Export Directory")
            if export_dir:
                success, result = self.pm.export_profile(name, export_dir, include_data_var.get())
                if success:
                    self.log(get_string("export_success") + f": {result}")
                    messagebox.showinfo("Success", f"Profile exported to:\n{result}")
                else:
                    messagebox.showerror(get_string("error"), get_string("export_error", error=result))
                export_window.destroy()
        
        ctk.CTkButton(export_window, text="Export", fg_color=COLORS["accent"],
                     hover_color=COLORS["accent_hover"], command=do_export).pack(pady=20)

    def update_stats(self):
        self.stats_lbl.configure(text=get_string("total_profiles", count=len(self.pm.profiles)))

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
        self.expanded_log_window.title(get_string("activity_log_fullscreen"))
        self.expanded_log_window.geometry("800x600")
        self.expanded_log_window.configure(fg_color=COLORS["bg"])
        self.expanded_log_window.attributes("-topmost", True)
        
        self.expanded_log_window.update_idletasks()
        width = 800
        height = 600
        x = (self.expanded_log_window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.expanded_log_window.winfo_screenheight() // 2) - (height // 2)
        self.expanded_log_window.geometry(f"{width}x{height}+{x}+{y}")
        self.expanded_log_window.focus_force()
        
        self.expanded_log_window.protocol("WM_DELETE_WINDOW", self.close_expanded_log)
        
        self.expanded_log_box = ctk.CTkTextbox(self.expanded_log_window, font=("Consolas", 12), 
                                               fg_color="#151515", text_color="#888888")
        self.expanded_log_box.pack(fill="both", expand=True, padx=20, pady=20)
        
        current_logs = self.log_box.get("1.0", "end")
        self.expanded_log_box.insert("1.0", current_logs)
        self.expanded_log_box.configure(state="disabled")
        self.expanded_log_box.see("end")
        
        self.toggle_btn.configure(text=get_string("minimize"))

    def close_expanded_log(self):
        if self.expanded_log_window and self.expanded_log_window.winfo_exists():
            self.expanded_log_window.destroy()
        self.expanded_log_window = None
        self.toggle_btn.configure(text=get_string("expand"))
