import customtkinter as ctk
from tkinter import messagebox
from ..config import COLORS
from ..services.profile_manager import ProfileManager
from ..services.browser_launcher import BrowserLauncher
from .components.profile_card import ProfileCard
from .dialogs.add_profile_dialog import AddProfileDialog

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.pm = ProfileManager()
        
        # Pagination State
        self.current_page = 1
        self.items_per_page = 10

        
        self.title("Camoufox Manager")
        self.geometry("1000x700")
        self.configure(fg_color=COLORS["bg"])
        
        # Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color=COLORS["sidebar"])
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(4, weight=1)
        
        # Logo Area
        ctk.CTkLabel(self.sidebar, text="CMNGR", font=("Roboto Black", 32), text_color=COLORS["accent"]).grid(row=0, column=0, padx=25, pady=(40, 5), sticky="w")
        ctk.CTkLabel(self.sidebar, text="PREMIUM EDITION", font=("Roboto Medium", 10), text_color=COLORS["text_sub"]).grid(row=1, column=0, padx=25, pady=(0, 40), sticky="w")
        
        # Main Action
        self.add_btn = ctk.CTkButton(self.sidebar, text="+ NEW PROFILE", fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
                                     height=50, font=("Roboto Medium", 14), corner_radius=8, command=self.open_add_dialog)
        self.add_btn.grid(row=2, column=0, padx=25, pady=10, sticky="ew")
        
        # Stats or Info
        self.stats_lbl = ctk.CTkLabel(self.sidebar, text=f"Total Profiles: {len(self.pm.profiles)}", font=("Roboto", 12), text_color=COLORS["text_sub"])
        self.stats_lbl.grid(row=3, column=0, padx=25, pady=10, sticky="w")
        
        # Log Area
        self.log_header_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.log_header_frame.grid(row=5, column=0, padx=25, pady=(10, 5), sticky="ew")
        self.log_header_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.log_header_frame, text="ACTIVITY LOG", font=("Roboto Medium", 11), text_color=COLORS["text_sub"]).grid(row=0, column=0, sticky="w")
        
        self.expanded_log_window = None
        self.toggle_btn = ctk.CTkButton(self.log_header_frame, text="Expand", width=40, height=20, 
                                        font=("Roboto", 10), fg_color="transparent", text_color=COLORS["accent"], 
                                        hover_color=COLORS["sidebar"], command=self.toggle_log)
        self.toggle_btn.grid(row=0, column=1, sticky="e")

        self.log_box = ctk.CTkTextbox(self.sidebar, height=150, font=("Consolas", 11), fg_color="#151515", text_color="#888888", corner_radius=8)
        self.log_box.grid(row=6, column=0, padx=20, pady=(0, 25), sticky="ew")
        self.log_box.configure(state="disabled")
        
        # Main Content Area
        self.main_area = ctk.CTkFrame(self, fg_color="transparent")
        self.main_area.grid(row=0, column=1, sticky="nsew", padx=30, pady=30)
        self.main_area.grid_rowconfigure(1, weight=1)
        self.main_area.grid_columnconfigure(0, weight=1)
        
        # Header
        ctk.CTkLabel(self.main_area, text="Your Profiles", font=("Roboto", 28, "bold"), text_color=COLORS["text_main"]).grid(row=0, column=0, sticky="w", pady=(0, 20))
        
        # Scrollable List
        self.scrollable_frame = ctk.CTkScrollableFrame(self.main_area, fg_color="transparent")
        self.scrollable_frame.grid(row=1, column=0, sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        
        # Pagination Controls
        self.pagination_frame = ctk.CTkFrame(self.main_area, fg_color="transparent")
        self.pagination_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        self.pagination_frame.grid_columnconfigure(1, weight=1)
        
        self.prev_btn = ctk.CTkButton(self.pagination_frame, text="Previous", width=100, command=self.prev_page)
        self.prev_btn.grid(row=0, column=0, sticky="w")
        
        self.page_lbl = ctk.CTkLabel(self.pagination_frame, text="Page 1 of 1", font=("Roboto", 12))
        self.page_lbl.grid(row=0, column=1)
        
        self.next_btn = ctk.CTkButton(self.pagination_frame, text="Next", width=100, command=self.next_page)
        self.next_btn.grid(row=0, column=2, sticky="e")
        
        self.refresh_list()


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

    def refresh_list(self):
        # Update stats
        all_profiles = self.pm.list_profiles()
        self.stats_lbl.configure(text=f"Total Profiles: {len(all_profiles)}")
        
        # Clear existing
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        # Pagination Logic
        total_pages = (len(all_profiles) + self.items_per_page - 1) // self.items_per_page
        if total_pages == 0: total_pages = 1
        if self.current_page > total_pages: self.current_page = total_pages
        
        start_idx = (self.current_page - 1) * self.items_per_page
        end_idx = start_idx + self.items_per_page
        current_profiles = all_profiles[start_idx:end_idx]
        
        if not current_profiles:
            empty_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
            empty_frame.pack(pady=100)
            ctk.CTkLabel(empty_frame, text="No profiles yet", font=("Roboto", 20, "bold"), text_color=COLORS["text_sub"]).pack()
            ctk.CTkLabel(empty_frame, text="Create a new profile to get started", font=("Roboto", 14), text_color=COLORS["text_sub"]).pack(pady=5)
        else:
            for p in current_profiles:
                card = ProfileCard(self.scrollable_frame, p, self.launch_profile, self.delete_profile)
                card.pack(fill="x", pady=8)
                
        self.update_pagination_controls(len(all_profiles))

    def update_pagination_controls(self, total_items=0):
        total_pages = (total_items + self.items_per_page - 1) // self.items_per_page
        if total_items == 0: total_pages = 1
        
        self.page_lbl.configure(text=f"Page {self.current_page} of {total_pages}")
        
        if self.current_page <= 1:
            self.prev_btn.configure(state="disabled")
        else:
            self.prev_btn.configure(state="normal")
            
        if self.current_page >= total_pages:
            self.next_btn.configure(state="disabled")
        else:
            self.next_btn.configure(state="normal")

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.refresh_list()

    def next_page(self):
        self.current_page += 1
        self.refresh_list()


    def open_add_dialog(self):
        AddProfileDialog(self, self.create_profile)

    def create_profile(self, name, proxy, os_type):
        if self.pm.add_profile(name, proxy, os_type):
            self.log(f"Created: {name}")
            self.refresh_list()
        else:
            messagebox.showerror("Error", "Profile already exists!")

    def delete_profile(self, profile):
        if messagebox.askyesno("Confirm", f"Delete profile '{profile.name}'?"):
            self.pm.delete_profile(profile.name)
            self.log(f"Deleted: {profile.name}")
            self.refresh_list()

    def launch_profile(self, profile):
        self.log(f"Launching {profile.name}...")
        BrowserLauncher.start_thread(profile, self.log)

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
