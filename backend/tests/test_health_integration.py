"""
Integration tests for health check API.
Tests readiness endpoint for application health monitoring.
"""


def test_health_ready_endpoint_accessible(client):
    """Test that health ready endpoint is accessible without auth"""
    response = client.get("/api/v1/health/ready")
    assert response.status_code == 200


def test_health_ready_returns_expected_fields(client):
    """Test that health ready endpoint returns all required fields"""
    response = client.get("/api/v1/health/ready")
    assert response.status_code == 200
    
    data = response.json()
    assert "status" in data
    assert "app_version" in data
    assert "database" in data
    assert "checked_at" in data
    
    assert data["status"] == "ready"
    assert data["app_version"] == "1.0.0"
    assert data["database"] == "connected"
    assert isinstance(data["checked_at"], str)


def test_health_ready_database_connection_check(client, db_session):
    """Test that health endpoint verifies database connectivity"""
    response = client.get("/api/v1/health/ready")
    assert response.status_code == 200
    
    data = response.json()
    # With a working db_session fixture, database should be connected
    assert data["database"] == "connected"


def test_health_ready_timestamp_format(client):
    """Test that checked_at timestamp is properly formatted"""
    response = client.get("/api/v1/health/ready")
    assert response.status_code == 200
    
    data = response.json()
    checked_at = data["checked_at"]
    
    # Verify it's ISO format timestamp
    assert "T" in checked_at
    from datetime import datetime
    # Should be parseable as ISO format
    parsed = datetime.fromisoformat(checked_at.replace("Z", "+00:00"))
    assert parsed is not None
