"""Tests for four-eyes enforcement in officer assignment and decision recording."""
import uuid
from datetime import datetime, timezone, timedelta
from app.models.case import AmlCase
from app.models.alert import Alert
from app.models.customer import Customer
from app.models.account import Account
from app.models.transaction import Transaction
from app.models.case_alert_link import CaseAlertLink


def test_assign_officer_prevents_case_creator_assignment(auth_client, db_session):
    """Test that officer assignment prevents case creator from being assigned."""
    # Create customer, account, transaction, alert
    customer = Customer(
        customer_id=uuid.uuid4(),
        customer_name="Test Customer",
        pep_flag=False,
        country_code="US"
    )
    db_session.add(customer)
    
    account = Account(
        account_id=uuid.uuid4(),
        customer_id=customer.customer_id,
        account_ref="ACC-TEST-001",
        account_type="Checking"
    )
    db_session.add(account)
    
    transaction = Transaction(
        transaction_id=uuid.uuid4(),
        account_id=account.account_id,
        transaction_ref="TXN-TEST-001",
        amount=50000.00,
        currency_code="USD",
        source_country_code="US",
        destination_country_code="CH",
        executed_at_utc=datetime.now(timezone.utc) - timedelta(hours=1)
    )
    db_session.add(transaction)
    
    alert = Alert(
        alert_id=uuid.uuid4(),
        alert_ref="ALT-TEST-001",
        transaction_id=transaction.transaction_id,
        customer_id=customer.customer_id,
        priority="High",
        risk_score=85,
        status="New",
        owner_user_id=None,
        triggered_at_utc=datetime.now(timezone.utc) - timedelta(hours=1)
    )
    db_session.add(alert)
    
    # Get test user ID from auth_client
    login_response = auth_client.get("/api/v1/auth/me")
    assert login_response.status_code == 200
    investigator_user_id = uuid.UUID(login_response.json()["user_id"])
    
    # Create case as investigator
    case = AmlCase(
        case_id=uuid.uuid4(),
        case_ref="CS-TEST-001",
        primary_alert_id=alert.alert_id,
        created_by_user_id=investigator_user_id,
        assigned_officer_user_id=None,
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
    
    db_session.commit()
    
    # Attempt to assign case creator as officer (should fail with 409)
    response = auth_client.post(
        f"/api/v1/cases/{case.case_id}/assign-officer",
        json={"officer_user_id": str(investigator_user_id)}
    )
    
    assert response.status_code == 409
    assert "four-eyes" in response.json()["detail"].lower()


def test_decision_recording_prevents_case_creator_decision(auth_client, db_session):
    """Test that decision recording prevents case creator from deciding own case."""
    # Create customer, account, transaction, alert
    customer = Customer(
        customer_id=uuid.uuid4(),
        customer_name="Test Customer 2",
        pep_flag=False,
        country_code="US"
    )
    db_session.add(customer)
    
    account = Account(
        account_id=uuid.uuid4(),
        customer_id=customer.customer_id,
        account_ref="ACC-TEST-002",
        account_type="Checking"
    )
    db_session.add(account)
    
    transaction = Transaction(
        transaction_id=uuid.uuid4(),
        account_id=account.account_id,
        transaction_ref="TXN-TEST-002",
        amount=60000.00,
        currency_code="USD",
        source_country_code="US",
        destination_country_code="UK",
        executed_at_utc=datetime.now(timezone.utc) - timedelta(hours=2)
    )
    db_session.add(transaction)
    
    alert = Alert(
        alert_id=uuid.uuid4(),
        alert_ref="ALT-TEST-002",
        transaction_id=transaction.transaction_id,
        customer_id=customer.customer_id,
        priority="High",
        risk_score=80,
        status="Under Review",
        owner_user_id=None,
        triggered_at_utc=datetime.now(timezone.utc) - timedelta(hours=2)
    )
    db_session.add(alert)
    
    # Get test user ID
    login_response = auth_client.get("/api/v1/auth/me")
    assert login_response.status_code == 200
    investigator_user_id = uuid.UUID(login_response.json()["user_id"])
    
    # Create case as investigator
    case = AmlCase(
        case_id=uuid.uuid4(),
        case_ref="CS-TEST-002",
        primary_alert_id=alert.alert_id,
        created_by_user_id=investigator_user_id,
        assigned_officer_user_id=investigator_user_id,  # Assigned to self
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
        linked_by_user_id=investigator_user_id,
        linked_at_utc=datetime.now(timezone.utc)
    )
    db_session.add(link)
    
    db_session.commit()
    
    # Attempt to record decision as case creator (should fail with 403)
    response = auth_client.post(
        f"/api/v1/cases/{case.case_id}/decision",
        json={
            "outcome": "APPROVE",
            "rationale_text": "Case approved after thorough review."
        }
    )
    
    assert response.status_code == 403
    assert "four-eyes" in response.json()["detail"].lower() or "own case" in response.json()["detail"].lower()


def test_readiness_excludes_case_creator_from_eligible_officers(auth_client, db_session):
    """Test that readiness endpoint excludes case creator from eligible officers list."""
    # Create customer, account, transaction, alert
    customer = Customer(
        customer_id=uuid.uuid4(),
        customer_name="Test Customer 3",
        pep_flag=False,
        country_code="US"
    )
    db_session.add(customer)
    
    account = Account(
        account_id=uuid.uuid4(),
        customer_id=customer.customer_id,
        account_ref="ACC-TEST-003",
        account_type="Checking"
    )
    db_session.add(account)
    
    transaction = Transaction(
        transaction_id=uuid.uuid4(),
        account_id=account.account_id,
        transaction_ref="TXN-TEST-003",
        amount=75000.00,
        currency_code="USD",
        source_country_code="US",
        destination_country_code="FR",
        executed_at_utc=datetime.now(timezone.utc) - timedelta(hours=3)
    )
    db_session.add(transaction)
    
    alert = Alert(
        alert_id=uuid.uuid4(),
        alert_ref="ALT-TEST-003",
        transaction_id=transaction.transaction_id,
        customer_id=customer.customer_id,
        priority="High",
        risk_score=88,
        status="Under Review",
        owner_user_id=None,
        triggered_at_utc=datetime.now(timezone.utc) - timedelta(hours=3)
    )
    db_session.add(alert)
    
    # Get test user ID
    login_response = auth_client.get("/api/v1/auth/me")
    assert login_response.status_code == 200
    investigator_user_id = uuid.UUID(login_response.json()["user_id"])
    
    # Create case as investigator
    case = AmlCase(
        case_id=uuid.uuid4(),
        case_ref="CS-TEST-003",
        primary_alert_id=alert.alert_id,
        created_by_user_id=investigator_user_id,
        assigned_officer_user_id=None,
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
    
    # Add a note so checklist items are complete
    from app.models.case_note import CaseNote
    note = CaseNote(
        note_id=uuid.uuid4(),
        case_id=case.case_id,
        note_category="investigation",
        note_text="Initial investigation complete.",
        author_user_id=investigator_user_id,
        authored_at_utc=datetime.now(timezone.utc)
    )
    db_session.add(note)
    
    db_session.commit()
    
    # Get readiness checklist
    response = auth_client.get(f"/api/v1/cases/{case.case_id}/readiness")
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify eligible_officers field exists
    assert "eligible_officers" in data
    
    # Verify case creator is NOT in eligible officers list
    eligible_officer_ids = [officer["user_id"] for officer in data["eligible_officers"]]
    assert str(investigator_user_id) not in eligible_officer_ids
