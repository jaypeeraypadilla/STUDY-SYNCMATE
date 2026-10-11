import random
from typing import List, Dict, Any, Tuple, Optional
from database.db_connection import db
from logic.my_notes import NotesManager


class QuizGenerator:
    """Generates flashcards and practice quizzes dynamically from saved study notes."""

    def __init__(self):
        self.db = db
        self.notes_manager = NotesManager()

    def get_available_subjects(self, user_id: int) -> List[str]:
        """Retrieves subjects that have saved notes available for quizzing."""
        return self.notes_manager.get_subjects_by_user(user_id)

    def generate_flashcards(self, user_id: int, subject: str) -> List[Dict[str, str]]:
        """Creates flashcards using note titles (Front) and note content (Back)."""
        notes = self.notes_manager.get_user_notes(user_id, subject_filter=subject)
        flashcards = []
        
        for note in notes:
            title = note.get("title", "Untitled Topic")
            content = note.get("content", "No content provided.")
            if content.strip():
                flashcards.append({
                    "question": f"Topic: {title}",
                    "answer": content,
                    "subject": subject
                })
        
        # Shuffle flashcards for active study sessions
        random.shuffle(flashcards)
        return flashcards

    def generate_practice_quiz(self, user_id: int, subject: str) -> List[Dict[str, Any]]:
        """Generates mock multiple-choice questions or true/false prompts from notes."""
        notes = self.notes_manager.get_user_notes(user_id, subject_filter=subject)
        if len(notes) < 2:
            return []  # Need at least a couple of notes to generate distractors

        questions = []
        for i, note in enumerate(notes):
            correct_title = note["title"]
            correct_content = note["content"]

            # Generate distractors (wrong answers) from other notes in the same subject
            other_notes = [n["title"] for n in notes if n["title"] != correct_title]
            if len(other_notes) < 2:
                continue

            distractors = random.sample(other_notes, min(3, len(other_notes)))
            options = distractors + [correct_title]
            random.shuffle(options)

            questions.append({
                "prompt": f"Which note topic corresponds to this definition/summary?\n\n\"{correct_content[:150]}...\"",
                "options": options,
                "correct_answer": correct_title
            })

        random.shuffle(questions)
        return questions

    def save_quiz_result(self, user_id: int, quiz_title: str, subject: str, score: int, total_questions: int) -> Tuple[bool, str]:
        """Logs quiz performance into SQLite for progress analytics."""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO quiz_results (user_id, quiz_title, subject, score, total_questions)
                    VALUES (?, ?, ?, ?, ?)
                """, (user_id, quiz_title, subject, score, total_questions))
                conn.commit()
                return True, "Quiz score logged successfully!"
        except Exception as e:
            return False, f"Failed to save quiz score: {str(e)}"