"""Readiness checklist API endpoints."""
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.middleware.auth import get_current_active_user
from app.models.user import User
from app.services.readiness_service import ReadinessService
from app.schemas.readiness_schemas import ReadinessProjection

router = APIRouter()


@router.get(
    "/api/v1/cases/{case_id}/readiness",
    response_model=ReadinessProjection
)
def get_case_readiness(
    case_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get readiness checklist and package summary for a case.
    
    Checklist items:
    1. linked_evidence - complete if >= 1 linked alert
    2. investigation_notes - complete if >= 1 note
    3. responses_reviewed - complete if all requests status != OPEN
    4. no_open_requests - complete if no requests with status OPEN or OVERDUE
    
    Args:
        case_id: Case ID
        current_user: Authenticated user
        db: Database session
    
    Returns:
        Readiness checklist with package summary
    
    Raises:
        HTTPException: 404 if case not found
    """
    try:
        service = ReadinessService(db)
        readiness = service.derive_checklist(case_id)
        return readiness
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
