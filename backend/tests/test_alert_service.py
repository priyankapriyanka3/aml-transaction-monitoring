"""Tests for alert service."""
import uuid
import pytest
from app.services.alert_service import AlertService
from app.models.alert import Alert
from app.models.transaction import Transaction
from app.models.account import Account
from app.models.customer import Customer
from app.models.user import User
from app.core.security import hash_password
from decimal import Decimal
from datetime import datetime, timezone, timedelta


def test_get_alert_queue_returns_prioritized_list(db_session):
    """Test that get_alert_queue returns alerts ordered by risk score DESC."""
    # Create test data
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
        account_ref="TEST-ACC-001",
        account_type="Checking"
    )
    db_session.add(account)
    
    transaction1 = Transaction(
        transaction_id=uuid.uuid4(),
        account_id=account.account_id,
        transaction_ref="TXN-TEST-001",
        amount=Decimal("10000.00"),
        currency_code="USD",
        source_country_code="US",
        destination_country_code="GB",
        executed_at_utc=datetime.now(timezone.utc)
    )
    transaction2 = Transaction(
        transaction_id=uuid.uuid4(),
        account_id=account.account_id,
        transaction_ref="TXN-TEST-002",
        amount=Decimal("20000.00"),
        currency_code="USD",
        source_country_code="US",
        destination_country_code="CH",
        executed_at_utc=datetime.now(timezone.utc)
    )
    db_session.add(transaction1)
    db_session.add(transaction2)
    
    # Create alerts with different risk scores
    alert_low = Alert(
        alert_id=uuid.uuid4(),
        alert_ref="ALT-LOW",
        transaction_id=transaction1.transaction_id,
        customer_id=customer.customer_id,
        priority="Low",
        risk_score=50,
        status="New",
        triggered_at_utc=datetime.now(timezone.utc)
    )
    alert_high = Alert(
        alert_id=uuid.uuid4(),
        alert_ref="ALT-HIGH",
        transaction_id=transaction2.transaction_id,
        customer_id=customer.customer_id,
        priority="Critical",
        risk_score=95,
        status="New",
        triggered_at_utc=datetime.now(timezone.utc)
    )
    db_session.add(alert_low)
    db_session.add(alert_high)
    db_session.commit()
    
    # Get alert queue
    service = AlertService(db_session)
    items, total = service.get_alert_queue(
        priority=None,
        ownership=None,
        status=None,
        search=None,
        page=1,
        page_size=20,
        current_user_id=None
    )
    
    # Assert ordering: high risk score first
    assert total == 2
    assert len(items) == 2
    assert items[0]["risk_score"] == 95
    assert items[1]["risk_score"] == 50


def test_get_alert_queue_filters_by_priority(db_session):
    """Test that get_alert_queue filters by priority."""
    # Create test data
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
        account_ref="TEST-ACC-002",
        account_type="Checking"
    )
    db_session.add(account)
    
    transaction1 = Transaction(
        transaction_id=uuid.uuid4(),
        account_id=account.account_id,
        transaction_ref="TXN-TEST-003",
        amount=Decimal("10000.00"),
        currency_code="USD",
        source_country_code="US",
        destination_country_code="GB",
        executed_at_utc=datetime.now(timezone.utc)
    )
    transaction2 = Transaction(
        transaction_id=uuid.uuid4(),
        account_id=account.account_id,
        transaction_ref="TXN-TEST-004",
        amount=Decimal("20000.00"),
        currency_code="USD",
        source_country_code="US",
        destination_country_code="CH",
        executed_at_utc=datetime.now(timezone.utc)
    )
    db_session.add(transaction1)
    db_session.add(transaction2)
    
    alert_critical = Alert(
        alert_id=uuid.uuid4(),
        alert_ref="ALT-CRIT-001",
        transaction_id=transaction1.transaction_id,
        customer_id=customer.customer_id,
        priority="Critical",
        risk_score=95,
        status="New",
        triggered_at_utc=datetime.now(timezone.utc)
    )
    alert_high = Alert(
        alert_id=uuid.uuid4(),
        alert_ref="ALT-HIGH-001",
        transaction_id=transaction2.transaction_id,
        customer_id=customer.customer_id,
        priority="High",
        risk_score=85,
        status="New",
        triggered_at_utc=datetime.now(timezone.utc)
    )
    db_session.add(alert_critical)
    db_session.add(alert_high)
    db_session.commit()
    
    # Filter by Critical priority
    service = AlertService(db_session)
    items, total = service.get_alert_queue(
        priority="Critical",
        ownership=None,
        status=None,
        search=None,
        page=1,
        page_size=20,
        current_user_id=None
    )
    
    assert total == 1
    assert len(items) == 1
    assert items[0]["priority"] == "Critical"


