"""Alert service for business logic."""
import uuid
import json
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.repositories.alert_repository import AlertRepository
from app.models.audit_event import AuditEvent
from app.models.user import User


class AlertService:
    """Service for alert business logic including assignment and audit."""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = AlertRepository(db)
    
    def get_alert_queue(
        self,
        priority: str | None,
        ownership: str | None,
        status: str | None,
        search: str | None,
        page: int,
        page_size: int,
        current_user_id: uuid.UUID | None,
    ) -> tuple[list, int]:
        """
        Get prioritized alert queue with filters.
        
        Returns:
            Tuple of (alert items, total count)
        """
        return self.repository.list_prioritized(
            priority=priority,
            ownership=ownership,
            status=status,
            search=search,
            page=page,
            page_size=page_size,
            current_user_id=current_user_id,
        )
    
    def assign_alert(
        self,
        alert_id: uuid.UUID,
        user_id: uuid.UUID,
        user_role: str,
        correlation_id: str,
    ) -> dict:
        """
        Assign alert to user and create audit event.
        
        Args:
            alert_id: Alert to assign
            user_id: User to assign to
            user_role: Role of the user
            correlation_id: Correlation ID for audit trail
        
        Returns:
            Assignment response dict
        
        Raises:
            ValueError: If alert not found or already assigned to different user
        """
        # Get alert
        alert = self.repository.get_by_id(alert_id)
        if not alert:
            raise ValueError("Alert not found")
        
        # Check if already assigned to different user
        if alert.owner_user_id and alert.owner_user_id != user_id:
            raise ValueError(f"Alert already assigned to user {alert.owner_user_id}")
        
        # Idempotent: if already assigned to same user, return success
        if alert.owner_user_id == user_id:
            return {
                "alert_id": alert.alert_id,
                "owner_user_id": alert.owner_user_id,
                "assigned_at_utc": alert.created_at_utc,  # Use existing timestamp
            }
        
        # Assign alert
        assigned_at_utc = datetime.now(timezone.utc)
        alert.owner_user_id = user_id
        self.repository.update(alert)
        
        # Create audit event
        audit_event = AuditEvent(
            entity_type="ALERT",
            entity_id=alert_id,
            action_type="ALERT_ASSIGNED",
            actor_user_id=user_id,
            actor_role=user_role,
            correlation_id=correlation_id,
            details_json=json.dumps({
                "alert_id": str(alert_id),
                "alert_ref": alert.alert_ref,
                "owner_user_id": str(user_id),
                "assigned_at_utc": assigned_at_utc.isoformat(),
            }),
            occurred_at_utc=assigned_at_utc,
        )
        self.db.add(audit_event)
        self.db.commit()
        
        return {
            "alert_id": alert.alert_id,
            "owner_user_id": alert.owner_user_id,
            "assigned_at_utc": assigned_at_utc,
        }
