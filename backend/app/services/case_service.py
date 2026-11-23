"""Case service for case creation and management."""
import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.repositories.case_repository import CaseRepository
from app.repositories.alert_repository import AlertRepository
from app.models.audit_event import AuditEvent
from app.models.case import AmlCase
from app.models.case_note import CaseNote


class CaseService:
    """Service for case business logic."""
    
    def __init__(self, db: Session):
        self.db = db
        self.case_repo = CaseRepository(db)
        self.alert_repo = AlertRepository(db)
    
    def create_case_from_alert(
        self,
        alert_id: uuid.UUID,
        created_by_user_id: uuid.UUID,
        actor_role: str,
        correlation_id: str
    ) -> AmlCase:
        """Create a new case from an alert.
        
        Args:
            alert_id: Primary alert to create case from
            created_by_user_id: User creating the case
            actor_role: Role of the creating user
            correlation_id: Request correlation ID for audit trail
        
        Returns:
            Created AmlCase
        
        Raises:
            ValueError: If alert not found
        """
        # Verify alert exists
        alert = self.alert_repo.get_by_id(alert_id)
        if not alert:
            raise ValueError(f"Alert {alert_id} not found")
        
        # Generate next case reference
        case_ref = self.case_repo.get_next_case_ref()
        
        # Create case
        case = self.case_repo.create_case(
            case_ref=case_ref,
            primary_alert_id=alert_id,
            created_by_user_id=created_by_user_id,
            status="OPEN"
        )
        
        # Create primary alert link
        self.case_repo.create_case_alert_link(
            case_id=case.case_id,
            alert_id=alert_id,
            linked_by_user_id=created_by_user_id,
            is_primary=True
        )
        
        # Emit case creation audit event
        self._emit_audit_event(
            entity_type="CASE",
            entity_id=case.case_id,
            action_type="CASE_CREATED",
            actor_user_id=created_by_user_id,
            actor_role=actor_role,
            correlation_id=correlation_id,
            details={
                "case_ref": case_ref,
                "primary_alert_id": str(alert_id),
                "status": "OPEN"
            }
        )
        
        # Emit alert linkage audit event
        self._emit_audit_event(
            entity_type="CASE",
            entity_id=case.case_id,
            action_type="ALERT_LINKED",
            actor_user_id=created_by_user_id,
            actor_role=actor_role,
            correlation_id=correlation_id,
            details={
                "case_id": str(case.case_id),
                "alert_id": str(alert_id),
                "is_primary": True
            }
        )
        
        self.db.commit()
        return case
    
    def add_note(
        self,
        case_id: uuid.UUID,
        note_category: str,
        note_text: str,
        author_user_id: uuid.UUID,
        actor_role: str,
        correlation_id: str
    ) -> CaseNote:
        """Add an investigation note to a case.
        
        Args:
            case_id: Case to add note to
            note_category: Note category (investigation, recommendation, etc.)
            note_text: Note content
            author_user_id: User authoring the note
            actor_role: Role of the authoring user
            correlation_id: Request correlation ID for audit trail
        
        Returns:
            Created CaseNote
        
        Raises:
            ValueError: If case not found
        """
        # Verify case exists
        case = self.case_repo.get_by_id(case_id)
        if not case:
            raise ValueError(f"Case {case_id} not found")
        
        # Create note
        note = self.case_repo.add_note(
            case_id=case_id,
            note_category=note_category,
            note_text=note_text,
            author_user_id=author_user_id
        )
        
        # Emit audit event
        self._emit_audit_event(
            entity_type="CASE",
            entity_id=case_id,
            action_type="NOTE_ADDED",
            actor_user_id=author_user_id,
            actor_role=actor_role,
            correlation_id=correlation_id,
            details={
                "note_id": str(note.note_id),
                "note_category": note_category,
                "note_text_length": len(note_text)
            }
        )
        
        self.db.commit()
        return note
    
    def _emit_audit_event(
        self,
        entity_type: str,
        entity_id: uuid.UUID,
        action_type: str,
        actor_user_id: uuid.UUID,
        actor_role: str,
        correlation_id: str,
        details: dict
    ) -> None:
        """Emit an audit event for case operations."""
        import json
        
        event = AuditEvent(
            entity_type=entity_type,
            entity_id=entity_id,
            action_type=action_type,
            actor_user_id=actor_user_id,
            actor_role=actor_role,
            correlation_id=correlation_id,
            details_json=json.dumps(details),
            occurred_at_utc=datetime.now(timezone.utc)
        )
        self.db.add(event)
        self.db.flush()
