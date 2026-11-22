"""
Evidence repository for customer, account, and transaction evidence retrieval.
Implements FR-011, FR-012, FR-013.
"""
from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from ..models.account import Account
from ..models.alert import Alert
from ..models.case_alert_link import CaseAlertLink
from ..models.customer import Customer
from ..models.detection_rule_snapshot import DetectionRuleSnapshot
from ..models.risk_profile import RiskProfile
from ..models.rule_evaluation_result import RuleEvaluationResult
from ..models.transaction import Transaction


class EvidenceRepository:
    """Repository for evidence package assembly"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_customer_context(self, customer_id: UUID | str) -> tuple[Customer | None, RiskProfile | None]:
        """
        Get customer profile and latest risk profile.
        
        Args:
            customer_id: Customer identifier
            
        Returns:
            Tuple of (Customer, RiskProfile) or (None, None) if customer not found
        """
        customer_uuid = UUID(customer_id) if isinstance(customer_id, str) else customer_id
        customer = self.db.scalar(
            select(Customer).where(Customer.customer_id == customer_uuid)
        )
        
        if not customer:
            return None, None
        
        # Get latest risk profile by effective_at
        risk_profile = self.db.scalar(
            select(RiskProfile)
            .where(RiskProfile.customer_id == customer_uuid)
            .order_by(desc(RiskProfile.effective_at))
            .limit(1)
        )
        
        return customer, risk_profile
    
    def get_accounts_by_customer(self, customer_id: UUID | str) -> list[Account]:
        """
        Get all accounts for a customer with masked account numbers.
        
        Args:
            customer_id: Customer identifier
            
        Returns:
            List of Account objects
        """
        customer_uuid = UUID(customer_id) if isinstance(customer_id, str) else customer_id
        return list(
            self.db.scalars(
                select(Account)
                .where(Account.customer_id == customer_uuid)
                .order_by(Account.created_at)
            ).all()
        )
    
    def get_transactions_by_case(self, case_id: UUID | str) -> list[tuple[Transaction, str]]:
        """
        Get all transactions linked to a case through alerts.
        
        Returns transactions from linked alerts with alert_id for context,
        sorted by booked_at DESC (newest first).
        
        Args:
            case_id: Case identifier
            
        Returns:
            List of (Transaction, alert_id) tuples sorted by booked_at DESC
        """
        case_uuid = UUID(case_id) if isinstance(case_id, str) else case_id
        # Get all alert IDs linked to this case
        stmt = (
            select(Alert.alert_id, Alert.transaction_id)
            .join(CaseAlertLink, CaseAlertLink.alert_id == Alert.alert_id)
            .where(CaseAlertLink.case_id == case_uuid)
        )
        
        alert_transactions = self.db.execute(stmt).all()
        
        if not alert_transactions:
            return []
        
        # Get transactions with their associated alert IDs
        transaction_ids = [at.transaction_id for at in alert_transactions]
        alert_map = {at.transaction_id: at.alert_id for at in alert_transactions}
        
        transactions = list(
            self.db.scalars(
                select(Transaction)
                .where(Transaction.transaction_id.in_(transaction_ids))
                .order_by(desc(Transaction.booked_at))
            ).all()
        )
        
        # Return tuples of (transaction, alert_id)
        return [(txn, alert_map[txn.transaction_id]) for txn in transactions]
    
    def get_rule_evaluations_by_case(self, case_id: UUID | str) -> list[RuleEvaluationResult]:
        """
        Get all rule evaluation results for alerts linked to a case.
        Includes immutable historical rule snapshot context (FR-013).
        
        Args:
            case_id: Case identifier
            
        Returns:
            List of RuleEvaluationResult objects with joined DetectionRuleSnapshot data
        """
        case_uuid = UUID(case_id) if isinstance(case_id, str) else case_id
        stmt = (
            select(RuleEvaluationResult)
            .join(CaseAlertLink, CaseAlertLink.alert_id == RuleEvaluationResult.alert_id)
            .where(CaseAlertLink.case_id == case_uuid)
            .order_by(RuleEvaluationResult.evaluated_at)
        )
        
        return list(self.db.scalars(stmt).all())
    
    def get_rule_snapshot(self, snapshot_id: str) -> DetectionRuleSnapshot | None:
        """
        Get immutable rule snapshot by ID.
        
        Args:
            snapshot_id: Detection rule snapshot identifier
            
        Returns:
            DetectionRuleSnapshot or None
        """
        return self.db.scalar(
            select(DetectionRuleSnapshot)
            .where(DetectionRuleSnapshot.detection_rule_snapshot_id == snapshot_id)
        )
