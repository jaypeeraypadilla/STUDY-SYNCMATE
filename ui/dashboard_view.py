import calendar
import datetime
import os
import customtkinter as ctk
from PIL import Image
from database.db_connection import db
from logic.my_notes import NotesManager
from logic.quiz_generator import QuizGenerator
from logic.schedule import ScheduleManager
from logic.progress import ProgressTracker
from logic.user_prof import ProfileManager
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
        self.profile_logic = ProfileManager()

        self.active_view_key = "home"

        # Bilingual Translation Dictionary for Dashboard & Sidebar
        self.translations = {
            "English": {
                "welcome_default": "Welcome to Study SyncMate",
                "nav_header": "NAVIGATION",
                "nav_home": "🏠 Home",
                "nav_notes": "📓 My Notes",
                "nav_quizzes": "📝 Quizzes",
                "nav_schedule": "📅 Schedule",
                "nav_progress": "📊 Progress",
                "nav_settings": "⚙️ Settings",
                "habit_text": "Better habits,\nBrighter future.",
                "logout": "Logout",
                "title_home": "Dashboard Overview",
                "title_notes": "My Notes Workspace",
                "title_profile": "User Profile Settings",
                "title_quizzes": "Quizzes & Flashcards Generator",
                "title_schedule": "Study Schedule & Task Planner",
                "title_progress": "Academic Progress Analytics",
                "title_settings": "App Settings & Help",
                "hero_welcome": "Welcome back, {name}!",
                "hero_sub": "Your goals are within reach. Let's keep learning!",
                "stat_notes": "Total Notes",
                "stat_tasks": "Pending Tasks",
                "stat_quiz": "Quiz Average",
                "stat_hours": "Study Hours",
                "cal_header": "📅 Current Calendar",
                "deadline_header": "🔔 Upcoming Deadlines",
                "view_all": "View all",
                "activity_header": "⚡ Recent Activity",
                "no_tasks": "🎉 No pending tasks or deadlines.",
                "tip_title": "💡 Tip",
                "tip_sub": "Start creating notes and taking quizzes!"
            },
            "Filipino": {
                "welcome_default": "Maligayang pagdating sa Study SyncMate",
                "nav_header": "NAVIGASYON",
                "nav_home": "🏠 Tahanan",
                "nav_notes": "📓 Aking mga Tala",
                "nav_quizzes": "📝 Mga Pagsusulit",
                "nav_schedule": "📅 Iskedyul",
                "nav_progress": "📊 Progreso",
                "nav_settings": "⚙️ Mga Setting",
                "habit_text": "Mas magandang gawi,\nMaliwanag na kinabukasan.",
                "logout": "Mag-logout",
                "title_home": "Pangkalahatang-ideya ng Dashboard",
                "title_notes": "Workspace ng Aking mga Tala",
                "title_profile": "Mga Setting ng Profile ng Gumagamit",
                "title_quizzes": "Generator ng Pagsusulit at Flashcard",
                "title_schedule": "Iskedyul ng Pag-aaral at Tagaplano",
                "title_progress": "Analitika ng Akademikong Progreso",
                "title_settings": "Mga Setting ng App at Tulong",
                "hero_welcome": "Maligayang pagbabalik, {name}!",
                "hero_sub": "Abot-kamay mo ang iyong mga layunin. Magpatuloy tayo sa pag-aaral!",
                "stat_notes": "Kabuuang Tala",
                "stat_tasks": "Mga Nakabinbing Gawain",
                "stat_quiz": "Karaniwan sa Pagsusulit",
                "stat_hours": "Oras ng Pag-aaral",
                "cal_header": "📅 Kasalukuyang Kalendaryo",
                "deadline_header": "🔔 Mga Darating na Deadline",
                "view_all": "Tingnan lahat",
                "activity_header": "⚡ Kamakailang Aktibidad",
                "no_tasks": "🎉 Walang mga nakabinbing gawain o deadline.",
                "tip_title": "💡 Tip",
                "tip_sub": "Magsimulang gumawa ng mga tala at sumagot ng mga pagsusulit!"
            }
        }

        # Grid configuration: Row 0 (Top Header), Row 1 (Sidebar + Main Workspace)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # =============================================================
        # 1. TOP NAVBAR / HEADER
        # =============================================================
        self.header_frame = ctk.CTkFrame(self, corner_radius=10, fg_color=("gray90", "#1E1E2E"))
        self.header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=(10, 5))

        self.header_left_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.header_left_frame.pack(side="left", padx=15, pady=8)

        self.logo_label = ctk.CTkLabel(
            self.header_left_frame, 
            text="📘", 
            font=("Poppins", 20),
            text_color=("gray10", "#FFFFFF")
        )
        self.logo_label.pack(side="left", padx=(0, 10))

        self.welcome_label = ctk.CTkLabel(
            self.header_left_frame, 
            text=self.get_text("welcome_default"), 
            font=("Poppins", 18, "bold"), 
            text_color=("gray10", "#FFFFFF")
        )
        self.welcome_label.pack(side="left")

        self.btn_logout = ctk.CTkButton(
            self.header_frame, 
            text=self.get_text("logout"), 
            width=80, 
            height=32,
            font=("Poppins", 12, "bold"), 
            fg_color="#8B0000", 
            hover_color="#550000",
            command=self.handle_logout
        )
        self.btn_logout.pack(side="right", padx=(5, 15), pady=12)

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

        self.lbl_nav_title = ctk.CTkLabel(
            self.sidebar_frame, 
            text=self.get_text("nav_header"), 
            font=("Poppins", 11, "bold"), 
            text_color=("gray40", "#AAAAAA")
        )
        self.lbl_nav_title.pack(anchor="w", padx=15, pady=(15, 10))

        self.sidebar_buttons = {}
        nav_items = [
            ("home", self.get_text("nav_home"), self.nav_home),
            ("notes", self.get_text("nav_notes"), self.nav_notes),
            ("quizzes", self.get_text("nav_quizzes"), self.nav_quizzes),
            ("schedule", self.get_text("nav_schedule"), self.nav_schedule),
            ("progress", self.get_text("nav_progress"), self.nav_progress),
            ("settings", self.get_text("nav_settings"), self.nav_settings),
        ]

        for key, text, command_fn in nav_items:
            btn = ctk.CTkButton(
                self.sidebar_frame,
                text=text,
                font=("Poppins", 13),
                anchor="w",
                fg_color="transparent",
                hover_color=("gray75", "#3A3A3A"),
                text_color=("gray10", "#FFFFFF"),
                height=38,
                command=command_fn
            )
            btn.pack(fill="x", padx=8, pady=3)
            self.sidebar_buttons[key] = btn

        # Bottom Motivational Widget
        self.habit_widget = ctk.CTkFrame(self.sidebar_frame, fg_color=("gray95", "#1E1E2E"), corner_radius=8)
        self.habit_widget.pack(side="bottom", fill="x", padx=10, pady=15)
        ctk.CTkLabel(self.habit_widget, text="🎯", font=("Poppins", 18), text_color=("gray10", "#FFFFFF")).pack(pady=(8, 0))
        self.lbl_habit = ctk.CTkLabel(
            self.habit_widget, text=self.get_text("habit_text"), font=("Poppins", 9, "bold"), text_color="#10B981", justify="center"
        )
        self.lbl_habit.pack(pady=(2, 8))

        # =============================================================
        # 3. MAIN WORKSPACE & SUB-VIEW SWITCHER
        # =============================================================
        self.main_content = ctk.CTkFrame(self, corner_radius=10, fg_color=("gray95", "#1E1E1E"))
        self.main_content.grid(row=1, column=1, sticky="nsew", padx=(5, 10), pady=5)

        self.content_title = ctk.CTkLabel(
            self.main_content, 
            text=self.get_text("title_home"), 
            font=("Poppins", 20, "bold"),
            text_color=("gray10", "#FFFFFF")
        )
        self.content_title.pack(anchor="nw", padx=25, pady=(15, 5))

        self.workspace_container = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.workspace_container.pack(fill="both", expand=True, padx=10, pady=5)

        self.sub_views = {}

        # -------------------------------------------------------------
        # 3A. HOME SUB-VIEW
        # -------------------------------------------------------------
        self.home_view = ctk.CTkFrame(self.workspace_container, fg_color="transparent")
        self.home_view.grid_columnconfigure(0, weight=3)
        self.home_view.grid_columnconfigure(1, weight=2)
        self.home_view.grid_rowconfigure(0, weight=1)

        self.center_column = ctk.CTkScrollableFrame(self.home_view, fg_color="transparent")
        self.center_column.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        self.hero_banner = ctk.CTkFrame(self.center_column, fg_color=("white", "#1E1E2E"), corner_radius=10)
        self.hero_banner.pack(fill="x", pady=(0, 10))

        self.hero_avatar_container = ctk.CTkFrame(self.hero_banner, width=64, height=64, corner_radius=32, fg_color=("gray90", "#2B2B3D"))
        self.hero_avatar_container.pack(side="right", padx=20, pady=15)
        self.hero_avatar_container.pack_propagate(False)

        self.lbl_hero_avatar = ctk.CTkLabel(self.hero_avatar_container, text="👤", font=("Poppins", 22), text_color=("gray40", "#AAAAAA"))
        self.lbl_hero_avatar.pack(expand=True)

        hero_text_box = ctk.CTkFrame(self.hero_banner, fg_color="transparent")
        hero_text_box.pack(side="left", fill="both", expand=True, padx=20, pady=15)

        self.lbl_hero_welcome = ctk.CTkLabel(
            hero_text_box, text=self.get_text("hero_welcome").format(name="Student"), font=("Poppins", 18, "bold"), text_color=("gray10", "#FFFFFF"), justify="left", wraplength=330
        )
        self.lbl_hero_welcome.pack(anchor="w")

        self.lbl_hero_sub = ctk.CTkLabel(
            hero_text_box, text=self.get_text("hero_sub"), font=("Poppins", 11), text_color=("gray50", "#AAAAAA"), justify="left", wraplength=330
        )
        self.lbl_hero_sub.pack(anchor="w", pady=(4, 0))

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

        self.card_notes_lbl, self.card_notes_val = self._create_stat_card(self.stats_container, self.get_text("stat_notes"), "0", "#3B82F6", 0)
        self.card_tasks_lbl, self.card_tasks_val = self._create_stat_card(self.stats_container, self.get_text("stat_tasks"), "0", "#10B981", 1)
        self.card_quiz_lbl, self.card_quiz_val   = self._create_stat_card(self.stats_container, self.get_text("stat_quiz"), "0%", "#F59E0B", 2)
        self.card_hours_lbl, self.card_hours_val = self._create_stat_card(self.stats_container, self.get_text("stat_hours"), "0 hrs", "#8B5CF6", 3)

        # --- RIGHT COLUMN ---
        self.right_column = ctk.CTkScrollableFrame(self.home_view, fg_color="transparent")
        self.right_column.grid(row=0, column=1, sticky="nsew")

        # Mini Calendar Widget
        self.mini_cal_card = ctk.CTkFrame(self.right_column, fg_color=("white", "#1E1E2E"), corner_radius=10)
        self.mini_cal_card.pack(fill="x", pady=(0, 10))

        cal_header = ctk.CTkFrame(self.mini_cal_card, fg_color="transparent")
        cal_header.pack(fill="x", padx=12, pady=(10, 4))
        self.lbl_cal_header = ctk.CTkLabel(cal_header, text=self.get_text("cal_header"), font=("Poppins", 11, "bold"), text_color=("gray10", "#FFFFFF"))
        self.lbl_cal_header.pack(side="left")

        self.cal_grid = ctk.CTkFrame(self.mini_cal_card, fg_color="transparent")
        self.cal_grid.pack(fill="x", padx=8, pady=(0, 10))
        self.render_mini_calendar()

        # Task Notifications & Upcoming Deadlines Feed
        self.notif_frame = ctk.CTkFrame(self.right_column, fg_color=("white", "#1E1E2E"), corner_radius=10)
        self.notif_frame.pack(fill="x", pady=(0, 10))

        up_head = ctk.CTkFrame(self.notif_frame, fg_color="transparent")
        up_head.pack(fill="x", padx=12, pady=(10, 4))
        self.lbl_deadline_header = ctk.CTkLabel(up_head, text=self.get_text("deadline_header"), font=("Poppins", 12, "bold"), text_color=("gray10", "#FFFFFF"))
        self.lbl_deadline_header.pack(side="left")
        
        self.btn_view_all = ctk.CTkButton(up_head, text=self.get_text("view_all"), width=60, height=22, fg_color="transparent", text_color="#3B82F6", command=self.nav_schedule)
        self.btn_view_all.pack(side="right")

        self.scroll_notifications = ctk.CTkFrame(self.notif_frame, fg_color="transparent")
        self.scroll_notifications.pack(fill="x", expand=True, padx=8, pady=(0, 10))

        # Recent Activity Feed
        self.activity_frame = ctk.CTkFrame(self.right_column, fg_color=("white", "#1E1E2E"), corner_radius=10)
        self.activity_frame.pack(fill="x")

        act_head = ctk.CTkFrame(self.activity_frame, fg_color="transparent")
        act_head.pack(fill="x", padx=12, pady=(10, 4))
        self.lbl_activity_header = ctk.CTkLabel(act_head, text=self.get_text("activity_header"), font=("Poppins", 12, "bold"), text_color=("gray10", "#FFFFFF"))
        self.lbl_activity_header.pack(side="left")

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

        self.show_sub_view("home")

    def get_text(self, key: str) -> str:
        lang = getattr(self.controller, "current_language", "English")
        return self.translations.get(lang, self.translations["English"]).get(key, key)

    def open_tutorial(self):
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

        title_lbl = ctk.CTkLabel(card, text=title, font=("Poppins", 10), text_color=("gray50", "#AAAAAA"), wraplength=90)
        title_lbl.pack(anchor="w", padx=10, pady=(10, 0))
        val_lbl = ctk.CTkLabel(card, text=initial_val, font=("Poppins", 15, "bold"), text_color=color)
        val_lbl.pack(anchor="w", padx=10, pady=(0, 10))
        return title_lbl, val_lbl

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
        
        profile = self.profile_logic.get_user_profile(user_id)
        if profile:
            if hasattr(self.controller, "current_user") and self.controller.current_user:
                self.controller.current_user.update(profile)

            name = profile.get("full_name", "Student")
            first_name = name.split()[0]
            self.lbl_hero_welcome.configure(text=self.get_text("hero_welcome").format(name=first_name))

            pic_path = profile.get("profile_pic_path")
            if pic_path and os.path.exists(pic_path):
                try:
                    pil_img = Image.open(pic_path)
                    ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(60, 60))
                    self.lbl_hero_avatar.configure(text="", image=ctk_img)
                    self.lbl_hero_avatar.image = ctk_img
                except Exception as e:
                    print(f"[DashboardView] Error loading avatar: {e}")
                    self.lbl_hero_avatar.configure(text="👤", image=None)
            else:
                self.lbl_hero_avatar.configure(text="👤", image=None)

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
                text=self.get_text("no_tasks"), 
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
            recent_items.append((self.get_text("tip_title"), self.get_text("tip_sub")))

        for title, sub in recent_items:
            act_card = ctk.CTkFrame(self.scroll_activity, fg_color=("gray95", "#2B2B3D"), corner_radius=6)
            act_card.pack(fill="x", pady=2, padx=2)
            ctk.CTkLabel(act_card, text=title, font=("Poppins", 10, "bold"), text_color=("gray10", "#FFFFFF")).pack(anchor="w", padx=8, pady=(4, 0))
            ctk.CTkLabel(act_card, text=sub, font=("Poppins", 9), text_color=("gray50", "#AAAAAA")).pack(anchor="w", padx=8, pady=(0, 4))
    
    def refresh_language(self):
        """Refreshes all labels, titles, buttons, and sub-views when language changes."""
        # Top Header
        self.welcome_label.configure(text=self.get_text("welcome_default"))
        self.btn_logout.configure(text=self.get_text("logout"))

        # Sidebar
        self.lbl_nav_title.configure(text=self.get_text("nav_header"))
        self.sidebar_buttons["home"].configure(text=self.get_text("nav_home"))
        self.sidebar_buttons["notes"].configure(text=self.get_text("nav_notes"))
        self.sidebar_buttons["quizzes"].configure(text=self.get_text("nav_quizzes"))
        self.sidebar_buttons["schedule"].configure(text=self.get_text("nav_schedule"))
        self.sidebar_buttons["progress"].configure(text=self.get_text("nav_progress"))
        self.sidebar_buttons["settings"].configure(text=self.get_text("nav_settings"))
        self.lbl_habit.configure(text=self.get_text("habit_text"))

        # Active Workspace Title
        title_map = {
            "home": "title_home",
            "notes": "title_notes",
            "profile": "title_profile",
            "quizzes": "title_quizzes",
            "schedule": "title_schedule",
            "progress": "title_progress",
            "settings": "title_settings"
        }
        self.content_title.configure(text=self.get_text(title_map.get(self.active_view_key, "title_home")))

        # Home View Elements
        self.lbl_hero_sub.configure(text=self.get_text("hero_sub"))
        self.card_notes_lbl.configure(text=self.get_text("stat_notes"))
        self.card_tasks_lbl.configure(text=self.get_text("stat_tasks"))
        self.card_quiz_lbl.configure(text=self.get_text("stat_quiz"))
        self.card_hours_lbl.configure(text=self.get_text("stat_hours"))
        self.lbl_cal_header.configure(text=self.get_text("cal_header"))
        self.lbl_deadline_header.configure(text=self.get_text("deadline_header"))
        self.btn_view_all.configure(text=self.get_text("view_all"))
        self.lbl_activity_header.configure(text=self.get_text("activity_header"))

        # Refresh home dashboard contents & broadcast to active sub-views
        if self.active_view_key == "home":
            self.refresh_home_dashboard()

        for sub_view in self.sub_views.values():
            if hasattr(sub_view, "refresh_language"):
                sub_view.refresh_language()

    def _get_user_id(self) -> int:
        if hasattr(self.controller, "current_user") and self.controller.current_user:
            return self.controller.current_user.get("id", 1)
        return 1

    # =============================================================
    # SUB-VIEW NAVIGATION SWITCHER
    # =============================================================
    def show_sub_view(self, key: str):
        self.active_view_key = key
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
        self.active_view_key = "home"
        self.content_title.configure(text=self.get_text("title_home"))
        self.show_sub_view("home")

    def nav_notes(self):
        self.active_view_key = "notes"
        self.content_title.configure(text=self.get_text("title_notes"))
        self.show_sub_view("notes")

    def nav_profile(self):
        self.active_view_key = "profile"
        self.content_title.configure(text=self.get_text("title_profile"))
        self.show_sub_view("profile")

    def nav_quizzes(self):
        self.active_view_key = "quizzes"
        self.content_title.configure(text=self.get_text("title_quizzes"))
        self.show_sub_view("quizzes")

    def nav_schedule(self):
        self.active_view_key = "schedule"
        self.content_title.configure(text=self.get_text("title_schedule"))
        self.show_sub_view("schedule")

    def nav_progress(self):
        self.active_view_key = "progress"
        self.content_title.configure(text=self.get_text("title_progress"))
        self.show_sub_view("progress")

    def nav_settings(self):
        self.active_view_key = "settings"
        self.content_title.configure(text=self.get_text("title_settings"))
        self.show_sub_view("settings")

    # =============================================================
    # CONTROLLER LIFECYCLE
    # =============================================================
    def on_show(self):
        user_id = self._get_user_id()
        profile = self.profile_logic.get_user_profile(user_id)
        if profile:
            if hasattr(self.controller, "current_user") and self.controller.current_user:
                self.controller.current_user.update(profile)

            name = profile.get("full_name", "Student")
            first_name = name.split()[0]
            self.lbl_hero_welcome.configure(text=self.get_text("hero_welcome").format(name=first_name))

        for key, frame in self.sub_views.items():
            if frame.winfo_ismapped():
                if key == "home":
                    self.refresh_home_dashboard()
                elif hasattr(frame, "on_show"):
                    frame.on_show()

    def handle_logout(self):
        self.controller.logout()