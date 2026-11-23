"""Tests for case service."""
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from app.models.alert import Alert
from app.models.transaction import Transaction
from app.models.customer import Customer
from app.models.account import Account
from app.models.user import User
from app.models.audit_event import AuditEvent
from app.models.case_alert_link import CaseAlertLink
from app.services.case_service import CaseService
from app.repositories.case_repository import CaseRepository
from app.core.security import hash_password


def test_create_case_from_alert_success(db_session):
    """Test creating a case from an alert with audit events."""
    # Create user
    user = User(
        user_id=uuid.UUID("11111111-0000-0000-0000-000000000001"),
        display_name="Test User",
        email="test@example.com",
        hashed_password=hash_password("test123"),
        role="INVESTIGATOR",
        is_active=True,
        created_at_utc=datetime.now(timezone.utc),
        updated_at_utc=datetime.now(timezone.utc)
    )
    db_session.add(user)
    
    # Create customer
    customer = Customer(
        customer_id=uuid.UUID("22222222-0000-0000-0000-000000000001"),
        customer_name="Test Customer",
        pep_flag=False,
        country_code="US",
        created_at_utc=datetime.now(timezone.utc)
    )
    db_session.add(customer)
    
    # Create account
    account = Account(
        account_id=uuid.UUID("33333333-0000-0000-0000-000000000001"),
        customer_id=customer.customer_id,
        account_ref="ACC-001",
        account_type="CHECKING",
        created_at_utc=datetime.now(timezone.utc)
    )
    db_session.add(account)
    
    # Create transaction
    transaction = Transaction(
        transaction_id=uuid.UUID("44444444-0000-0000-0000-000000000001"),
        account_id=account.account_id,
        transaction_ref="TXN-001",
        amount=Decimal("15000.00"),
        currency_code="USD",
        source_country_code="US",
        destination_country_code="GB",
        executed_at_utc=datetime.now(timezone.utc),
        created_at_utc=datetime.now(timezone.utc)
    )
    db_session.add(transaction)
    
    # Create alert
    alert = Alert(
        alert_id=uuid.UUID("55555555-0000-0000-0000-000000000001"),
        alert_ref="ALT-001",
        transaction_id=transaction.transaction_id,
        customer_id=customer.customer_id,
        priority="Critical",
        risk_score=95,
        status="New",
        owner_user_id=None,
        triggered_at_utc=datetime.now(timezone.utc),
        created_at_utc=datetime.now(timezone.utc)
    )
    db_session.add(alert)
    db_session.commit()
    
    # Create case
    service = CaseService(db_session)
    case = service.create_case_from_alert(
        alert_id=alert.alert_id,
        created_by_user_id=user.user_id,
        actor_role="INVESTIGATOR",
        correlation_id="test-corr-123"
    )
    
    # Verify case created
    assert case.case_id is not None
    assert case.case_ref.startswith("CS-")
    assert case.primary_alert_id == alert.alert_id
    assert case.created_by_user_id == user.user_id
    assert case.status == "OPEN"
    assert case.current_blocker_state == "NONE"
    
    # Verify audit events created
    audit_events = db_session.query(AuditEvent).filter_by(
        correlation_id="test-corr-123"
    ).all()
    
    assert len(audit_events) == 2
    
    # Check case creation event
    creation_event = next(e for e in audit_events if e.action_type == "CASE_CREATED")
    assert creation_event.entity_type == "CASE"
    assert creation_event.entity_id == case.case_id
    assert creation_event.actor_user_id == user.user_id
    assert creation_event.actor_role == "INVESTIGATOR"
    
    # Check alert linkage event
    link_event = next(e for e in audit_events if e.action_type == "ALERT_LINKED")
    assert link_event.entity_type == "CASE"
    assert link_event.entity_id == case.case_id
    assert link_event.actor_user_id == user.user_id


def test_create_case_from_nonexistent_alert(db_session):
    """Test creating case from non-existent alert raises ValueError."""
    # Create user
    user = User(
        user_id=uuid.UUID("11111111-0000-0000-0000-000000000001"),
        display_name="Test User",
        email="test@example.com",
        hashed_password=hash_password("test123"),
        role="INVESTIGATOR",
        is_active=True,
        created_at_utc=datetime.now(timezone.utc),
        updated_at_utc=datetime.now(timezone.utc)
    )
    db_session.add(user)
    db_session.commit()
    
    service = CaseService(db_session)
    
    try:
        service.create_case_from_alert(
            alert_id=uuid.uuid4(),
            created_by_user_id=user.user_id,
            actor_role="INVESTIGATOR",
            correlation_id="test-corr-123"
        )
        assert False, "Expected ValueError"
    except ValueError as e:
        assert "not found" in str(e).lower()


