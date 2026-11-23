"""
Integration tests for complete audit trail capture.

Tests that all state-changing operations create audit events with proper
attribution (actor, role, timestamp, correlation ID) and that audit trail
provides complete case history.
"""

import pytest
import json
import uuid
from datetime import datetime, timezone
from uuid import uuid4

from app.models import (
    User, Alert, Transaction, Customer, Account,
    AmlCase, CaseNote, AuditEvent
)
from app.core.security import hash_password


@pytest.fixture
def investigator_user(db_session):
    """Create investigator user."""
    email = f"audit_inv_{uuid4().hex[:8]}@example.com"
    user = User(
        user_id=uuid4(),
        email=email,
        display_name="Audit Investigator",
        hashed_password=hash_password("password123"),
        role="INVESTIGATOR",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def officer_user(db_session):
    """Create officer user."""
    email = f"audit_off_{uuid4().hex[:8]}@example.com"
    user = User(
        user_id=uuid4(),
        email=email,
        display_name="Audit Officer",
        hashed_password=hash_password("password123"),
        role="OFFICER",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_alert(db_session, investigator_user):
    """Create test alert with full chain."""
    customer = Customer(
        customer_id=uuid4(),
        customer_name="Audit Test Corp",
        pep_flag=False,
        country_code="US",
        created_at_utc=datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    )
    db_session.add(customer)
    
    account = Account(
        account_id=uuid4(),
        customer_id=customer.customer_id,
        account_ref="ACC-AUDIT-001",
        account_type="Business",
        created_at_utc=datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    )
    db_session.add(account)
    
    transaction = Transaction(
        transaction_id=uuid4(),
        account_id=account.account_id,
        transaction_ref="TXN-AUDIT-001",
        amount=100000.00,
        currency_code="USD",
        source_country_code="US",
        destination_country_code="CN",
        executed_at_utc=datetime(2026, 11, 1, 0, 0, 0, tzinfo=timezone.utc),
        created_at_utc=datetime(2026, 11, 1, 0, 0, 0, tzinfo=timezone.utc)
    )
    db_session.add(transaction)
    
    alert = Alert(
        alert_id=uuid4(),
        alert_ref="AL-AUDIT-001",
        transaction_id=transaction.transaction_id,
        customer_id=customer.customer_id,
        priority="Critical",
        risk_score=92,
        status="New",
        owner_user_id=None,
        triggered_at_utc=datetime(2026, 11, 1, 0, 0, 0, tzinfo=timezone.utc),
        created_at_utc=datetime(2026, 11, 1, 0, 0, 0, tzinfo=timezone.utc)
    )
    db_session.add(alert)
    db_session.commit()
    
    db_session.refresh(alert)
    return alert


def test_alert_assignment_creates_audit_event(client, db_session, investigator_user, test_alert):
    """Test that alert assignment creates audit event with proper attribution."""
    # Login
    login_response = client.post("/api/v1/auth/login", json={
        "email": investigator_user.email,
        "password": "password123"
    })
    client.headers["Authorization"] = f"Bearer {login_response.json()['access_token']}"
    
    correlation_id = "test-corr-audit-001"
    
    # Assign alert
    response = client.post(f"/api/v1/alerts/{test_alert.alert_id}/assign", headers={
        "X-Correlation-ID": correlation_id
    })
    assert response.status_code == 200
    
    # Verify audit event created
    audit_event = db_session.query(AuditEvent).filter(
        AuditEvent.entity_id == test_alert.alert_id,
        AuditEvent.action_type == "ALERT_ASSIGNED"
    ).first()
    
    assert audit_event is not None
    assert audit_event.actor_user_id == investigator_user.user_id
    assert audit_event.actor_role == "INVESTIGATOR"
    assert audit_event.correlation_id == correlation_id
    assert audit_event.entity_type == "ALERT"
    assert audit_event.occurred_at_utc is not None
    
    # Verify details include relevant information
    details = json.loads(audit_event.details_json)
    assert "alert_id" in details or "alert_ref" in details


def test_case_creation_creates_audit_events(client, db_session, investigator_user, test_alert):
    """Test that case creation creates both CASE_CREATED and ALERT_LINKED audit events."""
    # Login
    login_response = client.post("/api/v1/auth/login", json={
        "email": investigator_user.email,
        "password": "password123"
    })
    client.headers["Authorization"] = f"Bearer {login_response.json()['access_token']}"
    
    correlation_id = "test-corr-audit-002"
    
    # Create case
    response = client.post("/api/v1/cases", json={
        "alert_id": str(test_alert.alert_id)
    }, headers={
        "X-Correlation-ID": correlation_id
    })
    assert response.status_code == 201
    case_id = uuid.UUID(response.json()["case_id"])
    
    # Verify CASE_CREATED audit event
    case_created_event = db_session.query(AuditEvent).filter(
        AuditEvent.entity_id == case_id,
        AuditEvent.action_type == "CASE_CREATED"
    ).first()
    
    assert case_created_event is not None
    assert case_created_event.actor_user_id == investigator_user.user_id
    assert case_created_event.actor_role == "INVESTIGATOR"
    assert case_created_event.correlation_id == correlation_id
    assert case_created_event.entity_type == "CASE"
    
    # Verify ALERT_LINKED audit event
    alert_linked_event = db_session.query(AuditEvent).filter(
        AuditEvent.entity_id == case_id,
        AuditEvent.action_type == "ALERT_LINKED"
    ).first()
    
    assert alert_linked_event is not None
    assert alert_linked_event.actor_user_id == investigator_user.user_id
    assert alert_linked_event.correlation_id == correlation_id


def test_note_capture_creates_audit_event(client, db_session, investigator_user, test_alert):
    """Test that note capture creates NOTE_ADDED audit event."""
    # Create case first
    login_response = client.post("/api/v1/auth/login", json={
        "email": investigator_user.email,
        "password": "password123"
    })
    client.headers["Authorization"] = f"Bearer {login_response.json()['access_token']}"
    
    case_response = client.post("/api/v1/cases", json={
        "alert_id": str(test_alert.alert_id)
    }, headers={"X-Correlation-ID": "test-corr-audit-003"})
    case_id = uuid.UUID(case_response.json()["case_id"])
    
    correlation_id = "test-corr-audit-004"
    
    # Add note
    response = client.post(f"/api/v1/cases/{case_id}/notes", json={
        "note_category": "investigation",
        "note_text": "Initial investigation findings documented"
    }, headers={
        "X-Correlation-ID": correlation_id
    })
    assert response.status_code == 201
    
    # Verify NOTE_ADDED audit event
    note_event = db_session.query(AuditEvent).filter(
        AuditEvent.entity_id == case_id,
        AuditEvent.action_type == "NOTE_ADDED"
    ).first()
    
    assert note_event is not None
    assert note_event.actor_user_id == investigator_user.user_id
    assert note_event.actor_role == "INVESTIGATOR"
    assert note_event.correlation_id == correlation_id
    assert note_event.entity_type == "CASE"


def test_officer_assignment_creates_audit_event(client, db_session, investigator_user, officer_user, test_alert):
    """Test that officer assignment creates OFFICER_ASSIGNED audit event."""
    # Setup case
    login_response = client.post("/api/v1/auth/login", json={
        "email": investigator_user.email,
        "password": "password123"
    })
    client.headers["Authorization"] = f"Bearer {login_response.json()['access_token']}"
    
    case_response = client.post("/api/v1/cases", json={
        "alert_id": str(test_alert.alert_id)
    }, headers={"X-Correlation-ID": "test-corr-audit-005"})
    case_id = uuid.UUID(case_response.json()["case_id"])
    
    correlation_id = "test-corr-audit-006"
    
    # Assign officer
    response = client.post(f"/api/v1/cases/{case_id}/assign-officer", json={
        "officer_user_id": str(officer_user.user_id)
    }, headers={
        "X-Correlation-ID": correlation_id
    })
    assert response.status_code == 200
    
    # Verify OFFICER_ASSIGNED audit event
    officer_event = db_session.query(AuditEvent).filter(
        AuditEvent.entity_id == case_id,
        AuditEvent.action_type == "OFFICER_ASSIGNED"
    ).first()
    
    assert officer_event is not None
    assert officer_event.actor_user_id == investigator_user.user_id
    assert officer_event.correlation_id == correlation_id


def test_decision_recording_creates_audit_event(client, db_session, investigator_user, officer_user, test_alert):
    """Test that decision recording creates DECISION_RECORDED audit event."""
    # Setup case with officer
    login_response = client.post("/api/v1/auth/login", json={
        "email": investigator_user.email,
        "password": "password123"
    })
    client.headers["Authorization"] = f"Bearer {login_response.json()['access_token']}"
    
    case_response = client.post("/api/v1/cases", json={
        "alert_id": str(test_alert.alert_id)
    }, headers={"X-Correlation-ID": "test-corr-audit-007"})
    case_id = uuid.UUID(case_response.json()["case_id"])
    
    # Add note to satisfy readiness
    client.post(f"/api/v1/cases/{case_id}/notes", json={
        "note_category": "investigation",
        "note_text": "Investigation complete"
    }, headers={"X-Correlation-ID": "test-corr-audit-008"})
    
    # Assign officer and share
    client.post(f"/api/v1/cases/{case_id}/assign-officer", json={
        "officer_user_id": str(officer_user.user_id)
    }, headers={"X-Correlation-ID": "test-corr-audit-009"})
    
    client.post(f"/api/v1/cases/{case_id}/share-for-review", headers={
        "X-Correlation-ID": "test-corr-audit-010"
    })
    
    # Login as officer
    client.headers.pop("Authorization")
    officer_login = client.post("/api/v1/auth/login", json={
        "email": officer_user.email,
        "password": "password123"
    })
    client.headers["Authorization"] = f"Bearer {officer_login.json()['access_token']}"
    
    correlation_id = "test-corr-audit-011"
    
    # Record decision
    response = client.post(f"/api/v1/cases/{case_id}/decision", json={
        "outcome": "APPROVE",
        "rationale_text": "All requirements satisfied, case approved."
    }, headers={
        "X-Correlation-ID": correlation_id
    })
    assert response.status_code == 201
    
    # Verify DECISION_RECORDED audit event
    decision_event = db_session.query(AuditEvent).filter(
        AuditEvent.entity_id == case_id,
        AuditEvent.action_type == "DECISION_RECORDED"
    ).first()
    
    assert decision_event is not None
    assert decision_event.actor_user_id == officer_user.user_id
    assert decision_event.actor_role == "OFFICER"
    assert decision_event.correlation_id == correlation_id
    assert decision_event.entity_type == "CASE"


def test_audit_trail_provides_complete_case_history(client, db_session, investigator_user, officer_user, test_alert):
    """Test that audit trail captures complete case lifecycle from creation to decision."""
    # Login
    login_response = client.post("/api/v1/auth/login", json={
        "email": investigator_user.email,
        "password": "password123"
    })
    client.headers["Authorization"] = f"Bearer {login_response.json()['access_token']}"
    
    # Create case
    case_response = client.post("/api/v1/cases", json={
        "alert_id": str(test_alert.alert_id)
    }, headers={"X-Correlation-ID": "test-corr-full-001"})
    case_id = uuid.UUID(case_response.json()["case_id"])
    
    # Add note
    client.post(f"/api/v1/cases/{case_id}/notes", json={
        "note_category": "investigation",
        "note_text": "Investigation findings"
    }, headers={"X-Correlation-ID": "test-corr-full-002"})
    
    # Assign officer
    client.post(f"/api/v1/cases/{case_id}/assign-officer", json={
        "officer_user_id": str(officer_user.user_id)
    }, headers={"X-Correlation-ID": "test-corr-full-003"})
    
    # Share for review
    client.post(f"/api/v1/cases/{case_id}/share-for-review", headers={
        "X-Correlation-ID": "test-corr-full-004"
    })
    
    # Login as officer and record decision
    client.headers.pop("Authorization")
    officer_login = client.post("/api/v1/auth/login", json={
        "email": officer_user.email,
        "password": "password123"
    })
    client.headers["Authorization"] = f"Bearer {officer_login.json()['access_token']}"
    
    client.post(f"/api/v1/cases/{case_id}/decision", json={
        "outcome": "APPROVE",
        "rationale_text": "Case approved"
    }, headers={"X-Correlation-ID": "test-corr-full-005"})
    
    # Query all audit events for this case
    audit_events = db_session.query(AuditEvent).filter(
        AuditEvent.entity_id == case_id
    ).order_by(AuditEvent.occurred_at_utc.asc()).all()
    
    # Verify complete audit trail
    action_types = [event.action_type for event in audit_events]
    assert "CASE_CREATED" in action_types
    assert "ALERT_LINKED" in action_types
    assert "NOTE_ADDED" in action_types
    assert "OFFICER_ASSIGNED" in action_types
    assert "DECISION_RECORDED" in action_types
    
    # Verify all events have proper attribution
    for event in audit_events:
        assert event.actor_user_id is not None
        assert event.actor_role in ["INVESTIGATOR", "OFFICER"]
        assert event.correlation_id is not None
        assert event.occurred_at_utc is not None
        assert event.details_json is not None
