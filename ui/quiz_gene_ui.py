import customtkinter as ctk
from tkinter import messagebox
from logic.quiz_generator import QuizGenerator


class QuizGeneView(ctk.CTkFrame):
    """Unified Interactive Quiz & Flashcard workspace combining sketch layouts, animated hovers, and multi-mode AI generation."""

    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.quiz_logic = QuizGenerator()

        self.active_flashcards = []
        self.current_flashcard_idx = 0
        self.showing_answer = False
        self.showing_hint = False

        self.active_quiz_questions = []
        self.current_quiz_idx = 0
        self.user_score = 0
        self.selected_subject = ctk.StringVar(value="")
        self.selected_mode = ctk.StringVar(value="Multiple Choice")
        self.selected_option_var = ctk.StringVar(value="")
        self.enum_entry_vars = []

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Main Container Frame (Theme Adaptive Scrollable Frame for Font Size & Scaling Responsiveness)
        self.main_card = ctk.CTkScrollableFrame(self, corner_radius=12, fg_color=("white", "#1E1E2E"))
        self.main_card.pack(fill="both", expand=True, padx=15, pady=15)

        self.build_setup_screen()

    def _get_user_id(self) -> int:
        if hasattr(self.controller, "current_user") and self.controller.current_user:
            return self.controller.current_user.get("id", 1)
        return 1

    def clear_container(self):
        for widget in self.main_card.winfo_children():
            widget.destroy()

    # =============================================================
    # 1. LANDING SETUP SCREEN (Sketch Layout + Subject/Mode Selection)
    # =============================================================
    def build_setup_screen(self):
        self.clear_container()

        # Header Title & Subtitle
        ctk.CTkLabel(
            self.main_card, 
            text="Quiz & Flashcards", 
            font=("Poppins", 20, "bold"), 
            text_color=("gray10", "#FFFFFF")
        ).pack(anchor="w", padx=25, pady=(20, 4))

        ctk.CTkLabel(
            self.main_card, 
            text="Test your knowledge and build better recall with interactive quizzes and flashcards.", 
            font=("Poppins", 12), 
            text_color=("gray50", "#AAAAAA")
        ).pack(anchor="w", padx=25, pady=(0, 15))

        # Two Main Feature Cards Container (Quizzes vs Flashcards) with Hover Animations
        cards_row = ctk.CTkFrame(self.main_card, fg_color="transparent")
        cards_row.pack(fill="x", padx=20, pady=(0, 15))
        cards_row.grid_columnconfigure((0, 1), weight=1)

        # --- CARD 1: QUIZZES ---
        self.quiz_card = ctk.CTkFrame(cards_row, fg_color=("#F3F4F6", "#2B2B3D"), corner_radius=12, border_width=2, border_color=("#F3F4F6", "#2B2B3D"))
        self.quiz_card.grid(row=0, column=0, sticky="nsew", padx=8)

        ctk.CTkLabel(self.quiz_card, text="📋?", font=("Poppins", 26)).pack(pady=(15, 2))
        ctk.CTkLabel(self.quiz_card, text="Quizzes", font=("Poppins", 14, "bold"), text_color=("gray10", "#FFFFFF")).pack(pady=2)
        ctk.CTkLabel(
            self.quiz_card, 
            text="Answer questions to improve your understanding.", 
            font=("Poppins", 10), 
            text_color=("gray50", "#AAAAAA"), 
            justify="center", 
            wraplength=200
        ).pack(padx=15, pady=(2, 10))

        self.btn_start_quiz = ctk.CTkButton(
            self.quiz_card,
            text="Start Quiz ➔",
            font=("Poppins", 12, "bold"),
            fg_color="#3B82F6",
            hover_color="#2563EB",
            height=34,
            command=lambda: self.start_session("Quiz")
        )
        self.btn_start_quiz.pack(padx=20, pady=(0, 15), fill="x")

        # --- CARD 2: FLASHCARDS ---
        self.flash_card = ctk.CTkFrame(cards_row, fg_color=("#F3F4F6", "#2B2B3D"), corner_radius=12, border_width=2, border_color=("#F3F4F6", "#2B2B3D"))
        self.flash_card.grid(row=0, column=1, sticky="nsew", padx=8)

        ctk.CTkLabel(self.flash_card, text="🎴★", font=("Poppins", 26)).pack(pady=(15, 2))
        ctk.CTkLabel(self.flash_card, text="Flashcards", font=("Poppins", 14, "bold"), text_color=("gray10", "#FFFFFF")).pack(pady=2)
        ctk.CTkLabel(
            self.flash_card, 
            text="Review key concepts and definitions at your own pace.", 
            font=("Poppins", 10), 
            text_color=("gray50", "#AAAAAA"), 
            justify="center", 
            wraplength=200
        ).pack(padx=15, pady=(2, 10))

        self.btn_start_flash = ctk.CTkButton(
            self.flash_card,
            text="Start Flashcards ➔",
            font=("Poppins", 12, "bold"),
            fg_color="#10B981",
            hover_color="#059669",
            height=34,
            command=lambda: self.start_session("Flashcards")
        )
        self.btn_start_flash.pack(padx=20, pady=(0, 15), fill="x")

        # Bind Hover Animations
        self._bind_card_hover(self.quiz_card, "#3B82F6")
        self._bind_card_hover(self.flash_card, "#10B981")

        # --- SUBJECT SELECTION PILLS ---
        ctk.CTkLabel(
            self.main_card, text="Select Subject", font=("Poppins", 12, "bold"), text_color=("gray10", "#FFFFFF")
        ).pack(anchor="w", padx=25, pady=(5, 4))

        user_id = self._get_user_id()
        subjects = self.quiz_logic.get_available_subjects(user_id)
        if not subjects:
            subjects = ["ITE 260", "ITE 366", "GEN 006", "OTHERS"]

        if not self.selected_subject.get() or self.selected_subject.get() not in subjects:
            self.selected_subject.set(subjects[0])

        pills_frame = ctk.CTkFrame(self.main_card, fg_color="transparent")
        pills_frame.pack(anchor="w", padx=25, pady=(0, 10))

        self.subject_pill_buttons = {}
        for subj in subjects:
            is_active = (subj == self.selected_subject.get())
            pill_btn = ctk.CTkButton(
                pills_frame,
                text=subj,
                font=("Poppins", 11, "bold"),
                width=75,
                height=28,
                corner_radius=14,
                fg_color="#3B82F6" if is_active else ("gray85", "#2B2B3D"),
                text_color="white" if is_active else ("gray30", "#AAAAAA"),
                command=lambda s=subj: self.select_subject_pill(s)
            )
            pill_btn.pack(side="left", padx=3)
            self.subject_pill_buttons[subj] = pill_btn

        # --- STUDY MODE SELECTION PILLS (Retaining Identification, Enumeration, & Mixed Modes) ---
        ctk.CTkLabel(
            self.main_card, text="Quiz Mode", font=("Poppins", 12, "bold"), text_color=("gray10", "#FFFFFF")
        ).pack(anchor="w", padx=25, pady=(5, 4))

        modes = ["Multiple Choice", "Identification", "Enumeration", "Comprehensive Mixed"]
        modes_frame = ctk.CTkFrame(self.main_card, fg_color="transparent")
        modes_frame.pack(anchor="w", padx=25, pady=(0, 15))

        self.mode_pill_buttons = {}
        for m in modes:
            is_active = (m == self.selected_mode.get())
            m_btn = ctk.CTkButton(
                modes_frame,
                text=m,
                font=("Poppins", 10, "bold"),
                width=110,
                height=28,
                corner_radius=14,
                fg_color="#10B981" if is_active else ("gray85", "#2B2B3D"),
                text_color="white" if is_active else ("gray30", "#AAAAAA"),
                command=lambda md=m: self.select_mode_pill(md)
            )
            m_btn.pack(side="left", padx=3)
            self.mode_pill_buttons[m] = m_btn

    def _bind_card_hover(self, card_frame, border_color):
        """Adds smooth animated hover feedback when the mouse points to cards."""
        def on_enter(e):
            card_frame.configure(border_color=border_color)
        def on_leave(e):
            card_frame.configure(border_color=("#F3F4F6", "#2B2B3D"))

        card_frame.bind("<Enter>", on_enter)
        card_frame.bind("<Leave>", on_leave)
        for child in card_frame.winfo_children():
            child.bind("<Enter>", on_enter)
            child.bind("<Leave>", on_leave)

    def select_subject_pill(self, subject: str):
        self.selected_subject.set(subject)
        for subj, btn in self.subject_pill_buttons.items():
            if subj == subject:
                btn.configure(fg_color="#3B82F6", text_color="white")
            else:
                btn.configure(fg_color=("gray85", "#2B2B3D"), text_color=("gray30", "#AAAAAA"))

    def select_mode_pill(self, mode: str):
        self.selected_mode.set(mode)
        for md, btn in self.mode_pill_buttons.items():
            if md == mode:
                btn.configure(fg_color="#10B981", text_color="white")
            else:
                btn.configure(fg_color=("gray85", "#2B2B3D"), text_color=("gray30", "#AAAAAA"))

    def show_loading_state(self):
        """Displays loading UI while Gemini AI analyzes notes inside the scrollable container."""
        self.clear_container()
        load_box = ctk.CTkFrame(self.main_card, fg_color="transparent")
        load_box.pack(fill="both", expand=True, padx=20, pady=80)

        inner = ctk.CTkFrame(load_box, fg_color="transparent")
        inner.pack(expand=True)

        ctk.CTkLabel(inner, text="⚡", font=("Poppins", 48)).pack(pady=(0, 10))
        ctk.CTkLabel(
            inner, 
            text="Gemini AI is analyzing your notes...", 
            font=("Poppins", 16, "bold"), 
            text_color="#3B82F6"
        ).pack(pady=(0, 5))
        ctk.CTkLabel(
            inner, 
            text="Generating customized study content and questions...", 
            font=("Poppins", 11), 
            text_color=("gray50", "#AAAAAA")
        ).pack()
        self.update_idletasks()

    def start_session(self, mode_type: str):
        user_id = self._get_user_id()
        subject = self.selected_subject.get()
        mode = self.selected_mode.get()

        if not subject or subject == "No subjects available":
            messagebox.showwarning("Warning", "Please select a valid subject with saved notes.")
            return

        self.show_loading_state()

        if mode_type == "Flashcards":
            self.active_flashcards = self.quiz_logic.generate_flashcards(user_id, subject)
            if not self.active_flashcards:
                messagebox.showinfo("Info", f"No notes found under subject '{subject}'.")
                self.build_setup_screen()
                return
            self.current_flashcard_idx = 0
            self.showing_answer = False
            self.showing_hint = False
            self.build_flashcard_screen()
        else:
            if mode == "Multiple Choice":
                self.active_quiz_questions = self.quiz_logic.generate_multiple_choice_questions(user_id, subject)
            elif mode == "Identification":
                self.active_quiz_questions = self.quiz_logic.generate_identification_questions(user_id, subject)
            elif mode == "Enumeration":
                self.active_quiz_questions = self.quiz_logic.generate_enumeration_questions(user_id, subject)
            else:
                self.active_quiz_questions = self.quiz_logic.generate_practice_quiz(user_id, subject)

            if not self.active_quiz_questions:
                messagebox.showinfo("Info", f"Not enough structured notes available to generate '{mode}' questions for '{subject}'.")
                self.build_setup_screen()
                return

            self.current_quiz_idx = 0
            self.user_score = 0
            self.build_quiz_question_screen(subject)

    # =============================================================
    # 2. FLASHCARDS REVIEW SCREEN (With Flip, Hints & Sketch Layout)
    # =============================================================
    def build_flashcard_screen(self):
        self.clear_container()

        card_data = self.active_flashcards[self.current_flashcard_idx]
        total_cards = len(self.active_flashcards)

        # Header Bar
        header_frame = ctk.CTkFrame(self.main_card, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=15)

        ctk.CTkButton(
            header_frame, text="← Flashcards", fg_color="transparent", text_color="#3B82F6", font=("Poppins", 13, "bold"),
            hover_color=("gray90", "#2B2B3D"), command=self.build_setup_screen
        ).pack(side="left")

        progress_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        progress_frame.pack(side="right")

        ctk.CTkLabel(
            progress_frame, text=f"{self.current_flashcard_idx + 1}/{total_cards}", font=("Poppins", 11, "bold"), text_color=("gray50", "#AAAAAA")
        ).pack(side="right", padx=(8, 0))

        # Main Flashcard Box
        self.card_box = ctk.CTkFrame(self.main_card, fg_color=("gray95", "#2B2B3D"), corner_radius=12, height=240)
        self.card_box.pack(fill="both", expand=True, padx=25, pady=10)
        self.card_box.pack_propagate(False)

        mode_text = "❓ Front (Term / Question)" if not self.showing_answer else "💡 Back (Definition / Explanation)"
        ctk.CTkLabel(
            self.card_box, 
            text=mode_text, 
            font=("Poppins", 11, "bold"), 
            text_color=("#059669", "#10B981") if self.showing_answer else ("#3B82F6", "#60A5FA")
        ).pack(anchor="w", padx=20, pady=(15, 2))

        display_text = card_data["front"] if not self.showing_answer else card_data["back"]
        ctk.CTkLabel(
            self.card_box, 
            text=display_text, 
            font=("Poppins", 14, "bold" if not self.showing_answer else "normal"), 
            text_color=("gray10", "#FFFFFF"), 
            justify="left", 
            wraplength=480
        ).pack(anchor="w", padx=20, pady=8, fill="both", expand=True)

        # Hint Section (If revealed)
        if card_data.get("hint") and self.showing_hint:
            hint_box = ctk.CTkFrame(self.card_box, fg_color=("gray90", "#1E1E2E"), corner_radius=6)
            hint_box.pack(fill="x", padx=20, pady=(0, 10))
            ctk.CTkLabel(
                hint_box, 
                text=f"💡 Hint: {card_data['hint']}", 
                font=("Poppins", 10, "italic"), 
                text_color="#F59E0B",
                justify="left",
                wraplength=460
            ).pack(anchor="w", padx=10, pady=5)

        # Navigation & Action Row
        nav_frame = ctk.CTkFrame(self.main_card, fg_color="transparent")
        nav_frame.pack(fill="x", padx=25, pady=15)

        ctk.CTkButton(
            nav_frame, text="←", font=("Poppins", 14, "bold"), fg_color="gray50", hover_color="gray40", width=45, height=38, 
            command=self.prev_flashcard if self.current_flashcard_idx > 0 else lambda: None
        ).pack(side="left")

        if card_data.get("hint"):
            hint_btn_text = "Hide Hint" if self.showing_hint else "💡 Hint"
            ctk.CTkButton(
                nav_frame, text=hint_btn_text, fg_color="#8B5CF6", hover_color="#7C3AED", height=38, width=80, command=self.toggle_hint
            ).pack(side="left", padx=8)

        ctk.CTkButton(
            nav_frame, text="🔄 FLIP", font=("Poppins", 12, "bold"), fg_color="#F59E0B", hover_color="#D97706", height=38, 
            command=self.flip_flashcard
        ).pack(side="left", expand=True, fill="x", padx=8)

        if self.current_flashcard_idx < total_cards - 1:
            ctk.CTkButton(
                nav_frame, text="→", font=("Poppins", 14, "bold"), fg_color="#3B82F6", hover_color="#2563EB", width=45, height=38, 
                command=self.next_flashcard
            ).pack(side="right")
        else:
            ctk.CTkButton(
                nav_frame, text="✨ Finish", font=("Poppins", 12, "bold"), fg_color="#10B981", hover_color="#059669", width=80, height=38, 
                command=self.build_setup_screen
            ).pack(side="right")

    def toggle_hint(self):
        self.showing_hint = not self.showing_hint
        self.build_flashcard_screen()

    def flip_flashcard(self):
        self.showing_answer = not self.showing_answer
        self.build_flashcard_screen()

    def next_flashcard(self):
        self.current_flashcard_idx += 1
        self.showing_answer = False
        self.showing_hint = False
        self.build_flashcard_screen()

    def prev_flashcard(self):
        if self.current_flashcard_idx > 0:
            self.current_flashcard_idx -= 1
            self.showing_answer = False
            self.showing_hint = False
            self.build_flashcard_screen()

    # =============================================================
    # 3. QUIZ QUESTION SCREEN (Supports MC, Identification, Enumeration)
    # =============================================================
    def build_quiz_question_screen(self, subject):
        self.clear_container()

        q_data = self.active_quiz_questions[self.current_quiz_idx]
        q_type = q_data.get("type", "Multiple Choice")
        self.selected_option_var.set("")
        self.enum_entry_vars = []

        header_frame = ctk.CTkFrame(self.main_card, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=15)

        # Match flashcards back button styling: transparent background, blue text ("← Quizzes") with confirmation dialog
        ctk.CTkButton(
            header_frame, text="← Quizzes", fg_color="transparent", text_color="#3B82F6", font=("Poppins", 13, "bold"),
            hover_color=("gray90", "#2B2B3D"), command=self.confirm_exit_quiz
        ).pack(side="left")

        badge = ctk.CTkFrame(header_frame, fg_color=("#E5E7EB", "#2B2B3D"), corner_radius=6)
        badge.pack(side="left", padx=(15, 0))
        ctk.CTkLabel(badge, text=f"  {q_type}  ", font=("Poppins", 11, "bold"), text_color=("#3B82F6", "#60A5FA")).pack(padx=6, pady=4)

        ctk.CTkLabel(
            header_frame, text=f"Question {self.current_quiz_idx + 1} of {len(self.active_quiz_questions)}", font=("Poppins", 11), text_color=("gray50", "#AAAAAA")
        ).pack(side="right")

        ctk.CTkLabel(
            self.main_card, 
            text=q_data["prompt"], 
            font=("Poppins", 13, "bold"), 
            text_color=("gray10", "#FFFFFF"), 
            justify="left", 
            wraplength=550
        ).pack(anchor="w", padx=25, pady=(10, 15))

        if q_type == "Multiple Choice":
            for idx, option in enumerate(q_data["options"]):
                prefix = ["A.", "B.", "C.", "D."][idx] if idx < 4 else "•"
                option_text = f"O {prefix} {option}"
                
                rb_btn = ctk.CTkRadioButton(
                    self.main_card, 
                    text=option_text, 
                    variable=self.selected_option_var, 
                    value=option, 
                    font=("Poppins", 12),
                    text_color=("gray10", "#FFFFFF"),
                    fg_color="#3B82F6",
                    hover_color="#2563EB"
                )
                rb_btn.pack(anchor="w", padx=35, pady=6)

        elif q_type == "Identification":
            self.id_entry = ctk.CTkEntry(
                self.main_card, placeholder_text="Type the correct term or topic here...", height=40, font=("Poppins", 12)
            )
            self.id_entry.pack(fill="x", padx=35, pady=15)

        elif q_type == "Enumeration":
            scroll_enum = ctk.CTkScrollableFrame(self.main_card, fg_color="transparent", height=140)
            scroll_enum.pack(fill="x", padx=25, pady=10)

            items_count = len(q_data.get("items", []))
            for idx in range(items_count):
                row_f = ctk.CTkFrame(scroll_enum, fg_color="transparent")
                row_f.pack(fill="x", pady=4)
                ctk.CTkLabel(row_f, text=f"Item {idx + 1}:", font=("Poppins", 11, "bold"), text_color=("gray10", "#FFFFFF"), width=65).pack(side="left")
                
                v = ctk.StringVar(value="")
                self.enum_entry_vars.append(v)
                ctk.CTkEntry(row_f, textvariable=v, height=32, font=("Poppins", 11)).pack(side="left", fill="x", expand=True, padx=5)

        # Bottom Navigation (Previous & Next/Submit)
        btn_frame = ctk.CTkFrame(self.main_card, fg_color="transparent")
        btn_frame.pack(fill="x", padx=25, pady=(25, 10))

        if self.current_quiz_idx > 0:
            ctk.CTkButton(
                btn_frame, text="← Previous", font=("Poppins", 12, "bold"), fg_color=("gray85", "#2B2B3D"), text_color=("gray10", "#FFFFFF"),
                hover_color=("gray75", "#3A3A4E"), height=38, width=100, command=lambda: self.prev_quiz_answer(subject)
            ).pack(side="left")

        ctk.CTkButton(
            btn_frame, text="Next →", font=("Poppins", 12, "bold"), fg_color="#10B981", hover_color="#059669", height=38, width=110,
            command=lambda: self.submit_quiz_answer(subject, q_type)
        ).pack(side="right")

    def confirm_exit_quiz(self):
        """Prompts user for confirmation before exiting an active quiz session."""
        if messagebox.askyesno("Exit Quiz", "Are you sure you want to exit? Your current quiz progress will be lost."):
            self.build_setup_screen()

    def submit_quiz_answer(self, subject, q_type):
        q_data = self.active_quiz_questions[self.current_quiz_idx]
        is_correct = False

        if q_type == "Multiple Choice":
            chosen = self.selected_option_var.get()
            if not chosen:
                messagebox.showwarning("Warning", "Please select an answer option.")
                return
            if chosen.strip().lower() == q_data["correct_answer"].strip().lower():
                is_correct = True

        elif q_type == "Identification":
            entered = self.id_entry.get().strip()
            if not entered:
                messagebox.showwarning("Warning", "Please type your answer.")
                return
            if entered.lower() in q_data["correct_answer"].strip().lower() or q_data["correct_answer"].strip().lower() in entered.lower():
                is_correct = True

        elif q_type == "Enumeration":
            user_items = [v.get().strip().lower() for v in self.enum_entry_vars if v.get().strip()]
            correct_items = [item.strip().lower() for item in q_data.get("items", [])]
            
            matched = sum(1 for ui in user_items if any(ci in ui or ui in ci for ci in correct_items))
            if matched >= max(1, len(correct_items) // 2):  
                is_correct = True

        if is_correct:
            self.user_score += 1

        self.current_quiz_idx += 1
        if self.current_quiz_idx < len(self.active_quiz_questions):
            self.build_quiz_question_screen(subject)
        else:
            total = len(self.active_quiz_questions)
            self.quiz_logic.save_quiz_result(
                user_id=self._get_user_id(),
                quiz_title=f"{subject} {q_type} Quiz",
                subject=subject,
                score=self.user_score,
                total_questions=total
            )
            self.build_quiz_results_screen(subject, total)

    def prev_quiz_answer(self, subject):
        if self.current_quiz_idx > 0:
            self.current_quiz_idx -= 1
            self.build_quiz_question_screen(subject)

    # =============================================================
    # 4. QUIZ RESULTS SCREEN (Sketch Layout with Stats & Motivational Banner)
    # =============================================================
    def build_quiz_results_screen(self, subject, total):
        self.clear_container()

        percentage = round((self.user_score / total) * 100)

        # Check Icon Badge
        ctk.CTkLabel(self.main_card, text="✅", font=("Poppins", 36)).pack(pady=(25, 5))

        ctk.CTkLabel(
            self.main_card, text="Quiz Complete!", font=("Poppins", 18, "bold"), text_color=("gray10", "#FFFFFF")
        ).pack()

        ctk.CTkLabel(
            self.main_card, text=f"You answered {self.user_score} out of {total} correctly!", font=("Poppins", 12), text_color=("gray50", "#AAAAAA")
        ).pack(pady=(2, 20))

        # Stats 3-Column Card (Accuracy | Correct Answer | Time Taken)
        stats_card = ctk.CTkFrame(self.main_card, fg_color=("#F3F4F6", "#2B2B3D"), corner_radius=10)
        stats_card.pack(fill="x", padx=25, pady=(0, 20))
        stats_card.grid_columnconfigure((0, 1, 2), weight=1)

        # Stat 1: Accuracy
        s1 = ctk.CTkFrame(stats_card, fg_color="transparent")
        s1.grid(row=0, column=0, pady=12)
        ctk.CTkLabel(s1, text=f"{percentage}%", font=("Poppins", 15, "bold"), text_color="#3B82F6").pack()
        ctk.CTkLabel(s1, text="Accuracy", font=("Poppins", 10), text_color=("gray50", "#AAAAAA")).pack()

        # Stat 2: Correct Answer
        s2 = ctk.CTkFrame(stats_card, fg_color="transparent")
        s2.grid(row=0, column=1, pady=12)
        ctk.CTkLabel(s2, text=f"{self.user_score}/{total}", font=("Poppins", 15, "bold"), text_color="#10B981").pack()
        ctk.CTkLabel(s2, text="Correct Answer", font=("Poppins", 10), text_color=("gray50", "#AAAAAA")).pack()

        # Stat 3: Time Taken
        s3 = ctk.CTkFrame(stats_card, fg_color="transparent")
        s3.grid(row=0, column=2, pady=12)
        ctk.CTkLabel(s3, text="1m 30s", font=("Poppins", 15, "bold"), text_color="#F59E0B").pack()
        ctk.CTkLabel(s3, text="Time Taken", font=("Poppins", 10), text_color=("gray50", "#AAAAAA")).pack()

        # Action Buttons
        btn_row = ctk.CTkFrame(self.main_card, fg_color="transparent")
        btn_row.pack(fill="x", padx=25, pady=(0, 20))
        btn_row.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            btn_row, text="Review Answers", font=("Poppins", 12, "bold"), fg_color=("gray85", "#2B2B3D"), text_color=("gray10", "#FFFFFF"),
            hover_color=("gray75", "#3A3A4E"), height=38, command=lambda: messagebox.showinfo("Review", "Review mode enabled.")
        ).grid(row=0, column=0, sticky="ew", padx=(0, 6))

        ctk.CTkButton(
            btn_row, text="Back to Quiz & Flashcards", font=("Poppins", 12, "bold"), fg_color="#3B82F6", hover_color="#2563EB", height=38,
            command=self.build_setup_screen
        ).grid(row=0, column=1, sticky="ew", padx=(6, 0))

        # Motivational Footer Banner
        footer_box = ctk.CTkFrame(self.main_card, fg_color=("#ECFDF5", "#1E293B"), corner_radius=8)
        footer_box.pack(fill="x", padx=25, pady=(10, 20))
        ctk.CTkLabel(
            footer_box, text="🌱 Great Job! Keep going, you're making progress!", font=("Poppins", 11, "bold"), text_color="#10B981"
        ).pack(pady=10)

    def on_show(self):
        self.build_setup_screen()