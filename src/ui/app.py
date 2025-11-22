import customtkinter as ctk
from tkinter import messagebox
from ..config import COLORS
from ..services.profile_manager import ProfileManager
from ..services.browser_launcher import BrowserLauncher
from .components.sidebar import Sidebar
from .components.profile_list import ProfileList
from .dialogs.add_profile_dialog import AddProfileDialog
from .dialogs.edit_profile_dialog import EditProfileDialog

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.pm = ProfileManager()
        
        self.title("Camoufox Manager")
        self.geometry("1000x700")
        self.configure(fg_color=COLORS["bg"])
        
        # Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Sidebar
        self.sidebar = Sidebar(self, self.pm, self.open_add_dialog)
        
        # Main Content Area
        self.main_area = ctk.CTkFrame(self, fg_color="transparent")
        self.main_area.grid(row=0, column=1, sticky="nsew", padx=30, pady=30)
        self.main_area.grid_rowconfigure(0, weight=1)
        self.main_area.grid_columnconfigure(0, weight=1)
        
        self.profile_list = ProfileList(self.main_area, self.pm, self.launch_profile, self.delete_profile, self.edit_profile, self.sidebar.update_stats)
        self.profile_list.grid(row=0, column=0, sticky="nsew")

    def log(self, message):
        self.sidebar.log(message)

    def open_add_dialog(self):
        AddProfileDialog(self, self.create_profile)

    def create_profile(self, name, proxy, os_type):
        if self.pm.add_profile(name, proxy, os_type):
            self.log(f"Created: {name}")
            self.profile_list.refresh_list()
        else:
            messagebox.showerror("Error", "Profile already exists!")

    def delete_profile(self, profile):
        if messagebox.askyesno("Confirm", f"Delete profile '{profile.name}'?"):
            self.pm.delete_profile(profile.name)
            self.log(f"Deleted: {profile.name}")
            self.profile_list.refresh_list()

    def edit_profile(self, profile):
        EditProfileDialog(self, profile, self.save_profile_edit)

    def save_profile_edit(self, original_name, new_name, new_proxy, new_os):
        if self.pm.update_profile(original_name, new_name, new_proxy, new_os):
            self.log(f"Updated: {original_name} -> {new_name}")
            self.profile_list.refresh_list()
        else:
            messagebox.showerror("Error", "Could not update profile (Name might exist)")

    def launch_profile(self, profile):
        # Check if already running
        if profile.name in BrowserLauncher.active_sessions:
            self.log(f"Stopping {profile.name}...")
            BrowserLauncher.stop_profile(profile.name)
            return

        self.log(f"Launching {profile.name}...")
        
        self.profile_list.update_card_state(profile.name, "loading")

        def on_start():
            pass # Already set to loading

        def on_ready():
            try:
                self.profile_list.update_card_state(profile.name, "running")
            except Exception:
                pass

        def on_stop():
            try:
                self.profile_list.update_card_state(profile.name, "idle")
            except Exception:
                pass

        BrowserLauncher.start_thread(profile, self.log, on_start, on_ready, on_stop)
