import pytest
import uuid
from datetime import datetime, timedelta
from app.services.auth_service import AuthService
from app.models.user import User
from app.models.session_record import SessionRecord


def test_login_success(db_session):
    """Test successful login with valid credentials"""
    # Create test user
    user = User(
        user_id=uuid.UUID("00000000-0000-0000-0000-000017e8815b"),
        username="testuser",
        display_name="Test User",
        email="test@example.com",
        password_hash=AuthService.hash_password("testpass123"),
        primary_role="investigator",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    
    # Test login
    auth_service = AuthService(db_session)
    result = auth_service.login("testuser", "testpass123")
    
    assert result is not None
    auth_token, session_id, returned_user = result
    assert auth_token is not None
    assert session_id is not None
    assert returned_user.user_id == uuid.UUID("00000000-0000-0000-0000-000017e8815b")
    assert returned_user.username == "testuser"
    
    # Verify session record was created
    session = db_session.query(SessionRecord).filter_by(session_id=uuid.UUID(session_id)).first()
    assert session is not None
    assert session.user_id == uuid.UUID("00000000-0000-0000-0000-000017e8815b")
    assert session.revoked_at is None


def test_login_invalid_username(db_session):
    """Test login with non-existent username"""
    auth_service = AuthService(db_session)
    result = auth_service.login("nonexistent", "password")
    assert result is None


def test_login_invalid_password(db_session):
    """Test login with incorrect password"""
    # Create test user
    user = User(
        user_id=uuid.UUID("00000000-0000-0000-0000-000012ba99e8"),
        username="testuser2",
        display_name="Test User 2",
        email="test2@example.com",
        password_hash=AuthService.hash_password("correctpass"),
        primary_role="investigator",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    
    # Test login with wrong password
    auth_service = AuthService(db_session)
    result = auth_service.login("testuser2", "wrongpass")
    assert result is None


def test_login_inactive_user(db_session):
    """Test login with inactive user account"""
    # Create inactive user
    user = User(
        user_id=uuid.UUID("00000000-0000-0000-0000-0000d2b3e07a"),
        username="inactive",
        display_name="Inactive User",
        email="inactive@example.com",
        password_hash=AuthService.hash_password("password"),
        primary_role="investigator",
        is_active=False
    )
    db_session.add(user)
    db_session.commit()
    
    # Test login
    auth_service = AuthService(db_session)
    result = auth_service.login("inactive", "password")
    assert result is None


def test_logout_success(db_session):
    """Test successful logout"""
    # Create user and session
    user = User(
        user_id=uuid.UUID("00000000-0000-0000-0000-0000fc6be6c8"),
        username="logouttest",
        display_name="Logout Test",
        email="logout@example.com",
        password_hash=AuthService.hash_password("password"),
        primary_role="investigator",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    
    # Login
    auth_service = AuthService(db_session)
    auth_token, session_id, _ = auth_service.login("logouttest", "password")
    
    # Logout
    success = auth_service.logout(session_id)
    assert success is True
    
    # Verify session is revoked
    session = db_session.query(SessionRecord).filter_by(session_id=uuid.UUID(session_id)).first()
    assert session.revoked_at is not None


def test_logout_invalid_session(db_session):
    """Test logout with non-existent session"""
    auth_service = AuthService(db_session)
    success = auth_service.logout("nonexistent-session-id")
    assert success is False


def test_validate_token_success(db_session):
    """Test token validation with valid token"""
    # Create user
    user = User(
        user_id=uuid.UUID("00000000-0000-0000-0000-0000bd343ba0"),
        username="tokentest",
        display_name="Token Test",
        email="token@example.com",
        password_hash=AuthService.hash_password("password"),
        primary_role="investigator",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    
    # Login to get token
    auth_service = AuthService(db_session)
    auth_token, session_id, _ = auth_service.login("tokentest", "password")
    
    # Validate token
    validated_user = auth_service.validate_token(auth_token)
    assert validated_user is not None
    assert validated_user.user_id == uuid.UUID("00000000-0000-0000-0000-0000bd343ba0")
    assert validated_user.username == "tokentest"


def test_validate_token_invalid(db_session):
    """Test token validation with invalid token"""
    auth_service = AuthService(db_session)
    validated_user = auth_service.validate_token("invalid.token.here")
    assert validated_user is None


def test_validate_token_revoked_session(db_session):
    """Test token validation with revoked session"""
    # Create user
    user = User(
        user_id=uuid.UUID("00000000-0000-0000-0000-000076490518"),
        username="revoketest",
        display_name="Revoke Test",
        email="revoke@example.com",
        password_hash=AuthService.hash_password("password"),
        primary_role="investigator",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    
    # Login and logout
    auth_service = AuthService(db_session)
    auth_token, session_id, _ = auth_service.login("revoketest", "password")
    auth_service.logout(session_id)
    
    # Try to validate revoked token
    validated_user = auth_service.validate_token(auth_token)
    assert validated_user is None


def test_password_hashing():
    """Test password hashing and verification"""
    password = "test_password_123"
    hashed = AuthService.hash_password(password)
    
    # Hash should not equal plain password
    assert hashed != password
    
    # Hash should start with bcrypt prefix
    assert hashed.startswith("$2b$")
    
    # Create service and verify
    auth_service = AuthService.__new__(AuthService)
    assert auth_service._verify_password(password, hashed) is True
    assert auth_service._verify_password("wrong_password", hashed) is False
