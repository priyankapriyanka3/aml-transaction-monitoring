"""Evidence service for assembling alert evidence read models."""
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.alert import Alert
from app.models.transaction import Transaction
from app.models.customer import Customer
from app.models.account import Account
from app.repositories.rule_snapshot_repository import RuleSnapshotRepository
from app.schemas.evidence_schemas import (
    AlertEvidenceResponse,
    TransactionFactsView,
    CustomerContextView,
    AccountContextView,
    RuleSnapshotItem
)


class EvidenceService:
    """Service for building alert evidence read models."""
    
    def __init__(self, db: Session):
        self.db = db
        self.rule_snapshot_repo = RuleSnapshotRepository(db)
    
    def get_alert_evidence(self, alert_id: uuid.UUID) -> AlertEvidenceResponse | None:
        """Build full alert evidence read model with nested context.
        
        Args:
            alert_id: Alert to retrieve evidence for
        
        Returns:
            AlertEvidenceResponse with transaction, customer, account context,
            and historical rule snapshots, or None if alert not found
        """
        # Query alert with joined entities
        stmt = (
            select(Alert, Transaction, Customer, Account)
            .join(Transaction, Alert.transaction_id == Transaction.transaction_id)
            .join(Account, Transaction.account_id == Account.account_id)
            .join(Customer, Alert.customer_id == Customer.customer_id)
            .where(Alert.alert_id == alert_id)
        )
        
        result = self.db.execute(stmt).first()
        
        if not result:
            return None
        
        alert, transaction, customer, account = result
        
        # Get rule snapshots for this alert
        rule_snapshots = self.rule_snapshot_repo.list_for_alert(alert_id)
        
        # Build nested response
        return AlertEvidenceResponse(
            alert_id=alert.alert_id,
            alert_ref=alert.alert_ref,
            priority=alert.priority,
            risk_score=alert.risk_score,
            status=alert.status,
            triggered_at_utc=alert.triggered_at_utc,
            transaction=TransactionFactsView(
                transaction_id=transaction.transaction_id,
                transaction_ref=transaction.transaction_ref,
                amount=transaction.amount,
                currency_code=transaction.currency_code,
                source_country_code=transaction.source_country_code,
                destination_country_code=transaction.destination_country_code,
                executed_at_utc=transaction.executed_at_utc
            ),
            customer=CustomerContextView(
                customer_id=customer.customer_id,
                customer_name=customer.customer_name,
                pep_flag=customer.pep_flag,
                country_code=customer.country_code
            ),
            account=AccountContextView(
                account_id=account.account_id,
                account_ref=account.account_ref,
                account_type=account.account_type
            ),
            rule_snapshots=[
                RuleSnapshotItem(
                    snapshot_id=snap.snapshot_id,
                    rule_code=snap.rule_code,
                    rule_name=snap.rule_name,
                    rule_version=snap.rule_version,
                    outcome=snap.outcome,
                    condition_text=snap.condition_text,
                    evaluated_from_utc=snap.evaluated_from_utc,
                    evaluated_to_utc=snap.evaluated_to_utc
                )
                for snap in rule_snapshots
            ]
        )
