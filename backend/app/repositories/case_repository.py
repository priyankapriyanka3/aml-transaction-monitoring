"""Case repository for data access."""
import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.case import AmlCase
from app.models.case_alert_link import CaseAlertLink
from app.models.case_note import CaseNote
from app.models.evidence_gap import EvidenceGap


class CaseRepository:
    """Repository for case data access."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_case(
        self,
        case_ref: str,
        primary_alert_id: uuid.UUID,
        created_by_user_id: uuid.UUID,
        status: str = "OPEN"
    ) -> AmlCase:
        """Create a new case.
        
        Args:
            case_ref: Unique case reference (e.g., CS-204)
            primary_alert_id: Alert that triggered the case
            created_by_user_id: User creating the case
            status: Initial case status
        
        Returns:
            Created AmlCase
        """
        case = AmlCase(
            case_ref=case_ref,
            primary_alert_id=primary_alert_id,
            created_by_user_id=created_by_user_id,
            status=status
        )
        self.db.add(case)
        self.db.flush()  # Flush to get the case_id
        return case
    
    def create_case_alert_link(
        self,
        case_id: uuid.UUID,
        alert_id: uuid.UUID,
        linked_by_user_id: uuid.UUID,
        is_primary: bool = False
    ) -> CaseAlertLink:
        """Link an alert to a case.
        
        Args:
            case_id: Case to link to
            alert_id: Alert to link
            linked_by_user_id: User creating the link
            is_primary: Whether this is the primary opening alert
        
        Returns:
            Created CaseAlertLink
        """
        link = CaseAlertLink(
            case_id=case_id,
            alert_id=alert_id,
            linked_by_user_id=linked_by_user_id,
            is_primary=is_primary
        )
        self.db.add(link)
        self.db.flush()
        return link
    
    def add_alert_link(
        self,
        case_id: uuid.UUID,
        alert_id: uuid.UUID,
        linked_by_user_id: uuid.UUID
    ) -> CaseAlertLink:
        """Add a secondary alert link to an existing case.
        
        This is a convenience method for linking additional alerts
        after case creation. Always sets is_primary=False.
        
        Args:
            case_id: Case to link to
            alert_id: Alert to link
            linked_by_user_id: User creating the link
        
        Returns:
            Created CaseAlertLink with is_primary=False
        """
        return self.create_case_alert_link(
            case_id=case_id,
            alert_id=alert_id,
            linked_by_user_id=linked_by_user_id,
            is_primary=False
        )
    
    def add_note(
        self,
        case_id: uuid.UUID,
        note_category: str,
        note_text: str,
        author_user_id: uuid.UUID
    ) -> CaseNote:
        """Add an investigation note to a case.
        
        Args:
            case_id: Case to add note to
            note_category: Note category (investigation, recommendation, etc.)
            note_text: Note content
            author_user_id: User authoring the note
        
        Returns:
            Created CaseNote
        """
        note = CaseNote(
            case_id=case_id,
            note_category=note_category,
            note_text=note_text,
            author_user_id=author_user_id
        )
        self.db.add(note)
        self.db.flush()
        return note
    
    def get_by_id(self, case_id: uuid.UUID) -> AmlCase | None:
        """Get case by ID."""
        return self.db.get(AmlCase, case_id)
    
    def update_case_status(
        self,
        case_id: uuid.UUID,
        status: str,
        blocker_state: str | None = None
    ) -> AmlCase:
        """Update case status and optionally blocker state.
        
        Args:
            case_id: Case to update
            status: New status
            blocker_state: New blocker state (optional)
        
        Returns:
            Updated AmlCase
        
        Raises:
            ValueError: If case not found
        """
        case = self.get_by_id(case_id)
        if not case:
            raise ValueError(f"Case {case_id} not found")
        
        case.status = status
        if blocker_state is not None:
            case.current_blocker_state = blocker_state
        
        from datetime import datetime, timezone
        case.updated_at_utc = datetime.now(timezone.utc)
        
        self.db.flush()
        return case
    
    def get_workspace_data(self, case_id: uuid.UUID) -> dict | None:
        """Get complete case workspace with linked alerts, notes, gaps, and timeline.
        
        Args:
            case_id: Case ID to retrieve workspace for
        
        Returns:
            Dictionary with case metadata and aggregated arrays, or None if not found
        """
        from app.models.alert import Alert
        from app.models.audit_event import AuditEvent
        
        # Get case
        case = self.get_by_id(case_id)
        if not case:
            return None
        
        # Get linked alerts with alert details
        linked_alerts_stmt = (
            select(CaseAlertLink, Alert)
            .join(Alert, CaseAlertLink.alert_id == Alert.alert_id)
            .where(CaseAlertLink.case_id == case_id)
            .order_by(CaseAlertLink.linked_at_utc.asc())
        )
        linked_alerts_result = self.db.execute(linked_alerts_stmt).all()
        
        linked_alerts = [
            {
                "alert_id": alert.alert_id,
                "alert_ref": alert.alert_ref,
                "is_primary": link.is_primary,
                "linked_at_utc": link.linked_at_utc
            }
            for link, alert in linked_alerts_result
        ]
        
        # Get notes ordered by authored_at_utc DESC
        notes_stmt = (
            select(CaseNote)
            .where(CaseNote.case_id == case_id)
            .order_by(CaseNote.authored_at_utc.desc())
        )
        notes_result = self.db.scalars(notes_stmt).all()
        
        notes = [
            {
                "note_id": note.note_id,
                "note_category": note.note_category,
                "note_text": note.note_text,
                "author_user_id": note.author_user_id,
                "authored_at_utc": note.authored_at_utc
            }
            for note in notes_result
        ]
        
        # Get timeline entries (audit events for this case)
        timeline_stmt = (
            select(AuditEvent)
            .where(AuditEvent.entity_type == "CASE")
            .where(AuditEvent.entity_id == case_id)
            .order_by(AuditEvent.occurred_at_utc.desc())
        )
        timeline_result = self.db.scalars(timeline_stmt).all()
        
        timeline_entries = [
            {
                "event_id": event.audit_event_id,
                "action_type": event.action_type,
                "actor_user_id": event.actor_user_id,
                "occurred_at_utc": event.occurred_at_utc,
                "details_json": event.details_json
            }
            for event in timeline_result
        ]
        
        # Build workspace response with {items, total} structure
        return {
            "case_id": case.case_id,
            "case_ref": case.case_ref,
            "status": case.status,
            "current_blocker_state": case.current_blocker_state,
            "created_by_user_id": case.created_by_user_id,
            "assigned_officer_user_id": case.assigned_officer_user_id,
            "created_at_utc": case.created_at_utc,
            "updated_at_utc": case.updated_at_utc,
            "linked_alerts": {
                "items": linked_alerts,
                "total": len(linked_alerts)
            },
            "notes": {
                "items": notes,
                "total": len(notes)
            },
            "evidence_gaps": {
                "items": [
                    {
                        "gap_id": gap.gap_id,
                        "title": gap.title,
                        "description": gap.description,
                        "status": gap.status,
                        "created_by_user_id": gap.created_by_user_id,
                        "created_at_utc": gap.created_at_utc,
                        "resolved_at_utc": gap.resolved_at_utc
                    }
                    for gap in case.evidence_gaps
                ],
                "total": len(case.evidence_gaps)
            },
            "timeline_entries": {
                "items": timeline_entries,
                "total": len(timeline_entries)
            }
        }
    
    def get_next_case_ref(self) -> str:
        """Generate next sequential case reference.
        
        Returns:
            Next case reference like CS-204
        """
        # Get max case number from existing case refs
        from sqlalchemy import func, cast, Integer
        
        # Extract numeric part after 'CS-' prefix
        max_ref = (
            self.db.query(
                func.max(
                    cast(
                        func.substr(AmlCase.case_ref, 4),
                        Integer
                    )
                )
            )
            .filter(AmlCase.case_ref.like("CS-%"))
            .scalar()
        )
        
        next_num = (max_ref or 0) + 1
        return f"CS-{next_num}"
