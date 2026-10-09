import os
import sqlite3
import hashlib
from typing import Optional, Tuple, Dict, Any


class AuthManager:
    def __init__(self, db_filename: str = "syncmate.db"):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_dir = os.path.join(base_dir, "database")

        if not os.path.exists(db_dir):
            os.makedirs(db_dir)

        self.db_path = os.path.join(db_dir, db_filename)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
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
            conn.commit()

    def _hash_value(self, text: str, salt: Optional[bytes] = None) -> Tuple[str, str]:
        if salt is None:
            salt = os.urandom(16)

        key = hashlib.pbkdf2_hmac(
            'sha256',
            text.encode('utf-8'),
            salt,
            100000
        )
        return key.hex(), salt.hex()

    def _verify_password(self, text: str, stored_hash: str, stored_salt: str) -> bool:
        salt_bytes = bytes.fromhex(stored_salt)
        new_hash, _ = self._hash_value(text, salt_bytes)
        return new_hash == stored_hash

    def register_user(self, name: str, age: Any, gender: str, course: str, 
                      year_level: str, sec_question: str, sec_answer: str, 
                      username: str, password: str) -> Tuple[bool, str]:
        name = str(name).strip()
        age_str = str(age).strip()
        gender = str(gender).strip()
        course = str(course).strip()
        year_level = str(year_level).strip()
        sec_question = str(sec_question).strip()
        sec_answer = str(sec_answer).strip().lower()
        username = str(username).strip()
        password = str(password).strip()

        if not all([name, age_str, gender, course, year_level, sec_question, sec_answer, username, password]):
            return False, "All fields are required."

        if not age_str.isdigit() or int(age_str) <= 0:
            return False, "Please enter a valid age."

        if len(username) < 3:
            return False, "Username must be at least 3 characters long."

        if len(password) < 6:
            return False, "Password must be at least 6 characters long."

        pwd_hash, pwd_salt = self._hash_value(password)
        ans_hash, ans_salt = self._hash_value(sec_answer)

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO users (
                        full_name, age, gender, course, year_level, 
                        security_question, security_answer_hash, 
                        username, password_hash, salt
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    name, int(age_str), gender, course, year_level, 
                    sec_question, f"{ans_hash}:{ans_salt}", 
                    username, pwd_hash, pwd_salt
                ))
                conn.commit()
                return True, "User registered successfully!"

        except sqlite3.IntegrityError:
            return False, "Username already exists. Please choose a different username."
        except Exception as e:
            return False, f"An error occurred: {str(e)}"

    def login_user(self, username: str, password: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        username = username.strip()
        password = password.strip()

        if not username or not password:
            return False, "Username and password are required.", None

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, full_name, age, gender, course, year_level, password_hash, salt 
                FROM users WHERE username = ?
            """, (username,))
            user = cursor.fetchone()

        if not user:
            return False, "Invalid username or password.", None

        user_id, full_name, age, gender, course, year_level, stored_hash, stored_salt = user

        # Clean method call without type hints or 'self' argument
        if self._verify_password(password, stored_hash, stored_salt):
            user_data = {
                "id": user_id,
                "username": username,
                "full_name": full_name,
                "age": age,
                "gender": gender,
                "course": course,
                "year_level": year_level
            }
            return True, "Login successful!", user_data
        else:
            return False, "Invalid username or password.", None

    def get_security_question(self, username: str) -> Tuple[bool, str, Optional[str]]:
        username = username.strip()

        if not username:
            return False, "Username is required.", None

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT security_question FROM users WHERE username = ?
            """, (username,))
            result = cursor.fetchone()

        if result:
            return True, "Security question retrieved successfully.", result[0]
        else:
            return False, "Username not found.", None

    def reset_password(self, username: str, sec_answer: str, new_password: str) -> Tuple[bool, str]:
        username = username.strip()
        sec_answer = sec_answer.strip().lower()
        new_password = new_password.strip()

        if not username or not sec_answer or not new_password:
            return False, "All fields are required."

        if len(new_password) < 6:
            return False, "New password must be at least 6 characters long."

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT security_answer_hash FROM users WHERE username = ?
            """, (username,))
            result = cursor.fetchone()

            if not result:
                return False, "Username not found."

            # Security answer hash stored as "hash:salt"
            sec_hash_salt = result[0]
            stored_ans_hash, stored_ans_salt = sec_hash_salt.split(":")

            if not self._verify_password(sec_answer, stored_ans_hash, stored_ans_salt):
                return False, "Incorrect security answer."

            new_hash, new_salt = self._hash_value(new_password)
            cursor.execute("""
                UPDATE users 
                SET password_hash = ?, salt = ? 
                WHERE username = ?
            """, (new_hash, new_salt, username))
            conn.commit()

        return True, "Password reset successfully! You can now log in."