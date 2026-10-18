import os
import sqlite3
import hashlib
import shutil
from typing import Tuple, Dict, Any, Optional
from database.db_connection import db

class ProfileManager:
    """Handles fetching and updating user profile data, profile pictures, and credentials."""

    def __init__(self):
        self.db = db
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.profile_pics_dir = os.path.join(base_dir, "uploads", "profile_pics")
        os.makedirs(self.profile_pics_dir, exist_ok=True)
        self._ensure_profile_pic_column()

    def _ensure_profile_pic_column(self) -> None:
        """Migrates database if profile_pic_path column is missing in users table."""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA table_info(users)")
                columns = [row["name"] for row in cursor.fetchall()]
                if "profile_pic_path" not in columns:
                    cursor.execute("ALTER TABLE users ADD COLUMN profile_pic_path TEXT DEFAULT NULL")
                    conn.commit()
        except Exception as e:
            print(f"[ProfileManager] Migration check note: {e}")

    def _hash_password(self, password: str, salt: Optional[bytes] = None) -> Tuple[str, str]:
        """Hashes password using PBKDF2 HMAC SHA-256."""
        if salt is None:
            salt = os.urandom(16)
        key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
        return key.hex(), salt.hex()

    def get_user_profile(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Retrieves full profile details for a given user ID."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, username, full_name, age, gender, course, year_level, security_question, profile_pic_path, created_at
                FROM users WHERE id = ?
            """, (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def update_profile(
        self, user_id: int, full_name: str, age: str, gender: str, course: str, year_level: str
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Updates personal information for the user."""
        full_name = full_name.strip()
        age_str = str(age).strip()
        gender = gender.strip()
        course = course.strip()
        year_level = year_level.strip()

        if not all([full_name, age_str, gender, course, year_level]):
            return False, "All profile fields are required.", None

        if not age_str.isdigit() or int(age_str) <= 0:
            return False, "Please enter a valid age.", None

        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE users
                    SET full_name = ?, age = ?, gender = ?, course = ?, year_level = ?
                    WHERE id = ?
                """, (full_name, int(age_str), gender, course, year_level, user_id))
                conn.commit()

            updated_data = {
                "id": user_id,
                "full_name": full_name,
                "age": int(age_str),
                "gender": gender,
                "course": course,
                "year_level": year_level
            }
            return True, "Profile updated successfully!", updated_data

        except Exception as e:
            return False, f"Failed to update profile: {str(e)}", None

    def update_profile_picture(self, user_id: int, source_path: str) -> Tuple[bool, str, Optional[str]]:
        """Copies an image file to profile_pics directory and updates database record."""
        if not os.path.exists(source_path):
            return False, "Source image file not found.", None

        ext = os.path.splitext(source_path)[1].lower()
        if ext not in {".png", ".jpg", ".jpeg", ".webp", ".bmp"}:
            return False, "Invalid image format. Please select PNG, JPG, JPEG, or WEBP.", None

        unique_filename = f"user_{user_id}_{os.path.basename(source_path)}"
        destination_path = os.path.join(self.profile_pics_dir, unique_filename)

        try:
            shutil.copy2(source_path, destination_path)

            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE users SET profile_pic_path = ? WHERE id = ?
                """, (destination_path, user_id))
                conn.commit()

            return True, "Profile picture updated successfully!", destination_path
        except Exception as e:
            return False, f"Failed to update profile picture: {str(e)}", None

    def update_security_answer(self, user_id: int, security_answer: str) -> Tuple[bool, str]:
        """Updates the user's security answer securely with a new hash."""
        security_answer = security_answer.strip().lower()
        if not security_answer:
            return False, "Security answer cannot be empty."

        try:
            answer_hash, _ = self._hash_password(security_answer)
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE users SET security_answer_hash = ? WHERE id = ?
                """, (answer_hash, user_id))
                conn.commit()
            return True, "Security answer updated successfully!"
        except Exception as e:
            return False, f"Failed to update security answer: {str(e)}"

    def change_password(self, user_id: int, current_pass: str, new_pass: str) -> Tuple[bool, str]:
        """Verifies old password and updates user credentials with new PBKDF2 hash and salt."""
        current_pass = current_pass.strip()
        new_pass = new_pass.strip()

        if not current_pass or not new_pass:
            return False, "Both current and new password are required."

        if len(new_pass) < 6:
            return False, "New password must be at least 6 characters long."

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT password_hash, salt FROM users WHERE id = ?", (user_id,))
            result = cursor.fetchone()

            if not result:
                return False, "User account not found."

            stored_hash, stored_salt = result["password_hash"], result["salt"]
            salt_bytes = bytes.fromhex(stored_salt)
            check_hash, _ = self._hash_password(current_pass, salt_bytes)

            if check_hash != stored_hash:
                return False, "Current password is incorrect."

            new_hash, new_salt = self._hash_password(new_pass)
            cursor.execute("""
                UPDATE users SET password_hash = ?, salt = ? WHERE id = ?
            """, (new_hash, new_salt, user_id))
            conn.commit()

            return True, "Password updated successfully!"