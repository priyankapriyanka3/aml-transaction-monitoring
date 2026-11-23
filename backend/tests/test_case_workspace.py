"""Tests for case workspace endpoint."""
import uuid
from datetime import datetime, timezone, timedelta
from decimal import Decimal


def test_get_case_workspace(auth_client, db_session):
    """Test retrieving case workspace with linked alerts, notes, and timeline."""
    from app.models.user import User
    from app.models.customer import Customer
    from app.models.account import Account
    from app.models.transaction import Transaction
    from app.models.alert import Alert
    from app.models.case import AmlCase
    from app.models.case_alert_link import CaseAlertLink
    from app.models.case_note import CaseNote
    from app.core.security import hash_password
    
    # Create test user
    user = User(
        display_name="Test Investigator",
        email="workspace_test@example.com",
        hashed_password=hash_password("test123"),
        role="INVESTIGATOR",
        is_active=True
    )
    db_session.add(user)
    
    # Create test customer, account, transaction, alerts
    customer = Customer(
        customer_name="Workspace Test Customer",
        pep_flag=False,
        country_code="US"
    )
    db_session.add(customer)
    db_session.flush()
    
    account = Account(
        customer_id=customer.customer_id,
        account_ref="WS-TEST-001",
        account_type="Business"
    )
    db_session.add(account)
    db_session.flush()
    
    transaction1 = Transaction(
        account_id=account.account_id,
        transaction_ref="TXN-WS-001",
        amount=Decimal("75000.00"),
        currency_code="USD",
        source_country_code="US",
        destination_country_code="KY",
        executed_at_utc=datetime.now(timezone.utc) - timedelta(hours=2)
    )
    db_session.add(transaction1)
    db_session.flush()
    
    transaction2 = Transaction(
        account_id=account.account_id,
        transaction_ref="TXN-WS-002",
        amount=Decimal("45000.00"),
        currency_code="USD",
        source_country_code="US",
        destination_country_code="PA",
        executed_at_utc=datetime.now(timezone.utc) - timedelta(hours=4)
    )
    db_session.add(transaction2)
    db_session.flush()
    
    alert1 = Alert(
        alert_ref="ALT-WS-001",
        transaction_id=transaction1.transaction_id,
        customer_id=customer.customer_id,
        priority="High",
        risk_score=85,
        status="Under Review",
        owner_user_id=user.user_id,
        triggered_at_utc=datetime.now(timezone.utc) - timedelta(hours=2)
    )
    db_session.add(alert1)
    db_session.flush()
    
    alert2 = Alert(
        alert_ref="ALT-WS-002",
        transaction_id=transaction2.transaction_id,
        customer_id=customer.customer_id,
        priority="Medium",
        risk_score=70,
        status="Under Review",
        owner_user_id=user.user_id,
        triggered_at_utc=datetime.now(timezone.utc) - timedelta(hours=4)
    )
    db_session.add(alert2)
    db_session.flush()
    
    # Create test case
    case = AmlCase(
        case_ref="CS-WS-001",
        primary_alert_id=alert1.alert_id,
        created_by_user_id=user.user_id,
        status="INVESTIGATING"
    )
    db_session.add(case)
    db_session.flush()
    
    # Create alert links (primary and secondary)
    link1 = CaseAlertLink(
        case_id=case.case_id,
        alert_id=alert1.alert_id,
        is_primary=True,
        linked_by_user_id=user.user_id,
        linked_at_utc=datetime.now(timezone.utc) - timedelta(hours=1)
    )
    db_session.add(link1)
    
    link2 = CaseAlertLink(
        case_id=case.case_id,
        alert_id=alert2.alert_id,
        is_primary=False,
        linked_by_user_id=user.user_id,
        linked_at_utc=datetime.now(timezone.utc) - timedelta(minutes=30)
    )
    db_session.add(link2)
    
    # Create notes
    note1 = CaseNote(
        case_id=case.case_id,
        note_category="investigation",
        note_text="Initial review shows high-value offshore transaction.",
        author_user_id=user.user_id,
        authored_at_utc=datetime.now(timezone.utc) - timedelta(minutes=45)
    )
    db_session.add(note1)
    
    note2 = CaseNote(
        case_id=case.case_id,
        note_category="recommendation",
        note_text="Recommend requesting additional documentation from customer.",
        author_user_id=user.user_id,
        authored_at_utc=datetime.now(timezone.utc) - timedelta(minutes=15)
    )
    db_session.add(note2)
    
    note3 = CaseNote(
        case_id=case.case_id,
        note_category="investigation",
        note_text="Customer provided invoice supporting the transaction.",
        author_user_id=user.user_id,
        authored_at_utc=datetime.now(timezone.utc) - timedelta(minutes=5)
    )
    db_session.add(note3)
    
    db_session.commit()
    
    # Call workspace endpoint
    response = auth_client.get(f"/api/v1/cases/{case.case_id}/workspace")
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify case metadata
    assert data["case_id"] == str(case.case_id)
    assert data["case_ref"] == "CS-WS-001"
    assert data["status"] == "INVESTIGATING"
    assert data["current_blocker_state"] == "NONE"
    
    # Verify linked alerts structure {items, total}
    assert "linked_alerts" in data
    assert "items" in data["linked_alerts"]
    assert "total" in data["linked_alerts"]
    assert data["linked_alerts"]["total"] == 2
    assert len(data["linked_alerts"]["items"]) == 2
    
    # Verify primary alert is first (ordered by linked_at_utc asc)
    primary_alert = data["linked_alerts"]["items"][0]
    assert primary_alert["is_primary"] is True
    assert primary_alert["alert_ref"] == "ALT-WS-001"
    
    secondary_alert = data["linked_alerts"]["items"][1]
    assert secondary_alert["is_primary"] is False
    assert secondary_alert["alert_ref"] == "ALT-WS-002"
    
    # Verify notes structure {items, total}
    assert "notes" in data
    assert "items" in data["notes"]
    assert "total" in data["notes"]
    assert data["notes"]["total"] == 3
    assert len(data["notes"]["items"]) == 3
    
    # Verify notes ordered by authored_at_utc DESC (most recent first)
    assert data["notes"]["items"][0]["note_text"] == "Customer provided invoice supporting the transaction."
    assert data["notes"]["items"][1]["note_text"] == "Recommend requesting additional documentation from customer."
    assert data["notes"]["items"][2]["note_text"] == "Initial review shows high-value offshore transaction."
    
    # Verify evidence gaps structure (empty for now)
    assert "evidence_gaps" in data
    assert data["evidence_gaps"]["total"] == 0
    assert len(data["evidence_gaps"]["items"]) == 0
    
    # Verify timeline structure
    assert "timeline_entries" in data
    assert "items" in data["timeline_entries"]
    assert "total" in data["timeline_entries"]
    # Timeline should be empty if no audit events created


def test_get_case_workspace_not_found(auth_client):
    """Test workspace endpoint returns 404 for non-existent case."""
    fake_case_id = uuid.uuid4()
    response = auth_client.get(f"/api/v1/cases/{fake_case_id}/workspace")
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
