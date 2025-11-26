import customtkinter as ctk
from ...config import COLORS
from ...strings import get_string
from ...services.browser_launcher import BrowserLauncher
from .profile_card import ProfileCard


class ProfileList(ctk.CTkFrame):
    def __init__(self, master, profile_manager, on_launch, on_delete, on_edit, on_update_stats):
        super().__init__(master, fg_color="transparent")
        self.pm = profile_manager
        self.on_launch = on_launch
        self.on_delete = on_delete
        self.on_edit = on_edit
        self.on_update_stats = on_update_stats
        
        self.current_page = 1
        self.items_per_page = 10
        
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self._create_widgets()
        self.refresh_list()
        
    def _create_widgets(self):
        ctk.CTkLabel(self, text=get_string("your_profiles"), font=("Roboto", 28, "bold"), 
                     text_color=COLORS["text_main"]).grid(row=0, column=0, sticky="w", pady=(0, 20))
        
        self.scrollable_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scrollable_frame.grid(row=1, column=0, sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        
        self.pagination_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.pagination_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        self.pagination_frame.grid_columnconfigure(1, weight=1)
        
        self.prev_btn = ctk.CTkButton(self.pagination_frame, text=get_string("previous"), width=100, 
                                      command=self.prev_page)
        self.prev_btn.grid(row=0, column=0, sticky="w")
        
        self.page_lbl = ctk.CTkLabel(self.pagination_frame, text=get_string("page_of", current=1, total=1), 
                                     font=("Roboto", 12))
        self.page_lbl.grid(row=0, column=1)
        
        self.next_btn = ctk.CTkButton(self.pagination_frame, text=get_string("next"), width=100, 
                                      command=self.next_page)
        self.next_btn.grid(row=0, column=2, sticky="e")

    def refresh_list(self):
        if self.on_update_stats:
            self.on_update_stats()
            
        all_profiles = self.pm.list_profiles()
        
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        total_pages = (len(all_profiles) + self.items_per_page - 1) // self.items_per_page
        if total_pages == 0:
            total_pages = 1
        if self.current_page > total_pages:
            self.current_page = total_pages
        
        start_idx = (self.current_page - 1) * self.items_per_page
        end_idx = start_idx + self.items_per_page
        current_profiles = all_profiles[start_idx:end_idx]
        
        if not current_profiles:
            empty_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
            empty_frame.pack(pady=100)
            ctk.CTkLabel(empty_frame, text=get_string("no_profiles_yet"), font=("Roboto", 20, "bold"), 
                         text_color=COLORS["text_sub"]).pack()
            ctk.CTkLabel(empty_frame, text=get_string("create_profile_hint"), font=("Roboto", 14), 
                         text_color=COLORS["text_sub"]).pack(pady=5)
        else:
            for p in current_profiles:
                card = ProfileCard(self.scrollable_frame, p, self.on_launch, self.on_delete, self.on_edit)
                card.pack(fill="x", pady=8)
                
                if BrowserLauncher.is_running(p.name):
                    card.set_state("running")
                
        self.update_pagination_controls(len(all_profiles))

    def update_pagination_controls(self, total_items=0):
        total_pages = (total_items + self.items_per_page - 1) // self.items_per_page
        if total_items == 0:
            total_pages = 1
        
        self.page_lbl.configure(text=get_string("page_of", current=self.current_page, total=total_pages))
        
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
    
    def update_card_state(self, profile_name, state):
        for widget in self.scrollable_frame.winfo_children():
            if isinstance(widget, ProfileCard) and widget.profile.name == profile_name:
                widget.set_state(state)
                break
