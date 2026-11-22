"""
Repository for information request operations.
"""
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from ..models.information_request import InformationRequest


class InformationRequestRepository:
    """Repository for information request data operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, request: InformationRequest) -> InformationRequest:
        """Create a new information request"""
        self.db.add(request)
        self.db.flush()
        return request
    
    def list_by_case(self, case_id: UUID | str) -> list[InformationRequest]:
        """
        List all information requests for a case.
        Returns in chronological order (created_at DESC, newest first).
        """
        case_uuid = UUID(case_id) if isinstance(case_id, str) else case_id
        return self.db.query(InformationRequest).filter(
            InformationRequest.case_id == case_uuid
        ).order_by(InformationRequest.created_at.desc()).all()
    
    def count_open_for_case(self, case_id: UUID | str) -> int:
        """Count of open information requests for a case"""
        case_uuid = UUID(case_id) if isinstance(case_id, str) else case_id
        return self.db.query(InformationRequest).filter(
            InformationRequest.case_id == case_uuid,
            InformationRequest.status == "OPEN"
        ).count()
    
    def count_overdue_for_case(self, case_id: UUID | str) -> int:
        """
        Count of overdue information requests.
        Overdue means due_at < now and status is still OPEN.
        """
        case_uuid = UUID(case_id) if isinstance(case_id, str) else case_id
        now = datetime.now(timezone.utc)
        return self.db.query(InformationRequest).filter(
            InformationRequest.case_id == case_uuid,
            InformationRequest.status == "OPEN",
            InformationRequest.due_at < now
        ).count()
    
    def get_by_id(self, information_request_id: str) -> InformationRequest | None:
        """Get information request by ID"""
        return self.db.query(InformationRequest).filter(
            InformationRequest.information_request_id == information_request_id
        ).first()
