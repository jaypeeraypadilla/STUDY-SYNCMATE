import os
import sys
import sqlite3
from typing import List, Dict, Any, Optional

class DatabaseManager:
    def __init__(self, db_filename: str = "syncmate.db"):
        """Initializes database path inside the database directory and creates required tables."""
        try:
            if getattr(sys, 'frozen', False):
                # If running as a compiled .exe, save the database right next to the .exe file
                base_dir = os.path.dirname(sys.executable)
            else:
                # Running as a normal Python script
                base_dir = os.path.dirname(os.path.abspath(__file__))
                
            self.db_path = os.path.join(base_dir, db_filename)
            self.init_db()
        except Exception as e:
            print(f"[DatabaseManager Critical Error] Failed to initialize database at path: {e}")

    def get_connection(self) -> sqlite3.Connection:
        """Establishes SQLite connection with foreign key enforcement and row factory."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enables column access by key (e.g., row["username"])
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def init_db(self) -> None:
        """Creates all relational tables required for Study SyncMate modules."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # 1. USERS TABLE (Authentication & Profile Management)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    full_name TEXT NOT NULL,
                    age INTEGER NOT NULL,
                    gender TEXT NOT NULL,
                    course TEXT NOT NULL,
                    year_level TEXT NOT NULL,
                    security_question TEXT NOT NULL,
                    security_answer_hash TEXT NOT NULL,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 2. NOTES TABLE (Rich Text Notes with JSON Tags & File/Media Attachments)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    subject TEXT DEFAULT 'General',
                    tags_json TEXT DEFAULT '[]',
                    attachments_json TEXT DEFAULT '[]', -- Stores array [{filename, saved_path, file_type}]
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            """)

            # 3. SCHEDULE & TASKS TABLE (Planner & Reminders)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    due_date TEXT NOT NULL,
                    priority TEXT DEFAULT 'Medium',
                    status TEXT DEFAULT 'Pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            """)

            # 4. QUIZZES TABLE (Flashcards & Quiz Records)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS quiz_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    quiz_title TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    score INTEGER NOT NULL,
                    total_questions INTEGER NOT NULL,
                    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            """)

            # 5. PROGRESS & STUDY SESSIONS TABLE (Analytics)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS study_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    subject TEXT NOT NULL,
                    duration_minutes INTEGER NOT NULL,
                    session_date DATE DEFAULT (DATE('now')),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            """)

            conn.commit()

    # ==========================================
    # NOTES MODULE CRUD METHODS (With Media Support)
    # ==========================================
    def create_note(
        self, user_id: int, title: str, content: str, subject: str = "General", 
        tags_json: str = "[]", attachments_json: str = "[]"
    ) -> int:
        """Inserts a new note with subject, tags, and media attachments."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO notes (user_id, title, content, subject, tags_json, attachments_json)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, title, content, subject, tags_json, attachments_json))
            conn.commit()
            return cursor.lastrowid

    def get_user_notes(self, user_id: int, subject_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieves all notes for a specific user, with optional subject filtering."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if subject_filter and subject_filter != "All":
                cursor.execute("""
                    SELECT * FROM notes WHERE user_id = ? AND subject = ? ORDER BY updated_at DESC
                """, (user_id, subject_filter))
            else:
                cursor.execute("""
                    SELECT * FROM notes WHERE user_id = ? ORDER BY updated_at DESC
                """, (user_id,))
            return [dict(row) for row in cursor.fetchall()]

    def update_note(
        self, note_id: int, title: str, content: str, subject: str, 
        tags_json: str, attachments_json: str
    ) -> bool:
        """Updates note content, subject, tags, and attachments."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE notes
                SET title = ?, content = ?, subject = ?, tags_json = ?, attachments_json = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (title, content, subject, tags_json, attachments_json, note_id))
            conn.commit()
            return cursor.rowcount > 0

    def delete_note(self, note_id: int) -> bool:
        """Deletes a note by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
            conn.commit()
            return cursor.rowcount > 0

    # ==========================================
    # SCHEDULE & TASKS CRUD METHODS
    # ==========================================
    def create_task(self, user_id: int, title: str, description: str, due_date: str, priority: str = "Medium") -> int:
        """Adds a task to the study schedule."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO tasks (user_id, title, description, due_date, priority, status)
                VALUES (?, ?, ?, ?, ?, 'Pending')
            """, (user_id, title, description, due_date, priority))
            conn.commit()
            return cursor.lastrowid

    def update_task(self, task_id: int, title: str, description: str, due_date: str, priority: str) -> bool:
        """Updates task parameters (title, description, due_date, priority)."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE tasks 
                SET title = ?, description = ?, due_date = ?, priority = ? 
                WHERE id = ?
            """, (title, description, due_date, priority, task_id))
            conn.commit()
            return cursor.rowcount > 0

    def get_user_tasks(self, user_id: int, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieves tasks for a user, with optional status filtering ('Pending', 'Completed')."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if status_filter and status_filter != "All":
                cursor.execute("""
                    SELECT * FROM tasks WHERE user_id = ? AND status = ? ORDER BY due_date ASC
                """, (user_id, status_filter))
            else:
                cursor.execute("""
                    SELECT * FROM tasks WHERE user_id = ? ORDER BY due_date ASC
                """, (user_id,))
            return [dict(row) for row in cursor.fetchall()]

    def update_task_status(self, task_id: int, status: str) -> bool:
        """Updates task status ('Pending', 'In Progress', 'Completed')."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE tasks SET status = ? WHERE id = ?", (status, task_id))
            conn.commit()
            return cursor.rowcount > 0

    def delete_task(self, task_id: int) -> bool:
        """Deletes a task by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            conn.commit()
            return cursor.rowcount > 0

    # ==========================================
    # QUIZZES & PROGRESS ANALYTICS METHODS
    # ==========================================
    def log_quiz_score(self, user_id: int, quiz_title: str, subject: str, score: int, total_questions: int) -> int:
        """Logs completed quiz score into history."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO quiz_results (user_id, quiz_title, subject, score, total_questions)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, quiz_title, subject, score, total_questions))
            conn.commit()
            return cursor.lastrowid

    def log_study_session(self, user_id: int, subject: str, duration_minutes: int) -> int:
        """Logs time spent studying for progress analytics."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO study_sessions (user_id, subject, duration_minutes)
                VALUES (?, ?, ?)
            """, (user_id, subject, duration_minutes))
            conn.commit()
            return cursor.lastrowid

    def get_user_stats_summary(self, user_id: int) -> Dict[str, Any]:
        """Fetches aggregated statistics for the Dashboard view."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM notes WHERE user_id = ?", (user_id,))
            total_notes = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM tasks WHERE user_id = ? AND status != 'Completed'", (user_id,))
            pending_tasks = cursor.fetchone()[0]

            cursor.execute("SELECT SUM(duration_minutes) FROM study_sessions WHERE user_id = ?", (user_id,))
            total_minutes = cursor.fetchone()[0] or 0

            cursor.execute("""
                SELECT AVG(CAST(score AS FLOAT) / total_questions * 100) 
                FROM quiz_results WHERE user_id = ?
            """, (user_id,))
            avg_quiz_score = cursor.fetchone()[0] or 0.0

            return {
                "total_notes": total_notes,
                "pending_tasks": pending_tasks,
                "total_study_hours": round(total_minutes / 60.0, 1),
                "avg_quiz_score": f"{round(avg_quiz_score, 1)}%"
            }

# Singleton database instance for convenient app-wide usage
db = DatabaseManager()