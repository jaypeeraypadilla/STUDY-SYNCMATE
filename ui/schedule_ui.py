import calendar
import datetime
import customtkinter as ctk
from tkinter import messagebox
from logic.schedule import ScheduleManager
from logic.quiz_generator import QuizGenerator


class ScheduleViewFrame(ctk.CTkFrame):
    """Schedule Workspace featuring 3-Panel Layout: Monthly Calendar, Daily Agenda, and Task Manager."""

    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.schedule_logic = ScheduleManager()
        self.quiz_logic = QuizGenerator()

        # Track active date and month
        today = datetime.date.today()
        self.current_year = today.year
        self.current_month = today.month
        self.selected_date_str = today.strftime("%Y-%m-%d")
        self.active_tab = "Calendar"

        # Grid configuration: 3 Columns matching layout structure
        self.grid_columnconfigure(0, weight=2)  # Column 0: Monthly Calendar / Panel View Switcher
        self.grid_columnconfigure(1, weight=2)  # Column 1: Daily Agenda / Schedule
        self.grid_columnconfigure(2, weight=2)  # Column 2: My Tasks Manager
        self.grid_rowconfigure(0, weight=1)

        # =============================================================
        # COLUMN 0: CALENDAR & PANEL VIEW SWITCHER PANEL
        # =============================================================
        self.cal_panel = ctk.CTkFrame(self, corner_radius=10, fg_color=("white", "#1E1E2E"))
        self.cal_panel.grid(row=0, column=0, sticky="nsew", padx=6, pady=10)
        self.cal_panel.grid_rowconfigure(2, weight=1)
        self.cal_panel.grid_columnconfigure(0, weight=1)

        # Top View Toggles (Calendar | Tasks)
        cal_top_nav = ctk.CTkFrame(self.cal_panel, fg_color="transparent")
        cal_top_nav.pack(fill="x", padx=12, pady=(12, 8))
        
        ctk.CTkLabel(cal_top_nav, text="Schedule", font=("Poppins", 16, "bold"), text_color=("gray10", "#FFFFFF")).pack(side="left")
        
        toggle_frame = ctk.CTkFrame(cal_top_nav, fg_color=("gray90", "#2B2B3D"), corner_radius=6)
        toggle_frame.pack(side="right")
        
        self.btn_tab_cal = ctk.CTkButton(toggle_frame, text="CALENDAR", width=75, height=24, font=("Poppins", 9, "bold"), fg_color="#3B82F6", command=lambda: self.switch_tab("Calendar"))
        self.btn_tab_cal.pack(side="left", padx=2, pady=2)
        
        self.btn_tab_tsk = ctk.CTkButton(toggle_frame, text="TASKS", width=65, height=24, font=("Poppins", 9, "bold"), fg_color="transparent", text_color=("gray50", "#AAAAAA"), command=lambda: self.switch_tab("Tasks"))
        self.btn_tab_tsk.pack(side="right", padx=2, pady=2)

        # --- SUB-CONTAINER A: CALENDAR VIEW ---
        self.calendar_view_container = ctk.CTkFrame(self.cal_panel, fg_color="transparent")
        self.calendar_view_container.pack(fill="both", expand=True, padx=0, pady=0)

        # Month Navigation Header
        self.cal_header = ctk.CTkFrame(self.calendar_view_container, fg_color="transparent")
        self.cal_header.pack(fill="x", padx=12, pady=(5, 8))

        self.btn_prev_month = ctk.CTkButton(self.cal_header, text="◀", width=30, height=26, fg_color=("gray90", "#2B2B3D"), text_color=("gray10", "#FFFFFF"), command=self.prev_month)
        self.btn_prev_month.pack(side="left")

        self.lbl_month_year = ctk.CTkLabel(self.cal_header, text="", font=("Poppins", 13, "bold"), text_color=("gray10", "#FFFFFF"))
        self.lbl_month_year.pack(side="left", expand=True)

        self.btn_next_month = ctk.CTkButton(self.cal_header, text="▶", width=30, height=26, fg_color=("gray90", "#2B2B3D"), text_color=("gray10", "#FFFFFF"), command=self.next_month)
        self.btn_next_month.pack(side="right")

        # Calendar Days Grid Container
        self.cal_grid_frame = ctk.CTkFrame(self.calendar_view_container, fg_color=("gray95", "#2B2B3D"), corner_radius=8)
        self.cal_grid_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        # --- SUB-CONTAINER B: CONNECTED TASKS QUICK VIEW ---
        self.tasks_view_container = ctk.CTkFrame(self.cal_panel, fg_color="transparent")
        
        ctk.CTkLabel(
            self.tasks_view_container, text="📌 All Deadlines & Overview", font=("Poppins", 12, "bold"), text_color=("gray10", "#FFFFFF")
        ).pack(anchor="w", padx=12, pady=(5, 8))

        self.scroll_panel_tasks = ctk.CTkScrollableFrame(self.tasks_view_container, fg_color=("gray95", "#2B2B3D"), corner_radius=8)
        self.scroll_panel_tasks.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        # =============================================================
        # COLUMN 1: DAILY AGENDA / SCHEDULE PANEL
        # =============================================================
        self.agenda_panel = ctk.CTkFrame(self, corner_radius=10, fg_color=("white", "#1E1E2E"))
        self.agenda_panel.grid(row=0, column=1, sticky="nsew", padx=6, pady=10)
        self.agenda_panel.grid_rowconfigure(2, weight=1)
        self.agenda_panel.grid_columnconfigure(0, weight=1)

        agenda_top_bar = ctk.CTkFrame(self.agenda_panel, fg_color="transparent")
        agenda_top_bar.pack(fill="x", padx=12, pady=(12, 8))

        self.lbl_agenda_date = ctk.CTkLabel(agenda_top_bar, text="Today", font=("Poppins", 13, "bold"), text_color=("gray10", "#FFFFFF"))
        self.lbl_agenda_date.pack(side="left")

        ctk.CTkButton(agenda_top_bar, text="TODAY", width=60, height=24, font=("Poppins", 9, "bold"), fg_color="#3B82F6", command=self.go_to_today).pack(side="right")

        self.scroll_agenda = ctk.CTkScrollableFrame(self.agenda_panel, fg_color="transparent")
        self.scroll_agenda.pack(fill="both", expand=True, padx=8, pady=(0, 10))

        bottom_action_row = ctk.CTkFrame(self.agenda_panel, fg_color="transparent")
        bottom_action_row.pack(fill="x", padx=12, pady=(0, 12))
        
        ctk.CTkButton(
            bottom_action_row, 
            text="＋ Log Study Session", 
            font=("Poppins", 11, "bold"), 
            fg_color="#10B981", 
            hover_color="#059669",
            height=32,
            command=self.open_log_session_dialog
        ).pack(side="right")

        # =============================================================
        # COLUMN 2: MY TASKS PANEL
        # =============================================================
        self.tasks_panel = ctk.CTkFrame(self, corner_radius=10, fg_color=("white", "#1E1E2E"))
        self.tasks_panel.grid(row=0, column=2, sticky="nsew", padx=6, pady=10)
        self.tasks_panel.grid_rowconfigure(2, weight=1)
        self.tasks_panel.grid_columnconfigure(0, weight=1)

        tasks_top_bar = ctk.CTkFrame(self.tasks_panel, fg_color="transparent")
        tasks_top_bar.pack(fill="x", padx=12, pady=(12, 6))

        ctk.CTkLabel(tasks_top_bar, text="My Tasks", font=("Poppins", 14, "bold"), text_color=("gray10", "#FFFFFF")).pack(side="left")

        pills_row = ctk.CTkFrame(self.tasks_panel, fg_color="transparent")
        pills_row.pack(fill="x", padx=12, pady=(0, 8))

        self.task_filter_var = ctk.StringVar(value="All")
        for f_val in ["All", "Pending", "Completed"]:
            btn = ctk.CTkButton(
                pills_row,
                text=f_val.upper(),
                font=("Poppins", 9, "bold"),
                width=65,
                height=24,
                fg_color="#3B82F6" if f_val == "All" else ("gray90", "#2B2B3D"),
                text_color="white" if f_val == "All" else ("gray50", "#AAAAAA"),
                command=lambda val=f_val: self.set_task_filter(val)
            )
            btn.pack(side="left", padx=2)
            setattr(self, f"btn_pill_{f_val.lower()}", btn)

        self.scroll_tasks = ctk.CTkScrollableFrame(self.tasks_panel, fg_color="transparent")
        self.scroll_tasks.pack(fill="both", expand=True, padx=8, pady=(0, 10))

        quick_task_frame = ctk.CTkFrame(self.tasks_panel, fg_color=("gray95", "#2B2B3D"), corner_radius=8)
        quick_task_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.entry_quick_title = ctk.CTkEntry(quick_task_frame, placeholder_text="New Task Title...", height=28, font=("Poppins", 10), fg_color=("white", "#3A3A3A"), text_color=("gray10", "#FFFFFF"))
        self.entry_quick_title.pack(fill="x", padx=8, pady=(8, 4))

        quick_sub_row = ctk.CTkFrame(quick_task_frame, fg_color="transparent")
        quick_sub_row.pack(fill="x", padx=8, pady=(0, 8))

        self.combo_quick_priority = ctk.CTkOptionMenu(quick_sub_row, values=["High", "Medium", "Low"], width=90, height=24, font=("Poppins", 9), fg_color=("gray85", "#1E1E2E"), text_color=("gray10", "#FFFFFF"))
        self.combo_quick_priority.set("Medium")
        self.combo_quick_priority.pack(side="left")

        ctk.CTkButton(
            quick_sub_row, text="Add Task", width=70, height=24, font=("Poppins", 9, "bold"), fg_color="#10B981", command=self.save_quick_task
        ).pack(side="right")

        self.select_date(self.selected_date_str)

    def _get_user_id(self) -> int:
        if hasattr(self.controller, "current_user") and self.controller.current_user:
            return self.controller.current_user.get("id", 1)
        return 1

    def switch_tab(self, tab_name: str):
        self.active_tab = tab_name
        if tab_name == "Calendar":
            self.btn_tab_cal.configure(fg_color="#3B82F6", text_color="white")
            self.btn_tab_tsk.configure(fg_color="transparent", text_color=("gray50", "#AAAAAA"))
            self.tasks_view_container.pack_forget()
            self.calendar_view_container.pack(fill="both", expand=True, padx=0, pady=0)
        else:
            self.btn_tab_tsk.configure(fg_color="#3B82F6", text_color="white")
            self.btn_tab_cal.configure(fg_color="transparent", text_color=("gray50", "#AAAAAA"))
            self.calendar_view_container.pack_forget()
            self.tasks_view_container.pack(fill="both", expand=True, padx=0, pady=0)
            self.render_panel_tasks_overview()

    def prev_month(self):
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        self.render_calendar()

    def next_month(self):
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        self.render_calendar()

    def go_to_today(self):
        today = datetime.date.today()
        self.current_year = today.year
        self.current_month = today.month
        self.select_date(today.strftime("%Y-%m-%d"))

    def render_calendar(self):
        for widget in self.cal_grid_frame.winfo_children():
            widget.destroy()

        month_name = calendar.month_name[self.current_month]
        self.lbl_month_year.configure(text=f"{month_name} {self.current_year}")

        day_headers = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"]
        for col, h in enumerate(day_headers):
            ctk.CTkLabel(self.cal_grid_frame, text=h, font=("Poppins", 9, "bold"), text_color=("gray50", "#888888")).grid(row=0, column=col, padx=2, pady=2)

        user_id = self._get_user_id()
        task_dates = set(self.schedule_logic.get_task_dates_for_month(user_id, self.current_year, self.current_month))

        cal_matrix = calendar.monthcalendar(self.current_year, self.current_month)
        for row_idx, week in enumerate(cal_matrix, start=1):
            for col_idx, day_num in enumerate(week):
                if day_num != 0:
                    date_str = f"{self.current_year:04d}-{self.current_month:02d}-{day_num:02d}"
                    is_selected = (date_str == self.selected_date_str)
                    has_tasks = date_str in task_dates

                    btn_text = f"{day_num} •" if has_tasks else str(day_num)
                    btn_color = "#3B82F6" if is_selected else (("gray85", "#2B2B3D") if has_tasks else "transparent")

                    btn = ctk.CTkButton(
                        self.cal_grid_frame,
                        text=btn_text,
                        width=30,
                        height=28,
                        corner_radius=6,
                        fg_color=btn_color,
                        hover_color="#2563EB",
                        font=("Poppins", 10, "bold" if is_selected or has_tasks else "normal"),
                        text_color="white" if is_selected or has_tasks else ("gray10", "#DDDDDD"),
                        command=lambda d=date_str: self.select_date(d)
                    )
                    btn.grid(row=row_idx, column=col_idx, padx=1, pady=1)

    def select_date(self, date_str: str):
        self.selected_date_str = date_str
        try:
            dt = datetime.datetime.strptime(date_str, "%Y-%m-%d")
            self.lbl_agenda_date.configure(text=dt.strftime("%B %d, %Y"))
        except Exception:
            self.lbl_agenda_date.configure(text=date_str)
        self.render_calendar()
        self.render_daily_agenda()
        self.load_tasks()
        if self.active_tab == "Tasks":
            self.render_panel_tasks_overview()

    def render_daily_agenda(self):
        for widget in self.scroll_agenda.winfo_children():
            widget.destroy()

        user_id = self._get_user_id()
        all_tasks = self.schedule_logic.get_user_tasks(user_id)
        day_tasks = [t for t in all_tasks if t.get("due_date") == self.selected_date_str]

        if not day_tasks:
            ctk.CTkLabel(self.scroll_agenda, text=f"No deadlines for {self.selected_date_str}.", text_color=("gray50", "#888888"), font=("Poppins", 10), wraplength=180).pack(pady=20)
            return

        for task in day_tasks:
            card = ctk.CTkFrame(self.scroll_agenda, fg_color=("gray95", "#2B2B3D"), corner_radius=8)
            card.pack(fill="x", pady=4, padx=2)

            top_row = ctk.CTkFrame(card, fg_color="transparent")
            top_row.pack(fill="x", padx=8, pady=(6, 2))

            prio = task.get("priority", "Medium")
            prio_color = {"High": "#EF4444", "Medium": "#F59E0B", "Low": "#10B981"}.get(prio, "#3B82F6")

            ctk.CTkLabel(top_row, text=f"📌 {prio} Priority", font=("Poppins", 9, "bold"), text_color=prio_color).pack(side="left")
            
            # Display due time visibly in the agenda
            due_time = task.get("due_time", "12:00")
            ctk.CTkLabel(top_row, text=f"🕒 {due_time}", font=("Poppins", 9, "bold"), text_color="#3B82F6").pack(side="right")

            ctk.CTkLabel(card, text=task["title"], font=("Poppins", 11, "bold"), text_color=("gray10", "#FFFFFF")).pack(anchor="w", padx=8)
            
            if task.get("description"):
                ctk.CTkLabel(card, text=task["description"], font=("Poppins", 10), text_color=("gray50", "#AAAAAA")).pack(anchor="w", padx=8, pady=(0, 6))

    def render_panel_tasks_overview(self):
        for widget in self.scroll_panel_tasks.winfo_children():
            widget.destroy()

        user_id = self._get_user_id()
        all_tasks = self.schedule_logic.get_user_tasks(user_id)

        if not all_tasks:
            ctk.CTkLabel(self.scroll_panel_tasks, text="No tasks recorded yet.", text_color=("gray50", "#888888"), font=("Poppins", 10)).pack(pady=20)
            return

        for task in all_tasks:
            card = ctk.CTkFrame(self.scroll_panel_tasks, fg_color=("white", "#1E1E2E"), corner_radius=6)
            card.pack(fill="x", pady=3, padx=2)

            row = ctk.CTkFrame(card, fg_color="transparent")
            row.pack(fill="x", padx=6, pady=6)

            is_completed = task.get("status") == "Completed"
            status_icon = "☑" if is_completed else "☐"

            ctk.CTkLabel(row, text=status_icon, font=("Poppins", 11), text_color="#10B981" if is_completed else ("gray50", "#AAAAAA")).pack(side="left", padx=(0, 6))
            
            info = ctk.CTkFrame(row, fg_color="transparent")
            info.pack(side="left", fill="x", expand=True)

            ctk.CTkLabel(info, text=task["title"], font=("Poppins", 10, "bold"), text_color=("gray10", "#FFFFFF"), anchor="w").pack(anchor="w")
            
            due_time = task.get("due_time", "12:00")
            ctk.CTkLabel(info, text=f"Due: {task['due_date']} at {due_time}", font=("Poppins", 8), text_color=("gray50", "#AAAAAA"), anchor="w").pack(anchor="w")

    def open_log_session_dialog(self):
        """Opens a theme-responsive modal dialog to log study sessions."""
        user_id = self._get_user_id()
        subjects = self.quiz_logic.get_available_subjects(user_id)
        if not subjects:
            subjects = ["ITE 260", "ITE 366", "GEN 006", "General Study"]

        dialog = ctk.CTkToplevel(self)
        dialog.title("Log Study Session")
        dialog.geometry("320x280")
        dialog.resizable(False, False)
        dialog.grab_set()

        dialog.configure(fg_color=("white", "#1E1E2E"))
        dialog.update_idletasks()

        ctk.CTkLabel(
            dialog, text="📖 Log Study Session", font=("Poppins", 14, "bold"), text_color=("gray10", "#FFFFFF")
        ).pack(pady=(15, 10))

        ctk.CTkLabel(dialog, text="Subject / Course:", font=("Poppins", 11), text_color=("gray50", "#AAAAAA")).pack(anchor="w", padx=20)
        combo_subject = ctk.CTkOptionMenu(
            dialog, 
            values=subjects, 
            height=32,
            fg_color=("gray85", "#2B2B3D"), 
            button_color="#3B82F6",
            text_color=("gray10", "#FFFFFF")
        )
        combo_subject.set(subjects[0])
        combo_subject.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkLabel(dialog, text="Duration (Minutes):", font=("Poppins", 11), text_color=("gray50", "#AAAAAA")).pack(anchor="w", padx=20)
        entry_duration = ctk.CTkEntry(
            dialog, placeholder_text="e.g., 60", height=32, font=("Poppins", 11),
            fg_color=("gray90", "#3A3A3A"), text_color=("gray10", "#FFFFFF")
        )
        entry_duration.insert(0, "60")
        entry_duration.pack(fill="x", padx=20, pady=(0, 15))

        def submit_session():
            subject = combo_subject.get().strip()
            duration_str = entry_duration.get().strip()

            if not subject:
                messagebox.showwarning("Missing Field", "Please select or provide a study subject.", parent=dialog)
                return

            if not duration_str.isdigit() or int(duration_str) <= 0:
                messagebox.showwarning("Invalid Input", "Please enter a valid positive number for duration in minutes.", parent=dialog)
                return

            duration_minutes = int(duration_str)

            success, msg = self.schedule_logic.log_study_session(user_id, subject=subject, duration_minutes=duration_minutes)
            if success:
                messagebox.showinfo("Success", f"Successfully logged {duration_minutes} minutes for '{subject}'!", parent=dialog)
                dialog.destroy()
                self.render_daily_agenda()
                
                if hasattr(self.controller, "frames") and "ProgressViewFrame" in self.controller.frames:
                    self.controller.frames["ProgressViewFrame"].load_progress_data()
            else:
                messagebox.showerror("Error", msg, parent=dialog)

        ctk.CTkButton(
            dialog, text="Save Session", font=("Poppins", 11, "bold"),
            fg_color="#10B981", hover_color="#059669", height=35,
            command=submit_session
        ).pack(fill="x", padx=20, pady=(5, 15))

    def open_edit_task_dialog(self, task: dict):
        """Opens a theme-responsive modal dialog to edit an existing task including its due time."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Edit Task")
        dialog.geometry("340x450")
        dialog.resizable(False, False)
        dialog.grab_set()

        dialog.configure(fg_color=("white", "#1E1E2E"))

        ctk.CTkLabel(
            dialog, text="✏️ Edit Task", font=("Poppins", 14, "bold"), text_color=("gray10", "#FFFFFF")
        ).pack(pady=(15, 10))

        # Title
        ctk.CTkLabel(dialog, text="Task Title:", font=("Poppins", 11), text_color=("gray50", "#AAAAAA")).pack(anchor="w", padx=20)
        entry_title = ctk.CTkEntry(
            dialog, height=32, font=("Poppins", 11),
            fg_color=("gray90", "#3A3A3A"), text_color=("gray10", "#FFFFFF")
        )
        entry_title.insert(0, task.get("title", ""))
        entry_title.pack(fill="x", padx=20, pady=(0, 8))

        # Description
        ctk.CTkLabel(dialog, text="Description:", font=("Poppins", 11), text_color=("gray50", "#AAAAAA")).pack(anchor="w", padx=20)
        entry_desc = ctk.CTkEntry(
            dialog, height=32, font=("Poppins", 11),
            fg_color=("gray90", "#3A3A3A"), text_color=("gray10", "#FFFFFF")
        )
        entry_desc.insert(0, task.get("description", ""))
        entry_desc.pack(fill="x", padx=20, pady=(0, 8))

        # Due Date
        ctk.CTkLabel(dialog, text="Due Date (YYYY-MM-DD):", font=("Poppins", 11), text_color=("gray50", "#AAAAAA")).pack(anchor="w", padx=20)
        entry_date = ctk.CTkEntry(
            dialog, height=32, font=("Poppins", 11),
            fg_color=("gray90", "#3A3A3A"), text_color=("gray10", "#FFFFFF")
        )
        entry_date.insert(0, task.get("due_date", ""))
        entry_date.pack(fill="x", padx=20, pady=(0, 8))

        # Due Time
        ctk.CTkLabel(dialog, text="Due Time (HH:MM - 24hr):", font=("Poppins", 11), text_color=("gray50", "#AAAAAA")).pack(anchor="w", padx=20)
        entry_time = ctk.CTkEntry(
            dialog, height=32, font=("Poppins", 11),
            fg_color=("gray90", "#3A3A3A"), text_color=("gray10", "#FFFFFF")
        )
        entry_time.insert(0, task.get("due_time", "12:00"))
        entry_time.pack(fill="x", padx=20, pady=(0, 8))

        # Priority
        ctk.CTkLabel(dialog, text="Priority:", font=("Poppins", 11), text_color=("gray50", "#AAAAAA")).pack(anchor="w", padx=20)
        combo_priority = ctk.CTkOptionMenu(
            dialog, values=["High", "Medium", "Low"], height=32,
            fg_color=("gray85", "#2B2B3D"), button_color="#3B82F6", text_color=("gray10", "#FFFFFF")
        )
        combo_priority.set(task.get("priority", "Medium"))
        combo_priority.pack(fill="x", padx=20, pady=(0, 15))

        def save_edits():
            new_title = entry_title.get().strip()
            new_desc = entry_desc.get().strip()
            new_date = entry_date.get().strip()
            new_time = entry_time.get().strip()
            new_priority = combo_priority.get()

            if not new_title:
                messagebox.showwarning("Missing Title", "Task title cannot be empty.", parent=dialog)
                return

            if not new_date:
                messagebox.showwarning("Missing Date", "Due date is required.", parent=dialog)
                return

            try:
                datetime.datetime.strptime(new_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showwarning("Invalid Date Format", "Please use YYYY-MM-DD format for the due date.", parent=dialog)
                return

            if not new_time:
                new_time = "12:00"
            try:
                datetime.datetime.strptime(new_time, "%H:%M")
            except ValueError:
                messagebox.showwarning("Invalid Time Format", "Please use HH:MM format (e.g., 14:30).", parent=dialog)
                return

            success, msg = self.schedule_logic.update_task(
                task_id=task["id"],
                title=new_title,
                description=new_desc,
                due_date=new_date,
                due_time=new_time,
                priority=new_priority
            )

            if success:
                messagebox.showinfo("Success", msg, parent=dialog)
                dialog.destroy()
                self.load_tasks()
                self.render_daily_agenda()
                self.render_calendar()
                if self.active_tab == "Tasks":
                    self.render_panel_tasks_overview()
            else:
                messagebox.showerror("Error", msg, parent=dialog)

        ctk.CTkButton(
            dialog, text="Save Changes", font=("Poppins", 11, "bold"),
            fg_color="#10B981", hover_color="#059669", height=35,
            command=save_edits
        ).pack(fill="x", padx=20, pady=(5, 15))

    def set_task_filter(self, filter_name: str):
        self.task_filter_var.set(filter_name)
        for f_val in ["All", "Pending", "Completed"]:
            btn = getattr(self, f"btn_pill_{f_val.lower()}")
            if f_val == filter_name:
                btn.configure(fg_color="#3B82F6", text_color="white")
            else:
                btn.configure(fg_color=("gray90", "#2B2B3D"), text_color=("gray50", "#AAAAAA"))
        self.load_tasks()

    def save_quick_task(self):
        user_id = self._get_user_id()
        title = self.entry_quick_title.get().strip()
        priority = self.combo_quick_priority.get()

        if not title:
            messagebox.showwarning("Missing Title", "Please enter a task title.")
            return

        success, message = self.schedule_logic.create_task(
            user_id=user_id,
            title=title,
            description="",
            due_date=self.selected_date_str,
            priority=priority
        )

        if success:
            self.entry_quick_title.delete(0, "end")
            self.load_tasks()
            self.render_daily_agenda()
            self.render_calendar()
            if self.active_tab == "Tasks":
                self.render_panel_tasks_overview()
        else:
            messagebox.showerror("Error", message)

    def load_tasks(self):
        for widget in self.scroll_tasks.winfo_children():
            widget.destroy()

        user_id = self._get_user_id()
        filter_val = self.task_filter_var.get()
        status_map = {"All": None, "Pending": "Pending", "Completed": "Completed"}
        
        tasks = self.schedule_logic.get_user_tasks(user_id, status_filter=status_map.get(filter_val))

        if not tasks:
            ctk.CTkLabel(self.scroll_tasks, text="No tasks found.", text_color=("gray50", "#888888"), font=("Poppins", 10)).pack(pady=20)
            return

        for task in tasks:
            card = ctk.CTkFrame(self.scroll_tasks, fg_color=("gray95", "#2B2B3D"), corner_radius=8)
            card.pack(fill="x", pady=4, padx=2)

            row = ctk.CTkFrame(card, fg_color="transparent")
            row.pack(fill="x", padx=8, pady=8)

            is_completed = task.get("status") == "Completed"
            
            chk_btn = ctk.CTkButton(
                row,
                text="☑" if is_completed else "☐",
                width=24,
                height=24,
                font=("Poppins", 12),
                fg_color="transparent",
                text_color="#10B981" if is_completed else ("gray50", "#AAAAAA"),
                command=lambda t_id=task["id"], current_status=task.get("status", "Pending"): self.toggle_task_completion(t_id, current_status)
            )
            chk_btn.pack(side="left", padx=(0, 6))

            info_frame = ctk.CTkFrame(row, fg_color="transparent")
            info_frame.pack(side="left", fill="x", expand=True)

            ctk.CTkLabel(info_frame, text=task["title"], font=("Poppins", 11, "bold"), text_color=("gray10", "#FFFFFF"), anchor="w").pack(anchor="w")
            
            due_time = task.get("due_time", "12:00")
            ctk.CTkLabel(info_frame, text=f"Due {task['due_date']} at {due_time}", font=("Poppins", 9), text_color=("gray50", "#AAAAAA"), anchor="w").pack(anchor="w")

            prio = task.get("priority", "Medium")
            prio_color = {"High": "#EF4444", "Medium": "#F59E0B", "Low": "#10B981"}.get(prio, "#3B82F6")
            ctk.CTkLabel(row, text=prio, font=("Poppins", 9, "bold"), text_color=prio_color).pack(side="right", padx=4)

            def make_deleter(t_id):
                return lambda: self.delete_task(t_id)

            del_btn = ctk.CTkButton(
                row, text="🗑️", width=26, height=24, font=("Poppins", 10),
                fg_color="transparent", hover_color="#EF4444", text_color=("gray50", "#AAAAAA"),
                command=make_deleter(task["id"])
            )
            del_btn.pack(side="right", padx=2)

            def make_editor(t_data):
                return lambda: self.open_edit_task_dialog(t_data)

            edit_btn = ctk.CTkButton(
                row, text="✏️", width=26, height=24, font=("Poppins", 10),
                fg_color="transparent", hover_color="#3B82F6", text_color=("gray50", "#AAAAAA"),
                command=make_editor(task)
            )
            edit_btn.pack(side="right", padx=2)

    def toggle_task_completion(self, task_id: int, current_status: str):
        new_status = "Pending" if current_status == "Completed" else "Completed"
        self.schedule_logic.update_task_status(task_id, new_status)
        self.load_tasks()
        self.render_daily_agenda()
        self.render_calendar()
        if self.active_tab == "Tasks":
            self.render_panel_tasks_overview()

    def delete_task(self, task_id: int):
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this task?"):
            self.schedule_logic.delete_task(task_id)
            self.load_tasks()
            self.render_daily_agenda()
            self.render_calendar()
            if self.active_tab == "Tasks":
                self.render_panel_tasks_overview()

    def on_show(self):
        self.load_tasks()
        self.render_daily_agenda()
        self.render_calendar()