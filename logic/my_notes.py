import os
import json
import shutil
import uuid
from typing import List, Dict, Any, Optional, Tuple
from database.db_connection import db


class NotesManager:
    """Handles CRUD operations for notes and manages picture, video, and file attachments."""

    ALLOWED_IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"}
    ALLOWED_VIDEO_EXTS = {".mp4", ".mkv", ".avi", ".mov", ".webm"}

    def __init__(self):
        self.db = db
        # Base directory for storing uploaded note attachments
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.media_dir = os.path.join(base_dir, "uploads", "notes_media")
        os.makedirs(self.media_dir, exist_ok=True)
        self._ensure_attachment_column()

    def _ensure_attachment_column(self) -> None:
        """Migrates database if attachments_json column is missing."""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA table_info(notes)")
                columns = [row["name"] for row in cursor.fetchall()]
                if "attachments_json" not in columns:
                    cursor.execute("ALTER TABLE notes ADD COLUMN attachments_json TEXT DEFAULT '[]'")
                    conn.commit()
        except Exception as e:
            print(f"[NotesManager] Migration check note: {e}")

    # ==========================================
    # FILE / MEDIA MANAGEMENT
    # ==========================================

    def _categorize_file(self, file_path: str) -> str:
        """Categorizes a file into 'image', 'video', or 'file' based on extension."""
        ext = os.path.splitext(file_path)[1].lower()
        if ext in self.ALLOWED_IMAGE_EXTS:
            return "image"
        elif ext in self.ALLOWED_VIDEO_EXTS:
            return "video"
        return "file"

    def process_attachment(self, source_path: str) -> Optional[Dict[str, str]]:
        """Copies an attached file to the project's internal uploads directory."""
        if not os.path.exists(source_path):
            return None

        original_filename = os.path.basename(source_path)
        ext = os.path.splitext(original_filename)[1]
        
        # Generate a unique filename to prevent overwrites
        unique_filename = f"{uuid.uuid4().hex}{ext}"
        destination_path = os.path.join(self.media_dir, unique_filename)

        try:
            shutil.copy2(source_path, destination_path)
            return {
                "original_name": original_filename,
                "saved_path": destination_path,
                "file_type": self._categorize_file(source_path)
            }
        except Exception as e:
            print(f"Error saving attachment {original_filename}: {e}")
            return None

    # ==========================================
    # CRUD OPERATIONS
    # ==========================================

    def create_note(
        self, 
        user_id: int, 
        title: str, 
        content: str, 
        subject: str = "General", 
        attachment_paths: Optional[List[str]] = None,
        tags: Optional[List[str]] = None
    ) -> Tuple[bool, str, Optional[int]]:
        """Creates a new note with subject, content, and attached files/pictures/videos."""
        title = title.strip()
        content = content.strip()
        subject = subject.strip() if subject else "General"

        if not title:
            return False, "Note title cannot be empty.", None

        # Process and save file attachments
        processed_attachments = []
        if attachment_paths:
            for path in attachment_paths:
                media_info = self.process_attachment(path)
                if media_info:
                    processed_attachments.append(media_info)

        tags_json = json.dumps(tags or [])
        attachments_json = json.dumps(processed_attachments)

        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO notes (user_id, title, content, subject, tags_json, attachments_json)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (user_id, title, content, subject, tags_json, attachments_json))
                conn.commit()
                new_id = cursor.lastrowid
                return True, "Note saved successfully!", new_id
        except Exception as e:
            return False, f"Database error: {str(e)}", None

    def get_user_notes(self, user_id: int, subject_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieves user notes. Decodes JSON tags and attachments automatically."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            if subject_filter and subject_filter != "All":
                cursor.execute("""
                    SELECT * FROM notes 
                    WHERE user_id = ? AND subject = ? 
                    ORDER BY updated_at DESC
                """, (user_id, subject_filter))
            else:
                cursor.execute("""
                    SELECT * FROM notes 
                    WHERE user_id = ? 
                    ORDER BY updated_at DESC
                """, (user_id,))
            
            rows = cursor.fetchall()

        notes = []
        for row in rows:
            note_dict = dict(row)
            # Parse JSON strings into standard Python lists/dicts
            note_dict["tags"] = json.loads(note_dict.get("tags_json") or "[]")
            note_dict["attachments"] = json.loads(note_dict.get("attachments_json") or "[]")
            notes.append(note_dict)

        return notes

    def get_subjects_by_user(self, user_id: int) -> List[str]:
        """Gets all unique subject names created by the user for dropdown menus."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT subject FROM notes WHERE user_id = ? ORDER BY subject ASC
            """, (user_id,))
            subjects = [row["subject"] for row in cursor.fetchall()]
            return subjects if subjects else ["General"]

    def update_note(
        self, 
        note_id: int, 
        title: str, 
        content: str, 
        subject: str, 
        existing_attachments: List[Dict[str, str]], 
        new_attachment_paths: Optional[List[str]] = None,
        tags: Optional[List[str]] = None
    ) -> Tuple[bool, str]:
        """Updates an existing note, merging existing and new attachments."""
        title = title.strip()
        if not title:
            return False, "Title cannot be empty."

        updated_attachments = list(existing_attachments)
        if new_attachment_paths:
            for path in new_attachment_paths:
                media_info = self.process_attachment(path)
                if media_info:
                    updated_attachments.append(media_info)

        tags_json = json.dumps(tags or [])
        attachments_json = json.dumps(updated_attachments)

        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE notes
                    SET title = ?, content = ?, subject = ?, tags_json = ?, attachments_json = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (title, content, subject, tags_json, attachments_json, note_id))
                conn.commit()
                return True, "Note updated successfully!"
        except Exception as e:
            return False, f"Failed to update note: {str(e)}"

    def delete_note(self, note_id: int) -> Tuple[bool, str]:
        """Deletes a note and cleans up its stored media files from disk."""
        try:
            # Fetch attachments to remove files from drive
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT attachments_json FROM notes WHERE id = ?", (note_id,))
                row = cursor.fetchone()
                
                if row and row["attachments_json"]:
                    attachments = json.loads(row["attachments_json"])
                    for item in attachments:
                        file_path = item.get("saved_path")
                        if file_path and os.path.exists(file_path):
                            try:
                                os.remove(file_path)
                            except OSError as err:
                                print(f"Could not remove media file {file_path}: {err}")

                cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
                conn.commit()
                return True, "Note and associated media deleted."
        except Exception as e:
            return False, f"Delete failed: {str(e)}"