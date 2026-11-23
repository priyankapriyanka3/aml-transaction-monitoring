"""Information request API endpoints."""
import uuid
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.database import get_db
from app.middleware.auth import get_current_active_user
from app.models.user import User
from app.services.information_request_service import InformationRequestService
from app.repositories.readiness_repository import ReadinessRepository
from app.schemas.case_schemas import CreateInformationRequestRequest, InformationRequestResponse
from app.schemas.request_schemas import (
    RecordResponseRequest,
    RecordResponseResponse,
    InformationRequestDetail
)

router = APIRouter()


@router.post(
    "/api/v1/cases/{case_id}/requests",
    response_model=InformationRequestResponse,
    status_code=201
)
def create_information_request(
    case_id: uuid.UUID,
    request: CreateInformationRequestRequest,
    current_user: User = Depends(get_current_active_user),
    x_correlation_id: str | None = Header(None),
    db: Session = Depends(get_db)
):
    """Create a new information request for missing evidence.
    
    Args:
        case_id: Case ID
        request: Request body with gap details
        current_user: Authenticated user
        x_correlation_id: Correlation ID for audit trail
        db: Database session
    
    Returns:
        Created information request
    
    Raises:
        HTTPException: 404 if case not found, 400 for validation errors
    """
    correlation_id = x_correlation_id or str(uuid.uuid4())
    
    try:
        service = InformationRequestService(db)
        information_request = service.create_request(
            case_id=case_id,
            gap_id=request.gap_id,
            gap_title=request.gap_title,
            gap_description=request.gap_description,
            target_party=request.target_party,
            delivery_channel=request.delivery_channel,
            reason_text=request.reason_text,
            due_at_utc=request.due_at_utc,
            created_by_user_id=current_user.user_id,
            actor_role=current_user.role,
            correlation_id=correlation_id
        )
        
        return InformationRequestResponse(
            request_id=information_request.request_id,
            request_ref=information_request.request_ref,
            case_id=information_request.case_id,
            gap_id=information_request.gap_id,
            target_party=information_request.target_party,
            delivery_channel=information_request.delivery_channel,
            reason_text=information_request.reason_text,
            due_at_utc=information_request.due_at_utc,
            status=information_request.status,
            created_by_user_id=information_request.created_by_user_id,
            created_at_utc=information_request.created_at_utc
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get(
    "/api/v1/cases/{case_id}/requests/{request_id}",
    response_model=InformationRequestDetail
)
def get_information_request(
    case_id: uuid.UUID,
    request_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get information request details including blocker state.
    
    Args:
        case_id: Case ID
        request_id: Request ID
        current_user: Authenticated user
        db: Database session
    
    Returns:
        Information request details with blocker state
    
    Raises:
        HTTPException: 404 if request not found
    """
    service = InformationRequestService(db)
    request_obj = service.request_repo.get_by_id(request_id)
    
    if not request_obj:
        raise HTTPException(status_code=404, detail=f"Request {request_id} not found")
    
    if request_obj.case_id != case_id:
        raise HTTPException(status_code=404, detail=f"Request {request_id} not found in case {case_id}")
    
    # Derive blocker state for the case
    readiness_repo = ReadinessRepository(db)
    blocker_state = readiness_repo.derive_blocker_state(case_id)
    
    return InformationRequestDetail(
        request_id=request_obj.request_id,
        request_ref=request_obj.request_ref,
        case_id=request_obj.case_id,
        gap_id=request_obj.gap_id,
        target_party=request_obj.target_party,
        delivery_channel=request_obj.delivery_channel,
        reason_text=request_obj.reason_text,
        due_at_utc=request_obj.due_at_utc,
        status=request_obj.status,
        created_by_user_id=request_obj.created_by_user_id,
        response_summary=request_obj.response_summary,
        response_received_at_utc=request_obj.response_received_at_utc,
        created_at_utc=request_obj.created_at_utc,
        updated_at_utc=request_obj.updated_at_utc,
        blocker_state=blocker_state
    )


@router.post(
    "/api/v1/cases/{case_id}/requests/{request_id}/response",
    response_model=RecordResponseResponse
)
def record_information_response(
    case_id: uuid.UUID,
    request_id: uuid.UUID,
    request: RecordResponseRequest,
    current_user: User = Depends(get_current_active_user),
    x_correlation_id: str | None = Header(None),
    db: Session = Depends(get_db)
):
    """Record a response to an information request.
    
    Args:
        case_id: Case ID
        request_id: Request ID
        request: Response details
        current_user: Authenticated user
        x_correlation_id: Correlation ID for audit trail
        db: Database session
    
    Returns:
        Updated information request
    
    Raises:
        HTTPException: 404 if request not found, 422 for validation errors
    """
    correlation_id = x_correlation_id or str(uuid.uuid4())
    
    # Validate required fields
    if not request.response_summary or not request.response_summary.strip():
        raise HTTPException(status_code=422, detail="Response summary is required")
    
    if not request.received_at_utc:
        raise HTTPException(status_code=422, detail="Received date is required")
    
    try:
        service = InformationRequestService(db)
        information_request = service.record_response(
            request_id=request_id,
            response_summary=request.response_summary,
            received_at_utc=request.received_at_utc,
            actor_user_id=current_user.user_id,
            actor_role=current_user.role,
            correlation_id=correlation_id
        )
        
        return RecordResponseResponse(
            request_id=information_request.request_id,
            status=information_request.status,
            response_summary=information_request.response_summary or "",
            response_received_at_utc=information_request.response_received_at_utc or information_request.updated_at_utc
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
