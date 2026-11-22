from sqlalchemy.orm import Session

from ..models.audit_event import AuditEvent


class AuditEventRepository:
    """Repository for audit event data access"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, audit_event: AuditEvent) -> AuditEvent:
        """Create a new audit event"""
        self.db.add(audit_event)
        self.db.commit()
        self.db.refresh(audit_event)
        return audit_event
    
    def list_events(
        self,
        entity_type: str | None = None,
        entity_id: str | None = None,
        action_type: str | None = None,
        limit: int = 50,
        offset: int = 0
    ) -> tuple[list[AuditEvent], int]:
        """
        List audit events with optional filtering and pagination.
        
        Returns (events, total_count) tuple.
        Events are ordered by occurred_at DESC (newest first).
        """
        query = self.db.query(AuditEvent)
        
        # Apply filters
        if entity_type:
            query = query.filter(AuditEvent.entity_type == entity_type)
        if entity_id:
            query = query.filter(AuditEvent.entity_id == entity_id)
        if action_type:
            query = query.filter(AuditEvent.action_type == action_type)
        
        # Get total count before pagination
        total_count = query.count()
        
        # Apply pagination and ordering
        events = query.order_by(AuditEvent.occurred_at.desc()).limit(limit).offset(offset).all()
        
        return events, total_count
