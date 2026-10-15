import customtkinter as ctk
from logic.progress import ProgressTracker


class ProgressViewFrame(ctk.CTkFrame):
    """Progress & Analytics Workspace featuring Monthly Challenges, Subject Notes, Quiz Scores, and Completed Tasks."""

    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.progress_logic = ProgressTracker()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # =============================================================
        # TOP SUMMARY METRICS BAR
        # =============================================================
        self.metrics_frame = ctk.CTkFrame(self, fg_color="transparent", height=90)
        self.metrics_frame.pack(fill="x", padx=10, pady=(5, 10))
        self.metrics_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.card_notes = self._create_metric_card(self.metrics_frame, "Saved Notes", "0", "#3B82F6", 0)
        self.card_tasks = self._create_metric_card(self.metrics_frame, "Completed Tasks", "0", "#10B981", 1)
        self.card_quiz = self._create_metric_card(self.metrics_frame, "Avg Quiz Score", "0%", "#F59E0B", 2)
        self.card_hours = self._create_metric_card(self.metrics_frame, "Study Hours", "0 hrs", "#8B5CF6", 3)

        # =============================================================
        # MAIN SCROLLABLE CONTENT AREA (4 SECTIONS)
        # =============================================================
        self.scroll_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_container.pack(fill="both", expand=True, padx=10, pady=5)

        # SECTION 1: MONTHLY PRODUCTIVITY CHALLENGES
        self.build_badges_section()

        # SECTION 2: NOTES PER SUBJECT (DROPDOWN WITH NUMBER INDICATOR)
        self.build_notes_section()

        # SECTION 3: QUIZ GENERATOR SCORES & HISTORY
        self.build_quiz_section()

        # SECTION 4: COMPLETED TASKS LIST
        self.build_tasks_section()

    def _create_metric_card(self, parent, title, initial_val, color, col_idx):
        card = ctk.CTkFrame(parent, fg_color="#1E1E2E", corner_radius=10, height=80)
        card.grid(row=0, column=col_idx, sticky="nsew", padx=6)
        card.pack_propagate(False)

        ctk.CTkLabel(card, text=title, font=("Poppins", 11), text_color="#AAAAAA").pack(anchor="w", padx=12, pady=(10, 0))
        val_lbl = ctk.CTkLabel(card, text=initial_val, font=("Poppins", 16, "bold"), text_color=color)
        val_lbl.pack(anchor="w", padx=12)
        return val_lbl

    def _get_user_id(self) -> int:
        if hasattr(self.controller, "current_user") and self.controller.current_user:
            return self.controller.current_user.get("id", 1)
        return 1

    # =============================================================
    # SECTION BUILDERS
    # =============================================================

    def build_badges_section(self):
        """Section 1: Monthly Productivity Challenges Grid."""
        self.sec_badges_frame = ctk.CTkFrame(self.scroll_container, fg_color="#1E1E2E", corner_radius=10)
        self.sec_badges_frame.pack(fill="x", padx=5, pady=8)

        ctk.CTkLabel(
            self.sec_badges_frame, text="🏆 Monthly Productivity Challenges", font=("Poppins", 15, "bold"), text_color="#FFFFFF"
        ).pack(anchor="w", padx=20, pady=(15, 5))

        self.sec_badges_content = ctk.CTkFrame(self.sec_badges_frame, fg_color="transparent")
        self.sec_badges_content.pack(fill="x", padx=15, pady=(0, 15))
        self.sec_badges_content.grid_columnconfigure((0, 1), weight=1)

    def build_notes_section(self):
        """Section 2: Subject notes breakdown with count indicator and topic dropdown."""
        self.sec1_frame = ctk.CTkFrame(self.scroll_container, fg_color="#1E1E2E", corner_radius=10)
        self.sec1_frame.pack(fill="x", padx=5, pady=8)

        ctk.CTkLabel(
            self.sec1_frame, text="📚 Notes Library per Subject", font=("Poppins", 15, "bold"), text_color="#FFFFFF"
        ).pack(anchor="w", padx=20, pady=(15, 5))

        self.sec1_content = ctk.CTkFrame(self.sec1_frame, fg_color="transparent")
        self.sec1_content.pack(fill="x", padx=15, pady=(0, 15))

    def build_quiz_section(self):
        """Section 3: Quiz Generator Scores History."""
        self.sec2_frame = ctk.CTkFrame(self.scroll_container, fg_color="#1E1E2E", corner_radius=10)
        self.sec2_frame.pack(fill="x", padx=5, pady=8)

        ctk.CTkLabel(
            self.sec2_frame, text="🧠 Quiz Performance & Scores History", font=("Poppins", 15, "bold"), text_color="#FFFFFF"
        ).pack(anchor="w", padx=20, pady=(15, 5))

        self.sec2_content = ctk.CTkFrame(self.sec2_frame, fg_color="transparent")
        self.sec2_content.pack(fill="x", padx=15, pady=(0, 15))

    def build_tasks_section(self):
        """Section 4: Completed Tasks List."""
        self.sec3_frame = ctk.CTkFrame(self.scroll_container, fg_color="#1E1E2E", corner_radius=10)
        self.sec3_frame.pack(fill="x", padx=5, pady=8)

        ctk.CTkLabel(
            self.sec3_frame, text="✅ Completed Tasks Archive", font=("Poppins", 15, "bold"), text_color="#FFFFFF"
        ).pack(anchor="w", padx=20, pady=(15, 5))

        self.sec3_content = ctk.CTkFrame(self.sec3_frame, fg_color="transparent")
        self.sec3_content.pack(fill="x", padx=15, pady=(0, 15))

    # =============================================================
    # DATA REFRESH & BINDING
    # =============================================================

    def load_progress_data(self):
        user_id = self._get_user_id()
        summary = self.progress_logic.get_progress_summary(user_id)

        # Update Top Metrics
        self.card_notes.configure(text=str(summary["total_notes"]))
        self.card_tasks.configure(text=str(summary["completed_tasks_count"]))
        self.card_quiz.configure(text=summary["avg_quiz_score"])
        self.card_hours.configure(text=f"{summary['total_study_hours']} hrs")

        # 1. Populate Monthly Challenges Grid
        for widget in self.sec_badges_content.winfo_children():
            widget.destroy()

        badges = self.progress_logic.get_task_badges(user_id)
        for idx, badge in enumerate(badges):
            row = idx // 2
            col = idx % 2

            badge_card = ctk.CTkFrame(self.sec_badges_content, fg_color="#2B2B3D", corner_radius=8)
            badge_card.grid(row=row, column=col, sticky="nsew", padx=6, pady=6)

            header_f = ctk.CTkFrame(badge_card, fg_color="transparent")
            header_f.pack(fill="x", padx=12, pady=(10, 2))

            ctk.CTkLabel(header_f, text=badge["icon"], font=("Poppins", 18)).pack(side="left", padx=(0, 8))

            title_text = f"{badge['title']} {'✓' if badge['unlocked'] else ''}"
            t_color = "#10B981" if badge["unlocked"] else "#FFFFFF"
            ctk.CTkLabel(header_f, text=title_text, font=("Poppins", 12, "bold"), text_color=t_color).pack(side="left")

            ctk.CTkLabel(badge_card, text=badge["description"], font=("Poppins", 10), text_color="#AAAAAA").pack(anchor="w", padx=12, pady=(0, 4))

            prog_str = f"Progress: {badge['current']} / {badge['target']} ({badge['progress_percentage']}%)"
            p_color = "#3B82F6" if not badge["unlocked"] else "#10B981"
            ctk.CTkLabel(badge_card, text=prog_str, font=("Poppins", 10, "bold"), text_color=p_color).pack(anchor="w", padx=12, pady=(0, 10))

        # 2. Populate Notes per Subject Dropdown
        for widget in self.sec1_content.winfo_children():
            widget.destroy()

        grouped_notes = self.progress_logic.get_notes_grouped_by_subject(user_id)
        if not grouped_notes:
            ctk.CTkLabel(self.sec1_content, text="No notes recorded yet.", text_color="#888888").pack(anchor="w", pady=5)
        else:
            for subject, notes in grouped_notes.items():
                row_frame = ctk.CTkFrame(self.sec1_content, fg_color="#2B2B3D", corner_radius=8)
                row_frame.pack(fill="x", pady=4, padx=5)

                count_text = f"📚 {subject}  ({len(notes)} note{'s' if len(notes) > 1 else ''})"
                ctk.CTkLabel(row_frame, text=count_text, font=("Poppins", 12, "bold"), text_color="#3B82F6").pack(side="left", padx=15, pady=10)

                topic_titles = [n["title"] for n in notes]
                topic_dropdown = ctk.CTkOptionMenu(
                    row_frame,
                    values=topic_titles,
                    width=220,
                    height=30,
                    fg_color="#1E1E2E",
                    button_color="#3B82F6",
                    font=("Poppins", 11)
                )
                topic_dropdown.set("View Topics...")
                topic_dropdown.pack(side="right", padx=15, pady=8)

        # 3. Populate Quiz Scores History
        for widget in self.sec2_content.winfo_children():
            widget.destroy()

        quiz_history = self.progress_logic.get_quiz_history(user_id)
        if not quiz_history:
            ctk.CTkLabel(self.sec2_content, text="No quiz attempts recorded yet.", text_color="#888888").pack(anchor="w", pady=5)
        else:
            for q in quiz_history:
                q_card = ctk.CTkFrame(self.sec2_content, fg_color="#2B2B3D", corner_radius=8)
                q_card.pack(fill="x", pady=4, padx=5)

                pct = round((q["score"] / q["total_questions"]) * 100, 1)
                score_str = f"{q['score']} / {q['total_questions']} ({pct}%)"

                ctk.CTkLabel(q_card, text=q["quiz_title"], font=("Poppins", 12, "bold"), text_color="#FFFFFF").pack(side="left", padx=15, pady=8)
                ctk.CTkLabel(q_card, text=score_str, font=("Poppins", 12, "bold"), text_color="#10B981").pack(side="right", padx=15, pady=8)

        # 4. Populate Completed Tasks
        for widget in self.sec3_content.winfo_children():
            widget.destroy()

        completed_tasks = self.progress_logic.get_completed_tasks(user_id)
        if not completed_tasks:
            ctk.CTkLabel(self.sec3_content, text="No completed tasks found.", text_color="#888888").pack(anchor="w", pady=5)
        else:
            for task in completed_tasks:
                t_card = ctk.CTkFrame(self.sec3_content, fg_color="#2B2B3D", corner_radius=8)
                t_card.pack(fill="x", pady=4, padx=5)

                ctk.CTkLabel(t_card, text=f"✅ {task['title']}", font=("Poppins", 12, "bold"), text_color="#FFFFFF").pack(side="left", padx=15, pady=8)
                ctk.CTkLabel(t_card, text=f"Due: {task['due_date']}", font=("Poppins", 11), text_color="#AAAAAA").pack(side="right", padx=15, pady=8)

    def on_show(self):
        """Lifecycle method called when switching to Progress view."""
        self.load_progress_data()