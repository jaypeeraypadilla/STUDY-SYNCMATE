import random
import re
from typing import List, Dict, Any, Tuple, Optional
from database.db_connection import db
from logic.my_notes import NotesManager


class QuizGenerator:
    """Intelligently generates Identification, Multiple Choice, and Enumeration quizzes and flashcards from study notes."""

    def __init__(self):
        self.db = db
        self.notes_manager = NotesManager()

    def get_available_subjects(self, user_id: int) -> List[str]:
        """Retrieves subjects that have saved notes available for quizzing."""
        return self.notes_manager.get_subjects_by_user(user_id)

    def generate_flashcards(self, user_id: int, subject: str) -> List[Dict[str, str]]:
        """Creates intelligent flashcards using note titles (Front) and structured content (Back)."""
        notes = self.notes_manager.get_user_notes(user_id, subject_filter=subject)
        flashcards = []
        
        for note in notes:
            title = note.get("title", "Untitled Topic")
            content = note.get("content", "No content provided.")
            if content.strip():
                flashcards.append({
                    "question": f"Define / Explain: {title}",
                    "answer": content,
                    "subject": subject
                })
        
        random.shuffle(flashcards)
        return flashcards

    def generate_identification_questions(self, user_id: int, subject: str) -> List[Dict[str, Any]]:
        """Generates identification-style questions where the user must name the topic/term based on its description."""
        notes = self.notes_manager.get_user_notes(user_id, subject_filter=subject)
        questions = []

        for note in notes:
            title = note.get("title", "").strip()
            content = note.get("content", "").strip()

            if not title or len(content) < 20:
                continue

            snippet = content[:180] + "..." if len(content) > 180 else content
            questions.append({
                "type": "Identification",
                "prompt": f"Identify the term or topic described below:\n\n\"{snippet}\"",
                "correct_answer": title,
                "subject": subject
            })

        random.shuffle(questions)
        return questions

    def generate_multiple_choice_questions(self, user_id: int, subject: str) -> List[Dict[str, Any]]:
        """Generates intelligent multiple-choice questions with context-aware distractors."""
        notes = self.notes_manager.get_user_notes(user_id, subject_filter=subject)
        if len(notes) < 3:
            return []  # Need at least 3 notes for meaningful distractors

        questions = []
        all_titles = [n["title"] for n in notes if n.get("title")]

        for note in notes:
            correct_title = note["title"]
            correct_content = note["content"]

            if len(correct_content.strip()) < 15:
                continue

            distractors = [t for t in all_titles if t != correct_title]
            if len(distractors) < 2:
                continue

            selected_distractors = random.sample(distractors, min(3, len(distractors)))
            options = selected_distractors + [correct_title]
            random.shuffle(options)

            questions.append({
                "type": "Multiple Choice",
                "prompt": f"Which concept or topic matches this description?\n\n\"{correct_content[:140]}...\"",
                "options": options,
                "correct_answer": correct_title,
                "subject": subject
            })

        random.shuffle(questions)
        return questions

    def generate_enumeration_questions(self, user_id: int, subject: str) -> List[Dict[str, Any]]:
        """Intelligently parses note content to extract list items for enumeration questions."""
        notes = self.notes_manager.get_user_notes(user_id, subject_filter=subject)
        questions = []

        for note in notes:
            title = note.get("title", "").strip()
            content = note.get("content", "").strip()

            if not title or not content:
                continue

            # Parse markdown bullet points or numbered lists
            list_items = []
            lines = content.split('\n')
            for line in lines:
                cleaned_line = line.strip()
                if re.match(r'^([-*•]|\d+[\.)])\s+', cleaned_line):
                    item_text = re.sub(r'^([-*•]|\d+[\.)])\s+', '', cleaned_line).strip()
                    if item_text:
                        list_items.append(item_text)

            # Fallback: Parse comma-separated sequences after colons
            if len(list_items) < 2:
                for line in lines:
                    if ':' in line:
                        parts = line.split(':', 1)
                        if len(parts) > 1 and ',' in parts[1]:
                            sub_items = [s.strip() for s in parts[1].split(',') if s.strip()]
                            if len(sub_items) >= 2:
                                list_items = sub_items
                                break

            if len(list_items) >= 2:
                questions.append({
                    "type": "Enumeration",
                    "prompt": f"Enumerate {len(list_items)} key items related to: **{title}**",
                    "correct_answer": ", ".join(list_items),
                    "items": list_items,
                    "subject": subject
                })

        random.shuffle(questions)
        return questions

    def generate_practice_quiz(self, user_id: int, subject: str) -> List[Dict[str, Any]]:
        """Combines Multiple Choice, Identification, and Enumeration questions into a balanced practice quiz."""
        mc_q = self.generate_multiple_choice_questions(user_id, subject)
        id_q = self.generate_identification_questions(user_id, subject)
        enum_q = self.generate_enumeration_questions(user_id, subject)

        combined = mc_q + id_q + enum_q
        random.shuffle(combined)
        return combined

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