"""Tests for decision service functionality."""
import uuid
from datetime import datetime, timezone, timedelta
from app.models.case import AmlCase
from app.models.alert import Alert
from app.models.customer import Customer
from app.models.account import Account
from app.models.transaction import Transaction
from app.models.case_alert_link import CaseAlertLink
from app.models.case_note import CaseNote
from app.models.user import User


def test_share_for_review_success(auth_client, db_session):
    """Test successful case share-for-review transition."""
    # Create customer, account, transaction, alert
    customer = Customer(
        customer_id=uuid.uuid4(),
        customer_name="Share Test Customer",
        pep_flag=False,
        country_code="US"
    )
    db_session.add(customer)
    
    account = Account(
        account_id=uuid.uuid4(),
        customer_id=customer.customer_id,
        account_ref="ACC-SHARE-001",
        account_type="Checking"
    )
    db_session.add(account)
    
    transaction = Transaction(
        transaction_id=uuid.uuid4(),
        account_id=account.account_id,
        transaction_ref="TXN-SHARE-001",
        amount=50000.00,
        currency_code="USD",
        source_country_code="US",
        destination_country_code="CH",
        executed_at_utc=datetime.now(timezone.utc) - timedelta(hours=1)
    )
    db_session.add(transaction)
    
    alert = Alert(
        alert_id=uuid.uuid4(),
        alert_ref="ALT-SHARE-001",
        transaction_id=transaction.transaction_id,
        customer_id=customer.customer_id,
        priority="High",
        risk_score=85,
        status="New",
        owner_user_id=None,
        triggered_at_utc=datetime.now(timezone.utc) - timedelta(hours=1)
    )
    db_session.add(alert)
    
    # Get test user ID
    login_response = auth_client.get("/api/v1/auth/me")
    assert login_response.status_code == 200
    investigator_user_id = uuid.UUID(login_response.json()["user_id"])
    
    # Create officer user (must exist)
    from app.core.security import hash_password
    officer = User(
        user_id=uuid.uuid4(),
        display_name="Test Officer",
        email="test-officer@example.com",
        hashed_password=hash_password("officer123"),
        role="OFFICER",
        is_active=True
    )
    db_session.add(officer)
    
    # Create case as investigator
    case = AmlCase(
        case_id=uuid.uuid4(),
        case_ref="CS-SHARE-001",
        primary_alert_id=alert.alert_id,
        created_by_user_id=investigator_user_id,
        assigned_officer_user_id=officer.user_id,  # Officer assigned
        status="READY_FOR_REVIEW",
        current_blocker_state="NONE"
    )
    db_session.add(case)
    
    # Create case alert link (requirement: >= 1 alert)
    link = CaseAlertLink(
        case_alert_link_id=uuid.uuid4(),
        case_id=case.case_id,
        alert_id=alert.alert_id,
        is_primary=True,
        linked_by_user_id=investigator_user_id,
        linked_at_utc=datetime.now(timezone.utc)
    )
    db_session.add(link)
    
    # Add a note (requirement: >= 1 note)
    note = CaseNote(
        note_id=uuid.uuid4(),
        case_id=case.case_id,
        note_category="investigation",
        note_text="Investigation complete, ready for review.",
        author_user_id=investigator_user_id,
        authored_at_utc=datetime.now(timezone.utc)
    )
    db_session.add(note)
    
    db_session.commit()
    
    # Share for review
    response = auth_client.post(f"/api/v1/cases/{case.case_id}/share-for-review")
    
    assert response.status_code == 200
    data = response.json()
    assert data["case_id"] == str(case.case_id)
    assert data["status"] == "UNDER_REVIEW"
    assert "shared_at_utc" in data


