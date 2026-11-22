import pytest
import uuid
from app.models.user import User
from app.services.auth_service import AuthService


@pytest.fixture
def seeded_user(db_session):
    """Create a test user"""
    user = User(
        user_id=uuid.UUID("00000000-0000-0000-0000-00009add8fec"),
        username="integrationtest",
        display_name="Integration Test User",
        email="int@example.com",
        password_hash=AuthService.hash_password("testpass123"),
        primary_role="investigator",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    return user


def test_login_endpoint_success(client, seeded_user):
    """Test POST /api/v1/auth/login with valid credentials"""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "integrationtest",
            "password": "testpass123"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "auth_token" in data
    assert "session_id" in data
    assert "user" in data
    assert data["token_type"] == "Bearer"
    assert data["user"]["username"] == "integrationtest"
    assert data["user"]["primary_role"] == "investigator"


def test_login_endpoint_invalid_credentials(client, seeded_user):
    """Test POST /api/v1/auth/login with invalid credentials"""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "integrationtest",
            "password": "wrongpassword"
        }
    )
    
    assert response.status_code == 401
    assert "detail" in response.json()
    assert "Invalid credentials" in response.json()["detail"]


def test_login_endpoint_nonexistent_user(client):
    """Test POST /api/v1/auth/login with non-existent user"""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "nonexistent",
            "password": "password"
        }
    )
    
    assert response.status_code == 401


def test_login_endpoint_validation_error(client):
    """Test POST /api/v1/auth/login with missing fields"""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "test"
            # password missing
        }
    )
    
    assert response.status_code == 422


def test_logout_endpoint_success(client, seeded_user):
    """Test POST /api/v1/auth/logout with valid session"""
    # Login first
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "integrationtest",
            "password": "testpass123"
        }
    )
    session_id = login_response.json()["session_id"]
    
    # Logout
    response = client.post(
        "/api/v1/auth/logout",
        json={"session_id": session_id}
    )
    
    assert response.status_code == 200
    assert "detail" in response.json()
    assert "revoked" in response.json()["detail"].lower()


def test_logout_endpoint_invalid_session(client):
    """Test POST /api/v1/auth/logout with invalid session"""
    response = client.post(
        "/api/v1/auth/logout",
        json={"session_id": "nonexistent-session"}
    )
    
    assert response.status_code == 404


def test_protected_endpoint_without_auth(client):
    """Test accessing protected endpoint without authentication"""
    response = client.get("/api/v1/alerts")
    assert response.status_code == 401  # HTTPBearer returns 401 for missing credentials


def test_protected_endpoint_with_invalid_token(client):
    """Test accessing protected endpoint with invalid token"""
    response = client.get(
        "/api/v1/alerts",
        headers={"Authorization": "Bearer invalid.token.here"}
    )
    assert response.status_code == 401


def test_protected_endpoint_with_valid_token(client, seeded_user):
    """Test accessing protected endpoint with valid token"""
    # Login to get token
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "integrationtest",
            "password": "testpass123"
        }
    )
    token = login_response.json()["auth_token"]
    
    # Access protected endpoint
    response = client.get(
        "/api/v1/alerts",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Should return 200 (even if empty queue)
    assert response.status_code == 200
    assert "items" in response.json()


def test_auth_flow_end_to_end(client, seeded_user):
    """Test complete auth flow: login -> use token -> logout -> token invalid"""
    # 1. Login
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "integrationtest",
            "password": "testpass123"
        }
    )
    assert login_response.status_code == 200
    token = login_response.json()["auth_token"]
    session_id = login_response.json()["session_id"]
    
    # 2. Use token to access protected endpoint
    response = client.get(
        "/api/v1/alerts",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    
    # 3. Logout
    logout_response = client.post(
        "/api/v1/auth/logout",
        json={"session_id": session_id}
    )
    assert logout_response.status_code == 200
    
    # 4. Token should now be invalid
    response = client.get(
        "/api/v1/alerts",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 401
