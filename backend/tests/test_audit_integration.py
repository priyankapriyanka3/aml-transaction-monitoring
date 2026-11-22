"""
Integration tests for audit events API.
Tests audit event retrieval with filtering and pagination.
"""
import json
import uuid
from datetime import datetime, timedelta

from app.models.audit_event import AuditEvent
from app.models.user import User


def test_get_audit_events_requires_auth(client):
    """Test that audit events endpoint requires authentication"""
    response = client.get("/api/v1/audit-events")
    assert response.status_code == 401


def test_get_audit_events_no_filters(auth_client, db_session):
    """Test retrieving all audit events without filters"""
    # Create test user
    user = User(
        user_id=uuid.UUID("00000000-0000-0000-0000-00001fdb9834"),
        username="testuser",
        display_name="Test User",
        email="test@example.com",
        password_hash="hash",
        primary_role="investigator",
        is_active=True
    )
    db_session.add(user)
    
    # Create some audit events
    base_time = datetime.utcnow()
    events_data = [
        {
            "audit_event_id": uuid.UUID(int=1001),
            "entity_type": "case",
            "entity_id": "case-001",
            "action_type": "CASE_CREATED",
            "actor_user_id": uuid.UUID(int=1),
            "actor_role": "investigator",
            "correlation_id": "corr-001",
            "payload_json": json.dumps({"case_number": "CS-001"}),
            "occurred_at": base_time,
            "created_at": base_time
        },
        {
            "audit_event_id": uuid.UUID(int=1002),
            "entity_type": "alert",
            "entity_id": "alert-001",
            "action_type": "ALERT_ASSIGNED",
            "actor_user_id": uuid.UUID(int=1),
            "actor_role": "investigator",
            "correlation_id": "corr-002",
            "payload_json": json.dumps({"assigned_to": str(uuid.UUID(int=1))}),
            "occurred_at": base_time + timedelta(hours=1),
            "created_at": base_time + timedelta(hours=1)
        },
        {
            "audit_event_id": uuid.UUID(int=1003),
            "entity_type": "case",
            "entity_id": "case-001",
            "action_type": "CASE_STATUS_CHANGED",
            "actor_user_id": uuid.UUID(int=1),
            "actor_role": "investigator",
            "correlation_id": "corr-003",
            "payload_json": json.dumps({"previous_status": "INVESTIGATING", "new_status": "REVIEW_READY"}),
            "occurred_at": base_time + timedelta(hours=2),
            "created_at": base_time + timedelta(hours=2)
        }
    ]
    
    for event_data in events_data:
        event = AuditEvent(**event_data)
        db_session.add(event)
    db_session.commit()
    
    # Get all events
    response = auth_client.get("/api/v1/audit-events")
    assert response.status_code == 200
    
    data = response.json()
    assert "items" in data
    assert "total_count" in data
    assert data["total_count"] == 3
    assert len(data["items"]) == 3
    
    # Events should be ordered by occurred_at DESC (newest first)
    assert data["items"][0]["audit_event_id"] == str(uuid.UUID(int=1003))
    assert data["items"][1]["audit_event_id"] == str(uuid.UUID(int=1002))
    assert data["items"][2]["audit_event_id"] == str(uuid.UUID(int=1001))


def test_get_audit_events_filter_by_entity_type(auth_client, db_session):
    """Test filtering audit events by entity type"""
    # Create test user
    user = User(
        user_id=uuid.UUID("00000000-0000-0000-0000-00001fdb9834"),
        username="testuser",
        display_name="Test User",
        email="test@example.com",
        password_hash="hash",
        primary_role="investigator",
        is_active=True
    )
    db_session.add(user)
    
    # Create events with different entity types
    base_time = datetime.utcnow()
    events_data = [
        {
            "audit_event_id": uuid.UUID(int=1001),
            "entity_type": "case",
            "entity_id": "case-001",
            "action_type": "CASE_CREATED",
            "actor_user_id": uuid.UUID(int=1),
            "actor_role": "investigator",
            "correlation_id": "corr-001",
            "payload_json": json.dumps({}),
            "occurred_at": base_time,
            "created_at": base_time
        },
        {
            "audit_event_id": uuid.UUID(int=1002),
            "entity_type": "alert",
            "entity_id": "alert-001",
            "action_type": "ALERT_ASSIGNED",
            "actor_user_id": uuid.UUID(int=1),
            "actor_role": "investigator",
            "correlation_id": "corr-002",
            "payload_json": json.dumps({}),
            "occurred_at": base_time + timedelta(hours=1),
            "created_at": base_time + timedelta(hours=1)
        },
        {
            "audit_event_id": uuid.UUID(int=1003),
            "entity_type": "case",
            "entity_id": "case-002",
            "action_type": "CASE_STATUS_CHANGED",
            "actor_user_id": uuid.UUID(int=1),
            "actor_role": "investigator",
            "correlation_id": "corr-003",
            "payload_json": json.dumps({}),
            "occurred_at": base_time + timedelta(hours=2),
            "created_at": base_time + timedelta(hours=2)
        }
    ]
    
    for event_data in events_data:
        event = AuditEvent(**event_data)
        db_session.add(event)
    db_session.commit()
    
    # Filter by entity_type=case
    response = auth_client.get("/api/v1/audit-events?entity_type=case")
    assert response.status_code == 200
    
    data = response.json()
    assert data["total_count"] == 2
    assert len(data["items"]) == 2
    assert all(item["entity_type"] == "case" for item in data["items"])


