"""Tests for authentication service and endpoints."""
import uuid
import pytest
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.session import Session as SessionModel
from app.services.auth_service import AuthService
from app.core.security import hash_password, verify_password, create_access_token, decode_access_token


def test_hash_password():
    """Test password hashing with bcrypt."""
    password = "TestPassword123"
    hashed = hash_password(password)
    
    # Hashed password should be different from plain
    assert hashed != password
    
    # Should be bcrypt format
    assert hashed.startswith("$2b$")
    
    # Should verify correctly
    assert verify_password(password, hashed)
    
    # Wrong password should not verify
    assert not verify_password("WrongPassword", hashed)


def test_create_and_decode_token():
    """Test JWT token creation and decoding."""
    user_id = uuid.uuid4()
    role = "INVESTIGATOR"
    correlation_id = "test-corr-123"
    
    token, expires_at = create_access_token(user_id, role, correlation_id)
    
    # Token should be a string
    assert isinstance(token, str)
    assert len(token) > 0
    
    # Decode token
    payload = decode_access_token(token)
    
    # Verify payload contents
    assert payload["sub"] == str(user_id)
    assert payload["role"] == role
    assert payload["correlation_id"] == correlation_id
    assert "iat" in payload
    assert "exp" in payload


def test_authenticate_user_success(db_session: Session):
    """Test successful user authentication."""
    # Create test user
    user = User(
        email="test@example.com",
        display_name="Test User",
        hashed_password=hash_password("password123"),
        role="INVESTIGATOR",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    
    # Authenticate
    auth_service = AuthService(db_session)
    authenticated_user = auth_service.authenticate_user("test@example.com", "password123")
    
    assert authenticated_user is not None
    assert authenticated_user.email == "test@example.com"
    assert authenticated_user.role == "INVESTIGATOR"


def test_authenticate_user_wrong_password(db_session: Session):
    """Test authentication fails with wrong password."""
    # Create test user
    user = User(
        email="test@example.com",
        display_name="Test User",
        hashed_password=hash_password("password123"),
        role="INVESTIGATOR",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    
    # Try to authenticate with wrong password
    auth_service = AuthService(db_session)
    authenticated_user = auth_service.authenticate_user("test@example.com", "wrongpassword")
    
    assert authenticated_user is None


def test_authenticate_user_not_found(db_session: Session):
    """Test authentication fails for non-existent user."""
    auth_service = AuthService(db_session)
    authenticated_user = auth_service.authenticate_user("notfound@example.com", "password")
    
    assert authenticated_user is None


def test_authenticate_user_inactive(db_session: Session):
    """Test authentication fails for inactive user."""
    # Create inactive user
    user = User(
        email="inactive@example.com",
        display_name="Inactive User",
        hashed_password=hash_password("password123"),
        role="INVESTIGATOR",
        is_active=False
    )
    db_session.add(user)
    db_session.commit()
    
    # Try to authenticate
    auth_service = AuthService(db_session)
    authenticated_user = auth_service.authenticate_user("inactive@example.com", "password123")
    
    assert authenticated_user is None


def test_create_session(db_session: Session):
    """Test session creation for authenticated user."""
    # Create test user
    user = User(
        email="test@example.com",
        display_name="Test User",
        hashed_password=hash_password("password123"),
        role="INVESTIGATOR",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    
    # Create session
    auth_service = AuthService(db_session)
    token, session = auth_service.create_session(user, "test-corr-id")
    
    # Verify token
    assert isinstance(token, str)
    assert len(token) > 0
    
    # Verify session record
    assert session.user_id == user.user_id
    assert session.hashed_token is not None
    assert session.issued_at_utc is not None
    assert session.expires_at_utc is not None
    assert session.last_activity_utc is not None


def test_login_success(db_session: Session):
    """Test successful login flow."""
    # Create test user
    user = User(
        email="test@example.com",
        display_name="Test User",
        hashed_password=hash_password("password123"),
        role="INVESTIGATOR",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    
    # Login
    auth_service = AuthService(db_session)
    token, expires_in, logged_in_user = auth_service.login("test@example.com", "password123")
    
    # Verify response
    assert isinstance(token, str)
    assert expires_in > 0
    assert logged_in_user.email == "test@example.com"
    
    # Verify session was created
    from sqlalchemy import select
    stmt = select(SessionModel).where(SessionModel.user_id == user.user_id)
    session = db_session.scalars(stmt).first()
    assert session is not None


def test_login_invalid_credentials(db_session: Session):
    """Test login fails with invalid credentials."""
    auth_service = AuthService(db_session)
    
    with pytest.raises(Exception) as exc_info:
        auth_service.login("wrong@example.com", "wrongpassword")
    
    assert exc_info.value.status_code == 401


def test_logout(db_session: Session):
    """Test logout revokes session."""
    # Create user and session
    user = User(
        email="test@example.com",
        display_name="Test User",
        hashed_password=hash_password("password123"),
        role="INVESTIGATOR",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    
    auth_service = AuthService(db_session)
    token, _ = auth_service.create_session(user)
    
    # Verify session exists
    from sqlalchemy import select
    stmt = select(SessionModel).where(SessionModel.user_id == user.user_id)
    session = db_session.scalars(stmt).first()
    assert session is not None
    
    # Logout
    auth_service.logout(token)
    
    # Verify session was deleted
    db_session.expire_all()
    stmt = select(SessionModel).where(SessionModel.user_id == user.user_id)
    session = db_session.scalars(stmt).first()
    assert session is None


def test_verify_session_valid(db_session: Session):
    """Test session verification with valid token."""
    # Create user and session
    user = User(
        email="test@example.com",
        display_name="Test User",
        hashed_password=hash_password("password123"),
        role="INVESTIGATOR",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    
    auth_service = AuthService(db_session)
    token, _ = auth_service.create_session(user)
    
    # Verify session
    verified_user = auth_service.verify_session(token)
    
    assert verified_user is not None
    assert verified_user.user_id == user.user_id


def test_verify_session_invalid_token(db_session: Session):
    """Test session verification fails with invalid token."""
    auth_service = AuthService(db_session)
    verified_user = auth_service.verify_session("invalid-token")
    
    assert verified_user is None


def test_login_endpoint(client):
    """Test POST /api/v1/auth/login endpoint."""
    # Create user
    from app.models import User
    from app.database import SessionLocal
    from app.core.security import hash_password
    
    db = SessionLocal()
    user = User(
        email="test@example.com",
        display_name="Test User",
        hashed_password=hash_password("password123"),
        role="INVESTIGATOR",
        is_active=True
    )
    db.add(user)
    db.commit()
    db.close()
    
    # Login
    response = client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    
    assert response.status_code == 200
    data = response.json()
    
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "expires_in" in data
    assert "user" in data
    assert data["user"]["email"] == "test@example.com"
    assert data["user"]["role"] == "INVESTIGATOR"


def test_login_endpoint_invalid_credentials(client):
    """Test login endpoint fails with invalid credentials."""
    response = client.post("/api/v1/auth/login", json={
        "email": "notfound@example.com",
        "password": "wrongpassword"
    })
    
    assert response.status_code == 401
    assert "detail" in response.json()


def test_get_me_endpoint(auth_client):
    """Test GET /api/v1/auth/me endpoint."""
    response = auth_client.get("/api/v1/auth/me")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["email"] == "tester@example.com"
    assert data["display_name"] == "Test User"
    assert data["role"] == "INVESTIGATOR"


def test_get_me_endpoint_unauthorized(client):
    """Test /me endpoint requires authentication."""
    response = client.get("/api/v1/auth/me")
    
    assert response.status_code == 401  # No Bearer token returns 401


def test_logout_endpoint(auth_client):
    """Test POST /api/v1/auth/logout endpoint."""
    response = auth_client.post("/api/v1/auth/logout")
    
    assert response.status_code == 200
    data = response.json()
    assert data["detail"] == "Logged out successfully"
