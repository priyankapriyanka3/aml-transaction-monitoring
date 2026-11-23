"""Tests for case note service."""
import uuid
import pytest
from app.services.case_service import CaseService


def test_add_note(db_session):
    """Test adding an investigation note to a case."""
    from app.models.user import User
    from app.models.customer import Customer
    from app.models.account import Account
    from app.models.transaction import Transaction
    from app.models.alert import Alert
    from app.models.case import AmlCase
    from app.core.security import hash_password
    from datetime import datetime, timezone, timedelta
    from decimal import Decimal
    
    # Create test user
    user = User(
        display_name="Test Investigator",
        email="test@example.com",
        hashed_password=hash_password("test123"),
        role="INVESTIGATOR",
        is_active=True
    )
    db_session.add(user)
    
    # Create test customer, account, transaction, alert
    customer = Customer(
        customer_name="Test Customer",
        pep_flag=False,
        country_code="US"
    )
    db_session.add(customer)
    db_session.flush()
    
    account = Account(
        customer_id=customer.customer_id,
        account_ref="TEST-001",
        account_type="Checking"
    )
    db_session.add(account)
    db_session.flush()
    
    transaction = Transaction(
        account_id=account.account_id,
        transaction_ref="TXN-TEST-001",
        amount=Decimal("50000.00"),
        currency_code="USD",
        source_country_code="US",
        destination_country_code="VG",
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
        status="New",
        owner_user_id=None,
        triggered_at_utc=datetime.now(timezone.utc)
    )
    db_session.add(alert)
    db_session.flush()
    
    # Create test case
    case = AmlCase(
        case_ref="CS-TEST-001",
        primary_alert_id=alert.alert_id,
        created_by_user_id=user.user_id,
        status="OPEN"
    )
    db_session.add(case)
    db_session.commit()
    
    # Add note
    service = CaseService(db_session)
    note = service.add_note(
        case_id=case.case_id,
        note_category="investigation",
        note_text="This is a test investigation note.",
        author_user_id=user.user_id,
        actor_role="INVESTIGATOR",
        correlation_id="test-correlation-id"
    )
    
    # Verify note was created
    assert note.note_id is not None
    assert note.case_id == case.case_id
    assert note.note_category == "investigation"
    assert note.note_text == "This is a test investigation note."
    assert note.author_user_id == user.user_id
    assert note.authored_at_utc is not None
    
    # Verify audit event was created
    from app.models.audit_event import AuditEvent
    from sqlalchemy import select
    
    stmt = select(AuditEvent).where(
        AuditEvent.entity_type == "CASE",
        AuditEvent.entity_id == case.case_id,
        AuditEvent.action_type == "NOTE_ADDED"
    )
    audit_event = db_session.scalars(stmt).first()
    
    assert audit_event is not None
    assert audit_event.actor_user_id == user.user_id
    assert audit_event.correlation_id == "test-correlation-id"


def test_add_note_case_not_found(db_session):
    """Test adding note to non-existent case raises ValueError."""
    from app.models.user import User
    from app.core.security import hash_password
    
    # Create test user
    user = User(
        display_name="Test User",
        email="test2@example.com",
        hashed_password=hash_password("test123"),
        role="INVESTIGATOR",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    
    service = CaseService(db_session)
    
    # Try to add note to non-existent case
    with pytest.raises(ValueError, match="not found"):
        service.add_note(
            case_id=uuid.uuid4(),
            note_category="investigation",
            note_text="Test note",
            author_user_id=user.user_id,
            actor_role="INVESTIGATOR",
            correlation_id="test-corr-id"
        )
