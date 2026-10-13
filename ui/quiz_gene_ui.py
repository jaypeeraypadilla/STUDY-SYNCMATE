import customtkinter as ctk
from tkinter import messagebox
from logic.quiz_generator import QuizGenerator


class QuizGeneView(ctk.CTkFrame):
    """Interactive Quiz & Flashcard workspace supporting Multiple Choice, Identification, and Enumeration."""

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
        self.enum_entry_vars = []  # Stores string vars for enumeration input boxes

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Main Container Frame (Theme Adaptive)
        self.main_card = ctk.CTkFrame(self, corner_radius=12, fg_color=("white", "#1E1E2E"))
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
    # SETUP SCREEN (Select Subject & Study Mode)
    # =============================================================
    def build_setup_screen(self):
        self.clear_container()

        ctk.CTkLabel(
            self.main_card, 
            text="🧠 Intelligent Quiz & Flashcard Generator", 
            font=("Poppins", 20, "bold"), 
            text_color=("gray10", "#FFFFFF")
        ).pack(anchor="w", padx=25, pady=(20, 10))

        ctk.CTkLabel(
            self.main_card, 
            text="Select a subject and test mode generated from your saved notes:", 
            font=("Poppins", 12), 
            text_color=("gray30", "#AAAAAA")
        ).pack(anchor="w", padx=25, pady=(0, 15))

        user_id = self._get_user_id()
        subjects = self.quiz_logic.get_available_subjects(user_id)

        ctk.CTkLabel(self.main_card, text="Subject:", font=("Poppins", 12, "bold"), text_color=("gray10", "#FFFFFF")).pack(anchor="w", padx=25, pady=(5, 2))
        self.subject_dropdown = ctk.CTkOptionMenu(
            self.main_card, 
            values=subjects if subjects else ["No subjects available"],
            height=38,
            fg_color=("gray85", "#2B2B3D"),
            button_color="#3B82F6",
            text_color=("gray10", "#FFFFFF")
        )
        self.subject_dropdown.pack(fill="x", padx=25, pady=(0, 20))

        ctk.CTkLabel(self.main_card, text="Study Mode:", font=("Poppins", 12, "bold"), text_color=("gray10", "#FFFFFF")).pack(anchor="w", padx=25, pady=(5, 2))
        self.mode_dropdown = ctk.CTkOptionMenu(
            self.main_card, 
            values=[
                "Flashcards Review", 
                "Practice Quiz (Multiple Choice)", 
                "Identification Quiz", 
                "Enumeration Practice", 
                "Comprehensive Mixed Quiz"
            ],
            height=38,
            fg_color=("gray85", "#2B2B3D"),
            button_color="#10B981",
            text_color=("gray10", "#FFFFFF")
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
            if "Multiple Choice" in mode:
                self.active_quiz_questions = self.quiz_logic.generate_multiple_choice_questions(user_id, subject)
            elif "Identification" in mode:
                self.active_quiz_questions = self.quiz_logic.generate_identification_questions(user_id, subject)
            elif "Enumeration" in mode:
                self.active_quiz_questions = self.quiz_logic.generate_enumeration_questions(user_id, subject)
            else:  # Comprehensive Mixed Quiz
                self.active_quiz_questions = self.quiz_logic.generate_practice_quiz(user_id, subject)

            if not self.active_quiz_questions:
                messagebox.showinfo("Info", f"Not enough structured notes available to generate '{mode}' questions for '{subject}'.")
                return

            self.current_quiz_idx = 0
            self.user_score = 0
            self.build_quiz_question_screen(subject)

    # =============================================================
    # FLASHCARDS SCREEN
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

        self.card_box = ctk.CTkFrame(self.main_card, fg_color=("gray95", "#2B2B3D"), corner_radius=12, height=220)
        self.card_box.pack(fill="both", expand=True, padx=25, pady=10)
        self.card_box.pack_propagate(False)

        ctk.CTkLabel(
            self.card_box, 
            text=card_data["question"] if not self.showing_answer else "Answer / Summary:", 
            font=("Poppins", 12, "bold"), 
            text_color=("#059669", "#10B981")
        ).pack(anchor="w", padx=20, pady=(20, 5))

        ctk.CTkLabel(
            self.card_box, 
            text=card_data["answer"] if self.showing_answer else card_data["answer"][:250] + "...", 
            font=("Poppins", 13), 
            text_color=("gray10", "#FFFFFF"), 
            justify="left", 
            wraplength=550
        ).pack(anchor="w", padx=20, pady=10, fill="both", expand=True)

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
    # PRACTICE QUIZ SCREEN (Multiple Choice, Identification, Enumeration)
    # =============================================================
    def build_quiz_question_screen(self, subject):
        self.clear_container()

        q_data = self.active_quiz_questions[self.current_quiz_idx]
        q_type = q_data.get("type", "Multiple Choice")
        self.selected_option_var.set("")
        self.enum_entry_vars = []

        header_frame = ctk.CTkFrame(self.main_card, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=15)

        ctk.CTkLabel(
            header_frame, 
            text=f"[{q_type}]  Question {self.current_quiz_idx + 1} of {len(self.active_quiz_questions)}", 
            font=("Poppins", 14, "bold"), 
            text_color="#3B82F6"
        ).pack(side="left")

        ctk.CTkLabel(
            header_frame, text=f"Subject: {subject}", font=("Poppins", 11), text_color=("gray30", "#AAAAAA")
        ).pack(side="right")

        # Question Prompt
        ctk.CTkLabel(
            self.main_card, 
            text=q_data["prompt"], 
            font=("Poppins", 13), 
            text_color=("gray10", "#FFFFFF"), 
            justify="left", 
            wraplength=580
        ).pack(anchor="w", padx=25, pady=(5, 15))

        # RENDER INPUT WIDGETS BASED ON QUESTION TYPE
        if q_type == "Multiple Choice":
            for option in q_data["options"]:
                rb = ctk.CTkRadioButton(
                    self.main_card, 
                    text=option, 
                    variable=self.selected_option_var, 
                    value=option, 
                    font=("Poppins", 12),
                    text_color=("gray10", "#FFFFFF"),
                    fg_color="#3B82F6"
                )
                rb.pack(anchor="w", padx=35, pady=8)

        elif q_type == "Identification":
            self.id_entry = ctk.CTkEntry(
                self.main_card, placeholder_text="Type the correct term or topic here...", height=40, font=("Poppins", 12)
            )
            self.id_entry.pack(fill="x", padx=35, pady=15)

        elif q_type == "Enumeration":
            scroll_enum = ctk.CTkScrollableFrame(self.main_card, fg_color="transparent", height=150)
            scroll_enum.pack(fill="x", padx=25, pady=10)

            items_count = len(q_data.get("items", []))
            for idx in range(items_count):
                row_f = ctk.CTkFrame(scroll_enum, fg_color="transparent")
                row_f.pack(fill="x", pady=4)
                ctk.CTkLabel(row_f, text=f"Item {idx + 1}:", font=("Poppins", 11, "bold"), text_color=("gray10", "#FFFFFF"), width=65).pack(side="left")
                
                v = ctk.StringVar(value="")
                self.enum_entry_vars.append(v)
                ctk.CTkEntry(row_f, textvariable=v, height=32, font=("Poppins", 11)).pack(side="left", fill="x", expand=True, padx=5)

        # Submit Button
        ctk.CTkButton(
            self.main_card,
            text="Submit Answer ➔",
            font=("Poppins", 14, "bold"),
            fg_color="#10B981",
            hover_color="#059669",
            height=40,
            command=lambda: self.submit_quiz_answer(subject, q_type)
        ).pack(fill="x", padx=25, pady=(25, 10))

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
            entered_text = self.id_entry.get().strip()
            if not entered_text:
                messagebox.showwarning("Warning", "Please type your answer.")
                return
            if entered_text.lower() in q_data["correct_answer"].strip().lower() or q_data["correct_answer"].strip().lower() in entered_text.lower():
                is_correct = True

        elif q_type == "Enumeration":
            user_items = [v.get().strip().lower() for v in self.enum_entry_vars if v.get().strip()]
            correct_items = [item.strip().lower() for item in q_data["items"]]
            
            # Count how many items match
            matched = sum(1 for ui in user_items if any(ci in ui or ui in ci for ci in correct_items))
            if matched >= max(1, len(correct_items) // 2):  # Pass if at least half are correct
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
            text_color=("gray10", "#FFFFFF")
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