"""Repository for information request operations."""
import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.information_request import InformationRequest


class InformationRequestRepository:
    """Repository for managing information request persistence."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_request(
        self,
        request_ref: str,
        case_id: uuid.UUID,
        gap_id: uuid.UUID,
        target_party: str,
        delivery_channel: str,
        reason_text: str,
        due_at_utc: datetime,
        created_by_user_id: uuid.UUID
    ) -> InformationRequest:
        """Create a new information request.
        
        Args:
            request_ref: Unique request reference (e.g., "IR-012")
            case_id: Case ID
            gap_id: Evidence gap ID
            target_party: Target party for the request
            delivery_channel: Delivery channel
            reason_text: Reason for the request
            due_at_utc: Due date
            created_by_user_id: User creating the request
        
        Returns:
            Created InformationRequest
        """
        now = datetime.now(timezone.utc)
        
        request = InformationRequest(
            request_ref=request_ref,
            case_id=case_id,
            gap_id=gap_id,
            target_party=target_party,
            delivery_channel=delivery_channel,
            reason_text=reason_text,
            due_at_utc=due_at_utc,
            status="OPEN",
            created_by_user_id=created_by_user_id,
            created_at_utc=now,
            updated_at_utc=now
        )
        
        self.db.add(request)
        self.db.flush()
        return request
    
    def get_next_request_ref(self) -> str:
        """Generate the next sequential request reference.
        
        Returns:
            Next request reference (e.g., "IR-001", "IR-002", etc.)
        """
        # Query the highest existing request number
        result = self.db.query(InformationRequest.request_ref).order_by(
            InformationRequest.request_ref.desc()
        ).first()
        
        if result and result[0]:
            # Extract the numeric part from "IR-XXX"
            try:
                last_num = int(result[0].split("-")[1])
                next_num = last_num + 1
            except (IndexError, ValueError):
                # Fallback to 1 if parsing fails
                next_num = 1
        else:
            next_num = 1
        
        return f"IR-{next_num:03d}"
    
    def get_by_id(self, request_id: uuid.UUID) -> InformationRequest | None:
        """Get information request by ID.
        
        Args:
            request_id: Request ID
        
        Returns:
            InformationRequest or None if not found
        """
        return self.db.query(InformationRequest).filter(
            InformationRequest.request_id == request_id
        ).first()
    
    def record_response(
        self,
        request_id: uuid.UUID,
        response_summary: str,
        received_at_utc: datetime
    ) -> InformationRequest:
        """Record a response to an information request.
        
        Args:
            request_id: Request ID
            response_summary: Summary of the response
            received_at_utc: When the response was received
        
        Returns:
            Updated InformationRequest
        
        Raises:
            ValueError: If request not found
        """
        request = self.get_by_id(request_id)
        if not request:
            raise ValueError(f"Request {request_id} not found")
        
        request.response_summary = response_summary
        request.response_received_at_utc = received_at_utc
        request.status = "RESPONDED"
        request.updated_at_utc = datetime.now(timezone.utc)
        
        self.db.flush()
        return request
