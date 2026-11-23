"""Tests for officer review and decision endpoints."""
import uuid
from datetime import datetime, timedelta, timezone
from app.models.user import User
from app.models.case import AmlCase
from app.models.case_alert_link import CaseAlertLink
from app.models.alert import Alert
from app.models.customer import Customer
from app.models.account import Account
from app.models.transaction import Transaction
from app.models.case_note import CaseNote
from app.models.evidence_gap import EvidenceGap
from app.models.information_request import InformationRequest
from app.models.rule_snapshot import RuleEvaluationSnapshot
from app.core.security import hash_password


def test_get_officer_review_package_success(auth_client, db_session):
    """Test GET /api/v1/cases/{caseId}/officer-review success."""
    # Create users
    investigator = User(
        user_id=uuid.uuid4(),
        display_name="Test Investigator",
        email="investigator@test.com",
        hashed_password=hash_password("password123"),
        role="INVESTIGATOR",
        is_active=True
    )
    officer = User(
        user_id=uuid.uuid4(),
        display_name="Test Officer",
        email="officer@test.com",
        hashed_password=hash_password("password123"),
        role="OFFICER",
        is_active=True
    )
    db_session.add_all([investigator, officer])
    db_session.flush()
    
    # Create customer, account, transaction, alert
    customer = Customer(
        customer_name="Test Customer",
        pep_flag=False,
        country_code="US"
    )
    db_session.add(customer)
    db_session.flush()
    
    account = Account(
        customer_id=customer.customer_id,
        account_ref="ACC-TEST-001",
        account_type="CHECKING"
    )
    db_session.add(account)
    db_session.flush()
    
    transaction = Transaction(
        account_id=account.account_id,
        transaction_ref="TXN-TEST-001",
        amount=50000.00,
        currency_code="USD",
        source_country_code="US",
        destination_country_code="GB",
        executed_at_utc=datetime.now(timezone.utc)
    )
    db_session.add(transaction)
    db_session.flush()
    
    alert = Alert(
        alert_ref="ALT-TEST-001",
        transaction_id=transaction.transaction_id,
        customer_id=customer.customer_id,
        priority="High",
        risk_score=85,
        status="Escalated",
        triggered_at_utc=datetime.now(timezone.utc)
    )
    db_session.add(alert)
    db_session.flush()
    
    # Create case
    case = AmlCase(
        case_ref="CS-TEST-REVIEW-001",
        primary_alert_id=alert.alert_id,
        created_by_user_id=investigator.user_id,
        assigned_officer_user_id=officer.user_id,
        status="UNDER_REVIEW",
        current_blocker_state="NONE"
    )
    db_session.add(case)
    db_session.flush()
    
    # Create case alert link
    link = CaseAlertLink(
        case_id=case.case_id,
        alert_id=alert.alert_id,
        is_primary=True,
        linked_by_user_id=investigator.user_id
    )
    db_session.add(link)
    
    # Create case note
    note = CaseNote(
        case_id=case.case_id,
        note_category="investigation",
        note_text="Test investigation note",
        author_user_id=investigator.user_id
    )
    db_session.add(note)
    
    # Create rule snapshot
    snapshot = RuleEvaluationSnapshot(
        alert_id=alert.alert_id,
        rule_code="RULE-001",
        rule_name="Large Transaction Rule",
        rule_version="v1.0",
        outcome="MATCH",
        condition_text="amount > 25000",
        evaluated_from_utc=datetime.now(timezone.utc) - timedelta(days=30),
        evaluated_to_utc=datetime.now(timezone.utc),
        immutable_hash="test-hash"
    )
    db_session.add(snapshot)
    db_session.commit()
    
    # Login as officer
    response = auth_client.post("/api/v1/auth/login", json={
        "email": "officer@test.com",
        "password": "password123"
    })
    assert response.status_code == 200
    token = response.json()["access_token"]
    auth_client.headers["Authorization"] = f"Bearer {token}"
    
    # Get officer review package
    response = auth_client.get(f"/api/v1/cases/{case.case_id}/officer-review")
    
    assert response.status_code == 200
    data = response.json()
    assert data["case_id"] == str(case.case_id)
    assert data["case_ref"] == "CS-TEST-REVIEW-001"
    assert data["status"] == "UNDER_REVIEW"
    assert data["blocker_state"] == "NONE"
    assert data["is_conflicted_officer"] is False
    assert len(data["linked_alerts"]) == 1
    assert len(data["notes"]) == 1
    assert len(data["rule_snapshots"]) == 1