def test_get_alert_queue_filters_by_ownership(db_session):
    """Test that get_alert_queue filters by ownership."""
    # Create test user
    user = User(
        user_id=uuid.uuid4(),
        display_name="Test User",
        email="testuser@example.com",
        hashed_password=hash_password("test123"),
        role="INVESTIGATOR",
        is_active=True
    )
    db_session.add(user)
    
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
        account_ref="TEST-ACC-003",
        account_type="Checking"
    )
    db_session.add(account)
    
    transaction1 = Transaction(
        transaction_id=uuid.uuid4(),
        account_id=account.account_id,
        transaction_ref="TXN-TEST-005",
        amount=Decimal("10000.00"),
        currency_code="USD",
        source_country_code="US",
        destination_country_code="GB",
        executed_at_utc=datetime.now(timezone.utc)
    )
    transaction2 = Transaction(
        transaction_id=uuid.uuid4(),
        account_id=account.account_id,
        transaction_ref="TXN-TEST-006",
        amount=Decimal("20000.00"),
        currency_code="USD",
        source_country_code="US",
        destination_country_code="CH",
        executed_at_utc=datetime.now(timezone.utc)
    )
    db_session.add(transaction1)
    db_session.add(transaction2)
    
    # Create assigned and unassigned alerts
    alert_assigned = Alert(
        alert_id=uuid.uuid4(),
        alert_ref="ALT-ASSIGNED",
        transaction_id=transaction1.transaction_id,
        customer_id=customer.customer_id,
        priority="High",
        risk_score=85,
        status="Under Review",
        owner_user_id=user.user_id,
        triggered_at_utc=datetime.now(timezone.utc)
    )
    alert_unassigned = Alert(
        alert_id=uuid.uuid4(),
        alert_ref="ALT-UNASSIGNED",
        transaction_id=transaction2.transaction_id,
        customer_id=customer.customer_id,
        priority="High",
        risk_score=80,
        status="New",
        owner_user_id=None,
        triggered_at_utc=datetime.now(timezone.utc)
    )
    db_session.add(alert_assigned)
    db_session.add(alert_unassigned)
    db_session.commit()
    
    # Filter by Unassigned
    service = AlertService(db_session)
    items, total = service.get_alert_queue(
        priority=None,
        ownership="Unassigned",
        status=None,
        search=None,
        page=1,
        page_size=20,
        current_user_id=user.user_id
    )
    
    assert total == 1
    assert len(items) == 1
    assert items[0]["owner_user_id"] is None
    
    # Filter by Assigned to Me
    items, total = service.get_alert_queue(
        priority=None,
        ownership="Assigned to Me",
        status=None,
        search=None,
        page=1,
        page_size=20,
        current_user_id=user.user_id
    )
    
    assert total == 1
    assert len(items) == 1
    assert items[0]["owner_user_id"] == user.user_id


def test_assign_alert_success(db_session):
    """Test successful alert assignment."""
    # Create test user
    user = User(
        user_id=uuid.uuid4(),
        display_name="Test User",
        email="testuser2@example.com",
        hashed_password=hash_password("test123"),
        role="INVESTIGATOR",
        is_active=True
    )
    db_session.add(user)
    
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
        account_ref="TEST-ACC-004",
        account_type="Checking"
    )
    db_session.add(account)
    
    transaction = Transaction(
        transaction_id=uuid.uuid4(),
        account_id=account.account_id,
        transaction_ref="TXN-TEST-007",
        amount=Decimal("10000.00"),
        currency_code="USD",
        source_country_code="US",
        destination_country_code="GB",
        executed_at_utc=datetime.now(timezone.utc)
    )
    db_session.add(transaction)
    
    alert = Alert(
        alert_id=uuid.uuid4(),
        alert_ref="ALT-ASSIGN-TEST",
        transaction_id=transaction.transaction_id,
        customer_id=customer.customer_id,
        priority="High",
        risk_score=85,
        status="New",
        owner_user_id=None,
        triggered_at_utc=datetime.now(timezone.utc)
    )
    db_session.add(alert)
    db_session.commit()
    
    # Assign alert
    service = AlertService(db_session)
    result = service.assign_alert(
        alert_id=alert.alert_id,
        user_id=user.user_id,
        user_role=user.role,
        correlation_id="test-correlation-id"
    )
    
    assert result["alert_id"] == alert.alert_id
    assert result["owner_user_id"] == user.user_id
    assert "assigned_at_utc" in result


