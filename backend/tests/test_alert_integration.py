"""Integration tests for alert endpoints."""
import uuid
from app.models.alert import Alert
from app.models.transaction import Transaction
from app.models.account import Account
from app.models.customer import Customer
from decimal import Decimal
from datetime import datetime, timezone


def test_get_alert_queue_requires_auth(client):
    """Test that alert queue endpoint requires authentication."""
    response = client.get("/api/v1/alerts")
    assert response.status_code == 401


def test_get_alert_queue_success(auth_client, db_session):
    """Test successful alert queue retrieval."""
    # Create test data
    customer = Customer(
        customer_id=uuid.uuid4(),
        customer_name="John Doe",
        pep_flag=False,
        country_code="US"
    )
    db_session.add(customer)
    
    account = Account(
        account_id=uuid.uuid4(),
        customer_id=customer.customer_id,
        account_ref="ACC-INT-001",
        account_type="Checking"
    )
    db_session.add(account)
    
    transaction = Transaction(
        transaction_id=uuid.uuid4(),
        account_id=account.account_id,
        transaction_ref="TXN-INT-001",
        amount=Decimal("50000.00"),
        currency_code="USD",
        source_country_code="US",
        destination_country_code="CH",
        executed_at_utc=datetime.now(timezone.utc)
    )
    db_session.add(transaction)
    
    alert = Alert(
        alert_id=uuid.uuid4(),
        alert_ref="ALT-INT-001",
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
    
    # Get alert queue
    response = auth_client.get("/api/v1/alerts")
    
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert data["total"] >= 1


def test_get_alert_queue_with_priority_filter(auth_client, db_session):
    """Test alert queue with priority filter."""
    customer = Customer(
        customer_id=uuid.uuid4(),
        customer_name="Jane Smith",
        pep_flag=False,
        country_code="GB"
    )
    db_session.add(customer)
    
    account = Account(
        account_id=uuid.uuid4(),
        customer_id=customer.customer_id,
        account_ref="ACC-INT-002",
        account_type="Business"
    )
    db_session.add(account)
    
    transaction1 = Transaction(
        transaction_id=uuid.uuid4(),
        account_id=account.account_id,
        transaction_ref="TXN-INT-002",
        amount=Decimal("100000.00"),
        currency_code="GBP",
        source_country_code="GB",
        destination_country_code="VG",
        executed_at_utc=datetime.now(timezone.utc)
    )
    transaction2 = Transaction(
        transaction_id=uuid.uuid4(),
        account_id=account.account_id,
        transaction_ref="TXN-INT-003",
        amount=Decimal("5000.00"),
        currency_code="GBP",
        source_country_code="GB",
        destination_country_code="FR",
        executed_at_utc=datetime.now(timezone.utc)
    )
    db_session.add(transaction1)
    db_session.add(transaction2)
    
    alert_critical = Alert(
        alert_id=uuid.uuid4(),
        alert_ref="ALT-INT-CRIT",
        transaction_id=transaction1.transaction_id,
        customer_id=customer.customer_id,
        priority="Critical",
        risk_score=95,
        status="New",
        owner_user_id=None,
        triggered_at_utc=datetime.now(timezone.utc)
    )
    alert_medium = Alert(
        alert_id=uuid.uuid4(),
        alert_ref="ALT-INT-MED",
        transaction_id=transaction2.transaction_id,
        customer_id=customer.customer_id,
        priority="Medium",
        risk_score=60,
        status="New",
        owner_user_id=None,
        triggered_at_utc=datetime.now(timezone.utc)
    )
    db_session.add(alert_critical)
    db_session.add(alert_medium)
    db_session.commit()
    
    # Filter by Critical priority
    response = auth_client.get("/api/v1/alerts?priority=Critical")
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    # All returned items should be Critical
    for item in data["items"]:
        if item["alert_ref"] in ["ALT-INT-CRIT", "ALT-INT-MED"]:
            assert item["priority"] == "Critical"


def test_get_alert_queue_with_search(auth_client, db_session):
    """Test alert queue with search parameter."""
    customer = Customer(
        customer_id=uuid.uuid4(),
        customer_name="Searchable Customer",
        pep_flag=False,
        country_code="US"
    )
    db_session.add(customer)
    
    account = Account(
        account_id=uuid.uuid4(),
        customer_id=customer.customer_id,
        account_ref="ACC-SEARCH-001",
        account_type="Checking"
    )
    db_session.add(account)
    
    transaction = Transaction(
        transaction_id=uuid.uuid4(),
        account_id=account.account_id,
        transaction_ref="TXN-SEARCH-001",
        amount=Decimal("25000.00"),
        currency_code="USD",
        source_country_code="US",
        destination_country_code="MX",
        executed_at_utc=datetime.now(timezone.utc)
    )
    db_session.add(transaction)
    
    alert = Alert(
        alert_id=uuid.uuid4(),
        alert_ref="ALT-UNIQUE-SEARCH-123",
        transaction_id=transaction.transaction_id,
        customer_id=customer.customer_id,
        priority="High",
        risk_score=75,
        status="New",
        owner_user_id=None,
        triggered_at_utc=datetime.now(timezone.utc)
    )
    db_session.add(alert)
    db_session.commit()
    
    # Search by alert ref
    response = auth_client.get("/api/v1/alerts?search=UNIQUE-SEARCH")
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    found = any(item["alert_ref"] == "ALT-UNIQUE-SEARCH-123" for item in data["items"])
    assert found


def test_get_alert_queue_pagination(auth_client, db_session):
    """Test alert queue pagination."""
    customer = Customer(
        customer_id=uuid.uuid4(),
        customer_name="Pagination Test",
        pep_flag=False,
        country_code="US"
    )
    db_session.add(customer)
    
    account = Account(
        account_id=uuid.uuid4(),
        customer_id=customer.customer_id,
        account_ref="ACC-PAGE-001",
        account_type="Checking"
    )
    db_session.add(account)
    
    # Create multiple alerts
    for i in range(5):
        transaction = Transaction(
            transaction_id=uuid.uuid4(),
            account_id=account.account_id,
            transaction_ref=f"TXN-PAGE-{i:03d}",
            amount=Decimal("10000.00"),
            currency_code="USD",
            source_country_code="US",
            destination_country_code="CA",
            executed_at_utc=datetime.now(timezone.utc)
        )
        db_session.add(transaction)
        
        alert = Alert(
            alert_id=uuid.uuid4(),
            alert_ref=f"ALT-PAGE-{i:03d}",
            transaction_id=transaction.transaction_id,
            customer_id=customer.customer_id,
            priority="Medium",
            risk_score=60 + i,
            status="New",
            owner_user_id=None,
            triggered_at_utc=datetime.now(timezone.utc)
        )
        db_session.add(alert)
    
    db_session.commit()
    
    # Request page 1 with page_size=2
    response = auth_client.get("/api/v1/alerts?page=1&page_size=2")
    
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["page_size"] == 2
    assert data["total"] >= 5


def test_assign_alert_requires_auth(client):
    """Test that alert assignment requires authentication."""
    alert_id = uuid.uuid4()
    response = client.post(
        f"/api/v1/alerts/{alert_id}/assign",
        headers={"X-Correlation-ID": "test-correlation"}
    )
    assert response.status_code == 401


def test_assign_alert_success(auth_client, db_session):
    """Test successful alert assignment."""
    customer = Customer(
        customer_id=uuid.uuid4(),
        customer_name="Assignment Test",
        pep_flag=False,
        country_code="US"
    )
    db_session.add(customer)
    
    account = Account(
        account_id=uuid.uuid4(),
        customer_id=customer.customer_id,
        account_ref="ACC-ASSIGN-001",
        account_type="Checking"
    )
    db_session.add(account)
    
    transaction = Transaction(
        transaction_id=uuid.uuid4(),
        account_id=account.account_id,
        transaction_ref="TXN-ASSIGN-001",
        amount=Decimal("75000.00"),
        currency_code="USD",
        source_country_code="US",
        destination_country_code="CH",
        executed_at_utc=datetime.now(timezone.utc)
    )
    db_session.add(transaction)
    
    alert = Alert(
        alert_id=uuid.uuid4(),
        alert_ref="ALT-ASSIGN-INT",
        transaction_id=transaction.transaction_id,
        customer_id=customer.customer_id,
        priority="High",
        risk_score=88,
        status="New",
        owner_user_id=None,
        triggered_at_utc=datetime.now(timezone.utc)
    )
    db_session.add(alert)
    db_session.commit()
    
    # Assign alert
    response = auth_client.post(
        f"/api/v1/alerts/{alert.alert_id}/assign",
        headers={"X-Correlation-ID": "test-correlation-123"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["alert_id"] == str(alert.alert_id)
    assert "owner_user_id" in data
    assert "assigned_at_utc" in data


def test_assign_alert_not_found(auth_client):
    """Test alert assignment with non-existent alert."""
    non_existent_id = uuid.uuid4()
    response = auth_client.post(
        f"/api/v1/alerts/{non_existent_id}/assign",
        headers={"X-Correlation-ID": "test-correlation"}
    )
    
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


def test_assign_alert_already_assigned_conflict(auth_client, db_session):
    """Test assigning alert already assigned to different user returns 409."""
    from app.models.user import User
    from app.core.security import hash_password
    
    # Create another user
    other_user = User(
        user_id=uuid.uuid4(),
        display_name="Other User",
        email="other@example.com",
        hashed_password=hash_password("other123"),
        role="INVESTIGATOR",
        is_active=True
    )
    db_session.add(other_user)
    
    customer = Customer(
        customer_id=uuid.uuid4(),
        customer_name="Conflict Test",
        pep_flag=False,
        country_code="US"
    )
    db_session.add(customer)
    
    account = Account(
        account_id=uuid.uuid4(),
        customer_id=customer.customer_id,
        account_ref="ACC-CONFLICT-001",
        account_type="Checking"
    )
    db_session.add(account)
    
    transaction = Transaction(
        transaction_id=uuid.uuid4(),
        account_id=account.account_id,
        transaction_ref="TXN-CONFLICT-001",
        amount=Decimal("65000.00"),
        currency_code="USD",
        source_country_code="US",
        destination_country_code="PA",
        executed_at_utc=datetime.now(timezone.utc)
    )
    db_session.add(transaction)
    
    # Create alert already assigned to other_user
    alert = Alert(
        alert_id=uuid.uuid4(),
        alert_ref="ALT-CONFLICT-INT",
        transaction_id=transaction.transaction_id,
        customer_id=customer.customer_id,
        priority="Critical",
        risk_score=92,
        status="Under Review",
        owner_user_id=other_user.user_id,
        triggered_at_utc=datetime.now(timezone.utc)
    )
    db_session.add(alert)
    db_session.commit()
    
    # Try to assign to current authenticated user
    response = auth_client.post(
        f"/api/v1/alerts/{alert.alert_id}/assign",
        headers={"X-Correlation-ID": "test-correlation"}
    )
    
    assert response.status_code == 409
    data = response.json()
    assert "detail" in data
    assert "already assigned" in data["detail"].lower()