def test_case_ref_generation_sequential(db_session):
    """Test that case references are generated sequentially."""
    # Create user
    user = User(
        user_id=uuid.UUID("11111111-0000-0000-0000-000000000001"),
        display_name="Test User",
        email="test@example.com",
        hashed_password=hash_password("test123"),
        role="INVESTIGATOR",
        is_active=True,
        created_at_utc=datetime.now(timezone.utc),
        updated_at_utc=datetime.now(timezone.utc)
    )
    db_session.add(user)
    
    # Create customer, account, transaction, alert
    customer = Customer(
        customer_id=uuid.UUID("22222222-0000-0000-0000-000000000001"),
        customer_name="Test Customer",
        pep_flag=False,
        country_code="US",
        created_at_utc=datetime.now(timezone.utc)
    )
    db_session.add(customer)
    
    account = Account(
        account_id=uuid.UUID("33333333-0000-0000-0000-000000000001"),
        customer_id=customer.customer_id,
        account_ref="ACC-001",
        account_type="CHECKING",
        created_at_utc=datetime.now(timezone.utc)
    )
    db_session.add(account)
    
    transaction = Transaction(
        transaction_id=uuid.UUID("44444444-0000-0000-0000-000000000001"),
        account_id=account.account_id,
        transaction_ref="TXN-001",
        amount=Decimal("15000.00"),
        currency_code="USD",
        source_country_code="US",
        destination_country_code="GB",
        executed_at_utc=datetime.now(timezone.utc),
        created_at_utc=datetime.now(timezone.utc)
    )
    db_session.add(transaction)
    
    alert = Alert(
        alert_id=uuid.UUID("55555555-0000-0000-0000-000000000001"),
        alert_ref="ALT-001",
        transaction_id=transaction.transaction_id,
        customer_id=customer.customer_id,
        priority="Critical",
        risk_score=95,
        status="New",
        owner_user_id=None,
        triggered_at_utc=datetime.now(timezone.utc),
        created_at_utc=datetime.now(timezone.utc)
    )
    db_session.add(alert)
    db_session.commit()
    
    service = CaseService(db_session)
    
    # Create first case
    case1 = service.create_case_from_alert(
        alert_id=alert.alert_id,
        created_by_user_id=user.user_id,
        actor_role="INVESTIGATOR",
        correlation_id="test-corr-1"
    )
    
    assert case1.case_ref == "CS-1"


def test_add_alert_link(db_session):
    """Test adding a secondary alert link to an existing case."""
    # Create user
    user = User(
        user_id=uuid.UUID("11111111-0000-0000-0000-000000000001"),
        display_name="Test User",
        email="test@example.com",
        hashed_password=hash_password("test123"),
        role="INVESTIGATOR",
        is_active=True,
        created_at_utc=datetime.now(timezone.utc),
        updated_at_utc=datetime.now(timezone.utc)
    )
    db_session.add(user)
    
    # Create customer, account
    customer = Customer(
        customer_id=uuid.UUID("22222222-0000-0000-0000-000000000001"),
        customer_name="Test Customer",
        pep_flag=False,
        country_code="US",
        created_at_utc=datetime.now(timezone.utc)
    )
    db_session.add(customer)
    
    account = Account(
        account_id=uuid.UUID("33333333-0000-0000-0000-000000000001"),
        customer_id=customer.customer_id,
        account_ref="ACC-001",
        account_type="CHECKING",
        created_at_utc=datetime.now(timezone.utc)
    )
    db_session.add(account)
    
    # Create transactions and alerts
    transaction1 = Transaction(
        transaction_id=uuid.UUID("44444444-0000-0000-0000-000000000001"),
        account_id=account.account_id,
        transaction_ref="TXN-001",
        amount=Decimal("15000.00"),
        currency_code="USD",
        source_country_code="US",
        destination_country_code="GB",
        executed_at_utc=datetime.now(timezone.utc),
        created_at_utc=datetime.now(timezone.utc)
    )
    db_session.add(transaction1)
    
    alert1 = Alert(
        alert_id=uuid.UUID("55555555-0000-0000-0000-000000000001"),
        alert_ref="ALT-001",
        transaction_id=transaction1.transaction_id,
        customer_id=customer.customer_id,
        priority="Critical",
        risk_score=95,
        status="New",
        owner_user_id=None,
        triggered_at_utc=datetime.now(timezone.utc),
        created_at_utc=datetime.now(timezone.utc)
    )
    db_session.add(alert1)
    
    transaction2 = Transaction(
        transaction_id=uuid.UUID("44444444-0000-0000-0000-000000000002"),
        account_id=account.account_id,
        transaction_ref="TXN-002",
        amount=Decimal("8000.00"),
        currency_code="USD",
        source_country_code="US",
        destination_country_code="GB",
        executed_at_utc=datetime.now(timezone.utc),
        created_at_utc=datetime.now(timezone.utc)
    )
    db_session.add(transaction2)
    
    alert2 = Alert(
        alert_id=uuid.UUID("55555555-0000-0000-0000-000000000002"),
        alert_ref="ALT-002",
        transaction_id=transaction2.transaction_id,
        customer_id=customer.customer_id,
        priority="High",
        risk_score=85,
        status="New",
        owner_user_id=None,
        triggered_at_utc=datetime.now(timezone.utc),
        created_at_utc=datetime.now(timezone.utc)
    )
    db_session.add(alert2)
    db_session.commit()
    
    # Create case from alert1
    service = CaseService(db_session)
    case = service.create_case_from_alert(
        alert_id=alert1.alert_id,
        created_by_user_id=user.user_id,
        actor_role="INVESTIGATOR",
        correlation_id="test-corr-123"
    )
    
    # Add alert2 as secondary link
    case_repo = CaseRepository(db_session)
    link = case_repo.add_alert_link(
        case_id=case.case_id,
        alert_id=alert2.alert_id,
        linked_by_user_id=user.user_id
    )
    db_session.commit()
    
    # Verify link created with is_primary=False
    assert link.case_id == case.case_id
    assert link.alert_id == alert2.alert_id
    assert link.is_primary is False
    assert link.linked_by_user_id == user.user_id
    
    # Verify we now have 2 links for this case
    all_links = db_session.query(CaseAlertLink).filter_by(case_id=case.case_id).all()
    assert len(all_links) == 2
    assert sum(1 for l in all_links if l.is_primary) == 1
    assert sum(1 for l in all_links if not l.is_primary) == 1
