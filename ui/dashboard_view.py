import customtkinter as ctk
from ui.notes_dashboard_ui import NotesDashboardView
from ui.profile_view import ProfileViewFrame


class DashboardView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        # Grid configuration: Row 0 (Top Header), Row 1 (Sidebar + Main Workspace)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # =============================================================
        # 1. TOP NAVBAR / HEADER
        # =============================================================
        self.header_frame = ctk.CTkFrame(self, height=60, corner_radius=10, fg_color="#1E1E2E")
        self.header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=(10, 5))
        self.header_frame.pack_propagate(False)

        # Welcome Label
        self.welcome_label = ctk.CTkLabel(
            self.header_frame, 
            text="Welcome to Study SyncMate", 
            font=("Poppins", 18, "bold"), 
            text_color="#FFFFFF"
        )
        self.welcome_label.pack(side="left", padx=20)

        # Header Buttons
        self.btn_logout = ctk.CTkButton(
            self.header_frame, 
            text="Logout", 
            width=80, 
            height=32,
            font=("Poppins", 12, "bold"), 
            fg_color="#8B0000", 
            hover_color="#550000",
            command=self.handle_logout
        )
        self.btn_logout.pack(side="right", padx=(5, 15))

        self.btn_profile = ctk.CTkButton(
            self.header_frame, 
            text="Profile", 
            width=90, 
            height=32,
            font=("Poppins", 12, "bold"), 
            fg_color="#000080", 
            hover_color="#000055",
            command=self.nav_profile  # 👈 Directly opens Profile sub-view
        )
        self.btn_profile.pack(side="right", padx=5)

        # =============================================================
        # 2. LEFT SIDEBAR NAVIGATION
        # =============================================================
        self.sidebar_frame = ctk.CTkFrame(self, width=180, corner_radius=10, fg_color="#2B2B2B")
        self.sidebar_frame.grid(row=1, column=0, sticky="nsew", padx=(10, 5), pady=5)
        self.sidebar_frame.pack_propagate(False)

        ctk.CTkLabel(
            self.sidebar_frame, 
            text="NAVIGATION", 
            font=("Poppins", 11, "bold"), 
            text_color="#AAAAAA"
        ).pack(anchor="w", padx=15, pady=(15, 10))

        nav_buttons = [
            ("Home", self.nav_home),
            ("My Notes", self.nav_notes),
            ("Quizzes", self.nav_quizzes),
            ("Schedule", self.nav_schedule),
            ("Progress", self.nav_progress),
        ]

        for text, command_fn in nav_buttons:
            btn = ctk.CTkButton(
                self.sidebar_frame,
                text=f"  {text}",
                font=("Poppins", 13),
                anchor="w",
                fg_color="transparent",
                hover_color="#3A3A3A",
                height=38,
                command=command_fn
            )
            btn.pack(fill="x", padx=8, pady=3)

        # =============================================================
        # 3. MAIN WORKSPACE & SUB-VIEW SWITCHER
        # =============================================================
        self.main_content = ctk.CTkFrame(self, corner_radius=10, fg_color="#1E1E1E")
        self.main_content.grid(row=1, column=1, sticky="nsew", padx=(5, 10), pady=5)

        self.content_title = ctk.CTkLabel(
            self.main_content, 
            text="Dashboard Overview", 
            font=("Poppins", 20, "bold")
        )
        self.content_title.pack(anchor="nw", padx=25, pady=(15, 5))

        # Container holding sub-view frames
        self.workspace_container = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.workspace_container.pack(fill="both", expand=True, padx=10, pady=5)

        self.sub_views = {}

        # 3A. Home Sub-View Cards
        self.home_view = ctk.CTkFrame(self.workspace_container, fg_color="transparent")
        self.stats_container = ctk.CTkFrame(self.home_view, fg_color="transparent")
        self.stats_container.pack(fill="x", padx=10, pady=10)
        self._create_stat_card(self.stats_container, "Total Notes", "12 Notes", "#4A90E2")
        self._create_stat_card(self.stats_container, "Upcoming Tasks", "5 Pending", "#4CAF50")
        self._create_stat_card(self.stats_container, "Quiz Score Avg.", "92%", "#E57373")
        self.sub_views["home"] = self.home_view

        # 3B. My Notes Sub-View
        self.sub_views["notes"] = NotesDashboardView(self.workspace_container, self.controller)

        # 3C. User Profile Sub-View
        self.sub_views["profile"] = ProfileViewFrame(self.workspace_container, self.controller)

        # Display Home view by default
        self.show_sub_view("home")

    def _create_stat_card(self, parent, title, value, color):
        card = ctk.CTkFrame(parent, width=170, height=90, corner_radius=10, fg_color="#2B2B2B")
        card.pack(side="left", padx=8, expand=True, fill="x")
        card.pack_propagate(False)

        ctk.CTkLabel(card, text=title, font=("Poppins", 11), text_color="#AAAAAA").pack(anchor="w", padx=12, pady=(12, 2))
        ctk.CTkLabel(card, text=value, font=("Poppins", 18, "bold"), text_color=color).pack(anchor="w", padx=12)

    # =============================================================
    # SUB-VIEW NAVIGATION SWITCHER
    # =============================================================
    def show_sub_view(self, key: str):
        """Hides current view and raises selected view."""
        for frame in self.sub_views.values():
            frame.pack_forget()

        selected = self.sub_views.get(key)
        if selected:
            selected.pack(fill="both", expand=True)
            if hasattr(selected, "on_show"):
                selected.on_show()

    def nav_home(self):
        self.content_title.configure(text="Dashboard Overview")
        self.show_sub_view("home")

    def nav_notes(self):
        self.content_title.configure(text="My Notes Workspace")
        self.show_sub_view("notes")

    def nav_profile(self):
        self.content_title.configure(text="User Profile Settings")
        self.show_sub_view("profile")

    def nav_quizzes(self):
        self.content_title.configure(text="Quizzes & Flashcards")

    def nav_schedule(self):
        self.content_title.configure(text="Study Schedule & Planner")

    def nav_progress(self):
        self.content_title.configure(text="Academic Progress Analytics")

    # =============================================================
    # CONTROLLER LIFECYCLE
    # =============================================================
    def on_show(self):
        """Runs automatically when main window switches to DashboardView."""
        if hasattr(self.controller, "current_user") and self.controller.current_user:
            user = self.controller.current_user
            name = user.get("full_name", "Student")
            course = user.get("course", "")
            year = user.get("year_level", "")

            sub_info = f" ({course} – {year})" if course else ""
            self.welcome_label.configure(text=f"Welcome back, {name}{sub_info}!")

        # Refresh currently visible sub-view
        for frame in self.sub_views.values():
            if frame.winfo_ismapped() and hasattr(frame, "on_show"):
                frame.on_show()

    def handle_logout(self):
        self.controller.logout()