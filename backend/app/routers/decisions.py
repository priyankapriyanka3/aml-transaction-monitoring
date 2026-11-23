"""Decision and officer assignment API endpoints."""
import uuid
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.database import get_db
from app.middleware.auth import get_current_active_user
from app.models.user import User
from app.services.decision_service import DecisionService
from app.schemas.decision_schemas import (
    AssignOfficerRequest,
    AssignOfficerResponse,
    ShareForReviewResponse,
    RecordDecisionRequest,
    DecisionResponse,
    OfficerReviewPackage
)

router = APIRouter()


@router.get(
    "/api/v1/cases/{case_id}/officer-review",
    response_model=OfficerReviewPackage,
    status_code=200
)
def get_officer_review(
    case_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get officer review package for a case.
    
    Returns case summary, linked alerts, notes, and rule snapshots.
    Validates current user != case creator.
    
    Args:
        case_id: Case ID
        current_user: Authenticated user
        db: Database session
    
    Returns:
        Officer review package
    
    Raises:
        HTTPException: 403 if user is case creator, 404 if case not found
    """
    try:
        service = DecisionService(db)
        package = service.get_officer_review_package(
            case_id=case_id,
            current_user_id=current_user.user_id
        )
        return package
    except ValueError as e:
        error_msg = str(e)
        if "creator" in error_msg.lower():
            raise HTTPException(status_code=403, detail=error_msg)
        elif "not found" in error_msg.lower():
            raise HTTPException(status_code=404, detail=error_msg)
        else:
            raise HTTPException(status_code=400, detail=error_msg)


@router.post(
    "/api/v1/cases/{case_id}/assign-officer",
    response_model=AssignOfficerResponse,
    status_code=200
)
def assign_officer(
    case_id: uuid.UUID,
    request: AssignOfficerRequest,
    current_user: User = Depends(get_current_active_user),
    x_correlation_id: str = Header(default=""),
    db: Session = Depends(get_db)
):
    """Assign an independent officer to a case for review.
    
    Validates officer != case creator (four-eyes enforcement).
    
    Args:
        case_id: Case ID
        request: Officer assignment request
        current_user: Authenticated user
        x_correlation_id: Correlation ID header
        db: Database session
    
    Returns:
        Officer assignment details
    
    Raises:
        HTTPException: 404 if case not found, 409 if four-eyes violation
    """
    try:
        service = DecisionService(db)
        correlation_id = x_correlation_id or str(uuid.uuid4())
        
        assignment = service.assign_officer(
            case_id=case_id,
            officer_user_id=request.officer_user_id,
            assigned_by_user_id=current_user.user_id,
            assigned_by_role=current_user.role,
            correlation_id=correlation_id
        )
        return assignment
    except ValueError as e:
        error_msg = str(e)
        if "four-eyes" in error_msg.lower():
            raise HTTPException(status_code=409, detail=error_msg)
        elif "not found" in error_msg.lower():
            raise HTTPException(status_code=404, detail=error_msg)
        else:
            raise HTTPException(status_code=400, detail=error_msg)


@router.post(
    "/api/v1/cases/{case_id}/share-for-review",
    response_model=ShareForReviewResponse,
    status_code=200
)
def share_for_review(
    case_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    x_correlation_id: str = Header(default=""),
    db: Session = Depends(get_db)
):
    """Transition case to UNDER_REVIEW status after validation.
    
    Validates:
    - All checklist items complete (alerts linked, notes recorded, requests reviewed)
    - No open or overdue requests
    - Officer assigned
    - Officer != case creator
    
    Args:
        case_id: Case ID
        current_user: Authenticated user
        x_correlation_id: Correlation ID header
        db: Database session
    
    Returns:
        Case status after sharing
    
    Raises:
        HTTPException: 404 if case not found, 409 if validation fails
    """
    try:
        service = DecisionService(db)
        correlation_id = x_correlation_id or str(uuid.uuid4())
        
        response = service.share_for_review(
            case_id=case_id,
            actor_user_id=current_user.user_id,
            actor_role=current_user.role,
            correlation_id=correlation_id
        )
        return response
    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg.lower():
            raise HTTPException(status_code=404, detail=error_msg)
        else:
            raise HTTPException(status_code=409, detail=error_msg)


@router.post(
    "/api/v1/cases/{case_id}/decision",
    response_model=DecisionResponse,
    status_code=201
)
def record_decision(
    case_id: uuid.UUID,
    request: RecordDecisionRequest,
    current_user: User = Depends(get_current_active_user),
    x_correlation_id: str = Header(default=""),
    db: Session = Depends(get_db)
):
    """Record an immutable final decision on a case.
    
    Validates:
    - Current user != case creator (four-eyes enforcement)
    - No open or overdue requests
    - Rationale text is not empty
    
    Args:
        case_id: Case ID
        request: Decision request with outcome and rationale
        current_user: Authenticated user
        x_correlation_id: Correlation ID header
        db: Database session
    
    Returns:
        Decision record with immutable hash
    
    Raises:
        HTTPException: 403 if officer is case creator, 404 if case not found,
                      409 if blockers exist, 422 if rationale missing
    """
    try:
        service = DecisionService(db)
        correlation_id = x_correlation_id or str(uuid.uuid4())
        
        # Get rationale from either field for backward compatibility
        rationale = request.get_rationale()
        
        decision = service.record_decision(
            case_id=case_id,
            deciding_officer_user_id=current_user.user_id,
            deciding_officer_role=current_user.role,
            outcome=request.outcome,
            rationale_text=rationale,
            correlation_id=correlation_id
        )
        return decision
    except ValueError as e:
        error_msg = str(e)
        if "four-eyes" in error_msg.lower() or "own case" in error_msg.lower():
            raise HTTPException(status_code=403, detail=error_msg)
        elif "not found" in error_msg.lower():
            raise HTTPException(status_code=404, detail=error_msg)
        elif "rationale" in error_msg.lower():
            raise HTTPException(status_code=422, detail=error_msg)
        elif "open requests" in error_msg.lower() or "overdue requests" in error_msg.lower():
            raise HTTPException(status_code=409, detail=error_msg)
        else:
            raise HTTPException(status_code=400, detail=error_msg)
