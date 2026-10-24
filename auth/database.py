"""
IPL Analytics Pro - User Database Management
Manages local SQLite database for secure user accounts, registration, and authentication.
"""

import os
import sqlite3
from datetime import datetime

DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DB_DIR, "users.db")

def get_connection():
    """Returns a SQLite database connection with row factory enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the SQLite users table schema if it does not already exist."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL,
            role TEXT DEFAULT 'analyst'
        )
    """)
    conn.commit()
    conn.close()

def create_user(username: str, email: str, password_hash: str, role: str = "analyst"):
    """Inserts a new user record into the database."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, created_at, role)
            VALUES (?, ?, ?, ?, ?)
        """, (username.strip().lower(), email.strip().lower(), password_hash, datetime.now().isoformat(), role))
        conn.commit()
        return True, "User registered successfully."
    except sqlite3.IntegrityError as e:
        err_msg = str(e)
        if "UNIQUE constraint failed: users.username" in err_msg:
            return False, "Username already exists. Please choose another username."
        elif "UNIQUE constraint failed: users.email" in err_msg:
            return False, "Email already registered. Please log in or use a different email."
        return False, f"Registration error: {err_msg}"
    finally:
        conn.close()

def get_user_by_username(username: str):
    """Retrieves a user record by username."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username.strip().lower(),))
    user = cursor.fetchone()
    conn.close()
    return user

def get_user_by_email(email: str):
    """Retrieves a user record by email."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email.strip().lower(),))
    user = cursor.fetchone()
    conn.close()
    return user
