import calendar
import datetime
import customtkinter as ctk
from tkinter import messagebox
from logic.schedule import ScheduleManager


class ScheduleViewFrame(ctk.CTkFrame):
    """Schedule Workspace featuring Task Manager, Due Date Picker Calendar, and Study Planner."""

    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.schedule_logic = ScheduleManager()

        # Track active month and year for monthly calendar view
        today = datetime.date.today()
        self.current_year = today.year
        self.current_month = today.month
        self.selected_date_str = today.strftime("%Y-%m-%d")

        # Grid configuration: Left side = Calendar & Add Task, Right side = Task Cards List
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # =============================================================
        # LEFT PANEL: MONTHLY CALENDAR & TASK CREATION FORM
        # =============================================================
        self.left_panel = ctk.CTkFrame(self, corner_radius=10, fg_color="#1E1E2E")
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # 1. Calendar Navigation Header
        self.cal_header = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        self.cal_header.pack(fill="x", padx=15, pady=(15, 5))

        self.btn_prev_month = ctk.CTkButton(
            self.cal_header, text="◀", width=35, height=28, fg_color="#2B2B3D", command=self.prev_month
        )
        self.btn_prev_month.pack(side="left")

        self.lbl_month_year = ctk.CTkLabel(
            self.cal_header, text="", font=("Poppins", 15, "bold"), text_color="#FFFFFF"
        )
        self.lbl_month_year.pack(side="left", expand=True)

        self.btn_next_month = ctk.CTkButton(
            self.cal_header, text="▶", width=35, height=28, fg_color="#2B2B3D", command=self.next_month
        )
        self.btn_next_month.pack(side="right")

        # 2. Calendar Days Grid Container
        self.cal_grid_frame = ctk.CTkFrame(self.left_panel, fg_color="#2B2B3D", corner_radius=8)
        self.cal_grid_frame.pack(fill="x", padx=15, pady=8)

        # 3. Task Creation Form
        ctk.CTkLabel(
            self.left_panel, text="➕ Add New Task / Deadline", font=("Poppins", 14, "bold"), text_color="#FFFFFF"
        ).pack(anchor="w", padx=15, pady=(10, 5))

        # Selected Date Label Indicator
        self.lbl_selected_date = ctk.CTkLabel(
            self.left_panel, text=f"Due Date: {self.selected_date_str}", font=("Poppins", 11), text_color="#3B82F6"
        )
        self.lbl_selected_date.pack(anchor="w", padx=15, pady=(0, 5))

        self.entry_task_title = ctk.CTkEntry(self.left_panel, placeholder_text="Task Title (e.g., Submit Assignment)", height=32)
        self.entry_task_title.pack(fill="x", padx=15, pady=(0, 6))

        self.entry_task_desc = ctk.CTkEntry(self.left_panel, placeholder_text="Description / Notes", height=32)
        self.entry_task_desc.pack(fill="x", padx=15, pady=(0, 6))

        # Priority Selection
        self.priority_row = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        self.priority_row.pack(fill="x", padx=15, pady=(0, 8))

        ctk.CTkLabel(self.priority_row, text="Priority:", font=("Poppins", 11)).pack(side="left", padx=(0, 10))
        self.combo_priority = ctk.CTkOptionMenu(
            self.priority_row, 
            values=["Low", "Medium", "High"], 
            height=30, 
            fg_color="#2B2B3D", 
            button_color="#3B82F6"
        )
        self.combo_priority.set("Medium")
        self.combo_priority.pack(side="left", fill="x", expand=True)

        # Add Task Button
        self.btn_add_task = ctk.CTkButton(
            self.left_panel,
            text="📌 Save Task",
            font=("Poppins", 12, "bold"),
            fg_color="#10B981",
            hover_color="#059669",
            height=36,
            command=self.save_task
        )
        self.btn_add_task.pack(fill="x", padx=15, pady=(5, 15))

        # =============================================================
        # RIGHT PANEL: UPCOMING TASKS LIST & FILTER
        # =============================================================
        self.right_panel = ctk.CTkFrame(self, corner_radius=10, fg_color="#1E1E2E")
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        filter_row = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        filter_row.pack(fill="x", padx=15, pady=(15, 10))

        ctk.CTkLabel(
            filter_row, text="📋 Task Schedule", font=("Poppins", 16, "bold"), text_color="#FFFFFF"
        ).pack(side="left")

        self.combo_filter = ctk.CTkOptionMenu(
            filter_row,
            values=["All", "Pending", "In Progress", "Completed"],
            width=110,
            height=28,
            fg_color="#2B2B3D",
            button_color="#3B82F6",
            command=lambda val: self.load_tasks()
        )
        self.combo_filter.set("All")
        self.combo_filter.pack(side="right")

        self.scroll_tasks = ctk.CTkScrollableFrame(self.right_panel, fg_color="transparent")
        self.scroll_tasks.pack(fill="both", expand=True, padx=10, pady=10)

        # Render Calendar
        self.render_calendar()

    # =============================================================
    # CALENDAR RENDER & INTERACTION
    # =============================================================

    def _get_user_id(self) -> int:
        if hasattr(self.controller, "current_user") and self.controller.current_user:
            return self.controller.current_user.get("id", 1)
        return 1

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

    def render_calendar(self):
        """Builds monthly grid buttons for selecting due dates."""
        for widget in self.cal_grid_frame.winfo_children():
            widget.destroy()

        month_name = calendar.month_name[self.current_month]
        self.lbl_month_year.configure(text=f"{month_name} {self.current_year}")

        # Day Headers (Mon, Tue, Wed...)
        day_headers = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
        for col, day_str in enumerate(day_headers):
            lbl = ctk.CTkLabel(self.cal_grid_frame, text=day_str, font=("Poppins", 10, "bold"), text_color="#AAAAAA")
            lbl.grid(row=0, column=col, padx=4, pady=4)

        # Generate Days Matrix
        cal_matrix = calendar.monthcalendar(self.current_year, self.current_month)

        for row_idx, week in enumerate(cal_matrix, start=1):
            for col_idx, day_num in enumerate(week):
                if day_num != 0:
                    date_str = f"{self.current_year:04d}-{self.current_month:02d}-{day_num:02d}"
                    is_selected = (date_str == self.selected_date_str)

                    btn = ctk.CTkButton(
                        self.cal_grid_frame,
                        text=str(day_num),
                        width=32,
                        height=28,
                        corner_radius=6,
                        fg_color="#3B82F6" if is_selected else "transparent",
                        hover_color="#2563EB",
                        font=("Poppins", 10, "bold" if is_selected else "normal"),
                        command=lambda d=date_str: self.select_date(d)
                    )
                    btn.grid(row=row_idx, column=col_idx, padx=2, pady=2)

    def select_date(self, date_str: str):
        """Sets the selected due date from calendar click."""
        self.selected_date_str = date_str
        self.lbl_selected_date.configure(text=f"Due Date: {self.selected_date_str}")
        self.render_calendar()

    # =============================================================
    # TASK OPERATIONS & CARDS
    # =============================================================

    def save_task(self):
        """Reads form fields and logs a new task in database."""
        user_id = self._get_user_id()
        title = self.entry_task_title.get().strip()
        desc = self.entry_task_desc.get().strip()
        priority = self.combo_priority.get()

        if not title:
            messagebox.showwarning("Missing Title", "Please enter a title for the task.")
            return

        success, message = self.schedule_logic.create_task(
            user_id=user_id,
            title=title,
            description=desc,
            due_date=self.selected_date_str,
            priority=priority
        )

        if success:
            messagebox.showinfo("Success", message)
            self.entry_task_title.delete(0, "end")
            self.entry_task_desc.delete(0, "end")
            self.load_tasks()
        else:
            messagebox.showerror("Error", message)

    def load_tasks(self):
        """Fetches and builds UI task cards."""
        for widget in self.scroll_tasks.winfo_children():
            widget.destroy()

        user_id = self._get_user_id()
        status_filter = self.combo_filter.get()
        tasks = self.schedule_logic.get_user_tasks(user_id, status_filter=status_filter)

        if not tasks:
            ctk.CTkLabel(self.scroll_tasks, text="No tasks found for this filter.", text_color="#888888").pack(pady=20)
            return

        for task in tasks:
            card = ctk.CTkFrame(self.scroll_tasks, fg_color="#2B2B3D", corner_radius=8)
            card.pack(fill="x", pady=5, padx=5)

            # Priority Badge Color
            prio_colors = {"High": "#EF4444", "Medium": "#F59E0B", "Low": "#10B981"}
            p_color = prio_colors.get(task.get("priority"), "#3B82F6")

            # Header
            header = ctk.CTkFrame(card, fg_color="transparent")
            header.pack(fill="x", padx=10, pady=(8, 2))

            ctk.CTkLabel(header, text=task["title"], font=("Poppins", 13, "bold"), text_color="#FFFFFF").pack(side="left")
            ctk.CTkLabel(header, text=f"• {task['priority']}", font=("Poppins", 10, "bold"), text_color=p_color).pack(side="left", padx=5)

            # Due Date & Description
            ctk.CTkLabel(card, text=f"📅 Due: {task['due_date']}", font=("Poppins", 10), text_color="#AAAAAA").pack(anchor="w", padx=10)

            if task.get("description"):
                ctk.CTkLabel(card, text=task["description"], font=("Poppins", 11), text_color="#DDDDDD").pack(anchor="w", padx=10, pady=2)

            # Action Row (Status Dropdown & Delete Button)
            action_row = ctk.CTkFrame(card, fg_color="transparent")
            action_row.pack(fill="x", padx=10, pady=(5, 8))

            def make_status_updater(t_id):
                return lambda new_val: self.schedule_logic.update_task_status(t_id, new_val)

            status_menu = ctk.CTkOptionMenu(
                action_row,
                values=["Pending", "In Progress", "Completed"],
                width=110,
                height=26,
                font=("Poppins", 10),
                fg_color="#1E1E2E",
                button_color="#3B82F6",
                command=make_status_updater(task["id"])
            )
            status_menu.set(task.get("status", "Pending"))
            status_menu.pack(side="left")

            def make_deleter(t_id):
                def do_delete():
                    if messagebox.askyesno("Confirm Delete", "Delete this task?"):
                        self.schedule_logic.delete_task(t_id)
                        self.load_tasks()
                return do_delete

            ctk.CTkButton(
                action_row, text="🗑️ Delete", width=65, height=26, font=("Poppins", 10), fg_color="#EF4444", command=make_deleter(task["id"])
            ).pack(side="right")

    def on_show(self):
        """Lifecycle method triggered when workspace is shown."""
        self.load_tasks()