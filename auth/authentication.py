"""
IPL Analytics Pro - Authentication Engine
Provides bcrypt password hashing, input validation, session management, and access protection.
"""

import re
import bcrypt
import streamlit as st
from .database import init_db, create_user, get_user_by_username, get_user_by_email

# Pre-defined test account for local verification
DEMO_USERNAME = "demo"
DEMO_PASSWORD = "IPL@Analytics2026"
DEMO_EMAIL = "demo@iplanaytics.pro"

def hash_password(password: str) -> str:
    """Hashes a plaintext password using bcrypt with salt."""
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")

def check_password(password: str, hashed: str) -> bool:
    """Verifies a plaintext password against a stored bcrypt hash."""
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False

def validate_registration_inputs(username: str, email: str, password: str, confirm_password: str):
    """Validates registration input rules and formatting."""
    username = username.strip()
    email = email.strip()
    
    if len(username) < 3:
        return False, "Username must be at least 3 characters long."
    if not re.match(r"^[a-zA-Z0-9_]+$", username):
        return False, "Username can only contain alphanumeric characters and underscores."
    
    email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    if not re.match(email_regex, email):
        return False, "Please provide a valid email address (e.g., user@example.com)."
        
    if len(password) < 6:
        return False, "Password must be at least 6 characters long."
    if password != confirm_password:
        return False, "Passwords do not match. Please re-enter."
        
    return True, "Valid inputs."

def register_new_user(username: str, email: str, password: str, confirm_password: str):
    """Registers a new user account with hashed password storage."""
    is_valid, msg = validate_registration_inputs(username, email, password, confirm_password)
    if not is_valid:
        return False, msg
        
    pwd_hash = hash_password(password)
    success, db_msg = create_user(username, email, pwd_hash)
    return success, db_msg

def authenticate_user(identifier: str, password: str):
    """Authenticates credentials against the SQLite database."""
    identifier = identifier.strip().lower()
    
    # Check if username or email
    user = get_user_by_username(identifier)
    if user is None:
        user = get_user_by_email(identifier)
        
    if user is None:
        return False, "Invalid username or email. Please check your credentials.", None
        
    if check_password(password, user["password_hash"]):
        user_info = {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "role": user["role"]
        }
        return True, "Login successful.", user_info
    else:
        return False, "Incorrect password. Please try again.", None

def seed_demo_account():
    """Initializes database schema and ensures the local demo account is ready."""
    init_db()
    existing = get_user_by_username(DEMO_USERNAME)
    if existing is None:
        pwd_hash = hash_password(DEMO_PASSWORD)
        create_user(DEMO_USERNAME, DEMO_EMAIL, pwd_hash, role="admin")

def init_session_state():
    """Initializes Streamlit session authentication keys with default active RR scout session."""
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = True
    if "user" not in st.session_state:
        st.session_state["user"] = {
            "id": 1,
            "username": "RR Scout",
            "email": "scout@rajasthanroyals.com",
            "role": "analyst"
        }

def is_authenticated() -> bool:
    """Checks whether the current session is authenticated."""
    return st.session_state.get("authenticated", False)

def login_session(user_info: dict):
    """Sets session state flags for authenticated user."""
    st.session_state["authenticated"] = True
    st.session_state["user"] = user_info

def logout_session():
    """Clears authentication session flags."""
    st.session_state["authenticated"] = False
    st.session_state["user"] = None

def require_auth():
    """Decorator or barrier to protect dashboard pages."""
    init_session_state()
    if not is_authenticated():
        st.warning("⚠️ Access Restricted: Please sign in to access this scouting page.")
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("⚡ Sign in as RR Scout", use_container_width=True):
                login_session({
                    "id": 1,
                    "username": "RR Scout",
                    "email": "scout@rajasthanroyals.com",
                    "role": "analyst"
                })
                st.rerun()
        st.stop()
