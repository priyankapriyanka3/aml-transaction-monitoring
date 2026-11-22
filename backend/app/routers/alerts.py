from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..middleware.auth_middleware import get_current_user
from ..models.user import User
from ..schemas.alert_schemas import (
    AlertQueueResponse,
    ClaimRequest,
    ClaimResponse,
    TriageDispositionRequest,
    TriageDispositionResponse,
)
from ..schemas.case_schemas import CreateCaseFromAlertRequest, CreateCaseFromAlertResponse
from ..services.alert_service import AlertService
from ..services.case_service import CaseService

router = APIRouter(prefix="/api/v1/alerts", tags=["alerts"])


@router.get("", response_model=AlertQueueResponse)
def get_alert_queue(
    status: str | None = Query(None),
    priority: str | None = Query(None),
    assignee_id: str | None = Query(None),
    risk_score_min: int | None = Query(None, ge=0, le=100),
    risk_score_max: int | None = Query(None, ge=0, le=100),
    generation: str | None = Query(None),
    search: str | None = Query(None),
    sort_by: str = Query("priority"),
    sort_direction: str = Query("desc"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get paginated alert queue with filtering and sorting.
    Supports filtering by status, priority, assignee, risk score, and generation.
    """
    alert_service = AlertService(db)
    
    alerts, total_count = alert_service.get_queue(
        status=status,
        priority=priority,
        assignee_id=assignee_id,
        risk_score_min=risk_score_min,
        risk_score_max=risk_score_max,
        generation=generation,
        search=search,
        sort_by=sort_by,
        sort_direction=sort_direction,
        limit=limit,
        offset=offset
    )
    
    return AlertQueueResponse(
        items=alerts,
        total_count=total_count,
        limit=limit,
        offset=offset
    )


@router.post("/{alert_id}/claim", response_model=ClaimResponse)
def claim_alert(
    alert_id: str,
    request: ClaimRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Claim or reassign an alert.
    Creates an audit event for the assignment change.
    """
    alert_service = AlertService(db)
    
    try:
        alert_response, assigned_user_name = alert_service.claim_alert(
            alert_id=alert_id,
            assignee_user_id=request.assignee_user_id,
            assigned_by_user_id=current_user.user_id,
            assignment_reason=request.assignment_reason
        )
        
        return ClaimResponse(
            alert_id=alert_id,
            status=alert_response.status,
            assigned_user_id=request.assignee_user_id,
            assigned_user_name=assigned_user_name,
            assigned_at=datetime.now(timezone.utc),
            assigned_by_user_id=str(current_user.user_id)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/{alert_id}/triage-disposition", response_model=TriageDispositionResponse)
def save_triage_disposition(
    alert_id: str,
    request: TriageDispositionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Save triage disposition with mandatory rationale.
    
    Validates:
    - Rationale minimum 10 characters
    - Outcome is valid
    - existing_case_id provided when needed
    
    Updates alert status based on outcome:
    - INVESTIGATE: keeps current status
    - CLOSE_NON_ACTIONABLE: status -> CLOSED_NON_ACTIONABLE
    - MERGE_EXISTING_CASE: status -> MERGED_INTO_EXISTING_CASE
    
    Creates ALERT_TRIAGE_RECORDED audit event.
    """
    alert_service = AlertService(db)
    
    try:
        alert_response = alert_service.save_triage_disposition(
            alert_id=alert_id,
            outcome=request.outcome,
            rationale=request.rationale,
            actor_id=current_user.user_id,
            existing_case_id=request.existing_case_id
        )
        
        return TriageDispositionResponse(
            alert_id=alert_id,
            status=alert_response.status,
            triage_outcome=alert_response.triage_outcome or request.outcome,
            triage_rationale=alert_response.triage_rationale or request.rationale,
            triaged_by_user_id=str(current_user.user_id),
            triaged_at=alert_response.triaged_at or datetime.now(timezone.utc)
        )
    except ValueError as e:
        error_msg = str(e)
        if "at least 10 characters" in error_msg or "Invalid outcome" in error_msg or "existing_case_id" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=error_msg
            )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_msg
        )


@router.post("/{alert_id}/cases", response_model=CreateCaseFromAlertResponse)
def create_case_from_alert(
    alert_id: str,
    request: CreateCaseFromAlertRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a case from an alert.
    
    Transactionally:
    1. Creates case
    2. Links alert to case
    3. Updates alert status to ESCALATED_TO_CASE
    4. Creates CASE_CREATED and ALERT_LINKED_TO_CASE audit events
    
    Returns case_id and case_number.
    """
    case_service = CaseService(db)
    
    try:
        case_id, case_number = case_service.create_case_from_alert(
            alert_id=alert_id,
            case_priority=request.case_priority,
            initial_rationale=request.initial_rationale,
            actor_id=current_user.user_id
        )
        
        return {
            "case_id": case_id,
            "case_number": case_number,
            "source_alert_id": alert_id,
            "status": "INVESTIGATING",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
