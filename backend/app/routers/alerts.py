"""Alert API routes."""
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.orm import Session
from app.database import get_db
from app.middleware.auth import get_current_active_user
from app.models.user import User
from app.schemas.alert_schemas import (
    AlertQueueResponse,
    AlertAssignmentRequest,
    AlertAssignmentResponse,
    ErrorResponse,
)
from app.services.alert_service import AlertService


router = APIRouter(prefix="/api/v1/alerts", tags=["alerts"])


@router.get("", response_model=AlertQueueResponse)
def get_alert_queue(
    priority: str | None = Query(None, description="Filter by priority: Critical, High, Medium, Low"),
    ownership: str | None = Query(None, description="Filter by ownership: All, Unassigned, Assigned to Me"),
    status: str | None = Query(None, description="Filter by status: New, Under Review, Escalated, Resolved"),
    search: str | None = Query(None, description="Search by alert ID or customer name"),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> AlertQueueResponse:
    """
    Get prioritized alert queue with filtering, search, and pagination.
    
    Default ordering: risk_score DESC, triggered_at_utc DESC
    """
    service = AlertService(db)
    
    items, total = service.get_alert_queue(
        priority=priority,
        ownership=ownership,
        status=status,
        search=search,
        page=page,
        page_size=page_size,
        current_user_id=current_user.user_id,
    )
    
    return AlertQueueResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("/{alert_id}/assign", response_model=AlertAssignmentResponse)
def assign_alert(
    alert_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    x_correlation_id: str = Header(..., alias="X-Correlation-ID"),
    db: Session = Depends(get_db),
) -> AlertAssignmentResponse:
    """
    Assign alert to current user.
    
    Returns 409 if alert already assigned to another user.
    """
    service = AlertService(db)
    
    try:
        result = service.assign_alert(
            alert_id=alert_id,
            user_id=current_user.user_id,
            user_role=current_user.role,
            correlation_id=x_correlation_id,
        )
        return AlertAssignmentResponse(**result)
    except ValueError as e:
        if "already assigned" in str(e):
            raise HTTPException(status_code=409, detail=str(e))
        raise HTTPException(status_code=404, detail=str(e))