def test_get_audit_events_filter_by_entity_id(auth_client, db_session):
    """Test filtering audit events by entity ID"""
    # Create test user
    user = User(
        user_id=uuid.UUID("00000000-0000-0000-0000-00001fdb9834"),
        username="testuser",
        display_name="Test User",
        email="test@example.com",
        password_hash="hash",
        primary_role="investigator",
        is_active=True
    )
    db_session.add(user)
    
    # Create events for different entities
    base_time = datetime.utcnow()
    events_data = [
        {
            "audit_event_id": uuid.UUID(int=1001),
            "entity_type": "case",
            "entity_id": "case-001",
            "action_type": "CASE_CREATED",
            "actor_user_id": uuid.UUID(int=1),
            "actor_role": "investigator",
            "correlation_id": "corr-001",
            "payload_json": json.dumps({}),
            "occurred_at": base_time,
            "created_at": base_time
        },
        {
            "audit_event_id": uuid.UUID(int=1002),
            "entity_type": "case",
            "entity_id": "case-001",
            "action_type": "CASE_STATUS_CHANGED",
            "actor_user_id": uuid.UUID(int=1),
            "actor_role": "investigator",
            "correlation_id": "corr-002",
            "payload_json": json.dumps({}),
            "occurred_at": base_time + timedelta(hours=1),
            "created_at": base_time + timedelta(hours=1)
        },
        {
            "audit_event_id": uuid.UUID(int=1003),
            "entity_type": "case",
            "entity_id": "case-002",
            "action_type": "CASE_CREATED",
            "actor_user_id": uuid.UUID(int=1),
            "actor_role": "investigator",
            "correlation_id": "corr-003",
            "payload_json": json.dumps({}),
            "occurred_at": base_time + timedelta(hours=2),
            "created_at": base_time + timedelta(hours=2)
        }
    ]
    
    for event_data in events_data:
        event = AuditEvent(**event_data)
        db_session.add(event)
    db_session.commit()
    
    # Filter by entity_id=case-001
    response = auth_client.get("/api/v1/audit-events?entity_id=case-001")
    assert response.status_code == 200
    
    data = response.json()
    assert data["total_count"] == 2
    assert len(data["items"]) == 2
    assert all(item["entity_id"] == "case-001" for item in data["items"])


def test_get_audit_events_filter_by_action_type(auth_client, db_session):
    """Test filtering audit events by action type"""
    # Create test user
    user = User(
        user_id=uuid.UUID("00000000-0000-0000-0000-00001fdb9834"),
        username="testuser",
        display_name="Test User",
        email="test@example.com",
        password_hash="hash",
        primary_role="investigator",
        is_active=True
    )
    db_session.add(user)
    
    # Create events with different action types
    base_time = datetime.utcnow()
    events_data = [
        {
            "audit_event_id": uuid.UUID(int=1001),
            "entity_type": "case",
            "entity_id": "case-001",
            "action_type": "CASE_CREATED",
            "actor_user_id": uuid.UUID(int=1),
            "actor_role": "investigator",
            "correlation_id": "corr-001",
            "payload_json": json.dumps({}),
            "occurred_at": base_time,
            "created_at": base_time
        },
        {
            "audit_event_id": uuid.UUID(int=1002),
            "entity_type": "case",
            "entity_id": "case-001",
            "action_type": "CASE_STATUS_CHANGED",
            "actor_user_id": uuid.UUID(int=1),
            "actor_role": "investigator",
            "correlation_id": "corr-002",
            "payload_json": json.dumps({}),
            "occurred_at": base_time + timedelta(hours=1),
            "created_at": base_time + timedelta(hours=1)
        },
        {
            "audit_event_id": uuid.UUID(int=1003),
            "entity_type": "case",
            "entity_id": "case-002",
            "action_type": "CASE_CREATED",
            "actor_user_id": uuid.UUID(int=1),
            "actor_role": "investigator",
            "correlation_id": "corr-003",
            "payload_json": json.dumps({}),
            "occurred_at": base_time + timedelta(hours=2),
            "created_at": base_time + timedelta(hours=2)
        }
    ]
    
    for event_data in events_data:
        event = AuditEvent(**event_data)
        db_session.add(event)
    db_session.commit()
    
    # Filter by action_type=CASE_CREATED
    response = auth_client.get("/api/v1/audit-events?action_type=CASE_CREATED")
    assert response.status_code == 200
    
    data = response.json()
    assert data["total_count"] == 2
    assert len(data["items"]) == 2
    assert all(item["action_type"] == "CASE_CREATED" for item in data["items"])


