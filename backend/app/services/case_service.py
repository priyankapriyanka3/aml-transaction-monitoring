"""
Service for case creation, overview, and orchestration.
Handles case creation from alerts with transactional integrity.
"""
from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from ..models.case_alert_link import CaseAlertLink
from ..models.case_note import CaseNote
from ..repositories.alert_repository import AlertRepository
from ..repositories.case_note_repository import CaseNoteRepository
from ..repositories.case_repository import CaseRepository
from ..repositories.user_repository import UserRepository
from ..schemas.case_schemas import CaseNoteResponse, CaseOverviewResponse
from ..services.audit_service import AuditService
from ..services.readiness_service import ReadinessService


class CaseService:
    """Service for case workspace operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.case_repo = CaseRepository(db)
        self.alert_repo = AlertRepository(db)
        self.user_repo = UserRepository(db)
        self.case_note_repo = CaseNoteRepository(db)
        self.audit_service = AuditService(db)
        self.readiness_service = ReadinessService(db)
    
    def create_case_from_alert(
        self,
        alert_id: str,
        case_priority: str,
        initial_rationale: str,
        actor_id: str
    ) -> tuple[str, str]:
        """
        Create a case from an alert with full transactional integrity.
        
        Steps:
        1. Create case
        2. Create case_alert_link
        3. Update alert status to ESCALATED_TO_CASE
        4. Create CASE_CREATED audit event
        5. Create ALERT_LINKED_TO_CASE audit event
        
        All in same transaction.
        
        Returns (case_id, case_number)
        """
        # Get alert
        alert_uuid = UUID(alert_id) if isinstance(alert_id, str) else alert_id
        alert = self.alert_repo.get_by_id(alert_uuid)
        if not alert:
            raise ValueError("Alert not found")
        
        # Get actor for role
        actor_uuid = UUID(actor_id) if isinstance(actor_id, str) else actor_id
        actor = self.user_repo.get_by_id(actor_uuid)
        if not actor:
            raise ValueError("Actor user not found")
        
        # Generate case number
        # Simple sequential numbering - in production would use more sophisticated logic
        from sqlalchemy import func

        from ..models.aml_case import AMLCase as AMLCaseModel
        
        existing_count = self.db.query(func.count(AMLCaseModel.case_id)).scalar() or 0
        case_number = f"CS-{str(existing_count + 1).zfill(3)}"
        
        # Create case
        case = self.case_repo.create_from_alert(
            case_number=case_number,
            source_alert=alert,
            actor_id=actor_uuid,
            priority=case_priority,
            initial_rationale=initial_rationale
        )
        
        # Create case-alert link
        now = datetime.now(timezone.utc)
        link = CaseAlertLink(
            case_alert_link_id=uuid4(),
            case_id=case.case_id,
            alert_id=alert_uuid,
            linked_at=now,
            linked_by_user_id=actor_uuid,
            selection_basis=initial_rationale
        )
        self.db.add(link)
        
        # Update alert status
        alert.status = "ESCALATED_TO_CASE"
        alert.updated_at = now
        self.db.add(alert)
        
        # Create CASE_CREATED audit event
        self.audit_service.create_event(
            entity_type="case",
            entity_id=str(case.case_id),
            action_type="CASE_CREATED",
            actor_user_id=actor_uuid,
            actor_role=actor.primary_role,
            payload={
                "case_number": case_number,
                "source_alert_id": str(alert_uuid),
                "priority": case_priority,
                "initial_rationale": initial_rationale,
                "created_at": now.isoformat()
            }
        )
        
        # Create ALERT_LINKED_TO_CASE audit event
        self.audit_service.create_event(
            entity_type="alert",
            entity_id=str(alert_uuid),
            action_type="ALERT_LINKED_TO_CASE",
            actor_user_id=actor_uuid,
            actor_role=actor.primary_role,
            payload={
                "case_id": str(case.case_id),
                "case_number": case_number,
                "previous_status": "UNDER_REVIEW",  # Assuming typical flow
                "new_status": "ESCALATED_TO_CASE",
                "linked_at": now.isoformat()
            }
        )
        
        # Commit transaction
        self.db.commit()
        
        return str(case.case_id), case_number
    
    def get_case_overview(self, case_id: str) -> CaseOverviewResponse:
        """
        Get complete case overview with aggregations and recent activity.
        
        Includes:
        - Basic case metadata
        - Assigned user name
        - Linked alert count
        - Flagged value total
        - Open/overdue request counts
        - Recent activity from audit events
        
        Accepts either UUID or case_number (e.g., 'CS-001').
        """
        # Try to get case by UUID first, if that fails try case_number
        try:
            case = self.case_repo.get_overview(UUID(case_id))
        except (ValueError, AttributeError):
            # Not a valid UUID, try case_number
            case = self.case_repo.get_by_number(case_id)
        
        if not case:
            raise ValueError("Case not found")
        
        # Use the actual UUID for aggregation queries
        case_uuid = case.case_id
        
        # Get assigned user name if assigned
        assigned_user_name = None
        if case.assigned_user_id:
            user = self.user_repo.get_by_id(case.assigned_user_id)
            if user:
                assigned_user_name = user.display_name
        
        # Get aggregated counts
        linked_alert_count = self.case_repo.get_linked_alert_count(case_uuid)
        flagged_value_total = self.case_repo.get_flagged_value_total(case_uuid)
        open_request_count = self.case_repo.get_open_information_request_count(case_uuid)
        overdue_request_count = self.case_repo.get_overdue_information_request_count(case_uuid)
        
        # Get recent activity
        recent_events = self.case_repo.get_recent_activity(case_uuid, limit=10)
        recent_activity = []
        for event in recent_events:
            # Get actor display name
            actor = self.user_repo.get_by_id(event.actor_user_id)
            actor_display = actor.display_name if actor else "Unknown"
            
            recent_activity.append({
                "event_id": str(event.audit_event_id),
                "event_type": event.action_type,
                "occurred_at": event.occurred_at.isoformat(),
                "actor_display": actor_display,
                "summary": self._format_event_summary(event)
            })
        
        # Determine currency from flagged transactions (default to USD)
        currency = "USD"
        
        return CaseOverviewResponse(
            case_id=str(case.case_id),
            case_number=case.case_number,
            status=case.status,
            priority=case.priority,
            assigned_user_id=str(case.assigned_user_id) if case.assigned_user_id else None,
            assigned_user_name=assigned_user_name,
            recommendation_state=case.recommendation_state,
            recommendation_outcome=case.recommendation_outcome,
            flagged_value_total=float(flagged_value_total),
            currency=currency,
            linked_alert_count=linked_alert_count,
            open_information_request_count=open_request_count,
            overdue_information_request_count=overdue_request_count,
            recent_activity=recent_activity,
            created_at=case.created_at,
            updated_at=case.updated_at
        )
    
    def _format_event_summary(self, event) -> str:
        """Format audit event into human-readable summary"""
        action_type = event.action_type
        
        if action_type == "CASE_CREATED":
            return "Case created from alert"
        elif action_type == "ALERT_LINKED_TO_CASE":
            return "Alert linked to case"
        elif action_type == "CASE_ASSIGNED":
            return "Case assigned"
        elif action_type == "CASE_STATUS_CHANGED":
            return "Case status changed"
        elif action_type == "INVESTIGATION_NOTE_ADDED":
            return "Investigation note added"
        elif action_type == "INVESTIGATION_RECOMMENDATION_SUBMITTED":
            return "Recommendation submitted"
        elif action_type == "INFORMATION_REQUEST_CREATED":
            return "Information request created"
        else:
            return f"Action: {action_type}"
    
    def create_note(
        self,
        case_id: str,
        note_type: str,
        stage: str,
        body: str,
        author_user_id: str
    ) -> CaseNoteResponse:
        """
        Create a case note with validation and audit trail.
        
        Validates:
        - body is not empty (minimum 1 character)
        - case exists
        - author exists
        
        Creates INVESTIGATION_NOTE_ADDED audit event.
        """
        # Validate body length
        if not body or len(body.strip()) == 0:
            raise ValueError("Note body cannot be empty")
        
        # Verify case exists
        case_uuid = UUID(case_id) if isinstance(case_id, str) else case_id
        case = self.case_repo.get_overview(case_uuid)
        if not case:
            raise ValueError("Case not found")
        
        # Get author for role
        author_uuid = UUID(author_user_id) if isinstance(author_user_id, str) else author_user_id
        author = self.user_repo.get_by_id(author_uuid)
        if not author:
            raise ValueError("Author user not found")
        
        # Create note
        note = CaseNote(
            note_id=uuid4(),
            case_id=case_uuid,
            note_type=note_type,
            stage=stage,
            body=body,
            author_user_id=author_uuid,
            superseded_by_note_id=None,
            created_at=datetime.now(timezone.utc)
        )
        note = self.case_note_repo.create(note)
        
        # Create audit event
        self.audit_service.create_event(
            entity_type="case",
            entity_id=case_id,
            action_type="INVESTIGATION_NOTE_ADDED",
            actor_user_id=author_uuid,
            actor_role=author.primary_role,
            payload={
                "note_id": str(note.note_id),
                "note_type": note_type,
                "stage": stage,
                "body_length": len(body),
                "created_at": note.created_at.isoformat()
            }
        )
        
        return CaseNoteResponse(
            note_id=str(note.note_id),
            case_id=str(note.case_id),
            note_type=note.note_type,
            stage=note.stage,
            body=note.body,
            author_user_id=str(note.author_user_id),
            author_display_name=author.display_name,
            created_at=note.created_at,
            superseded_by_note_id=note.superseded_by_note_id
        )
    
    def list_notes(self, case_id: str) -> list[CaseNoteResponse]:
        """
        List all notes for a case in chronological order.
        Returns notes from oldest to newest.
        Accepts either UUID or case_number (e.g., 'CS-001').
        """
        # Try to get case by UUID first, if that fails try case_number
        try:
            case_uuid = UUID(case_id)
            case = self.case_repo.get_overview(case_uuid)
        except (ValueError, AttributeError):
            # Not a valid UUID, try case_number
            case = self.case_repo.get_by_number(case_id)
            if case:
                case_uuid = case.case_id
            else:
                case_uuid = None
        
        if not case:
            raise ValueError("Case not found")
        
        # Get notes
        notes = self.case_note_repo.list_by_case(case_uuid)
        
        # Enrich with author names
        response_notes = []
        for note in notes:
            author = self.case_note_repo.get_user_by_id(note.author_user_id)
            author_display_name = author.display_name if author else "Unknown"
            
            response_notes.append(CaseNoteResponse(
                note_id=str(note.note_id),
                case_id=str(note.case_id),
                note_type=note.note_type,
                stage=note.stage,
                body=note.body,
                author_user_id=str(note.author_user_id),
                author_display_name=author_display_name,
                created_at=note.created_at,
                superseded_by_note_id=str(note.superseded_by_note_id) if note.superseded_by_note_id else None
            ))
        
        return response_notes
    
    def transition_status(
        self,
        case_id: str,
        new_status: str,
        actor_id: str,
        reason: str = "",
        trigger_event: str = ""
    ) -> dict:
        """
        Transition case to new status with state machine validation.
        
        Valid transitions:
        - INVESTIGATING -> PENDING_INFORMATION (on information request issuance)
        - INVESTIGATING -> REVIEW_READY (on recommendation submission + readiness pass)
        - PENDING_INFORMATION -> INVESTIGATING (on information response received)
        - REVIEW_READY -> SUBMITTED_FOR_REVIEW (on handoff submission)
        
        Returns 409 when transition is invalid.
        Creates CASE_STATUS_CHANGED audit event.
        """
        # Get case
        case_uuid = UUID(case_id) if isinstance(case_id, str) else case_id
        case = self.case_repo.get_overview(case_uuid)
        if not case:
            raise ValueError("Case not found")
        
        # Get actor for role
        actor_uuid = UUID(actor_id) if isinstance(actor_id, str) else actor_id
        actor = self.user_repo.get_by_id(actor_uuid)
        if not actor:
            raise ValueError("Actor user not found")
        
        # Validate state machine
        previous_status = case.status
        valid_transitions = {
            "INVESTIGATING": ["PENDING_INFORMATION", "REVIEW_READY"],
            "PENDING_INFORMATION": ["INVESTIGATING"],
            "REVIEW_READY": ["SUBMITTED_FOR_REVIEW"]
        }
        
        if previous_status not in valid_transitions:
            raise ValueError(f"No valid transitions from status {previous_status}")
        
        if new_status not in valid_transitions[previous_status]:
            raise ValueError(
                f"Invalid transition from {previous_status} to {new_status}. "
                f"Valid transitions: {', '.join(valid_transitions[previous_status])}"
            )
        
        # Transition case
        now = datetime.now(timezone.utc)
        case = self.case_repo.transition_status(case, new_status, actor_uuid)
        
        # Create CASE_STATUS_CHANGED audit event
        self.audit_service.create_event(
            entity_type="case",
            entity_id=case_id,
            action_type="CASE_STATUS_CHANGED",
            actor_user_id=actor_uuid,
            actor_role=actor.primary_role,
            payload={
                "previous_status": previous_status,
                "new_status": new_status,
                "reason": reason,
                "trigger_event": trigger_event,
                "transitioned_at": now.isoformat()
            }
        )
        
        # Commit transaction
        self.db.commit()
        
        return {
            "case_id": case_id,
            "previous_status": previous_status,
            "new_status": new_status,
            "transitioned_by_user_id": actor_id,
            "transitioned_at": now,
            "trigger_event": trigger_event
        }
    
    def submit_recommendation(
        self,
        case_id: str,
        recommendation_outcome: str,
        findings_summary: str,
        actor_id: str
    ) -> dict:
        """
        Submit investigation recommendation for review.
        
        Validates:
        - findings_summary minimum 50 characters
        - Case readiness (linked alerts, no open/overdue requests)
        
        Updates case with recommendation and creates audit event.
        Returns 409 if readiness check fails.
        """
        # Validate findings_summary length
        if not findings_summary or len(findings_summary.strip()) < 50:
            raise ValueError("Findings summary must be at least 50 characters")
        
        # Get case
        case_uuid = UUID(case_id) if isinstance(case_id, str) else case_id
        case = self.case_repo.get_overview(case_uuid)
        if not case:
            raise ValueError("Case not found")
        
        # Get actor for role
        actor_uuid = UUID(actor_id) if isinstance(actor_id, str) else actor_id
        actor = self.user_repo.get_by_id(actor_uuid)
        if not actor:
            raise ValueError("Actor user not found")
        
        # Check linked alerts
        if self.case_repo.get_linked_alert_count(case_uuid) == 0:
            raise ValueError("Cannot submit recommendation: no alerts linked to case")
        
        # Check open/overdue requests
        open_count = self.case_repo.get_open_information_request_count(case_uuid)
        overdue_count = self.case_repo.get_overdue_information_request_count(case_uuid)
        
        if open_count > 0 or overdue_count > 0:
            raise ValueError(
                f"Cannot submit recommendation: {open_count} open and {overdue_count} overdue information requests"
            )
        
        # Save recommendation
        now = datetime.now(timezone.utc)
        case = self.case_repo.save_recommendation(
            case=case,
            recommendation_outcome=recommendation_outcome,
            findings_summary=findings_summary,
            actor_id=actor_uuid
        )
        
        # Create INVESTIGATION_RECOMMENDATION_SUBMITTED audit event
        self.audit_service.create_event(
            entity_type="case",
            entity_id=case_id,
            action_type="INVESTIGATION_RECOMMENDATION_SUBMITTED",
            actor_user_id=actor_uuid,
            actor_role=actor.primary_role,
            payload={
                "recommendation_outcome": recommendation_outcome,
                "findings_summary_length": len(findings_summary),
                "recommendation_state": "SUBMITTED",
                "submitted_at": now.isoformat()
            }
        )
        
        # Commit transaction
        self.db.commit()
        
        return {
            "case_id": str(case.case_id),
            "recommendation_state": case.recommendation_state,
            "recommendation_outcome": case.recommendation_outcome,
            "findings_summary": case.findings_summary,
            "submitted_by_user_id": actor_id,
            "submitted_at": now
        }