def test_get_officer_review_package_conflicted_officer(auth_client, db_session):
    """Test GET /api/v1/cases/{caseId}/officer-review returns 403 for case creator."""
    # Create investigator
    investigator = User(
        user_id=uuid.uuid4(),
        display_name="Test Investigator",
        email="investigator2@test.com",
        hashed_password=hash_password("password123"),
        role="INVESTIGATOR",
        is_active=True
    )
    db_session.add(investigator)
    db_session.flush()
    
    # Create alert
    alert_id = uuid.uuid4()
    
    # Create case created by investigator
    case = AmlCase(
        case_ref="CS-TEST-CONFLICT-001",
        primary_alert_id=alert_id,
        created_by_user_id=investigator.user_id,
        status="UNDER_REVIEW",
        current_blocker_state="NONE"
    )
    db_session.add(case)
    db_session.commit()
    
    # Login as investigator (case creator)
    response = auth_client.post("/api/v1/auth/login", json={
        "email": "investigator2@test.com",
        "password": "password123"
    })
    assert response.status_code == 200
    token = response.json()["access_token"]
    auth_client.headers["Authorization"] = f"Bearer {token}"
    
    # Try to get officer review package
    response = auth_client.get(f"/api/v1/cases/{case.case_id}/officer-review")
    
    assert response.status_code == 403
    assert "creator" in response.json()["detail"].lower()