def test_get_audit_events_pagination(auth_client, db_session):
    """Test audit events pagination"""
    # Create test user
    user = User(
        user_id=uuid.UUID("00000000-0000-0000-0000-00001fdb9834"),
        username="testuser",
        display_name="Test User",
        email="test@example.com",
        password_hash="hash",
        primary_role="investigator",
        is_active=True
    )
    db_session.add(user)
    
    # Create 5 events
    base_time = datetime.utcnow()
    for i in range(5):
        event = AuditEvent(
            audit_event_id=uuid.UUID(int=1000 + i),
            entity_type="case",
            entity_id=str(uuid.UUID("00000000-0000-0000-0000-000056ae0fb0")),
            action_type="CASE_STATUS_CHANGED",
            actor_user_id=uuid.UUID("00000000-0000-0000-0000-00001fdb9834"),
            actor_role="investigator",
            correlation_id=f"corr-{i:03d}",
            payload_json=json.dumps({}),
            occurred_at=base_time + timedelta(hours=i),
            created_at=base_time + timedelta(hours=i)
        )
        db_session.add(event)
    db_session.commit()
    
    # Get first page (limit=2)
    response = auth_client.get("/api/v1/audit-events?limit=2&offset=0")
    assert response.status_code == 200
    
    data = response.json()
    assert data["total_count"] == 5
    assert len(data["items"]) == 2
    assert data["limit"] == 2
    assert data["offset"] == 0
    
    # Get second page
    response = auth_client.get("/api/v1/audit-events?limit=2&offset=2")
    assert response.status_code == 200
    
    data = response.json()
    assert data["total_count"] == 5
    assert len(data["items"]) == 2
    assert data["offset"] == 2


def test_get_audit_events_combined_filters(auth_client, db_session):
    """Test combining multiple filters"""
    # Create test user
    user = User(
        user_id=uuid.UUID("00000000-0000-0000-0000-00001fdb9834"),
        username="testuser",
        display_name="Test User",
        email="test@example.com",
        password_hash="hash",
        primary_role="investigator",
        is_active=True
    )
    db_session.add(user)
    
    # Create mixed events
    base_time = datetime.utcnow()
    events_data = [
        {
            "audit_event_id": uuid.UUID(int=1001),
            "entity_type": "case",
            "entity_id": "case-001",
            "action_type": "CASE_CREATED",
            "actor_user_id": uuid.UUID(int=1),
            "actor_role": "investigator",
            "correlation_id": "corr-001",
            "payload_json": json.dumps({}),
            "occurred_at": base_time,
            "created_at": base_time
        },
        {
            "audit_event_id": uuid.UUID(int=1002),
            "entity_type": "case",
            "entity_id": "case-001",
            "action_type": "CASE_STATUS_CHANGED",
            "actor_user_id": uuid.UUID(int=1),
            "actor_role": "investigator",
            "correlation_id": "corr-002",
            "payload_json": json.dumps({}),
            "occurred_at": base_time + timedelta(hours=1),
            "created_at": base_time + timedelta(hours=1)
        },
        {
            "audit_event_id": uuid.UUID(int=1003),
            "entity_type": "alert",
            "entity_id": "alert-001",
            "action_type": "ALERT_ASSIGNED",
            "actor_user_id": uuid.UUID(int=1),
            "actor_role": "investigator",
            "correlation_id": "corr-003",
            "payload_json": json.dumps({}),
            "occurred_at": base_time + timedelta(hours=2),
            "created_at": base_time + timedelta(hours=2)
        }
    ]
    
    for event_data in events_data:
        event = AuditEvent(**event_data)
        db_session.add(event)
    db_session.commit()
    
    # Filter by entity_type=case AND entity_id=case-001
    response = auth_client.get("/api/v1/audit-events?entity_type=case&entity_id=case-001")
    assert response.status_code == 200
    
    data = response.json()
    assert data["total_count"] == 2
    assert all(item["entity_type"] == "case" and item["entity_id"] == "case-001" for item in data["items"])
