import customtkinter as ctk
from tkinter import messagebox


class SettingsViewFrame(ctk.CTkFrame):
    """Settings Workspace for managing App Theme, Font Scaling, Help, and About information."""

    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # =============================================================
        # LEFT PANEL: APPEARANCE, THEME & FONT SIZE SETTINGS
        # =============================================================
        self.appearance_frame = ctk.CTkFrame(self, corner_radius=10, fg_color=("white", "#1E1E1E"))
        self.appearance_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        ctk.CTkLabel(
            self.appearance_frame, 
            text="🎨 Appearance & Display", 
            font=("Poppins", 16, "bold"), 
            text_color=("gray10", "#FFFFFF")
        ).pack(anchor="w", padx=20, pady=(15, 15))

        # 1. Theme Appearance Mode (Dark / Light / System)
        ctk.CTkLabel(
            self.appearance_frame, 
            text="Interface Theme Mode:", 
            font=("Poppins", 12, "bold"), 
            text_color=("gray10", "#FFFFFF")
        ).pack(anchor="w", padx=20, pady=(5, 2))
        
        self.combo_theme = ctk.CTkOptionMenu(
            self.appearance_frame,
            values=["Dark", "Light", "System"],
            command=self.change_appearance_mode,
            height=35,
            fg_color=("gray85", "#2B2B3D"),
            button_color="#3B82F6",
            text_color=("gray10", "#FFFFFF")
        )
        self.combo_theme.set("Dark")
        self.combo_theme.pack(fill="x", padx=20, pady=(0, 15))

        # 2. Font Size / UI Scaling Modifier
        ctk.CTkLabel(
            self.appearance_frame, 
            text="Font Size & UI Scale:", 
            font=("Poppins", 12, "bold"), 
            text_color=("gray10", "#FFFFFF")
        ).pack(anchor="w", padx=20, pady=(5, 2))
        
        self.combo_scaling = ctk.CTkOptionMenu(
            self.appearance_frame,
            values=["Small (90%)", "Normal (100%)", "Large (110%)", "Extra Large (120%)"],
            command=self.change_ui_scaling,
            height=35,
            fg_color=("gray85", "#2B2B3D"),
            button_color="#10B981",
            text_color=("gray10", "#FFFFFF")
        )
        self.combo_scaling.set("Normal (100%)")
        self.combo_scaling.pack(fill="x", padx=20, pady=(0, 20))

        # Divider line
        ctk.CTkFrame(self.appearance_frame, height=2, fg_color=("gray80", "#2B2B3D")).pack(fill="x", padx=20, pady=10)

        # =============================================================
        # RIGHT PANEL: ABOUT & HELP / FAQ
        # =============================================================
        self.info_frame = ctk.CTkFrame(self, corner_radius=10, fg_color=("white", "#1E1E1E"))
        self.info_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.info_tabview = ctk.CTkTabview(
            self.info_frame, 
            fg_color=("gray90", "#2B2B3D"), 
            segmented_button_fg_color=("gray80", "#1E1E2E"),
            text_color=("gray10", "#FFFFFF")
        )
        self.info_tabview.pack(fill="both", expand=True, padx=15, pady=15)

        self.tab_about = self.info_tabview.add("About")
        self.tab_help = self.info_tabview.add("Help & FAQ")

        # --- ABOUT TAB CONTENT ---
        ctk.CTkLabel(
            self.tab_about, text="Study SyncMate v0.1.6", font=("Poppins", 16, "bold"), text_color="#3B82F6"
        ).pack(anchor="w", padx=10, pady=(10, 5))

        about_text = (
            "Study SyncMate is a centralized, modular academic desktop application "
            "designed to help students organize notes, track tasks, generate practice quizzes, "
            "and monitor study progress seamlessly.\n\n"
            "Developers: SilverNox(Ray), Peony(Richboy), Yanyan(Jarylle), Athan(Nathanael), Exil3(Aron), and Xywinn(Russel).\n\n\n\n"
            "Developed with Python, Tkinter, CustomTkinter, and SQLite."
        )
        ctk.CTkLabel(
            self.tab_about, text=about_text, font=("Poppins", 13), text_color=("gray20", "#DDDDDD"), justify="left", wraplength=320
        ).pack(anchor="w", padx=10, pady=5)

        # --- HELP & FAQ TAB CONTENT ---
        self.help_scroll = ctk.CTkScrollableFrame(self.tab_help, fg_color="transparent")
        self.help_scroll.pack(fill="both", expand=True, padx=5, pady=5)

        faqs = [
            ("How do I save notes?", "Go to 'My Notes', enter your Subject and Topic, then click 'Save Note' or 'Save Text Note Only'."),
            ("How does Quiz Generator work?", "The AI quiz generator automatically pulls from your saved notes per subject to build practice tests and flashcards."),
            ("How do I track study time?", "Use the interactive Schedule calendar to plan deadlines and monitor task completion status."),
            ("Can I change my password?", "Yes! Navigate to the Profile workspace using the top header or settings to update your credentials.")
        ]

        for q, a in faqs:
            q_box = ctk.CTkFrame(self.help_scroll, fg_color=("gray95", "#1E1E2E"), corner_radius=6)
            q_box.pack(fill="x", pady=4, padx=2)
            ctk.CTkLabel(q_box, text=f"❓ {q}", font=("Poppins", 11, "bold"), text_color=("#059669", "#10B981")).pack(anchor="w", padx=8, pady=(6, 2))
            ctk.CTkLabel(q_box, text=a, font=("Poppins", 10), text_color=("gray30", "#AAAAAA"), justify="left", wraplength=300).pack(anchor="w", padx=8, pady=(0, 6))

    # =============================================================
    # EVENT HANDLERS
    # =============================================================

    def change_appearance_mode(self, new_mode: str):
        """Switches standard application appearance mode (Dark, Light, System)."""
        if new_mode in ["Dark", "Light", "System"]:
            ctk.set_appearance_mode(new_mode)

    def change_ui_scaling(self, scale_str: str):
        """Changes global font and widget scaling size."""
        scaling_map = {
            "Small (90%)": 0.9,
            "Normal (100%)": 1.0,
            "Large (110%)": 1.1,
            "Extra Large (120%)": 1.2
        }
        scale_val = scaling_map.get(scale_str, 1.0)
        ctk.set_widget_scaling(scale_val)

    def on_show(self):
        """Lifecycle method when switching to Settings view."""
        pass
