import uuid
from datetime import datetime, timezone

from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..models.alert import Alert
from ..models.customer import Customer
from ..models.transaction import Transaction
from ..models.user import User


class AlertRepository:
    """Repository for alert data access"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def list_queue(
        self,
        status: str | None = None,
        priority: str | None = None,
        assignee_id: str | None = None,
        risk_score_min: int | None = None,
        risk_score_max: int | None = None,
        generation: str | None = None,
        search: str | None = None,
        sort_by: str = "priority",
        sort_direction: str = "desc",
        limit: int = 20,
        offset: int = 0
    ) -> tuple[list[Alert], int]:
        """
        List alerts with filtering, sorting, and pagination.
        Returns (alerts, total_count)
        """
        query = self.db.query(Alert)
        
        # Apply filters
        if status:
            query = query.filter(Alert.status == status)
        if priority:
            query = query.filter(Alert.priority == priority)
        if assignee_id:
            if assignee_id == "UNASSIGNED":
                query = query.filter(Alert.assigned_user_id.is_(None))
            else:
                # Convert string UUID to UUID object
                try:
                    assignee_uuid = uuid.UUID(assignee_id)
                    query = query.filter(Alert.assigned_user_id == assignee_uuid)
                except ValueError:
                    # Invalid UUID, no results
                    query = query.filter(False)
        if risk_score_min is not None:
            query = query.filter(Alert.risk_score >= risk_score_min)
        if risk_score_max is not None:
            query = query.filter(Alert.risk_score <= risk_score_max)
        if generation:
            query = query.filter(Alert.generation == generation)
        if search:
            query = query.filter(
                or_(
                    Alert.alert_id.ilike(f"%{search}%"),
                    Alert.customer_id.ilike(f"%{search}%"),
                    Alert.transaction_id.ilike(f"%{search}%")
                )
            )
        
        # Count total before pagination
        total_count = query.count()
        
        # Apply sorting
        sort_column = {
            "priority": Alert.priority,
            "risk_score": Alert.risk_score,
            "created_at": Alert.created_at,
            "status": Alert.status
        }.get(sort_by, Alert.priority)
        
        if sort_direction == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())
        
        # Apply pagination
        alerts = query.limit(limit).offset(offset).all()
        
        return alerts, total_count
    
    def get_by_id(self, alert_id: str | uuid.UUID) -> Alert | None:
        """Get alert by ID"""
        # Convert string to UUID if needed
        if isinstance(alert_id, str):
            alert_id = uuid.UUID(alert_id)
        return self.db.query(Alert).filter(Alert.alert_id == alert_id).first()
    
    def claim(self, alert: Alert, user_id: str | uuid.UUID, assigned_by: str | uuid.UUID) -> Alert:
        """Claim or reassign an alert"""
        if isinstance(user_id, str):
            user_id = uuid.UUID(user_id)
        alert.assigned_user_id = user_id
        alert.updated_at = datetime.now(timezone.utc)
        self.db.flush()
        self.db.refresh(alert)
        return alert
    
    def get_customer_by_id(self, customer_id: str | uuid.UUID) -> Customer | None:
        """Get customer by ID for enrichment"""
        if isinstance(customer_id, str):
            customer_id = uuid.UUID(customer_id)
        return self.db.query(Customer).filter(Customer.customer_id == customer_id).first()
    
    def get_transaction_by_id(self, transaction_id: str | uuid.UUID) -> Transaction | None:
        """Get transaction by ID for enrichment"""
        if isinstance(transaction_id, str):
            transaction_id = uuid.UUID(transaction_id)
        return self.db.query(Transaction).filter(Transaction.transaction_id == transaction_id).first()
    
    def get_user_by_id(self, user_id: str | uuid.UUID) -> User | None:
        """Get user by ID for enrichment"""
        if isinstance(user_id, str):
            user_id = uuid.UUID(user_id)
        return self.db.query(User).filter(User.user_id == user_id).first()
    
    def save_triage_disposition(self, alert: Alert, outcome: str, rationale: str, actor_id: str | uuid.UUID) -> Alert:
        """
        Save triage disposition and update alert status.
        
        Status transitions based on outcome:
        - INVESTIGATE: no status change (remains in current state)
        - CLOSE_NON_ACTIONABLE: status -> CLOSED_NON_ACTIONABLE
        - MERGE_EXISTING_CASE: status -> MERGED_INTO_EXISTING_CASE
        """
        if isinstance(actor_id, str):
            actor_id = uuid.UUID(actor_id)
        alert.triage_outcome = outcome
        alert.triage_rationale = rationale
        alert.triaged_by_user_id = actor_id
        alert.triaged_at = datetime.now(timezone.utc)
        
        # Update status based on outcome
        if outcome == "CLOSE_NON_ACTIONABLE":
            alert.status = "CLOSED_NON_ACTIONABLE"
        elif outcome == "MERGE_EXISTING_CASE":
            alert.status = "MERGED_INTO_EXISTING_CASE"
        # INVESTIGATE keeps current status
        
        alert.updated_at = datetime.now(timezone.utc)
        self.db.flush()
        self.db.refresh(alert)
        return alert
