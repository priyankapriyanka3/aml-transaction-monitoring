"""Tests for rule snapshot repository."""
import uuid
from datetime import datetime, timezone
import pytest
from sqlalchemy.orm import Session
from app.models.alert import Alert
from app.models.transaction import Transaction
from app.models.customer import Customer
from app.models.account import Account
from app.models.rule_snapshot import RuleEvaluationSnapshot
from app.repositories.rule_snapshot_repository import RuleSnapshotRepository


def test_list_for_alert_returns_snapshots_ordered_by_outcome(db_session: Session):
    """Test that rule snapshots are returned ordered by outcome (MATCH first) then by rule_name."""
    # Create customer, account, transaction, alert
    customer = Customer(
        customer_name="Test Customer",
        pep_flag=False,
        country_code="US"
    )
    db_session.add(customer)
    db_session.flush()  # Flush to get customer_id
    
    account = Account(
        customer_id=customer.customer_id,
        account_ref="ACC-001",
        account_type="Checking"
    )
    db_session.add(account)
    db_session.flush()  # Flush to get account_id
    
    transaction = Transaction(
        account_id=account.account_id,
        transaction_ref="TXN-001",
        amount=50000,
        currency_code="USD",
        source_country_code="US",
        destination_country_code="PA",
        executed_at_utc=datetime.now(timezone.utc)
    )
    db_session.add(transaction)
    db_session.flush()  # Flush to get transaction_id
    
    alert = Alert(
        alert_ref="ALT-001",
        transaction_id=transaction.transaction_id,
        customer_id=customer.customer_id,
        priority="High",
        risk_score=85,
        status="New",
        triggered_at_utc=datetime.now(timezone.utc)
    )
    db_session.add(alert)
    db_session.flush()  # Flush to get alert_id
    
    # Create rule snapshots with different outcomes
    now = datetime.now(timezone.utc)
    
    snapshot1 = RuleEvaluationSnapshot(
        alert_id=alert.alert_id,
        rule_code="RULE-001",
        rule_name="B - Rule That Passes",
        rule_version="v1.0",
        outcome="PASS",
        condition_text="Some condition",
        evaluated_from_utc=now,
        evaluated_to_utc=now,
        immutable_hash="hash1"
    )
    
    snapshot2 = RuleEvaluationSnapshot(
        alert_id=alert.alert_id,
        rule_code="RULE-002",
        rule_name="A - Rule That Matches",
        rule_version="v1.0",
        outcome="MATCH",
        condition_text="Some condition",
        evaluated_from_utc=now,
        evaluated_to_utc=now,
        immutable_hash="hash2"
    )
    
    snapshot3 = RuleEvaluationSnapshot(
        alert_id=alert.alert_id,
        rule_code="RULE-003",
        rule_name="C - Another Match",
        rule_version="v1.0",
        outcome="MATCH",
        condition_text="Some condition",
        evaluated_from_utc=now,
        evaluated_to_utc=now,
        immutable_hash="hash3"
    )
    
    db_session.add_all([snapshot1, snapshot2, snapshot3])
    db_session.commit()
    
    # Retrieve snapshots
    repo = RuleSnapshotRepository(db_session)
    snapshots = repo.list_for_alert(alert.alert_id)
    
    # Verify ordering: MATCH outcomes first (in alphabetical order by rule_name), then PASS
    assert len(snapshots) == 3
    assert snapshots[0].outcome == "MATCH"
    assert snapshots[0].rule_name == "A - Rule That Matches"
    assert snapshots[1].outcome == "MATCH"
    assert snapshots[1].rule_name == "C - Another Match"
    assert snapshots[2].outcome == "PASS"
    assert snapshots[2].rule_name == "B - Rule That Passes"


def test_list_for_alert_returns_empty_for_nonexistent_alert(db_session: Session):
    """Test that an empty list is returned for an alert with no snapshots."""
    repo = RuleSnapshotRepository(db_session)
    nonexistent_alert_id = uuid.uuid4()
    
    snapshots = repo.list_for_alert(nonexistent_alert_id)
    
    assert snapshots == []
