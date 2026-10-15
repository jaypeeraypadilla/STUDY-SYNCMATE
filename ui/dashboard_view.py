import calendar
import datetime
import customtkinter as ctk
from database.db_connection import db
from logic.my_notes import NotesManager
from logic.quiz_generator import QuizGenerator
from logic.schedule import ScheduleManager
from logic.progress import ProgressTracker
from ui.onboarding_tutorial import OnboardingTutorial
from ui.notes_dashboard_ui import NotesDashboardView
from ui.profile_view import ProfileViewFrame
from ui.quiz_gene_ui import QuizGeneView
from ui.schedule_ui import ScheduleViewFrame
from ui.progress_ui import ProgressViewFrame
from ui.settings_view import SettingsViewFrame


class DashboardView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        
        # Initialize Backend Logic Modules
        self.notes_logic = NotesManager()
        self.quiz_logic = QuizGenerator()
        self.schedule_logic = ScheduleManager()
        self.progress_logic = ProgressTracker()

        # Grid configuration: Row 0 (Top Header), Row 1 (Sidebar + Main Workspace)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # =============================================================
        # 1. TOP NAVBAR / HEADER
        # =============================================================
        self.header_frame = ctk.CTkFrame(self, corner_radius=10, fg_color=("gray90", "#1E1E2E"))
        self.header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=(10, 5))

        # Left Header Container (Logo Icon + Welcome Text)
        self.header_left_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.header_left_frame.pack(side="left", padx=15, pady=8)

        # Logo Icon / Emblem
        self.logo_label = ctk.CTkLabel(
            self.header_left_frame, 
            text="📘", 
            font=("Poppins", 20),
            text_color=("gray10", "#FFFFFF")
        )
        self.logo_label.pack(side="left", padx=(0, 10))

        # Welcome Label
        self.welcome_label = ctk.CTkLabel(
            self.header_left_frame, 
            text="Welcome to Study SyncMate", 
            font=("Poppins", 18, "bold"), 
            text_color=("gray10", "#FFFFFF")
        )
        self.welcome_label.pack(side="left")

        # Header Buttons (Logout, Expanding Profile, Expanding Tutorial)
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
        self.btn_logout.pack(side="right", padx=(5, 15), pady=12)

        # Expanding Profile Button
        self.btn_profile = ctk.CTkButton(
            self.header_frame, 
            text="👤", 
            width=36, 
            height=36,
            corner_radius=18,
            font=("Poppins", 13, "bold"), 
            fg_color=("#E5E7EB", "#2B2B3D"), 
            hover_color=("#D1D5DB", "#3A3A4E"),
            text_color=("gray10", "#FFFFFF"),
            command=self.nav_profile
        )
        self.btn_profile.pack(side="right", padx=5, pady=12)
        self.btn_profile.bind("<Enter>", lambda e: self.btn_profile.configure(text="👤 Profile", width=110))
        self.btn_profile.bind("<Leave>", lambda e: self.btn_profile.configure(text="👤", width=36))

        # Expanding Tutorial Tour Button
        self.btn_tutorial = ctk.CTkButton(
            self.header_frame, 
            text="💡", 
            width=36, 
            height=36,
            corner_radius=18,
            font=("Poppins", 13, "bold"), 
            fg_color=("#E5E7EB", "#2B2B3D"), 
            hover_color=("#D1D5DB", "#3A3A4E"),
            text_color=("gray10", "#FFFFFF"),
            command=self.open_tutorial
        )
        self.btn_tutorial.pack(side="right", padx=5, pady=12)
        self.btn_tutorial.bind("<Enter>", lambda e: self.btn_tutorial.configure(text="💡 Tutorial", width=110))
        self.btn_tutorial.bind("<Leave>", lambda e: self.btn_tutorial.configure(text="💡", width=36))

        # =============================================================
        # 2. LEFT SIDEBAR NAVIGATION
        # =============================================================
        self.sidebar_frame = ctk.CTkFrame(self, width=190, corner_radius=10, fg_color=("gray85", "#2B2B2B"))
        self.sidebar_frame.grid(row=1, column=0, sticky="nsew", padx=(10, 5), pady=5)
        self.sidebar_frame.grid_propagate(False)

        ctk.CTkLabel(
            self.sidebar_frame, 
            text="NAVIGATION", 
            font=("Poppins", 11, "bold"), 
            text_color=("gray40", "#AAAAAA")
        ).pack(anchor="w", padx=15, pady=(15, 10))

        nav_buttons = [
            ("🏠 Home", self.nav_home),
            ("📓 My Notes", self.nav_notes),
            ("📝 Quizzes", self.nav_quizzes),
            ("📅 Schedule", self.nav_schedule),
            ("📊 Progress", self.nav_progress),
            ("⚙️ Settings", self.nav_settings),
        ]

        for text, command_fn in nav_buttons:
            btn = ctk.CTkButton(
                self.sidebar_frame,
                text=f"  {text}",
                font=("Poppins", 13),
                anchor="w",
                fg_color="transparent",
                hover_color=("gray75", "#3A3A3A"),
                text_color=("gray10", "#FFFFFF"),
                height=38,
                command=command_fn
            )
            btn.pack(fill="x", padx=8, pady=3)

        # Bottom Motivational Widget
        self.habit_widget = ctk.CTkFrame(self.sidebar_frame, fg_color=("gray95", "#1E1E2E"), corner_radius=8)
        self.habit_widget.pack(side="bottom", fill="x", padx=10, pady=15)
        ctk.CTkLabel(self.habit_widget, text="🎯", font=("Poppins", 18), text_color=("gray10", "#FFFFFF")).pack(pady=(8, 0))
        ctk.CTkLabel(
            self.habit_widget, text="Better habits,\nBrighter future.", font=("Poppins", 9, "bold"), text_color="#10B981", justify="center"
        ).pack(pady=(2, 8))

        # =============================================================
        # 3. MAIN WORKSPACE & SUB-VIEW SWITCHER
        # =============================================================
        self.main_content = ctk.CTkFrame(self, corner_radius=10, fg_color=("gray95", "#1E1E1E"))
        self.main_content.grid(row=1, column=1, sticky="nsew", padx=(5, 10), pady=5)

        self.content_title = ctk.CTkLabel(
            self.main_content, 
            text="Dashboard Overview", 
            font=("Poppins", 20, "bold"),
            text_color=("gray10", "#FFFFFF")
        )
        self.content_title.pack(anchor="nw", padx=25, pady=(15, 5))

        # Container holding sub-view frames
        self.workspace_container = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.workspace_container.pack(fill="both", expand=True, padx=10, pady=5)

        self.sub_views = {}

        # -------------------------------------------------------------
        # 3A. HOME SUB-VIEW (Theme-Adaptive & Fluid Layout)
        # -------------------------------------------------------------
        self.home_view = ctk.CTkFrame(self.workspace_container, fg_color="transparent")
        self.home_view.grid_columnconfigure(0, weight=3) # Left/Center section
        self.home_view.grid_columnconfigure(1, weight=2) # Right panel section
        self.home_view.grid_rowconfigure(0, weight=1)

        # --- LEFT/CENTER COLUMN ---
        self.center_column = ctk.CTkScrollableFrame(self.home_view, fg_color="transparent")
        self.center_column.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        # Hero Welcome Banner
        self.hero_banner = ctk.CTkFrame(self.center_column, fg_color=("white", "#1E1E2E"), corner_radius=10)
        self.hero_banner.pack(fill="x", pady=(0, 10))

        hero_text_box = ctk.CTkFrame(self.hero_banner, fg_color="transparent")
        hero_text_box.pack(side="left", fill="both", expand=True, padx=20, pady=15)

        self.lbl_hero_welcome = ctk.CTkLabel(
            hero_text_box, text="Welcome back, Student!", font=("Poppins", 18, "bold"), text_color=("gray10", "#FFFFFF"), justify="left", wraplength=350
        )
        self.lbl_hero_welcome.pack(anchor="w")

        ctk.CTkLabel(
            hero_text_box, text="Your goals are within reach. Let's keep learning!", font=("Poppins", 11), text_color=("gray50", "#AAAAAA"), justify="left", wraplength=350
        ).pack(anchor="w", pady=(4, 0))

        ctk.CTkLabel(self.hero_banner, text="🎓📚", font=("Poppins", 36), text_color=("gray10", "#FFFFFF")).pack(side="right", padx=25, pady=15)

        # Quick Action Cards Grid
        self.quick_actions_grid = ctk.CTkFrame(self.center_column, fg_color="transparent")
        self.quick_actions_grid.pack(fill="x", pady=(0, 10))
        self.quick_actions_grid.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self._create_quick_action_card(self.quick_actions_grid, "📱", "Notes", "View & manage", self.nav_notes, 0)
        self._create_quick_action_card(self.quick_actions_grid, "📋", "Quizzes", "Practice tests", self.nav_quizzes, 1)
        self._create_quick_action_card(self.quick_actions_grid, "🎴", "Flashcards", "Review terms", self.nav_quizzes, 2)
        self._create_quick_action_card(self.quick_actions_grid, "📅", "Schedule", "Planner tasks", self.nav_schedule, 3)

        # Progress Stats Cards Grid
        self.stats_container = ctk.CTkFrame(self.center_column, fg_color="transparent")
        self.stats_container.pack(fill="x", pady=5)
        self.stats_container.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.card_notes_val = self._create_stat_card(self.stats_container, "Total Notes", "0", "#3B82F6", 0)
        self.card_tasks_val = self._create_stat_card(self.stats_container, "Pending Tasks", "0", "#10B981", 1)
        self.card_quiz_val  = self._create_stat_card(self.stats_container, "Quiz Average", "0%", "#F59E0B", 2)
        self.card_hours_val = self._create_stat_card(self.stats_container, "Study Hours", "0 hrs", "#8B5CF6", 3)

        # --- RIGHT COLUMN (Calendar, Upcoming Deadlines, Recent Activity) ---
        self.right_column = ctk.CTkScrollableFrame(self.home_view, fg_color="transparent")
        self.right_column.grid(row=0, column=1, sticky="nsew")

        # Mini Calendar Widget
        self.mini_cal_card = ctk.CTkFrame(self.right_column, fg_color=("white", "#1E1E2E"), corner_radius=10)
        self.mini_cal_card.pack(fill="x", pady=(0, 10))

        cal_header = ctk.CTkFrame(self.mini_cal_card, fg_color="transparent")
        cal_header.pack(fill="x", padx=12, pady=(10, 4))
        ctk.CTkLabel(cal_header, text="📅 Current Calendar", font=("Poppins", 11, "bold"), text_color=("gray10", "#FFFFFF")).pack(side="left")

        self.cal_grid = ctk.CTkFrame(self.mini_cal_card, fg_color="transparent")
        self.cal_grid.pack(fill="x", padx=8, pady=(0, 10))
        self.render_mini_calendar()

        # Task Notifications & Upcoming Deadlines Feed
        self.notif_frame = ctk.CTkFrame(self.right_column, fg_color=("white", "#1E1E2E"), corner_radius=10)
        self.notif_frame.pack(fill="x", pady=(0, 10))

        up_head = ctk.CTkFrame(self.notif_frame, fg_color="transparent")
        up_head.pack(fill="x", padx=12, pady=(10, 4))
        ctk.CTkLabel(up_head, text="🔔 Upcoming Deadlines", font=("Poppins", 12, "bold"), text_color=("gray10", "#FFFFFF")).pack(side="left")
        ctk.CTkButton(up_head, text="View all", width=60, height=22, fg_color="transparent", text_color="#3B82F6", command=self.nav_schedule).pack(side="right")

        self.scroll_notifications = ctk.CTkFrame(self.notif_frame, fg_color="transparent")
        self.scroll_notifications.pack(fill="x", expand=True, padx=8, pady=(0, 10))

        # Recent Activity Feed
        self.activity_frame = ctk.CTkFrame(self.right_column, fg_color=("white", "#1E1E2E"), corner_radius=10)
        self.activity_frame.pack(fill="x")

        act_head = ctk.CTkFrame(self.activity_frame, fg_color="transparent")
        act_head.pack(fill="x", padx=12, pady=(10, 4))
        ctk.CTkLabel(act_head, text="⚡ Recent Activity", font=("Poppins", 12, "bold"), text_color=("gray10", "#FFFFFF")).pack(side="left")

        self.scroll_activity = ctk.CTkFrame(self.activity_frame, fg_color="transparent")
        self.scroll_activity.pack(fill="x", expand=True, padx=8, pady=(0, 10))

        self.sub_views["home"] = self.home_view

        # 3B. Other Sub-Views
        self.sub_views["notes"] = NotesDashboardView(self.workspace_container, self.controller)
        self.sub_views["profile"] = ProfileViewFrame(self.workspace_container, self.controller)
        self.sub_views["quizzes"] = QuizGeneView(self.workspace_container, self.controller)
        self.sub_views["schedule"] = ScheduleViewFrame(self.workspace_container, self.controller)
        self.sub_views["progress"] = ProgressViewFrame(self.workspace_container, self.controller)
        self.sub_views["settings"] = SettingsViewFrame(self.workspace_container, self.controller)

        # Display Home view by default
        self.show_sub_view("home")

    def open_tutorial(self):
        """Launches the floating onboarding tutorial pointing to specific app sections."""
        targets = {
            "notes": getattr(self, "btn_notes_sidebar", None),
            "quizzes": getattr(self, "btn_quizzes_sidebar", None),
            "schedule": getattr(self, "btn_schedule_sidebar", None),
            "progress": getattr(self, "btn_progress_sidebar", None)
        }
        OnboardingTutorial(self, self.controller, target_widgets=targets)

    def _create_stat_card(self, parent, title, initial_val, color, col_idx):
        card = ctk.CTkFrame(parent, fg_color=("white", "#1E1E2E"), corner_radius=10)
        card.grid(row=0, column=col_idx, sticky="nsew", padx=4)

        ctk.CTkLabel(card, text=title, font=("Poppins", 10), text_color=("gray50", "#AAAAAA"), wraplength=90).pack(anchor="w", padx=10, pady=(10, 0))
        val_lbl = ctk.CTkLabel(card, text=initial_val, font=("Poppins", 15, "bold"), text_color=color)
        val_lbl.pack(anchor="w", padx=10, pady=(0, 10))
        return val_lbl

    def _create_quick_action_card(self, parent, icon, title, subtitle, command_fn, col):
        card = ctk.CTkFrame(parent, fg_color=("white", "#1E1E2E"), corner_radius=10)
        card.grid(row=0, column=col, sticky="nsew", padx=4)

        ctk.CTkButton(
            card,
            text=icon,
            width=32,
            height=32,
            corner_radius=6,
            fg_color=("gray90", "#2B2B3D"),
            hover_color=("gray80", "#3A3A4E"),
            font=("Poppins", 14),
            text_color=("gray10", "#FFFFFF"),
            command=command_fn
        ).pack(anchor="w", padx=10, pady=(10, 2))

        ctk.CTkLabel(card, text=title, font=("Poppins", 11, "bold"), text_color=("gray10", "#FFFFFF"), wraplength=90).pack(anchor="w", padx=10)
        ctk.CTkLabel(card, text=subtitle, font=("Poppins", 9), text_color=("gray50", "#8A8A9E"), wraplength=90).pack(anchor="w", padx=10, pady=(0, 10))

    def render_mini_calendar(self):
        """Renders 7x5 month grid for mini calendar widget."""
        day_headers = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        for col, h in enumerate(day_headers):
            ctk.CTkLabel(self.cal_grid, text=h, font=("Poppins", 8, "bold"), text_color=("gray50", "#6C6C82")).grid(row=0, column=col, padx=2, pady=1)

        today = datetime.date.today()
        cal_matrix = calendar.monthcalendar(today.year, today.month)
        for row_idx, week in enumerate(cal_matrix, start=1):
            for col_idx, day_num in enumerate(week):
                if day_num != 0:
                    is_active = (day_num == today.day)
                    lbl = ctk.CTkLabel(
                        self.cal_grid,
                        text=str(day_num),
                        font=("Poppins", 8, "bold" if is_active else "normal"),
                        text_color=("gray10", "#FFFFFF") if is_active else ("gray40", "#A0A0B8"),
                        fg_color="#3B82F6" if is_active else "transparent",
                        corner_radius=4,
                        width=20,
                        height=18
                    )
                    lbl.grid(row=row_idx, column=col_idx, padx=1, pady=1)

    # =============================================================
    # DATA REFRESH FOR HOME DASHBOARD
    # =============================================================
    def refresh_home_dashboard(self):
        user_id = self._get_user_id()
        
        if hasattr(self.controller, "current_user") and self.controller.current_user:
            name = self.controller.current_user.get("full_name", "Student")
            first_name = name.split()[0]
            self.lbl_hero_welcome.configure(text=f"Welcome back, {first_name}!")

        stats = db.get_user_stats_summary(user_id)
        self.card_notes_val.configure(text=str(stats["total_notes"]))
        self.card_tasks_val.configure(text=str(stats["pending_tasks"]))
        self.card_quiz_val.configure(text=stats["avg_quiz_score"])
        self.card_hours_val.configure(text=f"{stats['total_study_hours']} hrs")

        # Populate Upcoming Deadlines
        for widget in self.scroll_notifications.winfo_children():
            widget.destroy()

        pending_tasks = self.schedule_logic.get_user_tasks(user_id, status_filter="Pending")
        in_progress_tasks = self.schedule_logic.get_user_tasks(user_id, status_filter="In Progress")
        active_tasks = pending_tasks + in_progress_tasks

        if not active_tasks:
            ctk.CTkLabel(
                self.scroll_notifications, 
                text="🎉 No pending tasks or deadlines.", 
                text_color="#10B981", 
                font=("Poppins", 11)
            ).pack(pady=10)
        else:
            for task in active_tasks[:3]:
                alert_card = ctk.CTkFrame(self.scroll_notifications, fg_color=("gray95", "#2B2B3D"), corner_radius=6)
                alert_card.pack(fill="x", pady=2, padx=2)

                prio_colors = {"High": "#EF4444", "Medium": "#F59E0B", "Low": "#10B981"}
                p_color = prio_colors.get(task.get("priority"), "#3B82F6")

                top_row = ctk.CTkFrame(alert_card, fg_color="transparent")
                top_row.pack(fill="x", padx=8, pady=(4, 0))

                ctk.CTkLabel(top_row, text=f"📌 {task['title']}", font=("Poppins", 11, "bold"), text_color=("gray10", "#FFFFFF")).pack(side="left")
                ctk.CTkLabel(top_row, text=task['priority'], font=("Poppins", 9, "bold"), text_color=p_color).pack(side="right")
                ctk.CTkLabel(alert_card, text=f"Due: {task['due_date']}", font=("Poppins", 9), text_color=("gray50", "#AAAAAA")).pack(anchor="w", padx=8, pady=(0, 4))

        # Populate Recent Activity
        for widget in self.scroll_activity.winfo_children():
            widget.destroy()

        quiz_history = self.progress_logic.get_quiz_history(user_id)
        notes_list = self.notes_logic.get_user_notes(user_id)
        
        recent_items = []
        if quiz_history:
            q = quiz_history[0]
            pct = round((q["score"] / q["total_questions"]) * 100)
            recent_items.append(("✔️ Quiz Completed", f"{q['quiz_title']} ({pct}%)"))
        if notes_list:
            n = notes_list[0]
            recent_items.append(("📓 Note Added", f"'{n['title']}' ({n['subject']})"))

        if not recent_items:
            recent_items.append(("💡 Tip", "Start creating notes and taking quizzes!"))

        for title, sub in recent_items:
            act_card = ctk.CTkFrame(self.scroll_activity, fg_color=("gray95", "#2B2B3D"), corner_radius=6)
            act_card.pack(fill="x", pady=2, padx=2)
            ctk.CTkLabel(act_card, text=title, font=("Poppins", 10, "bold"), text_color=("gray10", "#FFFFFF")).pack(anchor="w", padx=8, pady=(4, 0))
            ctk.CTkLabel(act_card, text=sub, font=("Poppins", 9), text_color=("gray50", "#AAAAAA")).pack(anchor="w", padx=8, pady=(0, 4))

    def _get_user_id(self) -> int:
        if hasattr(self.controller, "current_user") and self.controller.current_user:
            return self.controller.current_user.get("id", 1)
        return 1

    # =============================================================
    # SUB-VIEW NAVIGATION SWITCHER
    # =============================================================
    def show_sub_view(self, key: str):
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

    def nav_settings(self):
        self.content_title.configure(text="App Settings & Help")
        self.show_sub_view("settings")

    # =============================================================
    # CONTROLLER LIFECYCLE
    # =============================================================
    def on_show(self):
        if hasattr(self.controller, "current_user") and self.controller.current_user:
            user = self.controller.current_user
            name = user.get("full_name", "Student")
            course = user.get("course", "")
            year = user.get("year_level", "")

            sub_info = f" ({course} – {year})" if course else ""
            self.welcome_label.configure(text=f"Welcome back, {name}{sub_info}!")

        for key, frame in self.sub_views.items():
            if frame.winfo_ismapped():
                if key == "home":
                    self.refresh_home_dashboard()
                elif hasattr(frame, "on_show"):
                    frame.on_show()

    def handle_logout(self):
        self.controller.logout()