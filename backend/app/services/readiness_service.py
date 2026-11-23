"""Readiness service for case review preparation."""
import uuid
from sqlalchemy.orm import Session
from app.repositories.readiness_repository import ReadinessRepository
from app.repositories.case_repository import CaseRepository
from app.schemas.readiness_schemas import ReadinessProjection, ReadinessChecklistItem, PackageSummary, EligibleOfficer


class ReadinessService:
    """Service for readiness checklist derivation."""
    
    def __init__(self, db: Session):
        self.db = db
        self.readiness_repo = ReadinessRepository(db)
        self.case_repo = CaseRepository(db)
    
    def derive_checklist(self, case_id: uuid.UUID) -> ReadinessProjection:
        """Derive the readiness checklist for a case.
        
        Checklist items:
        1. linked_evidence - complete if >= 1 linked alert
        2. investigation_notes - complete if >= 1 note
        3. responses_reviewed - complete if all requests status != OPEN
        4. no_open_requests - complete if no requests with status OPEN or OVERDUE
        
        Args:
            case_id: Case ID
        
        Returns:
            ReadinessProjection with checklist, package summary, and eligible officers
        
        Raises:
            ValueError: If case not found
        """
        # Verify case exists
        case = self.case_repo.get_by_id(case_id)
        if not case:
            raise ValueError(f"Case {case_id} not found")
        
        # Get checklist state from repository
        checklist_state = self.readiness_repo.get_checklist_state(case_id)
        
        # Build checklist items
        checklist = [
            ReadinessChecklistItem(
                name="linked_evidence",
                complete=checklist_state["linked_alert_count"] >= 1,
                details=f"{checklist_state['linked_alert_count']} alert(s) linked"
            ),
            ReadinessChecklistItem(
                name="investigation_notes",
                complete=checklist_state["note_count"] >= 1,
                details=f"{checklist_state['note_count']} note(s) recorded"
            ),
            ReadinessChecklistItem(
                name="responses_reviewed",
                complete=checklist_state["open_request_count"] == 0,
                details=f"{checklist_state['total_request_count'] - checklist_state['open_request_count']} of {checklist_state['total_request_count']} requests reviewed"
            ),
            ReadinessChecklistItem(
                name="no_open_requests",
                complete=checklist_state["open_request_count"] == 0 and checklist_state["overdue_request_count"] == 0,
                details="No open or overdue requests" if (checklist_state["open_request_count"] == 0 and checklist_state["overdue_request_count"] == 0) else f"{checklist_state['open_request_count']} open, {checklist_state['overdue_request_count']} overdue"
            )
        ]
        
        # Build package summary
        package_summary = PackageSummary(
            alert_count=checklist_state["linked_alert_count"],
            note_count=checklist_state["note_count"],
            request_count=checklist_state["total_request_count"],
            evidence_count=checklist_state["linked_alert_count"]
        )
        
        # Get eligible officers (OFFICER role, not case creator)
        eligible_officers_models = self.readiness_repo.get_eligible_officers(case_id)
        eligible_officers = [
            EligibleOfficer(
                user_id=officer.user_id,
                display_name=officer.display_name,
                email=officer.email
            )
            for officer in eligible_officers_models
        ]
        
        return ReadinessProjection(
            checklist=checklist,
            package_summary=package_summary,
            eligible_officers=eligible_officers
        )