def test_record_decision_success(auth_client, db_session):
    """Test POST /api/v1/cases/{caseId}/decision success."""
    # Create users
    investigator = User(
        user_id=uuid.uuid4(),
        display_name="Test Investigator",
        email="investigator3@test.com",
        hashed_password=hash_password("password123"),
        role="INVESTIGATOR",
        is_active=True
    )
    officer = User(
        user_id=uuid.uuid4(),
        display_name="Test Officer",
        email="officer2@test.com",
        hashed_password=hash_password("password123"),
        role="OFFICER",
        is_active=True
    )
    db_session.add_all([investigator, officer])
    db_session.flush()
    
    # Create case (no blockers)
    case = AmlCase(
        case_ref="CS-TEST-DECISION-001",
        primary_alert_id=uuid.uuid4(),
        created_by_user_id=investigator.user_id,
        assigned_officer_user_id=officer.user_id,
        status="UNDER_REVIEW",
        current_blocker_state="NONE"
    )
    db_session.add(case)
    db_session.commit()
    
    # Login as officer
    response = auth_client.post("/api/v1/auth/login", json={
        "email": "officer2@test.com",
        "password": "password123"
    })
    assert response.status_code == 200
    token = response.json()["access_token"]
    auth_client.headers["Authorization"] = f"Bearer {token}"
    
    # Record decision
    response = auth_client.post(
        f"/api/v1/cases/{case.case_id}/decision",
        json={
            "outcome": "APPROVE",
            "rationale": "All evidence reviewed. Transaction is legitimate business activity."
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert "decision_id" in data
    assert data["case_id"] == str(case.case_id)
    assert data["outcome"] == "APPROVE"
    assert data["rationale"] == "All evidence reviewed. Transaction is legitimate business activity."
    assert "immutable_hash" in data


def test_record_decision_blocked_by_open_requests(auth_client, db_session):
    """Test POST /api/v1/cases/{caseId}/decision blocked by open requests."""
    # Create users
    investigator = User(
        user_id=uuid.uuid4(),
        display_name="Test Investigator",
        email="investigator4@test.com",
        hashed_password=hash_password("password123"),
        role="INVESTIGATOR",
        is_active=True
    )
    officer = User(
        user_id=uuid.uuid4(),
        display_name="Test Officer",
        email="officer3@test.com",
        hashed_password=hash_password("password123"),
        role="OFFICER",
        is_active=True
    )
    db_session.add_all([investigator, officer])
    db_session.flush()
    
    # Create case with open request
    case = AmlCase(
        case_ref="CS-TEST-BLOCKED-001",
        primary_alert_id=uuid.uuid4(),
        created_by_user_id=investigator.user_id,
        assigned_officer_user_id=officer.user_id,
        status="UNDER_REVIEW",
        current_blocker_state="OPEN_REQUESTS"
    )
    db_session.add(case)
    db_session.flush()
    
    # Create evidence gap
    gap = EvidenceGap(
        case_id=case.case_id,
        title="Test gap",
        description="Test description",
        status="OPEN",
        created_by_user_id=investigator.user_id,
        created_at_utc=datetime.now(timezone.utc)
    )
    db_session.add(gap)
    db_session.flush()
    
    # Create OPEN request
    request = InformationRequest(
        request_ref="IR-TEST-BLOCKED-001",
        case_id=case.case_id,
        gap_id=gap.gap_id,
        target_party="Test party",
        delivery_channel="Email",
        reason_text="Test reason",
        due_at_utc=datetime.now(timezone.utc) + timedelta(days=1),
        status="OPEN",
        created_by_user_id=investigator.user_id,
        created_at_utc=datetime.now(timezone.utc),
        updated_at_utc=datetime.now(timezone.utc)
    )
    db_session.add(request)
    db_session.commit()
    
    # Login as officer
    response = auth_client.post("/api/v1/auth/login", json={
        "email": "officer3@test.com",
        "password": "password123"
    })
    assert response.status_code == 200
    token = response.json()["access_token"]
    auth_client.headers["Authorization"] = f"Bearer {token}"
    
    # Try to record decision
    response = auth_client.post(
        f"/api/v1/cases/{case.case_id}/decision",
        json={
            "outcome": "APPROVE",
            "rationale": "Test rationale"
        }
    )
    
    assert response.status_code == 409
    assert "open requests" in response.json()["detail"].lower()


def test_record_decision_missing_rationale(auth_client, db_session):
    """Test POST /api/v1/cases/{caseId}/decision rejects empty rationale."""
    # Create users
    investigator = User(
        user_id=uuid.uuid4(),
        display_name="Test Investigator",
        email="investigator5@test.com",
        hashed_password=hash_password("password123"),
        role="INVESTIGATOR",
        is_active=True
    )
    officer = User(
        user_id=uuid.uuid4(),
        display_name="Test Officer",
        email="officer4@test.com",
        hashed_password=hash_password("password123"),
        role="OFFICER",
        is_active=True
    )
    db_session.add_all([investigator, officer])
    db_session.flush()
    
    # Create case
    case = AmlCase(
        case_ref="CS-TEST-RATIONALE-001",
        primary_alert_id=uuid.uuid4(),
        created_by_user_id=investigator.user_id,
        assigned_officer_user_id=officer.user_id,
        status="UNDER_REVIEW",
        current_blocker_state="NONE"
    )
    db_session.add(case)
    db_session.commit()
    
    # Login as officer
    response = auth_client.post("/api/v1/auth/login", json={
        "email": "officer4@test.com",
        "password": "password123"
    })
    assert response.status_code == 200
    token = response.json()["access_token"]
    auth_client.headers["Authorization"] = f"Bearer {token}"
    
    # Try to record decision without rationale
    response = auth_client.post(
        f"/api/v1/cases/{case.case_id}/decision",
        json={
            "outcome": "APPROVE",
            "rationale": ""
        }
    )
    
    assert response.status_code == 422
    assert "rationale" in response.json()["detail"].lower()