def test_assign_alert_idempotent(db_session):
    """Test that assigning alert to same user is idempotent."""
    # Create test user
    user = User(
        user_id=uuid.uuid4(),
        display_name="Test User",
        email="testuser3@example.com",
        hashed_password=hash_password("test123"),
        role="INVESTIGATOR",
        is_active=True
    )
    db_session.add(user)
    
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
        account_ref="TEST-ACC-005",
        account_type="Checking"
    )
    db_session.add(account)
    
    transaction = Transaction(
        transaction_id=uuid.uuid4(),
        account_id=account.account_id,
        transaction_ref="TXN-TEST-008",
        amount=Decimal("10000.00"),
        currency_code="USD",
        source_country_code="US",
        destination_country_code="GB",
        executed_at_utc=datetime.now(timezone.utc)
    )
    db_session.add(transaction)
    
    alert = Alert(
        alert_id=uuid.uuid4(),
        alert_ref="ALT-IDEMPOTENT",
        transaction_id=transaction.transaction_id,
        customer_id=customer.customer_id,
        priority="High",
        risk_score=85,
        status="New",
        owner_user_id=user.user_id,  # Already assigned
        triggered_at_utc=datetime.now(timezone.utc)
    )
    db_session.add(alert)
    db_session.commit()
    
    # Assign alert again
    service = AlertService(db_session)
    result = service.assign_alert(
        alert_id=alert.alert_id,
        user_id=user.user_id,
        user_role=user.role,
        correlation_id="test-correlation-id"
    )
    
    # Should succeed and return existing assignment
    assert result["alert_id"] == alert.alert_id
    assert result["owner_user_id"] == user.user_id


def test_assign_alert_already_assigned_to_different_user(db_session):
    """Test that assigning alert already assigned to different user raises error."""
    # Create test users
    user1 = User(
        user_id=uuid.uuid4(),
        display_name="User 1",
        email="user1@example.com",
        hashed_password=hash_password("test123"),
        role="INVESTIGATOR",
        is_active=True
    )
    user2 = User(
        user_id=uuid.uuid4(),
        display_name="User 2",
        email="user2@example.com",
        hashed_password=hash_password("test123"),
        role="INVESTIGATOR",
        is_active=True
    )
    db_session.add(user1)
    db_session.add(user2)
    
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
        account_ref="TEST-ACC-006",
        account_type="Checking"
    )
    db_session.add(account)
    
    transaction = Transaction(
        transaction_id=uuid.uuid4(),
        account_id=account.account_id,
        transaction_ref="TXN-TEST-009",
        amount=Decimal("10000.00"),
        currency_code="USD",
        source_country_code="US",
        destination_country_code="GB",
        executed_at_utc=datetime.now(timezone.utc)
    )
    db_session.add(transaction)
    
    alert = Alert(
        alert_id=uuid.uuid4(),
        alert_ref="ALT-CONFLICT",
        transaction_id=transaction.transaction_id,
        customer_id=customer.customer_id,
        priority="High",
        risk_score=85,
        status="Under Review",
        owner_user_id=user1.user_id,  # Already assigned to user1
        triggered_at_utc=datetime.now(timezone.utc)
    )
    db_session.add(alert)
    db_session.commit()
    
    # Try to assign to user2
    service = AlertService(db_session)
    
    with pytest.raises(ValueError, match="already assigned"):
        service.assign_alert(
            alert_id=alert.alert_id,
            user_id=user2.user_id,
            user_role=user2.role,
            correlation_id="test-correlation-id"
        )


def test_assign_alert_not_found(db_session):
    """Test that assigning non-existent alert raises error."""
    user = User(
        user_id=uuid.uuid4(),
        display_name="Test User",
        email="testuser4@example.com",
        hashed_password=hash_password("test123"),
        role="INVESTIGATOR",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    
    service = AlertService(db_session)
    
    with pytest.raises(ValueError, match="Alert not found"):
        service.assign_alert(
            alert_id=uuid.uuid4(),  # Non-existent ID
            user_id=user.user_id,
            user_role=user.role,
            correlation_id="test-correlation-id"
        )
