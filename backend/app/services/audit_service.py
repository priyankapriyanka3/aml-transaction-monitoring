import json
import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from ..models.audit_event import AuditEvent
from ..repositories.audit_event_repository import AuditEventRepository


class AuditService:
    """Service for audit event creation"""
    
    def __init__(self, db: Session):
        self.db = db
        self.audit_repo = AuditEventRepository(db)
    
    def create_event(
        self,
        entity_type: str,
        entity_id: str | uuid.UUID,
        action_type: str,
        actor_user_id: str | uuid.UUID,
        actor_role: str,
        payload: dict,
        correlation_id: str | None = None
    ) -> AuditEvent:
        """Create an audit event"""
        if correlation_id is None:
            correlation_id = str(uuid.uuid4())
        
        # entity_id should be string, actor_user_id should be UUID object
        entity_id_str = str(entity_id) if isinstance(entity_id, uuid.UUID) else entity_id
        actor_user_id_obj = actor_user_id if isinstance(actor_user_id, uuid.UUID) else uuid.UUID(actor_user_id)
        
        # Convert UUIDs in payload to strings for JSON serialization
        def convert_uuids(obj):
            if isinstance(obj, uuid.UUID):
                return str(obj)
            elif isinstance(obj, dict):
                return {k: convert_uuids(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_uuids(item) for item in obj]
            return obj
        
        serializable_payload = convert_uuids(payload)
        
        audit_event = AuditEvent(
            audit_event_id=uuid.uuid4(),
            entity_type=entity_type,
            entity_id=entity_id_str,
            action_type=action_type,
            actor_user_id=actor_user_id_obj,
            actor_role=actor_role,
            correlation_id=correlation_id,
            payload_json=json.dumps(serializable_payload),
            occurred_at=datetime.now(timezone.utc)
        )
        
        return self.audit_repo.create(audit_event)
