import time
import json
import random
import re
from typing import List, Dict, Any, Tuple, Optional
from database.db_connection import db
from logic.my_notes import NotesManager

try:
    from google import genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


class QuizGenerator:
    """Intelligently generates Identification, Multiple Choice, Enumeration, and optimized Flashcards from notes using Gemini AI."""

    def __init__(self):
        self.db = db
        self.notes_manager = NotesManager()
        self.api_key = "AQ.Ab8RN6KGAyKblVRxBciJa7LKQsJGjmGdoJZ4kNn8c_V1oZVC4Q"
        self.client = None

        if GENAI_AVAILABLE:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                print(f"Failed to initialize Gemini Client: {e}")

    def get_available_subjects(self, user_id: int) -> List[str]:
        """Retrieves subjects that have saved notes available for quizzing."""
        return self.notes_manager.get_subjects_by_user(user_id)

    def _call_gemini_ai(self, prompt: str) -> Optional[str]:
        """Sends prompt to Gemini API with automatic retry logic for temporary 503 high-demand errors."""
        if not self.client:
            return None
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.client.models.generate_content(
                    model='gemini-3.8-flash',
                    contents=prompt,
                )
                return response.text
            except Exception as e:
                print(f"Gemini API Error (Attempt {attempt + 1}/{max_retries}): {e}")
                if "503" in str(e) or "UNAVAILABLE" in str(e):
                    if attempt < max_retries - 1:
                        time.sleep(2 * (attempt + 1))
                        continue
                break
        return None

    def _extract_json_from_response(self, text: str) -> Optional[Any]:
        """Extracts JSON structure from markdown code blocks in AI response."""
        if not text:
            return None
        try:
            return json.loads(text.strip())
        except json.JSONDecodeError:
            pass

        match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
        if match:
            try:
                return json.loads(match.group(1).strip())
            except json.JSONDecodeError:
                pass
        return None

    # =============================================================
    # OPTIMIZED FLASHCARDS GENERATION
    # =============================================================
    def generate_flashcards(self, user_id: int, subject: str) -> List[Dict[str, str]]:
        """Generates structured, professional flashcards with front prompt, back explanation, and hint."""
        notes = self.notes_manager.get_user_notes(user_id, subject_filter=subject)
        if not notes:
            return []

        notes_dump = "\n\n".join([f"Title: {n['title']}\nContent: {n['content']}" for n in notes])
        prompt = (
            f"You are an expert instructional designer and tutor. Review the following study notes for subject '{subject}' "
            f"and create a JSON list of high-yield study flashcards.\n"
            f"Each flashcard must be structured with:\n"
            f"- 'front': A concise term, key concept, or direct question.\n"
            f"- 'back': A clear, comprehensive definition, explanation, or answer.\n"
            f"- 'hint': A short, helpful clue to jog memory without giving away the full answer.\n\n"
            f"Notes:\n{notes_dump}\n\n"
            f"Output strictly in JSON format as a list of objects: "
            f"[{{\"front\": \"...\", \"back\": \"...\", \"hint\": \"...\"}}]"
        )

        ai_res = self._call_gemini_ai(prompt)
        parsed = self._extract_json_from_response(ai_res)

        if parsed and isinstance(parsed, list):
            flashcards = []
            for item in parsed:
                if "front" in item and "back" in item:
                    flashcards.append({
                        "front": item["front"],
                        "back": item["back"],
                        "hint": item.get("hint", "Review your saved notes for this concept."),
                        "subject": subject
                    })
            if flashcards:
                random.shuffle(flashcards)
                return flashcards

        # Fallback to local structured generator
        return self._local_generate_flashcards(notes, subject)

    def _local_generate_flashcards(self, notes: List[Dict], subject: str) -> List[Dict[str, str]]:
        flashcards = []
        for note in notes:
            title = note.get("title", "Untitled Topic")
            content = note.get("content", "No content provided.")
            if content.strip():
                flashcards.append({
                    "front": f"What is {title}?",
                    "back": content,
                    "hint": f"Look up notes under topic: {title}",
                    "subject": subject
                })
        random.shuffle(flashcards)
        return flashcards

    # =============================================================
    # IDENTIFICATION QUESTIONS
    # =============================================================
    def generate_identification_questions(self, user_id: int, subject: str) -> List[Dict[str, Any]]:
        """Generates AI identification questions where the user names the term based on its description."""
        notes = self.notes_manager.get_user_notes(user_id, subject_filter=subject)
        if not notes:
            return []

        notes_dump = "\n\n".join([f"Term/Topic: {n['title']}\nDescription: {n['content']}" for n in notes])
        prompt = (
            f"You are an expert AI professor. Based on the following study notes for '{subject}', generate "
            f"identification questions. Each question requires the user to identify the term/topic from its description.\n\n"
            f"Notes:\n{notes_dump}\n\n"
            f"Output strictly in JSON format as a list of objects with keys: "
            f"\"type\": \"Identification\", \"prompt\": \"...\", \"correct_answer\": \"...\""
        )

        ai_res = self._call_gemini_ai(prompt)
        parsed = self._extract_json_from_response(ai_res)

        if parsed and isinstance(parsed, list):
            questions = []
            for item in parsed:
                if "prompt" in item and "correct_answer" in item:
                    questions.append({
                        "type": "Identification",
                        "prompt": item["prompt"],
                        "correct_answer": item["correct_answer"],
                        "subject": subject
                    })
            if questions:
                random.shuffle(questions)
                return questions

        return self._local_generate_identification(notes, subject)

    def _local_generate_identification(self, notes: List[Dict], subject: str) -> List[Dict[str, Any]]:
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

    # =============================================================
    # MULTIPLE CHOICE QUESTIONS
    # =============================================================
    def generate_multiple_choice_questions(self, user_id: int, subject: str) -> List[Dict[str, Any]]:
        """Generates AI multiple-choice questions with context-aware options and distractors."""
        notes = self.notes_manager.get_user_notes(user_id, subject_filter=subject)
        if not notes:
            return []

        notes_dump = "\n\n".join([f"Topic: {n['title']}\nContent: {n['content']}" for n in notes])
        prompt = (
            f"You are an expert AI quiz creator. Based on these study notes for '{subject}', create multiple choice questions. "
            f"Each question must have 4 options (one correct answer and three plausible distractors).\n\n"
            f"Notes:\n{notes_dump}\n\n"
            f"Output strictly in JSON format as a list of objects with keys: "
            f"\"type\": \"Multiple Choice\", \"prompt\": \"...\", \"options\": [\"opt1\", \"opt2\", \"opt3\", \"opt4\"], \"correct_answer\": \"...\""
        )

        ai_res = self._call_gemini_ai(prompt)
        parsed = self._extract_json_from_response(ai_res)

        if parsed and isinstance(parsed, list):
            questions = []
            for item in parsed:
                if "prompt" in item and "options" in item and "correct_answer" in item:
                    questions.append({
                        "type": "Multiple Choice",
                        "prompt": item["prompt"],
                        "options": item["options"],
                        "correct_answer": item["correct_answer"],
                        "subject": subject
                    })
            if questions:
                random.shuffle(questions)
                return questions

        return self._local_generate_multiple_choice(notes, subject)

    def _local_generate_multiple_choice(self, notes: List[Dict], subject: str) -> List[Dict[str, Any]]:
        if len(notes) < 3:
            return []
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

    # =============================================================
    # ENUMERATION QUESTIONS
    # =============================================================
    def generate_enumeration_questions(self, user_id: int, subject: str) -> List[Dict[str, Any]]:
        """Generates AI enumeration questions extracting lists from notes."""
        notes = self.notes_manager.get_user_notes(user_id, subject_filter=subject)
        if not notes:
            return []

        notes_dump = "\n\n".join([f"Topic: {n['title']}\nContent: {n['content']}" for n in notes])
        prompt = (
            f"You are an expert AI quiz generator. Based on these study notes for '{subject}', generate enumeration questions "
            f"where students list key items or steps related to a specific topic.\n\n"
            f"Notes:\n{notes_dump}\n\n"
            f"Output strictly in JSON format as a list of objects with keys: "
            f"\"type\": \"Enumeration\", \"prompt\": \"...\", \"items\": [\"item1\", \"item2\"], \"correct_answer\": \"item1, item2\""
        )

        ai_res = self._call_gemini_ai(prompt)
        parsed = self._extract_json_from_response(ai_res)

        if parsed and isinstance(parsed, list):
            questions = []
            for item in parsed:
                if "prompt" in item and "items" in item:
                    items_list = item["items"]
                    questions.append({
                        "type": "Enumeration",
                        "prompt": item["prompt"],
                        "correct_answer": ", ".join(items_list),
                        "items": items_list,
                        "subject": subject
                    })
            if questions:
                random.shuffle(questions)
                return questions

        return self._local_generate_enumeration(notes, subject)

    def _local_generate_enumeration(self, notes: List[Dict], subject: str) -> List[Dict[str, Any]]:
        questions = []
        for note in notes:
            title = note.get("title", "").strip()
            content = note.get("content", "").strip()
            if not title or not content:
                continue

            list_items = []
            lines = content.split('\n')
            for line in lines:
                cleaned_line = line.strip()
                if re.match(r'^([-*•]|\d+[\.)])\s+', cleaned_line):
                    item_text = re.sub(r'^([-*•]|\d+[\.)])\s+', '', cleaned_line).strip()
                    if item_text:
                        list_items.append(item_text)

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