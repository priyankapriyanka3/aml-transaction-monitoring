"""
Service for information request issuance and response recording.
Orchestrates request creation with case status transitions and audit trail.
"""
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from ..models.information_request import InformationRequest
from ..repositories.case_repository import CaseRepository
from ..repositories.information_request_repository import InformationRequestRepository
from ..repositories.user_repository import UserRepository
from ..schemas.information_request_schemas import InformationRequestResponse
from ..services.audit_service import AuditService


class InformationRequestService:
    """Service for information request operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.request_repo = InformationRequestRepository(db)
        self.case_repo = CaseRepository(db)
        self.user_repo = UserRepository(db)
        self.audit_service = AuditService(db)
    
    def create_request(
        self,
        case_id: str,
        recipient_channel: str,
        requested_summary: str,
        rationale: str,
        due_at: datetime,
        actor_id: str
    ) -> tuple[InformationRequestResponse, str]:
        """
        Create an information request and transition case to PENDING_INFORMATION.
        
        Steps:
        1. Validate requested_summary, rationale, and due_at
        2. Create information request
        3. Transition case status to PENDING_INFORMATION
        4. Create INFORMATION_REQUEST_CREATED audit event
        
        All in same transaction.
        
        Returns (InformationRequestResponse, case_status_after_create)
        """
        # Validate due_at is in future
        now = datetime.now(timezone.utc)
        # Convert due_at to timezone-aware if it's naive (assume UTC)
        if due_at.tzinfo is None:
            due_at = due_at.replace(tzinfo=timezone.utc)
        if due_at <= now:
            raise ValueError("due_at must be a future timestamp")
        
        # Verify case exists
        case_uuid = UUID(case_id) if isinstance(case_id, str) else case_id
        case = self.case_repo.get_overview(case_uuid)
        if not case:
            raise ValueError("Case not found")
        
        # Get actor for role
        actor_uuid = UUID(actor_id) if isinstance(actor_id, str) else actor_id
        actor = self.user_repo.get_by_id(actor_uuid)
        if not actor:
            raise ValueError("Actor user not found")
        
        # Generate request ID
        request_count = self.request_repo.count_open_for_case(case_uuid) + 1
        request_id = f"IR-{str(request_count).zfill(3)}"
        
        # Create request
        request = InformationRequest(
            information_request_id=request_id,
            case_id=case_uuid,
            recipient_channel=recipient_channel,
            requested_summary=requested_summary,
            rationale=rationale,
            status="OPEN",
            due_at=due_at,
            response_summary=None,
            response_channel=None,
            response_received_at=None,
            created_by_user_id=actor_uuid,
            created_at=now,
            updated_at=now
        )
        request = self.request_repo.create(request)
        
        # Transition case to PENDING_INFORMATION
        previous_status = case.status
        case.status = "PENDING_INFORMATION"
        case.updated_at = now
        self.db.add(case)
        
        # Create INFORMATION_REQUEST_CREATED audit event
        self.audit_service.create_event(
            entity_type="case",
            entity_id=case_id,
            action_type="INFORMATION_REQUEST_CREATED",
            actor_user_id=actor_uuid,
            actor_role=actor.primary_role,
            payload={
                "information_request_id": request_id,
                "recipient_channel": recipient_channel,
                "requested_summary": requested_summary,
                "due_at": due_at.isoformat(),
                "previous_status": previous_status,
                "new_status": "PENDING_INFORMATION",
                "created_at": now.isoformat()
            }
        )
        
        # Commit transaction
        self.db.commit()
        
        # Compute days remaining
        days_remaining = (due_at - now).days
        
        return (
            InformationRequestResponse(
                information_request_id=request.information_request_id,
                case_id=str(request.case_id),
                recipient_channel=request.recipient_channel,
                requested_summary=request.requested_summary,
                rationale=request.rationale,
                status=request.status,
                due_at=request.due_at,
                days_remaining=days_remaining,
                is_overdue=False,
                response_summary=None,
                response_channel=None,
                response_received_at=None,
                created_by_user_id=str(request.created_by_user_id),
                created_at=request.created_at
            ),
            case.status
        )
    
    def list_requests_for_case(self, case_id: str) -> list[InformationRequestResponse]:
        """
        List all information requests for a case with computed SLA fields.
        Returns newest first.
        """
        case_uuid = UUID(case_id) if isinstance(case_id, str) else case_id
        requests = self.request_repo.list_by_case(case_uuid)
        now = datetime.now(timezone.utc)
        
        response_list = []
        for req in requests:
            # Compute days remaining and overdue status
            if req.status == "OPEN":
                days_remaining = (req.due_at - now).days
                is_overdue = req.due_at < now
            else:
                days_remaining = None
                is_overdue = False
            
            response_list.append(InformationRequestResponse(
                information_request_id=req.information_request_id,
                case_id=str(req.case_id),
                recipient_channel=req.recipient_channel,
                requested_summary=req.requested_summary,
                rationale=req.rationale,
                status=req.status,
                due_at=req.due_at,
                days_remaining=days_remaining,
                is_overdue=is_overdue,
                response_summary=req.response_summary,
                response_channel=req.response_channel,
                response_received_at=req.response_received_at,
                created_by_user_id=str(req.created_by_user_id),
                created_at=req.created_at
            ))
        
        return response_list
    
    def record_response(
        self,
        information_request_id: str,
        response_summary: str,
        received_at: datetime,
        response_channel: str,
        actor_id: str
    ) -> tuple[InformationRequestResponse, str]:
        """
        Record a response to an information request and transition case back to INVESTIGATING.
        
        Steps:
        1. Validate response_summary and received_at
        2. Update request status to RESPONDED
        3. Transition case from PENDING_INFORMATION to INVESTIGATING
        4. Create INFORMATION_REQUEST_RESPONSE_RECORDED audit event
        
        All in same transaction.
        
        Returns (InformationRequestResponse, case_status_after_response)
        """
        now = datetime.now(timezone.utc)
        
        # Convert received_at to timezone-aware if it's naive (assume UTC)
        if received_at.tzinfo is None:
            received_at = received_at.replace(tzinfo=timezone.utc)
        
        # Validate received_at is not future
        if received_at > now:
            raise ValueError("received_at cannot be in the future")
        
        # Get request
        request = self.request_repo.get_by_id(information_request_id)
        if not request:
            raise ValueError("Information request not found")
        
        # Validate request is OPEN
        if request.status != "OPEN":
            raise ValueError(f"Cannot record response for request with status {request.status}")
        
        # Get case
        case = self.case_repo.get_overview(request.case_id)
        if not case:
            raise ValueError("Case not found")
        
        # Get actor for role
        actor_uuid = UUID(actor_id) if isinstance(actor_id, str) else actor_id
        actor = self.user_repo.get_by_id(actor_uuid)
        if not actor:
            raise ValueError("Actor user not found")
        
        # Update request
        request.status = "RESPONDED"
        request.response_summary = response_summary
        request.response_channel = response_channel
        request.response_received_at = received_at
        request.updated_at = now
        self.db.add(request)
        
        # Transition case back to INVESTIGATING
        previous_status = case.status
        case.status = "INVESTIGATING"
        case.updated_at = now
        self.db.add(case)
        
        # Create audit event
        self.audit_service.create_event(
            entity_type="case",
            entity_id=str(case.case_id),
            action_type="INFORMATION_REQUEST_RESPONSE_RECORDED",
            actor_user_id=actor_uuid,
            actor_role=actor.primary_role,
            payload={
                "information_request_id": information_request_id,
                "response_channel": response_channel,
                "received_at": received_at.isoformat(),
                "previous_status": previous_status,
                "new_status": "INVESTIGATING",
                "recorded_at": now.isoformat()
            }
        )
        
        # Commit transaction
        self.db.commit()
        
        return (
            InformationRequestResponse(
                information_request_id=request.information_request_id,
                case_id=str(request.case_id),
                recipient_channel=request.recipient_channel,
                requested_summary=request.requested_summary,
                rationale=request.rationale,
                status=request.status,
                due_at=request.due_at,
                days_remaining=None,
                is_overdue=False,
                response_summary=request.response_summary,
                response_channel=request.response_channel,
                response_received_at=request.response_received_at,
                created_by_user_id=str(request.created_by_user_id),
                created_at=request.created_at
            ),
            case.status
        )
