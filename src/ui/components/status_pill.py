import customtkinter as ctk

class StatusPill(ctk.CTkFrame):
    def __init__(self, parent, text, color):
        super().__init__(parent, fg_color=color, corner_radius=10, height=20)
        self.label = ctk.CTkLabel(self, text=text, font=("Roboto Medium", 10), text_color="black")
        self.label.grid(row=0, column=0, padx=8, pady=2)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
