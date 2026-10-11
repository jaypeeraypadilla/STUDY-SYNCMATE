import customtkinter as ctk
from tkinter import messagebox
from logic.quiz_generator import QuizGenerator


class QuizGeneView(ctk.CTkFrame):
    """Interactive Quiz & Flashcard workspace derived from saved notes."""

    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.quiz_logic = QuizGenerator()

        self.active_flashcards = []
        self.current_flashcard_idx = 0
        self.showing_answer = False

        self.active_quiz_questions = []
        self.current_quiz_idx = 0
        self.user_score = 0
        self.selected_option_var = ctk.StringVar(value="")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Main Container Frame
        self.main_card = ctk.CTkFrame(self, corner_radius=12, fg_color="#1E1E2E")
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
    # SETUP SCREEN (Select Subject & Mode)
    # =============================================================
    def build_setup_screen(self):
        self.clear_container()

        ctk.CTkLabel(
            self.main_card, 
            text="🧠 AI & Notes Quiz Generator", 
            font=("Poppins", 20, "bold"), 
            text_color="#FFFFFF"
        ).pack(anchor="w", padx=25, pady=(20, 10))

        ctk.CTkLabel(
            self.main_card, 
            text="Select a subject from your saved notes to start studying:", 
            font=("Poppins", 12), 
            text_color="#AAAAAA"
        ).pack(anchor="w", padx=25, pady=(0, 15))

        user_id = self._get_user_id()
        subjects = self.quiz_logic.get_available_subjects(user_id)

        ctk.CTkLabel(self.main_card, text="Subject:", font=("Poppins", 12, "bold")).pack(anchor="w", padx=25, pady=(5, 2))
        self.subject_dropdown = ctk.CTkOptionMenu(
            self.main_card, 
            values=subjects if subjects else ["No subjects available"],
            height=38,
            fg_color="#2B2B3D",
            button_color="#3B82F6"
        )
        self.subject_dropdown.pack(fill="x", padx=25, pady=(0, 20))

        ctk.CTkLabel(self.main_card, text="Study Mode:", font=("Poppins", 12, "bold")).pack(anchor="w", padx=25, pady=(5, 2))
        self.mode_dropdown = ctk.CTkOptionMenu(
            self.main_card, 
            values=["Flashcards Review", "Practice Quiz (Multiple Choice)"],
            height=38,
            fg_color="#2B2B3D",
            button_color="#10B981"
        )
        self.mode_dropdown.pack(fill="x", padx=25, pady=(0, 30))

        self.btn_start = ctk.CTkButton(
            self.main_card,
            text="🚀 Start Session",
            font=("Poppins", 14, "bold"),
            fg_color="#3B82F6",
            hover_color="#2563EB",
            height=42,
            command=self.start_session
        )
        self.btn_start.pack(fill="x", padx=25, pady=10)

    def start_session(self):
        user_id = self._get_user_id()
        subject = self.subject_dropdown.get()
        mode = self.mode_dropdown.get()

        if subject == "No subjects available" or not subject:
            messagebox.showwarning("Warning", "Please select a valid subject with saved notes.")
            return

        if "Flashcards" in mode:
            self.active_flashcards = self.quiz_logic.generate_flashcards(user_id, subject)
            if not self.active_flashcards:
                messagebox.showinfo("Info", f"No notes found under subject '{subject}'.")
                return
            self.current_flashcard_idx = 0
            self.showing_answer = False
            self.build_flashcard_screen()
        else:
            self.active_quiz_questions = self.quiz_logic.generate_practice_quiz(user_id, subject)
            if len(self.active_quiz_questions) < 1:
                messagebox.showinfo("Info", "You need at least 2 detailed notes in this subject to generate a practice quiz.")
                return
            self.current_quiz_idx = 0
            self.user_score = 0
            self.build_quiz_question_screen(subject)

    # =============================================================
    # FLASHCARDS INTERACTIVE SCREEN
    # =============================================================
    def build_flashcard_screen(self):
        self.clear_container()

        card_data = self.active_flashcards[self.current_flashcard_idx]

        header_frame = ctk.CTkFrame(self.main_card, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=15)

        ctk.CTkLabel(
            header_frame, 
            text=f"Flashcard {self.current_flashcard_idx + 1} of {len(self.active_flashcards)}", 
            font=("Poppins", 14, "bold"), 
            text_color="#3B82F6"
        ).pack(side="left")

        ctk.CTkButton(
            header_frame, text="❌ Exit", width=70, height=28, fg_color="#EF4444", command=self.build_setup_screen
        ).pack(side="right")

        # Flashcard Display Box
        self.card_box = ctk.CTkFrame(self.main_card, fg_color="#2B2B3D", corner_radius=12, height=220)
        self.card_box.pack(fill="both", expand=True, padx=25, pady=10)
        self.card_box.pack_propagate(False)

        self.lbl_card_title = ctk.CTkLabel(
            self.card_box, 
            text=card_data["question"] if not self.showing_answer else "Answer / Summary:", 
            font=("Poppins", 12, "bold"), 
            text_color="#10B981"
        )
        self.lbl_card_title.pack(anchor="w", padx=20, pady=(20, 5))

        self.lbl_card_content = ctk.CTkLabel(
            self.card_box, 
            text=card_data["answer"] if self.showing_answer else card_data["answer"][:250] + "...", 
            font=("Poppins", 13), 
            text_color="#FFFFFF", 
            justify="left", 
            wraplength=550
        )
        self.lbl_card_content.pack(anchor="w", padx=20, pady=10, fill="both", expand=True)

        # Navigation Controls
        nav_frame = ctk.CTkFrame(self.main_card, fg_color="transparent")
        nav_frame.pack(fill="x", padx=25, pady=20)

        ctk.CTkButton(
            nav_frame, text="🔄 Flip Card", fg_color="#F59E0B", hover_color="#D97706", height=38, command=self.flip_flashcard
        ).pack(side="left", expand=True, fill="x", padx=(0, 10))

        if self.current_flashcard_idx < len(self.active_flashcards) - 1:
            ctk.CTkButton(
                nav_frame, text="Next ➡️", fg_color="#3B82F6", height=38, command=self.next_flashcard
            ).pack(side="right", expand=True, fill="x", padx=(10, 0))
        else:
            ctk.CTkButton(
                nav_frame, text="✨ Finish Review", fg_color="#10B981", height=38, command=self.build_setup_screen
            ).pack(side="right", expand=True, fill="x", padx=(10, 0))

    def flip_flashcard(self):
        self.showing_answer = not self.showing_answer
        self.build_flashcard_screen()

    def next_flashcard(self):
        self.current_flashcard_idx += 1
        self.showing_answer = False
        self.build_flashcard_screen()

    # =============================================================
    # PRACTICE QUIZ SCREEN
    # =============================================================
    def build_quiz_question_screen(self, subject):
        self.clear_container()

        q_data = self.active_quiz_questions[self.current_quiz_idx]
        self.selected_option_var.set("")

        header_frame = ctk.CTkFrame(self.main_card, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=15)

        ctk.CTkLabel(
            header_frame, 
            text=f"Question {self.current_quiz_idx + 1} of {len(self.active_quiz_questions)}", 
            font=("Poppins", 14, "bold"), 
            text_color="#3B82F6"
        ).pack(side="left")

        # Question Prompt Box
        ctk.CTkLabel(
            self.main_card, 
            text=q_data["prompt"], 
            font=("Poppins", 13), 
            text_color="#FFFFFF", 
            justify="left", 
            wraplength=580
        ).pack(anchor="w", padx=25, pady=(5, 15))

        # Radio Options
        for option in q_data["options"]:
            rb = ctk.CTkRadioButton(
                self.main_card, 
                text=option, 
                variable=self.selected_option_var, 
                value=option, 
                font=("Poppins", 12),
                fg_color="#3B82F6"
            )
            rb.pack(anchor="w", padx=35, pady=8)

        # Submit Button
        ctk.CTkButton(
            self.main_card,
            text="Submit Answer ➔",
            font=("Poppins", 14, "bold"),
            fg_color="#10B981",
            hover_color="#059669",
            height=40,
            command=lambda: self.submit_quiz_answer(subject)
        ).pack(fill="x", padx=25, pady=(30, 10))

    def submit_quiz_answer(self, subject):
        chosen = self.selected_option_var.get()
        if not chosen:
            messagebox.showwarning("Warning", "Please select an answer option.")
            return

        q_data = self.active_quiz_questions[self.current_quiz_idx]
        if chosen == q_data["correct_answer"]:
            self.user_score += 1

        self.current_quiz_idx += 1
        if self.current_quiz_idx < len(self.active_quiz_questions):
            self.build_quiz_question_screen(subject)
        else:
            # Quiz Finished - Save Score
            total = len(self.active_quiz_questions)
            self.quiz_logic.save_quiz_result(
                user_id=self._get_user_id(),
                quiz_title=f"{subject} Review Quiz",
                subject=subject,
                score=self.user_score,
                total_questions=total
            )
            self.build_quiz_results_screen(subject, total)

    def build_quiz_results_screen(self, subject, total):
        self.clear_container()

        percentage = round((self.user_score / total) * 100, 1)

        ctk.CTkLabel(
            self.main_card, text="🎉 Quiz Completed!", font=("Poppins", 22, "bold"), text_color="#10B981"
        ).pack(pady=(40, 10))

        ctk.CTkLabel(
            self.main_card, 
            text=f"Your Score: {self.user_score} / {total} ({percentage}%)", 
            font=("Poppins", 16, "bold"), 
            text_color="#FFFFFF"
        ).pack(pady=10)

        ctk.CTkButton(
            self.main_card,
            text="🔄 Take Another Quiz",
            font=("Poppins", 14, "bold"),
            fg_color="#3B82F6",
            height=40,
            command=self.build_setup_screen
        ).pack(fill="x", padx=50, pady=(30, 10))

    def on_show(self):
        self.build_setup_screen()