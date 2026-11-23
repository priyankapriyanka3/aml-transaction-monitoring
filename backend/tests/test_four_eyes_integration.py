"""
Integration tests for four-eyes segregation of duties enforcement.

Tests that the system prevents case creator from being assigned as deciding officer
and validates independent officer assignment flows across the full lifecycle.
"""

import pytest
from datetime import datetime, timezone
from uuid import uuid4

from app.models import User, Alert, Transaction, Customer, Account, AmlCase
from app.core.security import hash_password


@pytest.fixture
def investigator_user(db_session):
    """Create investigator user."""
    email = f"investigator_four_eyes_{uuid4().hex[:8]}@example.com"
    user = User(
        user_id=uuid4(),
        email=email,
        display_name="Investigator One",
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
    email = f"officer_four_eyes_{uuid4().hex[:8]}@example.com"
    user = User(
        user_id=uuid4(),
        email=email,
        display_name="Officer One",
        hashed_password=hash_password("password123"),
        role="OFFICER",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_case(db_session, investigator_user):
    """Create a test case with linked alert."""
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
        account_ref="ACC-001",
        account_type="Personal",
        created_at_utc=datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    )
    db_session.add(account)
    
    transaction = Transaction(
        transaction_id=uuid4(),
        account_id=account.account_id,
        transaction_ref="TXN-001",
        amount=50000.00,
        currency_code="USD",
        source_country_code="US",
        destination_country_code="GB",
        executed_at_utc=datetime(2026, 11, 1, 0, 0, 0, tzinfo=timezone.utc),
        created_at_utc=datetime(2026, 11, 1, 0, 0, 0, tzinfo=timezone.utc)
    )
    db_session.add(transaction)
    
    alert = Alert(
        alert_id=uuid4(),
        alert_ref="AL-TEST-001",
        transaction_id=transaction.transaction_id,
        customer_id=customer.customer_id,
        priority="High",
        risk_score=80,
        status="Escalated",
        owner_user_id=investigator_user.user_id,
        triggered_at_utc=datetime(2026, 11, 1, 0, 0, 0, tzinfo=timezone.utc),
        created_at_utc=datetime(2026, 11, 1, 0, 0, 0, tzinfo=timezone.utc)
    )
    db_session.add(alert)
    
    case = AmlCase(
        case_id=uuid4(),
        case_ref="CS-TEST-001",
        primary_alert_id=alert.alert_id,
        created_by_user_id=investigator_user.user_id,
        status="INVESTIGATING",
        current_blocker_state="NONE",
        created_at_utc=datetime(2026, 11, 1, 0, 0, 0, tzinfo=timezone.utc),
        updated_at_utc=datetime(2026, 11, 1, 0, 0, 0, tzinfo=timezone.utc)
    )
    db_session.add(case)
    db_session.commit()
    
    db_session.refresh(case)
    return case


def test_four_eyes_prevents_self_assignment_as_officer(client, db_session, investigator_user, test_case):
    """Test that case creator cannot assign themselves as deciding officer."""
    # Login as investigator who created the case
    login_response = client.post("/api/v1/auth/login", json={
        "email": investigator_user.email,
        "password": "password123"
    })
    client.headers["Authorization"] = f"Bearer {login_response.json()['access_token']}"
    
    # Attempt to assign self as officer
    response = client.post(f"/api/v1/cases/{test_case.case_id}/assign-officer", json={
        "officer_user_id": str(investigator_user.user_id)
    }, headers={
        "X-Correlation-ID": "test-corr-four-eyes-001"
    })
    
    # Should be rejected with 409 conflict
    assert response.status_code == 409
    error = response.json()
    assert "officer cannot be the case creator" in error["detail"].lower()


def test_four_eyes_prevents_conflicted_officer_from_reviewing(client, db_session, investigator_user, test_case):
    """Test that case creator cannot access officer review endpoint even if assigned."""
    # Manually assign investigator as officer (should not happen in practice due to backend validation)
    test_case.assigned_officer_user_id = investigator_user.user_id
    test_case.status = "UNDER_REVIEW"
    db_session.commit()
    
    # Login as the conflicted investigator
    login_response = client.post("/api/v1/auth/login", json={
        "email": investigator_user.email,
        "password": "password123"
    })
    client.headers["Authorization"] = f"Bearer {login_response.json()['access_token']}"
    
    # Attempt to access officer review endpoint
    response = client.get(f"/api/v1/cases/{test_case.case_id}/officer-review")
    
    # Should be rejected with 403 forbidden due to four-eyes conflict
    assert response.status_code == 403
    error = response.json()
    assert "independent review required" in error["detail"].lower() or "cannot review own case" in error["detail"].lower()


def test_four_eyes_prevents_conflicted_officer_decision(client, db_session, investigator_user, test_case):
    """Test that case creator cannot record decision even if they reach decision endpoint."""
    # Set up case in review state with conflicted assignment
    test_case.assigned_officer_user_id = investigator_user.user_id
    test_case.status = "UNDER_REVIEW"
    db_session.commit()
    
    # Login as conflicted investigator
    login_response = client.post("/api/v1/auth/login", json={
        "email": investigator_user.email,
        "password": "password123"
    })
    client.headers["Authorization"] = f"Bearer {login_response.json()['access_token']}"
    
    # Attempt to record decision
    response = client.post(f"/api/v1/cases/{test_case.case_id}/decision", json={
        "outcome": "APPROVE",
        "rationale_text": "This should be rejected due to four-eyes conflict"
    }, headers={
        "X-Correlation-ID": "test-corr-four-eyes-003"
    })
    
    # Should be rejected with 403 forbidden
    assert response.status_code == 403
    error = response.json()
    assert "independent review" in error["detail"].lower() or "cannot decide own case" in error["detail"].lower()


def test_four_eyes_eligible_officers_excludes_case_creator(client, db_session, investigator_user, officer_user, test_case):
    """Test that readiness endpoint excludes case creator from eligible officers list."""
    # Login as investigator who created the case
    login_response = client.post("/api/v1/auth/login", json={
        "email": investigator_user.email,
        "password": "password123"
    })
    client.headers["Authorization"] = f"Bearer {login_response.json()['access_token']}"
    
    # Get readiness projection
    response = client.get(f"/api/v1/cases/{test_case.case_id}/readiness")
    assert response.status_code == 200
    
    readiness = response.json()
    eligible_officers = readiness["eligible_officers"]
    
    # Case creator should NOT be in eligible officers list
    eligible_user_ids = [o["user_id"] for o in eligible_officers]
    assert str(investigator_user.user_id) not in eligible_user_ids
    
    # Other officers should be present
    assert str(officer_user.user_id) in eligible_user_ids


def test_four_eyes_allows_independent_officer_assignment(client, db_session, investigator_user, officer_user, test_case):
    """Test that independent officer (not case creator) can be assigned successfully."""
    # Login as investigator
    login_response = client.post("/api/v1/auth/login", json={
        "email": investigator_user.email,
        "password": "password123"
    })
    client.headers["Authorization"] = f"Bearer {login_response.json()['access_token']}"
    
    # Assign independent officer
    response = client.post(f"/api/v1/cases/{test_case.case_id}/assign-officer", json={
        "officer_user_id": str(officer_user.user_id)
    }, headers={
        "X-Correlation-ID": "test-corr-four-eyes-005"
    })
    
    # Should succeed
    assert response.status_code == 200
    assignment = response.json()
    assert assignment["officer_user_id"] == str(officer_user.user_id)
    
    # Verify case record updated
    db_session.refresh(test_case)
    assert test_case.assigned_officer_user_id == officer_user.user_id


def test_four_eyes_independent_officer_can_review_and_decide(client, db_session, investigator_user, officer_user, test_case):
    """Test that independent officer can successfully review package and record decision."""
    # Set up case with independent officer assigned
    test_case.assigned_officer_user_id = officer_user.user_id
    test_case.status = "UNDER_REVIEW"
    db_session.commit()
    
    # Add a note so workspace has content
    from app.models import CaseNote
    note = CaseNote(
        note_id=uuid4(),
        case_id=test_case.case_id,
        note_category="investigation",
        note_text="Investigation complete, ready for review",
        author_user_id=investigator_user.user_id,
        authored_at_utc=datetime.now(timezone.utc)
    )
    db_session.add(note)
    db_session.commit()
    
    # Login as independent officer
    login_response = client.post("/api/v1/auth/login", json={
        "email": officer_user.email,
        "password": "password123"
    })
    client.headers["Authorization"] = f"Bearer {login_response.json()['access_token']}"
    
    # Access officer review endpoint - should succeed
    review_response = client.get(f"/api/v1/cases/{test_case.case_id}/officer-review")
    assert review_response.status_code == 200
    review_package = review_response.json()
    assert review_package["is_conflicted_officer"] is False
    
    # Record decision - should succeed
    decision_response = client.post(f"/api/v1/cases/{test_case.case_id}/decision", json={
        "outcome": "APPROVE",
        "rationale_text": "Investigation findings support approval. All evidence reviewed and validated."
    }, headers={
        "X-Correlation-ID": "test-corr-four-eyes-006"
    })
    
    assert decision_response.status_code == 201
    decision = decision_response.json()
    assert decision["outcome"] == "APPROVE"
    assert decision["deciding_officer_user_id"] == str(officer_user.user_id)
