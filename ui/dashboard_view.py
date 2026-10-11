import customtkinter as ctk
from database.db_connection import db
from logic.schedule import ScheduleManager
from ui.notes_dashboard_ui import NotesDashboardView
from ui.profile_view import ProfileViewFrame
from ui.quiz_gene_ui import QuizGeneView
from ui.schedule_ui import ScheduleViewFrame
from ui.progress_ui import ProgressViewFrame


class DashboardView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.schedule_logic = ScheduleManager()

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
            command=self.nav_profile
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

        # -------------------------------------------------------------
        # 3A. HOME SUB-VIEW (With Quick Stats & Task Notifications)
        # -------------------------------------------------------------
        self.home_view = ctk.CTkFrame(self.workspace_container, fg_color="transparent")
        
        # Stats Cards Grid
        self.stats_container = ctk.CTkFrame(self.home_view, fg_color="transparent", height=100)
        self.stats_container.pack(fill="x", padx=10, pady=10)
        self.stats_container.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.card_notes_val = self._create_stat_card(self.stats_container, "Total Notes", "0", "#3B82F6", 0)
        self.card_tasks_val = self._create_stat_card(self.stats_container, "Pending Tasks", "0", "#10B981", 1)
        self.card_quiz_val  = self._create_stat_card(self.stats_container, "Quiz Average", "0%", "#F59E0B", 2)
        self.card_hours_val = self._create_stat_card(self.stats_container, "Study Hours", "0 hrs", "#8B5CF6", 3)

        # Task Notifications / Upcoming Deadlines Feed
        self.notif_frame = ctk.CTkFrame(self.home_view, fg_color="#1E1E2E", corner_radius=10)
        self.notif_frame.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(
            self.notif_frame, 
            text="🔔 Task Notifications & Upcoming Deadlines", 
            font=("Poppins", 15, "bold"), 
            text_color="#FFFFFF"
        ).pack(anchor="w", padx=20, pady=(15, 5))

        self.scroll_notifications = ctk.CTkScrollableFrame(self.notif_frame, fg_color="transparent")
        self.scroll_notifications.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        self.sub_views["home"] = self.home_view

        # 3B. Other Sub-Views
        self.sub_views["notes"] = NotesDashboardView(self.workspace_container, self.controller)
        self.sub_views["profile"] = ProfileViewFrame(self.workspace_container, self.controller)
        self.sub_views["quizzes"] = QuizGeneView(self.workspace_container, self.controller)
        self.sub_views["schedule"] = ScheduleViewFrame(self.workspace_container, self.controller)
        self.sub_views["progress"] = ProgressViewFrame(self.workspace_container, self.controller)

        # Display Home view by default
        self.show_sub_view("home")

    def _create_stat_card(self, parent, title, initial_val, color, col_idx):
        card = ctk.CTkFrame(parent, fg_color="#1E1E2E", corner_radius=10, height=85)
        card.grid(row=0, column=col_idx, sticky="nsew", padx=6)
        card.pack_propagate(False)

        ctk.CTkLabel(card, text=title, font=("Poppins", 11), text_color="#AAAAAA").pack(anchor="w", padx=12, pady=(10, 0))
        val_lbl = ctk.CTkLabel(card, text=initial_val, font=("Poppins", 16, "bold"), text_color=color)
        val_lbl.pack(anchor="w", padx=12)
        return val_lbl

    # =============================================================
    # DATA REFRESH FOR HOME DASHBOARD
    # =============================================================
    def refresh_home_dashboard(self):
        """Fetches live progress stats and pending task notifications."""
        user_id = self._get_user_id()
        
        # 1. Update Progress Summary Cards
        stats = db.get_user_stats_summary(user_id)
        self.card_notes_val.configure(text=str(stats["total_notes"]))
        self.card_tasks_val.configure(text=str(stats["pending_tasks"]))
        self.card_quiz_val.configure(text=stats["avg_quiz_score"])
        self.card_hours_val.configure(text=f"{stats['total_study_hours']} hrs")

        # 2. Populate Task Notifications Feed
        for widget in self.scroll_notifications.winfo_children():
            widget.destroy()

        pending_tasks = self.schedule_logic.get_user_tasks(user_id, status_filter="Pending")
        in_progress_tasks = self.schedule_logic.get_user_tasks(user_id, status_filter="In Progress")
        active_tasks = pending_tasks + in_progress_tasks

        if not active_tasks:
            ctk.CTkLabel(
                self.scroll_notifications, 
                text="🎉 You're all caught up! No pending tasks or deadlines.", 
                text_color="#10B981", 
                font=("Poppins", 12)
            ).pack(pady=20)
            return

        for task in active_tasks:
            alert_card = ctk.CTkFrame(self.scroll_notifications, fg_color="#2B2B3D", corner_radius=8)
            alert_card.pack(fill="x", pady=5, padx=5)

            prio_colors = {"High": "#EF4444", "Medium": "#F59E0B", "Low": "#10B981"}
            p_color = prio_colors.get(task.get("priority"), "#3B82F6")

            top_row = ctk.CTkFrame(alert_card, fg_color="transparent")
            top_row.pack(fill="x", padx=12, pady=(8, 2))

            ctk.CTkLabel(top_row, text=f"📌 {task['title']}", font=("Poppins", 13, "bold"), text_color="#FFFFFF").pack(side="left")
            ctk.CTkLabel(top_row, text=f"Priority: {task['priority']}", font=("Poppins", 10, "bold"), text_color=p_color).pack(side="right")

            ctk.CTkLabel(
                alert_card, 
                text=f"📅 Due Date: {task['due_date']}  |  Status: {task['status']}", 
                font=("Poppins", 11), 
                text_color="#AAAAAA"
            ).pack(anchor="w", padx=12, pady=(0, 8))

    def _get_user_id(self) -> int:
        if hasattr(self.controller, "current_user") and self.controller.current_user:
            return self.controller.current_user.get("id", 1)
        return 1

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
            if key == "home":
                self.refresh_home_dashboard()
            elif hasattr(selected, "on_show"):
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
        self.content_title.configure(text="Quizzes & Flashcards Generator")
        self.show_sub_view("quizzes")

    def nav_schedule(self):
        self.content_title.configure(text="Study Schedule & Task Planner")
        self.show_sub_view("schedule")

    def nav_progress(self):
        self.content_title.configure(text="Academic Progress Analytics")
        self.show_sub_view("progress")

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
        for key, frame in self.sub_views.items():
            if frame.winfo_ismapped():
                if key == "home":
                    self.refresh_home_dashboard()
                elif hasattr(frame, "on_show"):
                    frame.on_show()

    def handle_logout(self):
        self.controller.logout()