def test_share_for_review_blocks_without_officer(auth_client, db_session):
    """Test that share-for-review fails without officer assignment."""
    # Create customer, account, transaction, alert
    customer = Customer(
        customer_id=uuid.uuid4(),
        customer_name="No Officer Customer",
        pep_flag=False,
        country_code="US"
    )
    db_session.add(customer)
    
    account = Account(
        account_id=uuid.uuid4(),
        customer_id=customer.customer_id,
        account_ref="ACC-NO-OFF-001",
        account_type="Checking"
    )
    db_session.add(account)
    
    transaction = Transaction(
        transaction_id=uuid.uuid4(),
        account_id=account.account_id,
        transaction_ref="TXN-NO-OFF-001",
        amount=40000.00,
        currency_code="USD",
        source_country_code="US",
        destination_country_code="UK",
        executed_at_utc=datetime.now(timezone.utc) - timedelta(hours=1)
    )
    db_session.add(transaction)
    
    alert = Alert(
        alert_id=uuid.uuid4(),
        alert_ref="ALT-NO-OFF-001",
        transaction_id=transaction.transaction_id,
        customer_id=customer.customer_id,
        priority="Medium",
        risk_score=70,
        status="New",
        owner_user_id=None,
        triggered_at_utc=datetime.now(timezone.utc) - timedelta(hours=1)
    )
    db_session.add(alert)
    
    # Get test user ID
    login_response = auth_client.get("/api/v1/auth/me")
    assert login_response.status_code == 200
    investigator_user_id = uuid.UUID(login_response.json()["user_id"])
    
    # Create case WITHOUT officer assignment
    case = AmlCase(
        case_id=uuid.uuid4(),
        case_ref="CS-NO-OFF-001",
        primary_alert_id=alert.alert_id,
        created_by_user_id=investigator_user_id,
        assigned_officer_user_id=None,  # No officer assigned
        status="INVESTIGATING",
        current_blocker_state="NONE"
    )
    db_session.add(case)
    
    # Create case alert link
    link = CaseAlertLink(
        case_alert_link_id=uuid.uuid4(),
        case_id=case.case_id,
        alert_id=alert.alert_id,
        is_primary=True,
        linked_by_user_id=investigator_user_id,
        linked_at_utc=datetime.now(timezone.utc)
    )
    db_session.add(link)
    
    # Add a note
    note = CaseNote(
        note_id=uuid.uuid4(),
        case_id=case.case_id,
        note_category="investigation",
        note_text="Investigation in progress.",
        author_user_id=investigator_user_id,
        authored_at_utc=datetime.now(timezone.utc)
    )
    db_session.add(note)
    
    db_session.commit()
    
    # Attempt share-for-review without officer (should fail with 409)
    response = auth_client.post(f"/api/v1/cases/{case.case_id}/share-for-review")
    
    assert response.status_code == 409
    assert "officer" in response.json()["detail"].lower()


def test_decision_recording_creates_immutable_hash(auth_client, db_session):
    """Test that decision recording creates immutable hash."""
    # Create customer, account, transaction, alert
    customer = Customer(
        customer_id=uuid.uuid4(),
        customer_name="Decision Customer",
        pep_flag=False,
        country_code="US"
    )
    db_session.add(customer)
    
    account = Account(
        account_id=uuid.uuid4(),
        customer_id=customer.customer_id,
        account_ref="ACC-DEC-001",
        account_type="Checking"
    )
    db_session.add(account)
    
    transaction = Transaction(
        transaction_id=uuid.uuid4(),
        account_id=account.account_id,
        transaction_ref="TXN-DEC-001",
        amount=60000.00,
        currency_code="USD",
        source_country_code="US",
        destination_country_code="FR",
        executed_at_utc=datetime.now(timezone.utc) - timedelta(hours=2)
    )
    db_session.add(transaction)
    
    alert = Alert(
        alert_id=uuid.uuid4(),
        alert_ref="ALT-DEC-001",
        transaction_id=transaction.transaction_id,
        customer_id=customer.customer_id,
        priority="High",
        risk_score=82,
        status="Under Review",
        owner_user_id=None,
        triggered_at_utc=datetime.now(timezone.utc) - timedelta(hours=2)
    )
    db_session.add(alert)
    
    # Create officer user
    from app.core.security import hash_password
    officer = User(
        user_id=uuid.uuid4(),
        display_name="Decision Officer",
        email="decision-officer@example.com",
        hashed_password=hash_password("officer123"),
        role="OFFICER",
        is_active=True
    )
    db_session.add(officer)
    
    # Create investigator
    investigator = User(
        user_id=uuid.uuid4(),
        display_name="Decision Investigator",
        email="decision-investigator@example.com",
        hashed_password=hash_password("investigator123"),
        role="INVESTIGATOR",
        is_active=True
    )
    db_session.add(investigator)
    
    # Create case
    case = AmlCase(
        case_id=uuid.uuid4(),
        case_ref="CS-DEC-001",
        primary_alert_id=alert.alert_id,
        created_by_user_id=investigator.user_id,
        assigned_officer_user_id=officer.user_id,
        status="UNDER_REVIEW",
        current_blocker_state="NONE"
    )
    db_session.add(case)
    
    # Create case alert link
    link = CaseAlertLink(
        case_alert_link_id=uuid.uuid4(),
        case_id=case.case_id,
        alert_id=alert.alert_id,
        is_primary=True,
        linked_by_user_id=investigator.user_id,
        linked_at_utc=datetime.now(timezone.utc)
    )
    db_session.add(link)
    
    db_session.commit()
    
    # Login as officer
    officer_client = auth_client.__class__(auth_client.app)
    login_response = officer_client.post(
        "/api/v1/auth/login",
        json={"email": "decision-officer@example.com", "password": "officer123"}
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    officer_client.headers["Authorization"] = f"Bearer {token}"
    
    # Record decision
    response = officer_client.post(
        f"/api/v1/cases/{case.case_id}/decision",
        json={
            "outcome": "APPROVE",
            "rationale_text": "Case approved after comprehensive review of all supporting documentation."
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert "decision_id" in data
    assert data["outcome"] == "APPROVE"
    assert "immutable_hash" in data
    assert len(data["immutable_hash"]) == 64  # SHA-256 hash length
    assert data["rationale_text"] == "Case approved after comprehensive review of all supporting documentation."
