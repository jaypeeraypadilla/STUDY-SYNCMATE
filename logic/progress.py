from typing import List, Dict, Any
from database.db_connection import db


class ProgressTracker:
    """Aggregates user academic performance, note statistics, quiz scores, and completed tasks."""

    def __init__(self):
        self.db = db

    def get_progress_summary(self, user_id: int) -> Dict[str, Any]:
        """Fetches overarching academic stats for summary cards."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Total Study Hours
            cursor.execute("SELECT SUM(duration_minutes) FROM study_sessions WHERE user_id = ?", (user_id,))
            total_minutes = cursor.fetchone()[0] or 0
            
            # Average Quiz Score Percentage
            cursor.execute("""
                SELECT AVG(CAST(score AS FLOAT) / total_questions * 100) 
                FROM quiz_results WHERE user_id = ?
            """, (user_id,))
            avg_score = cursor.fetchone()[0] or 0.0

            # Completed Tasks Count
            cursor.execute("SELECT COUNT(*) FROM tasks WHERE user_id = ? AND status = 'Completed'", (user_id,))
            completed_tasks_count = cursor.fetchone()[0]

            # Total Notes Count
            cursor.execute("SELECT COUNT(*) FROM notes WHERE user_id = ?", (user_id,))
            total_notes = cursor.fetchone()[0]

            return {
                "total_study_hours": round(total_minutes / 60.0, 1),
                "avg_quiz_score": f"{round(avg_score, 1)}%",
                "completed_tasks_count": completed_tasks_count,
                "total_notes": total_notes
            }

    def get_notes_grouped_by_subject(self, user_id: int) -> Dict[str, List[Dict[str, Any]]]:
        """Retrieves all notes grouped by subject with count indicators."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM notes WHERE user_id = ? ORDER BY subject ASC, title ASC
            """, (user_id,))
            rows = cursor.fetchall()

        grouped = {}
        for row in rows:
            note = dict(row)
            subj = note.get("subject", "General") or "General"
            if subj not in grouped:
                grouped[subj] = []
            grouped[subj].append(note)
        return grouped

    def get_quiz_history(self, user_id: int) -> List[Dict[str, Any]]:
        """Retrieves completed quiz scores and timestamps."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM quiz_results WHERE user_id = ? ORDER BY completed_at DESC
            """, (user_id,))
            return [dict(row) for row in cursor.fetchall()]

    def get_completed_tasks(self, user_id: int) -> List[Dict[str, Any]]:
        """Retrieves all tasks marked as 'Completed'."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM tasks WHERE user_id = ? AND status = 'Completed' ORDER BY due_date DESC
            """, (user_id,))
            return [dict(row) for row in cursor.fetchall()]