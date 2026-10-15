import os
import sqlite3
import hashlib
from typing import Tuple, Dict, Any, Optional
from database.db_connection import db

class ProfileManager:
    """Handles fetching and updating user profile data and credentials."""

    def __init__(self):
        self.db = db

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
                SELECT id, username, full_name, age, gender, course, year_level, security_question, created_at
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

            # Return updated dictionary to sync with controller session
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

            # Generate new hash and salt
            new_hash, new_salt = self._hash_password(new_pass)
            cursor.execute("""
                UPDATE users SET password_hash = ?, salt = ? WHERE id = ?
            """, (new_hash, new_salt, user_id))
            conn.commit()

            return True, "Password updated successfully!"