import sqlite3
from typing import List, Dict, Any, Tuple, Optional
from database.db_connection import db

class ScheduleManager:
    """Manages tasks, study planner items, and study session logs in SQLite."""

    def __init__(self):
        self.db = db

    # =============================================================
    # TASK MANAGEMENT (CRUD)
    # =============================================================

    def create_task(
        self, user_id: int, title: str, description: str, due_date: str, priority: str = "Medium"
    ) -> Tuple[bool, str]:
        """Creates a new task with due date (YYYY-MM-DD) and priority."""
        title = title.strip()
        description = description.strip()
        due_date = due_date.strip()

        if not title:
            return False, "Task title cannot be empty."

        if not due_date:
            return False, "Due date is required."

        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO tasks (user_id, title, description, due_date, priority, status)
                    VALUES (?, ?, ?, ?, ?, 'Pending')
                """, (user_id, title, description, due_date, priority))
                conn.commit()
                return True, "Task added successfully!"
        except Exception as e:
            return False, f"Failed to add task: {str(e)}"

    def get_user_tasks(self, user_id: int, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieves tasks for a user ordered by due date."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            if status_filter and status_filter != "All":
                cursor.execute("""
                    SELECT id, title, description, due_date, priority, status, created_at
                    FROM tasks WHERE user_id = ? AND status = ?
                    ORDER BY due_date ASC
                """, (user_id, status_filter))
            else:
                cursor.execute("""
                    SELECT id, title, description, due_date, priority, status, created_at
                    FROM tasks WHERE user_id = ?
                    ORDER BY due_date ASC
                """, (user_id,))
            
            return [dict(row) for row in cursor.fetchall()]

    def get_task_dates_for_month(self, user_id: int, year: int, month: int) -> List[str]:
        """Returns a list of unique due dates that have pending/active tasks for a given month."""
        month_str = f"{year:04d}-{month:02d}"
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT due_date FROM tasks 
                WHERE user_id = ? AND due_date LIKE ? AND status != 'Completed'
            """, (user_id, f"{month_str}%"))
            return [row["due_date"] for row in cursor.fetchall()]

    def update_task_status(self, task_id: int, new_status: str) -> Tuple[bool, str]:
        """Updates task status ('Pending', 'In Progress', 'Completed')."""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE tasks SET status = ? WHERE id = ?
                """, (new_status, task_id))
                conn.commit()
                return True, "Task status updated!"
        except Exception as e:
            return False, f"Failed to update task: {str(e)}"

    def delete_task(self, task_id: int) -> Tuple[bool, str]:
        """Deletes a task from the database."""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
                conn.commit()
                return True, "Task deleted successfully!"
        except Exception as e:
            return False, f"Delete failed: {str(e)}"

    # =============================================================
    # STUDY SESSION LOGS
    # =============================================================

    def log_study_session(self, user_id: int, subject: str, duration_minutes: int) -> Tuple[bool, str]:
        """Logs a completed study session duration."""
        subject = subject.strip() if subject else "General Study"
        if duration_minutes <= 0:
            return False, "Duration must be greater than 0 minutes."

        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO study_sessions (user_id, subject, duration_minutes)
                    VALUES (?, ?, ?)
                """, (user_id, subject, duration_minutes))
                conn.commit()
                return True, "Study session logged successfully!"
        except Exception as e:
            return False, f"Failed to log study session: {str(e)}"