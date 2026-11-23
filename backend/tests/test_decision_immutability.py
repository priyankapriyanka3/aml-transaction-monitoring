"""Tests for decision immutability and mandatory rationale."""
import uuid
from datetime import datetime, timezone, timedelta
from app.models.case import AmlCase
from app.models.alert import Alert
from app.models.customer import Customer
from app.models.account import Account
from app.models.transaction import Transaction
from app.models.case_alert_link import CaseAlertLink
from app.models.user import User


def test_decision_requires_rationale(auth_client, db_session):
    """Test that decision recording requires non-empty rationale."""
    # Create customer, account, transaction, alert
    customer = Customer(
        customer_id=uuid.uuid4(),
        customer_name="Rationale Customer",
        pep_flag=False,
        country_code="US"
    )
    db_session.add(customer)
    
    account = Account(
        account_id=uuid.uuid4(),
        customer_id=customer.customer_id,
        account_ref="ACC-RAT-001",
        account_type="Checking"
    )
    db_session.add(account)
    
    transaction = Transaction(
        transaction_id=uuid.uuid4(),
        account_id=account.account_id,
        transaction_ref="TXN-RAT-001",
        amount=45000.00,
        currency_code="USD",
        source_country_code="US",
        destination_country_code="UK",
        executed_at_utc=datetime.now(timezone.utc) - timedelta(hours=1)
    )
    db_session.add(transaction)
    
    alert = Alert(
        alert_id=uuid.uuid4(),
        alert_ref="ALT-RAT-001",
        transaction_id=transaction.transaction_id,
        customer_id=customer.customer_id,
        priority="Medium",
        risk_score=75,
        status="Under Review",
        owner_user_id=None,
        triggered_at_utc=datetime.now(timezone.utc) - timedelta(hours=1)
    )
    db_session.add(alert)
    
    # Create officer user
    from app.core.security import hash_password
    officer = User(
        user_id=uuid.uuid4(),
        display_name="Rationale Officer",
        email="rationale-officer@example.com",
        hashed_password=hash_password("officer123"),
        role="OFFICER",
        is_active=True
    )
    db_session.add(officer)
    
    # Create investigator
    investigator = User(
        user_id=uuid.uuid4(),
        display_name="Rationale Investigator",
        email="rationale-investigator@example.com",
        hashed_password=hash_password("investigator123"),
        role="INVESTIGATOR",
        is_active=True
    )
    db_session.add(investigator)
    
    # Create case
    case = AmlCase(
        case_id=uuid.uuid4(),
        case_ref="CS-RAT-001",
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
        json={"email": "rationale-officer@example.com", "password": "officer123"}
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    officer_client.headers["Authorization"] = f"Bearer {token}"
    
    # Attempt decision with empty rationale (should fail with 422)
    response = officer_client.post(
        f"/api/v1/cases/{case.case_id}/decision",
        json={
            "outcome": "APPROVE",
            "rationale_text": ""  # Empty rationale
        }
    )
    
    assert response.status_code == 422
    assert "rationale" in response.json()["detail"].lower()
    
    # Attempt decision with whitespace-only rationale (should fail with 422)
    response2 = officer_client.post(
        f"/api/v1/cases/{case.case_id}/decision",
        json={
            "outcome": "APPROVE",
            "rationale_text": "   "  # Whitespace only
        }
    )
    
    assert response2.status_code == 422
    assert "rationale" in response2.json()["detail"].lower()


def test_decision_blocks_with_open_requests(auth_client, db_session):
    """Test that decision recording is blocked when open requests exist."""
    # Create customer, account, transaction, alert
    customer = Customer(
        customer_id=uuid.uuid4(),
        customer_name="Open Request Customer",
        pep_flag=False,
        country_code="US"
    )
    db_session.add(customer)
    
    account = Account(
        account_id=uuid.uuid4(),
        customer_id=customer.customer_id,
        account_ref="ACC-OPEN-001",
        account_type="Checking"
    )
    db_session.add(account)
    
    transaction = Transaction(
        transaction_id=uuid.uuid4(),
        account_id=account.account_id,
        transaction_ref="TXN-OPEN-001",
        amount=55000.00,
        currency_code="USD",
        source_country_code="US",
        destination_country_code="CH",
        executed_at_utc=datetime.now(timezone.utc) - timedelta(hours=2)
    )
    db_session.add(transaction)
    
    alert = Alert(
        alert_id=uuid.uuid4(),
        alert_ref="ALT-OPEN-001",
        transaction_id=transaction.transaction_id,
        customer_id=customer.customer_id,
        priority="High",
        risk_score=88,
        status="Under Review",
        owner_user_id=None,
        triggered_at_utc=datetime.now(timezone.utc) - timedelta(hours=2)
    )
    db_session.add(alert)
    
    # Create officer user
    from app.core.security import hash_password
    officer = User(
        user_id=uuid.uuid4(),
        display_name="Open Request Officer",
        email="open-request-officer@example.com",
        hashed_password=hash_password("officer123"),
        role="OFFICER",
        is_active=True
    )
    db_session.add(officer)
    
    # Create investigator
    investigator = User(
        user_id=uuid.uuid4(),
        display_name="Open Request Investigator",
        email="open-request-investigator@example.com",
        hashed_password=hash_password("investigator123"),
        role="INVESTIGATOR",
        is_active=True
    )
    db_session.add(investigator)
    
    # Create case with OPEN request blocker
    case = AmlCase(
        case_id=uuid.uuid4(),
        case_ref="CS-OPEN-001",
        primary_alert_id=alert.alert_id,
        created_by_user_id=investigator.user_id,
        assigned_officer_user_id=officer.user_id,
        status="UNDER_REVIEW",
        current_blocker_state="OPEN_REQUESTS"  # Blocker present
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
    
    # Create an OPEN information request
    from app.models.evidence_gap import EvidenceGap
    from app.models.information_request import InformationRequest
    
    gap = EvidenceGap(
        gap_id=uuid.uuid4(),
        case_id=case.case_id,
        title="Missing documentation",
        description="Need additional supporting docs",
        status="OPEN",
        created_by_user_id=investigator.user_id,
        created_at_utc=datetime.now(timezone.utc)
    )
    db_session.add(gap)
    
    info_request = InformationRequest(
        request_id=uuid.uuid4(),
        request_ref="IR-OPEN-001",
        case_id=case.case_id,
        gap_id=gap.gap_id,
        target_party="Customer",
        delivery_channel="Email",
        reason_text="Need supporting documentation",
        due_at_utc=datetime.now(timezone.utc) + timedelta(days=3),
        status="OPEN",  # Open request
        created_by_user_id=investigator.user_id,
        created_at_utc=datetime.now(timezone.utc),
        updated_at_utc=datetime.now(timezone.utc)
    )
    db_session.add(info_request)
    
    db_session.commit()
    
    # Login as officer
    officer_client = auth_client.__class__(auth_client.app)
    login_response = officer_client.post(
        "/api/v1/auth/login",
        json={"email": "open-request-officer@example.com", "password": "officer123"}
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    officer_client.headers["Authorization"] = f"Bearer {token}"
    
    # Attempt decision with open request (should fail with 409)
    response = officer_client.post(
        f"/api/v1/cases/{case.case_id}/decision",
        json={
            "outcome": "APPROVE",
            "rationale_text": "Case approved with thorough review."
        }
    )
    
    assert response.status_code == 409
    assert "OPEN_REQUESTS" in response.json()["detail"] or "open" in response.json()["detail"].lower()
