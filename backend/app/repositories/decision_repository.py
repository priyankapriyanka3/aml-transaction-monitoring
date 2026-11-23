"""Decision repository for officer assignment and decision recording."""
import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.case_review_assignment import CaseReviewAssignment
from app.models.case_decision import CaseDecision
from app.models.case import AmlCase


class DecisionRepository:
    """Repository for officer assignment and decision recording."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def assign_officer(
        self,
        case_id: uuid.UUID,
        officer_user_id: uuid.UUID,
        assigned_by_user_id: uuid.UUID
    ) -> CaseReviewAssignment:
        """Assign an officer to a case or update existing assignment.
        
        Args:
            case_id: Case ID
            officer_user_id: Officer user ID
            assigned_by_user_id: User ID of assigner
        
        Returns:
            CaseReviewAssignment record
        """
        # Check for existing assignment
        existing = self.db.query(CaseReviewAssignment).filter(
            CaseReviewAssignment.case_id == case_id
        ).first()
        
        if existing:
            # Update existing assignment
            existing.officer_user_id = officer_user_id
            existing.assigned_by_user_id = assigned_by_user_id
            existing.assigned_at_utc = datetime.now(timezone.utc)
            self.db.flush()
            return existing
        else:
            # Create new assignment
            assignment = CaseReviewAssignment(
                case_id=case_id,
                officer_user_id=officer_user_id,
                assigned_by_user_id=assigned_by_user_id
            )
            self.db.add(assignment)
            self.db.flush()
            return assignment
    
    def get_assignment_by_case(self, case_id: uuid.UUID) -> CaseReviewAssignment | None:
        """Get officer assignment for a case.
        
        Args:
            case_id: Case ID
        
        Returns:
            CaseReviewAssignment or None if not found
        """
        return self.db.query(CaseReviewAssignment).filter(
            CaseReviewAssignment.case_id == case_id
        ).first()
    
    def create_decision(
        self,
        case_id: uuid.UUID,
        deciding_officer_user_id: uuid.UUID,
        outcome: str,
        rationale_text: str,
        immutable_hash: str
    ) -> CaseDecision:
        """Create an immutable decision record.
        
        Args:
            case_id: Case ID
            deciding_officer_user_id: Officer user ID
            outcome: Decision outcome
            rationale_text: Rationale text
            immutable_hash: Immutable hash
        
        Returns:
            CaseDecision record
        """
        decision = CaseDecision(
            case_id=case_id,
            deciding_officer_user_id=deciding_officer_user_id,
            outcome=outcome,
            rationale_text=rationale_text,
            immutable_hash=immutable_hash
        )
        self.db.add(decision)
        self.db.flush()
        return decision
    
    def update_case_status(self, case_id: uuid.UUID, status: str) -> None:
        """Update case status.
        
        Args:
            case_id: Case ID
            status: New status
        """
        case = self.db.get(AmlCase, case_id)
        if case:
            case.status = status
            case.updated_at_utc = datetime.now(timezone.utc)
            self.db.flush()
    
    def update_case_officer(self, case_id: uuid.UUID, officer_user_id: uuid.UUID) -> None:
        """Update case assigned officer.
        
        Args:
            case_id: Case ID
            officer_user_id: Officer user ID
        """
        case = self.db.get(AmlCase, case_id)
        if case:
            case.assigned_officer_user_id = officer_user_id
            case.updated_at_utc = datetime.now(timezone.utc)
            self.db.flush()
