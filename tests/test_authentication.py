"""
IPL Analytics Pro - Authentication Unit Tests
Tests password hashing, verification, input validation, user creation, and authentication logic.
"""

import os
import pytest
from auth.database import init_db, get_user_by_username
from auth.authentication import (
    hash_password,
    check_password,
    validate_registration_inputs,
    register_new_user,
    authenticate_user,
    seed_demo_account,
    DEMO_USERNAME,
    DEMO_PASSWORD
)

def test_password_hashing():
    raw_pwd = "SecureTestPassword123"
    hashed = hash_password(raw_pwd)
    
    assert hashed != raw_pwd
    assert check_password(raw_pwd, hashed) is True
    assert check_password("WrongPassword", hashed) is False

def test_input_validation():
    # Short username
    ok, _ = validate_registration_inputs("ab", "test@test.com", "pass123", "pass123")
    assert ok is False
    
    # Invalid email
    ok, _ = validate_registration_inputs("valid_user", "invalid-email", "pass123", "pass123")
    assert ok is False
    
    # Password mismatch
    ok, _ = validate_registration_inputs("valid_user", "test@test.com", "pass123", "pass456")
    assert ok is False
    
    # Valid
    ok, _ = validate_registration_inputs("valid_user", "test@test.com", "pass123", "pass123")
    assert ok is True

def test_demo_account_and_auth():
    seed_demo_account()
    
    # Authenticate with valid demo credentials
    success, msg, user = authenticate_user(DEMO_USERNAME, DEMO_PASSWORD)
    assert success is True
    assert user is not None
    assert user["username"] == DEMO_USERNAME
    
    # Authenticate with invalid password
    success, msg, user = authenticate_user(DEMO_USERNAME, "WrongPass!")
    assert success is False
    assert user is None
