"""
Information Requests API router.
Handles information request creation and response recording.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..middleware.auth_middleware import get_current_user
from ..models.user import User
from ..schemas.information_request_schemas import (
    InformationRequestCreateRequest,
    InformationRequestResponse,
    RecordResponseRequest,
)
from ..services.information_request_service import InformationRequestService

router = APIRouter(prefix="/api/v1/information-requests", tags=["information-requests"])


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_information_request(
    request: InformationRequestCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Issue a request for information from a case.
    
    Validates:
    - requested_summary (min 10 chars)
    - rationale (min 10 chars)
    - due_at is a future timestamp
    
    Automatically transitions case status to PENDING_INFORMATION.
    Creates INFORMATION_REQUEST_CREATED audit event.
    
    Returns the created request with case_status_after_create.
    """
    service = InformationRequestService(db)
    
    try:
        info_request, case_status = service.create_request(
            case_id=request.case_id,
            recipient_channel=request.recipient_channel,
            requested_summary=request.requested_summary,
            rationale=request.rationale,
            due_at=request.due_at,
            actor_id=current_user.user_id
        )
        return {
            "information_request_id": info_request.information_request_id,
            "case_id": info_request.case_id,
            "status": info_request.status,
            "due_at": info_request.due_at.isoformat(),
            "created_at": info_request.created_at.isoformat(),
            "case_status_after_create": case_status
        }
    except ValueError as e:
        error_msg = str(e)
        if "must be a future timestamp" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=error_msg
            )
        elif "not found" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_msg
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )


@router.get("", response_model=list[InformationRequestResponse])
def list_information_requests(
    case_id: str = Query(..., description="Case ID to filter by"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all information requests for a case.
    
    Returns requests in chronological order (newest first).
    Includes computed days_remaining and is_overdue fields.
    """
    service = InformationRequestService(db)
    return service.list_requests_for_case(case_id)


@router.post("/{information_request_id}/record-response", response_model=dict)
def record_information_request_response(
    information_request_id: str,
    request: RecordResponseRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Record a response to an information request.
    
    Validates:
    - response_summary (min 10 chars)
    - received_at is not in the future
    - request status is OPEN
    
    Transitions request status to RESPONDED.
    Transitions case status from PENDING_INFORMATION to INVESTIGATING.
    Creates INFORMATION_REQUEST_RESPONSE_RECORDED audit event.
    
    Returns updated request with case_status_after_response.
    """
    service = InformationRequestService(db)
    
    try:
        info_request, case_status = service.record_response(
            information_request_id=information_request_id,
            response_summary=request.response_summary,
            received_at=request.received_at,
            response_channel=request.response_channel,
            actor_id=current_user.user_id
        )
        return {
            "information_request_id": info_request.information_request_id,
            "status": info_request.status,
            "response_received_at": info_request.response_received_at.isoformat() if info_request.response_received_at else None,
            "case_status_after_response": case_status
        }
    except ValueError as e:
        error_msg = str(e)
        if "cannot be in the future" in error_msg or "Cannot record response" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=error_msg
            )
        elif "not found" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_msg
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
