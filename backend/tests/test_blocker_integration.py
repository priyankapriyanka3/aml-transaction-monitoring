"""
Integration tests for decision blocker enforcement.

Tests that the system prevents decision recording when open or overdue
information requests exist, enforcing this at both the readiness check
and decision recording stages.
"""

import pytest
from datetime import datetime, timezone, timedelta
from uuid import uuid4

from app.models import (
    User, Alert, Transaction, Customer, Account, AmlCase,
    InformationRequest, EvidenceGap, CaseNote
)
from app.core.security import hash_password


@pytest.fixture
def investigator_user(db_session):
    """Create investigator user."""
    email = f"inv_block_{uuid4().hex[:8]}@example.com"
    user = User(
        user_id=uuid4(),
        email=email,
        display_name="Investigator",
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
    email = f"off_block_{uuid4().hex[:8]}@example.com"
    user = User(
        user_id=uuid4(),
        email=email,
        display_name="Officer",
        hashed_password=hash_password("password123"),
        role="OFFICER",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_case_with_note(db_session, investigator_user, officer_user):
    """Create a test case ready for review with note."""
    # Create minimal customer, account, transaction, alert chain
    customer = Customer(
        customer_id=uuid4(),
        customer_name="Test Customer",
        pep_flag=False,
        country_code="US",
        created_at_utc=datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    )
    db_session.add(customer)
    
    account = Account(
        account_id=uuid4(),
        customer_id=customer.customer_id,
        account_ref="ACC-BLOCK-001",
        account_type="Personal",
        created_at_utc=datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    )
    db_session.add(account)
    
    transaction = Transaction(
        transaction_id=uuid4(),
        account_id=account.account_id,
        transaction_ref="TXN-BLOCK-001",
        amount=75000.00,
        currency_code="USD",
        source_country_code="US",
        destination_country_code="MX",
        executed_at_utc=datetime(2026, 11, 1, 0, 0, 0, tzinfo=timezone.utc),
        created_at_utc=datetime(2026, 11, 1, 0, 0, 0, tzinfo=timezone.utc)
    )
    db_session.add(transaction)
    
    alert = Alert(
        alert_id=uuid4(),
        alert_ref="AL-BLOCK-001",
        transaction_id=transaction.transaction_id,
        customer_id=customer.customer_id,
        priority="High",
        risk_score=85,
        status="Escalated",
        owner_user_id=investigator_user.user_id,
        triggered_at_utc=datetime(2026, 11, 1, 0, 0, 0, tzinfo=timezone.utc),
        created_at_utc=datetime(2026, 11, 1, 0, 0, 0, tzinfo=timezone.utc)
    )
    db_session.add(alert)
    
    case = AmlCase(
        case_id=uuid4(),
        case_ref="CS-BLOCK-001",
        primary_alert_id=alert.alert_id,
        created_by_user_id=investigator_user.user_id,
        assigned_officer_user_id=officer_user.user_id,
        status="UNDER_REVIEW",
        current_blocker_state="NONE",
        created_at_utc=datetime(2026, 11, 1, 0, 0, 0, tzinfo=timezone.utc),
        updated_at_utc=datetime(2026, 11, 1, 0, 0, 0, tzinfo=timezone.utc)
    )
    db_session.add(case)
    
    # Add note to satisfy readiness
    note = CaseNote(
        note_id=uuid4(),
        case_id=case.case_id,
        note_category="investigation",
        note_text="Investigation note for blocker test",
        author_user_id=investigator_user.user_id,
        authored_at_utc=datetime.now(timezone.utc)
    )
    db_session.add(note)
    
    db_session.commit()
    db_session.refresh(case)
    return case


def test_open_request_blocks_decision(client, db_session, investigator_user, officer_user, test_case_with_note):
    """Test that open information request blocks decision recording."""
    case = test_case_with_note
    
    # Create evidence gap
    gap = EvidenceGap(
        gap_id=uuid4(),
        case_id=case.case_id,
        title="Missing Documentation",
        description="Need transaction supporting documents",
        status="OPEN",
        created_by_user_id=investigator_user.user_id,
        created_at_utc=datetime.now(timezone.utc)
    )
    db_session.add(gap)
    
    # Create OPEN information request
    now = datetime.now(timezone.utc)
    request = InformationRequest(
        request_id=uuid4(),
        request_ref="IR-BLOCK-001",
        case_id=case.case_id,
        gap_id=gap.gap_id,
        target_party="Customer Team",
        delivery_channel="Email",
        reason_text="Need supporting documentation",
        due_at_utc=now + timedelta(days=3),
        status="OPEN",
        created_by_user_id=investigator_user.user_id,
        created_at_utc=now,
        updated_at_utc=now
    )
    db_session.add(request)
    
    # Update case blocker state
    case.current_blocker_state = "OPEN_REQUESTS"
    db_session.commit()
    
    # Login as officer
    login_response = client.post("/api/v1/auth/login", json={
        "email": officer_user.email,
        "password": "password123"
    })
    client.headers["Authorization"] = f"Bearer {login_response.json()['access_token']}"
    
    # Attempt to record decision
    response = client.post(f"/api/v1/cases/{case.case_id}/decision", json={
        "outcome": "APPROVE",
        "rationale_text": "This should be blocked by open request"
    }, headers={
        "X-Correlation-ID": "test-corr-blocker-001"
    })
    
    # Should be rejected with 409 conflict
    assert response.status_code == 409
    error = response.json()
    assert "open requests" in error["detail"].lower() or "blocker" in error["detail"].lower()


def test_overdue_request_blocks_decision(client, db_session, investigator_user, officer_user, test_case_with_note):
    """Test that overdue information request blocks decision recording."""
    case = test_case_with_note
    
    # Create evidence gap
    gap = EvidenceGap(
        gap_id=uuid4(),
        case_id=case.case_id,
        title="Overdue Documentation",
        description="Need transaction verification",
        status="OPEN",
        created_by_user_id=investigator_user.user_id,
        created_at_utc=datetime.now(timezone.utc)
    )
    db_session.add(gap)
    
    # Create OVERDUE information request (due date in past)
    now = datetime.now(timezone.utc)
    created_time = now - timedelta(days=5)
    request = InformationRequest(
        request_id=uuid4(),
        request_ref="IR-BLOCK-002",
        case_id=case.case_id,
        gap_id=gap.gap_id,
        target_party="Compliance Team",
        delivery_channel="Internal System",
        reason_text="Urgent verification needed",
        due_at_utc=now - timedelta(days=2),  # Overdue
        status="OPEN",
        created_by_user_id=investigator_user.user_id,
        created_at_utc=created_time,
        updated_at_utc=created_time
    )
    db_session.add(request)
    
    # Update case blocker state
    case.current_blocker_state = "OVERDUE_REQUESTS"
    db_session.commit()
    
    # Login as officer
    login_response = client.post("/api/v1/auth/login", json={
        "email": officer_user.email,
        "password": "password123"
    })
    client.headers["Authorization"] = f"Bearer {login_response.json()['access_token']}"
    
    # Attempt to record decision
    response = client.post(f"/api/v1/cases/{case.case_id}/decision", json={
        "outcome": "REJECT",
        "rationale_text": "This should be blocked by overdue request"
    }, headers={
        "X-Correlation-ID": "test-corr-blocker-002"
    })
    
    # Should be rejected with 409 conflict
    assert response.status_code == 409
    error = response.json()
    # An OPEN request that's overdue is still reported as "open requests"
    # because OPEN_REQUESTS check takes precedence in derive_blocker_state
    assert "open requests" in error["detail"].lower()


def test_readiness_shows_incomplete_when_open_requests_exist(client, db_session, investigator_user, test_case_with_note):
    """Test that readiness checklist shows incomplete when open requests exist."""
    case = test_case_with_note
    
    # Create evidence gap with open request
    gap = EvidenceGap(
        gap_id=uuid4(),
        case_id=case.case_id,
        title="Pending Information",
        description="Awaiting response",
        status="OPEN",
        created_by_user_id=investigator_user.user_id,
        created_at_utc=datetime.now(timezone.utc)
    )
    db_session.add(gap)
    
    now = datetime.now(timezone.utc)
    request = InformationRequest(
        request_id=uuid4(),
        request_ref="IR-READY-001",
        case_id=case.case_id,
        gap_id=gap.gap_id,
        target_party="External Party",
        delivery_channel="Email",
        reason_text="Additional information needed",
        due_at_utc=now + timedelta(days=5),
        status="OPEN",
        created_by_user_id=investigator_user.user_id,
        created_at_utc=now,
        updated_at_utc=now
    )
    db_session.add(request)
    
    # Update case blocker state
    case.current_blocker_state = "OPEN_REQUESTS"
    case.status = "INVESTIGATING"  # Set back to investigating since not ready
    db_session.commit()
    
    # Login as investigator
    login_response = client.post("/api/v1/auth/login", json={
        "email": investigator_user.email,
        "password": "password123"
    })
    client.headers["Authorization"] = f"Bearer {login_response.json()['access_token']}"
    
    # Check readiness
    response = client.get(f"/api/v1/cases/{case.case_id}/readiness")
    assert response.status_code == 200
    
    readiness = response.json()
    checklist = readiness["checklist"]
    
    # Find the no_open_requests checklist item
    no_open_requests_item = next((item for item in checklist if item["name"] == "no_open_requests"), None)
    assert no_open_requests_item is not None
    assert no_open_requests_item["complete"] is False
    assert "open" in no_open_requests_item["details"].lower() or "request" in no_open_requests_item["details"].lower()


def test_decision_succeeds_when_no_blockers(client, db_session, investigator_user, officer_user, test_case_with_note):
    """Test that decision recording succeeds when no blockers exist."""
    case = test_case_with_note
    
    # Ensure no blockers
    case.current_blocker_state = "NONE"
    db_session.commit()
    
    # Login as officer
    login_response = client.post("/api/v1/auth/login", json={
        "email": officer_user.email,
        "password": "password123"
    })
    client.headers["Authorization"] = f"Bearer {login_response.json()['access_token']}"
    
    # Record decision - should succeed
    response = client.post(f"/api/v1/cases/{case.case_id}/decision", json={
        "outcome": "APPROVE",
        "rationale_text": "All requirements satisfied, case approved for closure."
    }, headers={
        "X-Correlation-ID": "test-corr-blocker-004"
    })
    
    assert response.status_code == 201
    decision = response.json()
    assert decision["outcome"] == "APPROVE"
    assert decision["deciding_officer_user_id"] == str(officer_user.user_id)


def test_responding_to_request_clears_blocker(client, db_session, investigator_user, officer_user, test_case_with_note):
    """Test that recording response to last open request clears blocker state."""
    case = test_case_with_note
    
    # Create evidence gap with open request
    gap = EvidenceGap(
        gap_id=uuid4(),
        case_id=case.case_id,
        title="Documentation Gap",
        description="Need verification",
        status="OPEN",
        created_by_user_id=investigator_user.user_id,
        created_at_utc=datetime.now(timezone.utc)
    )
    db_session.add(gap)
    
    now = datetime.now(timezone.utc)
    request = InformationRequest(
        request_id=uuid4(),
        request_ref="IR-CLEAR-001",
        case_id=case.case_id,
        gap_id=gap.gap_id,
        target_party="Customer",
        delivery_channel="Email",
        reason_text="Need documents",
        due_at_utc=now + timedelta(days=3),
        status="OPEN",
        created_by_user_id=investigator_user.user_id,
        created_at_utc=now,
        updated_at_utc=now
    )
    db_session.add(request)
    
    # Set blocker
    case.current_blocker_state = "OPEN_REQUESTS"
    case.status = "INVESTIGATING"
    db_session.commit()
    
    # Login as investigator
    login_response = client.post("/api/v1/auth/login", json={
        "email": investigator_user.email,
        "password": "password123"
    })
    client.headers["Authorization"] = f"Bearer {login_response.json()['access_token']}"
    
    # Record response to request
    response = client.post(f"/api/v1/cases/{case.case_id}/requests/{request.request_id}/response", json={
        "response_summary": "Customer provided all required documentation",
        "received_at_utc": datetime.now(timezone.utc).isoformat()
    }, headers={
        "X-Correlation-ID": "test-corr-blocker-005"
    })
    
    assert response.status_code == 200
    
    # Verify blocker cleared
    db_session.refresh(case)
    assert case.current_blocker_state == "NONE"
