import customtkinter as ctk
from tkinter import messagebox
from ..config import COLORS
from ..strings import get_string
from ..services.profile_manager import ProfileManager
from ..services.browser_launcher import BrowserLauncher
from ..logging_config import setup_logging, get_logger
from .components.sidebar import Sidebar
from .components.profile_list import ProfileList
from .dialogs.add_profile_dialog import AddProfileDialog
from .dialogs.edit_profile_dialog import EditProfileDialog

logger = get_logger("app")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        setup_logging()
        logger.info("Application started")
        
        self.pm = ProfileManager()
        
        self.title("Camoufox Manager")
        self.geometry("1000x700")
        self.configure(fg_color=COLORS["bg"])
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.sidebar = Sidebar(self, self.pm, self.open_add_dialog, self.refresh_profiles)
        
        self.main_area = ctk.CTkFrame(self, fg_color="transparent")
        self.main_area.grid(row=0, column=1, sticky="nsew", padx=30, pady=30)
        self.main_area.grid_rowconfigure(0, weight=1)
        self.main_area.grid_columnconfigure(0, weight=1)
        
        self.profile_list = ProfileList(self.main_area, self.pm, self.launch_profile, 
                                        self.delete_profile, self.edit_profile, self.sidebar.update_stats)
        self.profile_list.grid(row=0, column=0, sticky="nsew")

    def refresh_profiles(self):
        self.profile_list.refresh_list()

    def log(self, message):
        self.sidebar.log(message)
        logger.info(message)

    def open_add_dialog(self):
        AddProfileDialog(self, self.create_profile)

    def create_profile(self, name, proxy, os_type):
        if self.pm.add_profile(name, proxy, os_type):
            self.log(get_string("created_profile", name=name))
            self.profile_list.refresh_list()
        else:
            messagebox.showerror(get_string("error"), get_string("profile_exists"))

    def delete_profile(self, profile):
        if messagebox.askyesno(get_string("confirm_delete"), 
                               get_string("confirm_delete_msg", name=profile.name)):
            self.pm.delete_profile(profile.name)
            self.log(get_string("deleted_profile", name=profile.name))
            self.profile_list.refresh_list()

    def edit_profile(self, profile):
        EditProfileDialog(self, profile, self.save_profile_edit)

    def save_profile_edit(self, original_name, new_name, new_proxy, new_os):
        if self.pm.update_profile(original_name, new_name, new_proxy, new_os):
            self.log(get_string("updated_profile", old=original_name, new=new_name))
            self.profile_list.refresh_list()
        else:
            messagebox.showerror(get_string("error"), get_string("update_failed"))

    def launch_profile(self, profile):
        if BrowserLauncher.is_running(profile.name):
            self.log(get_string("stopping_profile", name=profile.name))
            BrowserLauncher.stop_profile(profile.name)
            return

        self.log(get_string("launching_profile", name=profile.name))
        
        self.profile_list.update_card_state(profile.name, "loading")

        def on_start():
            pass

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
