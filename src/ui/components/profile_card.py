import customtkinter as ctk
from ...config import COLORS
from ...models.profile import Profile
from .os_badge import OSBadge
from .status_pill import StatusPill

class ProfileCard(ctk.CTkFrame):
    def __init__(self, parent, profile: Profile, launch_cb, delete_cb, edit_cb):
        super().__init__(parent, fg_color=COLORS["card_bg"], corner_radius=16, border_width=0)
        self.profile = profile
        self.launch_cb = launch_cb
        self.delete_cb = delete_cb
        self.edit_cb = edit_cb
        
        # Hover effects
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        
        self.grid_columnconfigure(1, weight=1)
        
        # OS Badge
        self.os_badge = OSBadge(self, profile.os_type)
        self.os_badge.grid(row=0, column=0, rowspan=2, padx=20, pady=20)
        
        # Info
        self.name_lbl = ctk.CTkLabel(self, text=profile.name, font=("Roboto", 18, "bold"), text_color=COLORS["text_main"])
        self.name_lbl.grid(row=0, column=1, sticky="sw", padx=(0, 10), pady=(15, 2))
        self.name_lbl.bind("<Enter>", self.on_enter)
        self.name_lbl.bind("<Leave>", self.on_leave)
        
        # Status Pill
        pill_color = COLORS["success"] if profile.proxy else COLORS["text_sub"]
        pill_text = "PROXY ACTIVE" if profile.proxy else "DIRECT CONNECTION"
        self.status_pill = StatusPill(self, pill_text, pill_color)
        self.status_pill.grid(row=1, column=1, sticky="nw", padx=(0, 10), pady=(2, 15))
        
        # Buttons
        self.launch_btn = ctk.CTkButton(self, text="LAUNCH", width=90, height=36, 
                                        fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
                                        font=("Roboto Medium", 12), corner_radius=18,
                                        command=lambda: self.launch_cb(self.profile))
        self.launch_btn.grid(row=0, column=2, rowspan=2, padx=(0, 5))

        self.edit_btn = ctk.CTkButton(self, text="✎", width=36, height=36,
                                      fg_color="transparent", hover_color=COLORS["sidebar"],
                                      text_color=COLORS["text_main"], font=("Arial", 16), corner_radius=18,
                                      command=lambda: self.edit_cb(self.profile))
        self.edit_btn.grid(row=0, column=3, rowspan=2, padx=(0, 5))
        
        self.delete_btn = ctk.CTkButton(self, text="×", width=36, height=36, 
                                        fg_color="transparent", hover_color=COLORS["delete_hover"],
                                        text_color=COLORS["text_sub"], font=("Arial", 20), corner_radius=18,
                                        command=lambda: self.delete_cb(self.profile))
        self.delete_btn.grid(row=0, column=4, rowspan=2, padx=(0, 20))

    def set_state(self, state):
        if state == "loading":
            self.launch_btn.configure(text="LOADING...", state="disabled", fg_color=COLORS["text_sub"])
        elif state == "running":
            self.launch_btn.configure(text="CLOSE", state="normal", fg_color=COLORS["error"], hover_color=COLORS["delete_hover"])
        else: # idle
            self.launch_btn.configure(text="LAUNCH", state="normal", fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"])

    def on_enter(self, event):
        self.configure(fg_color=COLORS["card_hover"])

    def on_leave(self, event):
        self.configure(fg_color=COLORS["card_bg"])
