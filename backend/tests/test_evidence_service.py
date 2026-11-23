"""Tests for evidence service."""
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from app.models.alert import Alert
from app.models.transaction import Transaction
from app.models.customer import Customer
from app.models.account import Account
from app.services.evidence_service import EvidenceService


def test_get_alert_evidence_success(db_session):
    """Test retrieving alert evidence with full nested context."""
    # Create customer
    customer = Customer(
        customer_id=uuid.UUID("11111111-0000-0000-0000-000000000001"),
        customer_name="Test Customer",
        pep_flag=False,
        country_code="US",
        created_at_utc=datetime.now(timezone.utc)
    )
    db_session.add(customer)
    
    # Create account
    account = Account(
        account_id=uuid.UUID("22222222-0000-0000-0000-000000000001"),
        customer_id=customer.customer_id,
        account_ref="ACC-001",
        account_type="CHECKING",
        created_at_utc=datetime.now(timezone.utc)
    )
    db_session.add(account)
    
    # Create transaction
    transaction = Transaction(
        transaction_id=uuid.UUID("33333333-0000-0000-0000-000000000001"),
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
        alert_id=uuid.UUID("44444444-0000-0000-0000-000000000001"),
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
    
    # Test evidence retrieval
    service = EvidenceService(db_session)
    evidence = service.get_alert_evidence(alert.alert_id)
    
    assert evidence is not None
    assert evidence.alert_id == alert.alert_id
    assert evidence.alert_ref == "ALT-001"
    assert evidence.priority == "Critical"
    assert evidence.risk_score == 95
    assert evidence.status == "New"
    
    # Check nested transaction
    assert evidence.transaction.transaction_id == transaction.transaction_id
    assert evidence.transaction.transaction_ref == "TXN-001"
    assert evidence.transaction.amount == Decimal("15000.00")
    assert evidence.transaction.currency_code == "USD"
    assert evidence.transaction.source_country_code == "US"
    assert evidence.transaction.destination_country_code == "GB"
    
    # Check nested customer
    assert evidence.customer.customer_id == customer.customer_id
    assert evidence.customer.customer_name == "Test Customer"
    assert evidence.customer.pep_flag is False
    assert evidence.customer.country_code == "US"
    
    # Check nested account
    assert evidence.account.account_id == account.account_id
    assert evidence.account.account_ref == "ACC-001"
    assert evidence.account.account_type == "CHECKING"


def test_get_alert_evidence_not_found(db_session):
    """Test retrieving evidence for non-existent alert."""
    service = EvidenceService(db_session)
    evidence = service.get_alert_evidence(uuid.uuid4())
    
    assert evidence is None
