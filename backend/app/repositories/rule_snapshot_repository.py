"""Rule snapshot repository for data access."""
import uuid
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.rule_snapshot import RuleEvaluationSnapshot


class RuleSnapshotRepository:
    """Repository for rule evaluation snapshot data access."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def list_for_alert(self, alert_id: uuid.UUID) -> list[RuleEvaluationSnapshot]:
        """Get all rule snapshots for an alert.
        
        Returns snapshots ordered by outcome (MATCH first) then by rule_name.
        
        Args:
            alert_id: Alert to retrieve snapshots for
        
        Returns:
            List of RuleEvaluationSnapshot ordered by outcome, rule_name
        """
        stmt = (
            select(RuleEvaluationSnapshot)
            .where(RuleEvaluationSnapshot.alert_id == alert_id)
            .order_by(
                # MATCH outcomes first (M < P in ASCII), then by rule name
                RuleEvaluationSnapshot.outcome,
                RuleEvaluationSnapshot.rule_name
            )
        )
        result = self.db.execute(stmt)
        return list(result.scalars().all())
