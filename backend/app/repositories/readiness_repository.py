"""Readiness repository for officer review package assembly."""
import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.models.case import AmlCase
from app.models.user import User
from app.models.information_request import InformationRequest
from app.models.case_alert_link import CaseAlertLink
from app.models.case_note import CaseNote


class ReadinessRepository:
    """Repository for readiness checks and decision blocker state."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def derive_blocker_state(self, case_id: uuid.UUID) -> str:
        """Derive blocker state from information requests.
        
        Blocker state logic:
        - OPEN_REQUESTS: At least one request has status == OPEN
        - OVERDUE_REQUESTS: At least one request has status != RESOLVED and due_at_utc < now
        - NONE: No blockers
        
        Args:
            case_id: Case ID to check
        
        Returns:
            Blocker state: NONE, OPEN_REQUESTS, or OVERDUE_REQUESTS
        """
        now = datetime.now(timezone.utc)
        
        # Check for OPEN requests
        open_count = self.db.query(func.count(InformationRequest.request_id)).filter(
            InformationRequest.case_id == case_id,
            InformationRequest.status == "OPEN"
        ).scalar()
        
        if open_count > 0:
            return "OPEN_REQUESTS"
        
        # Check for overdue requests (status != RESOLVED and due_at_utc < now)
        overdue_count = self.db.query(func.count(InformationRequest.request_id)).filter(
            InformationRequest.case_id == case_id,
            InformationRequest.status != "RESOLVED",
            InformationRequest.due_at_utc < now
        ).scalar()
        
        if overdue_count > 0:
            return "OVERDUE_REQUESTS"
        
        return "NONE"
    
    def check_conflicted_officer(
        self,
        case_id: uuid.UUID,
        officer_user_id: uuid.UUID
    ) -> bool:
        """Check if the officer is the case creator (four-eyes conflict).
        
        Args:
            case_id: Case ID
            officer_user_id: Officer user ID to check
        
        Returns:
            True if officer is case creator (conflicted), False otherwise
        """
        case = self.db.get(AmlCase, case_id)
        if not case:
            return False
        
        return case.created_by_user_id == officer_user_id
    
    def get_checklist_state(self, case_id: uuid.UUID) -> dict:
        """Get readiness checklist state for a case.
        
        Returns counts for:
        - linked_alert_count: Number of linked alerts
        - note_count: Number of case notes
        - total_request_count: Total number of information requests
        - open_request_count: Number of requests with status OPEN
        - overdue_request_count: Number of overdue requests
        
        Args:
            case_id: Case ID
        
        Returns:
            Dictionary with checklist state counts
        """
        now = datetime.now(timezone.utc)
        
        # Count linked alerts
        linked_alert_count = self.db.query(func.count(CaseAlertLink.case_alert_link_id)).filter(
            CaseAlertLink.case_id == case_id
        ).scalar() or 0
        
        # Count notes
        note_count = self.db.query(func.count(CaseNote.note_id)).filter(
            CaseNote.case_id == case_id
        ).scalar() or 0
        
        # Count total requests
        total_request_count = self.db.query(func.count(InformationRequest.request_id)).filter(
            InformationRequest.case_id == case_id
        ).scalar() or 0
        
        # Count OPEN requests
        open_request_count = self.db.query(func.count(InformationRequest.request_id)).filter(
            InformationRequest.case_id == case_id,
            InformationRequest.status == "OPEN"
        ).scalar() or 0
        
        # Count overdue requests
        overdue_request_count = self.db.query(func.count(InformationRequest.request_id)).filter(
            InformationRequest.case_id == case_id,
            InformationRequest.status != "RESOLVED",
            InformationRequest.due_at_utc < now
        ).scalar() or 0
        
        return {
            "linked_alert_count": linked_alert_count,
            "note_count": note_count,
            "total_request_count": total_request_count,
            "open_request_count": open_request_count,
            "overdue_request_count": overdue_request_count
        }
    
    def get_eligible_officers(self, case_id: uuid.UUID) -> list[User]:
        """Get list of eligible officers for case review.
        
        Eligible officers are users with role=OFFICER where user_id != case.created_by_user_id.
        
        Args:
            case_id: Case ID
        
        Returns:
            List of eligible User objects
        """
        case = self.db.get(AmlCase, case_id)
        if not case:
            return []
        
        # Get all officers except case creator
        stmt = select(User).where(
            User.role == "OFFICER",
            User.is_active == True,
            User.user_id != case.created_by_user_id
        ).order_by(User.display_name)
        
        return list(self.db.scalars(stmt).all())
