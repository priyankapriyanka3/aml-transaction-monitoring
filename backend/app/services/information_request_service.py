"""Information request service for evidence gap tracking."""
import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from app.repositories.information_request_repository import InformationRequestRepository
from app.repositories.case_repository import CaseRepository
from app.repositories.readiness_repository import ReadinessRepository
from app.models.audit_event import AuditEvent
from app.models.information_request import InformationRequest


class InformationRequestService:
    """Service for information request business logic."""
    
    def __init__(self, db: Session):
        self.db = db
        self.request_repo = InformationRequestRepository(db)
        self.case_repo = CaseRepository(db)
        self.readiness_repo = ReadinessRepository(db)
    
    def create_request(
        self,
        case_id: uuid.UUID,
        gap_id: uuid.UUID | None,
        gap_title: str | None,
        gap_description: str | None,
        target_party: str,
        delivery_channel: str,
        reason_text: str,
        due_at_utc: datetime,
        created_by_user_id: uuid.UUID,
        actor_role: str,
        correlation_id: str
    ) -> InformationRequest:
        """Create a new information request.
        
        Args:
            case_id: Case ID
            gap_id: Evidence gap ID (if already exists)
            gap_title: Title for new gap (if creating)
            gap_description: Description for new gap (if creating)
            target_party: Target party for the request
            delivery_channel: Delivery channel
            reason_text: Reason for the request
            due_at_utc: Due date
            created_by_user_id: User creating the request
            actor_role: Role of the creating user
            correlation_id: Request correlation ID for audit trail
        
        Returns:
            Created InformationRequest
        
        Raises:
            ValueError: If case not found or if neither gap_id nor gap_title provided
        """
        # Verify case exists
        case = self.case_repo.get_by_id(case_id)
        if not case:
            raise ValueError(f"Case {case_id} not found")
        
        # Create gap if gap_title and gap_description are provided
        if gap_id is None:
            if not gap_title or not gap_description:
                raise ValueError("Either gap_id or both gap_title and gap_description must be provided")
            
            from app.models.evidence_gap import EvidenceGap
            from datetime import timezone
            gap = EvidenceGap(
                gap_id=uuid.uuid4(),
                case_id=case_id,
                title=gap_title,
                description=gap_description,
                status="OPEN",
                created_by_user_id=created_by_user_id,
                created_at_utc=datetime.now(timezone.utc)
            )
            self.db.add(gap)
            self.db.flush()
            gap_id = gap.gap_id
        
        # Generate next request reference
        request_ref = self.request_repo.get_next_request_ref()
        
        # Create request
        request = self.request_repo.create_request(
            request_ref=request_ref,
            case_id=case_id,
            gap_id=gap_id,
            target_party=target_party,
            delivery_channel=delivery_channel,
            reason_text=reason_text,
            due_at_utc=due_at_utc,
            created_by_user_id=created_by_user_id
        )
        
        # Derive blocker state and transition case status to PENDING_INFORMATION
        blocker_state = self.readiness_repo.derive_blocker_state(case_id)
        self.case_repo.update_case_status(
            case_id=case_id,
            status="PENDING_INFORMATION",
            blocker_state=blocker_state
        )
        
        # Emit request creation audit event
        self._emit_audit_event(
            entity_type="REQUEST",
            entity_id=request.request_id,
            action_type="REQUEST_CREATED",
            actor_user_id=created_by_user_id,
            actor_role=actor_role,
            correlation_id=correlation_id,
            details={
                "request_ref": request_ref,
                "case_id": str(case_id),
                "gap_id": str(gap_id),
                "target_party": target_party,
                "due_at_utc": due_at_utc.isoformat(),
                "status": "OPEN"
            }
        )
        
        self.db.commit()
        return request
    
    def record_response(
        self,
        request_id: uuid.UUID,
        response_summary: str,
        received_at_utc: datetime,
        actor_user_id: uuid.UUID,
        actor_role: str,
        correlation_id: str
    ) -> InformationRequest:
        """Record a response to an information request.
        
        Args:
            request_id: Request ID
            response_summary: Summary of the response
            received_at_utc: When the response was received
            actor_user_id: User recording the response
            actor_role: Role of the recording user
            correlation_id: Request correlation ID for audit trail
        
        Returns:
            Updated InformationRequest
        
        Raises:
            ValueError: If request not found
        """
        # Record response
        request = self.request_repo.record_response(
            request_id=request_id,
            response_summary=response_summary,
            received_at_utc=received_at_utc
        )
        
        # Recalculate case blocker state
        blocker_state = self.readiness_repo.derive_blocker_state(request.case_id)
        case = self.case_repo.get_by_id(request.case_id)
        if case:
            self.case_repo.update_case_status(
                case_id=request.case_id,
                status=case.status,
                blocker_state=blocker_state
            )
        
        # Emit response recorded audit event
        self._emit_audit_event(
            entity_type="REQUEST",
            entity_id=request_id,
            action_type="RESPONSE_RECORDED",
            actor_user_id=actor_user_id,
            actor_role=actor_role,
            correlation_id=correlation_id,
            details={
                "request_ref": request.request_ref,
                "case_id": str(request.case_id),
                "status": request.status,
                "response_summary": response_summary[:200],
                "received_at_utc": received_at_utc.isoformat()
            }
        )
        
        self.db.commit()
        return request
    
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
        """Emit an audit event for request operations."""
        import json
        from datetime import timezone
        
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
