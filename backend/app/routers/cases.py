"""Case and evidence API routes."""
import uuid
from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.middleware.auth import get_current_active_user
from app.models.user import User
from app.schemas.evidence_schemas import AlertEvidenceResponse
from app.schemas.case_schemas import (
    CreateCaseRequest,
    CaseCreatedResponse,
    AddNoteRequest,
    NoteResponse,
    CaseWorkspaceResponse
)
from app.services.evidence_service import EvidenceService
from app.services.case_service import CaseService


router = APIRouter(tags=["cases"])


@router.get("/api/v1/alerts/{alert_id}/evidence", response_model=AlertEvidenceResponse)
def get_alert_evidence(
    alert_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> AlertEvidenceResponse:
    """
    Get alert evidence with transaction, customer, account context, and rule snapshots.
    
    Returns:
        AlertEvidenceResponse with nested transaction facts, customer context,
        account context, and historical rule evaluation snapshots
    
    Raises:
        404: Alert not found
    """
    service = EvidenceService(db)
    
    evidence = service.get_alert_evidence(alert_id)
    
    if not evidence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert {alert_id} not found"
        )
    
    return evidence


@router.post("/api/v1/cases", response_model=CaseCreatedResponse, status_code=status.HTTP_201_CREATED)
def create_case(
    request: CreateCaseRequest,
    current_user: User = Depends(get_current_active_user),
    x_correlation_id: str = Header(..., alias="X-Correlation-ID"),
    db: Session = Depends(get_db),
) -> CaseCreatedResponse:
    """
    Create a new case from an alert.
    
    Creates the case, links the primary alert, and emits audit events for:
    - Case creation (CASE_CREATED)
    - Alert linkage (ALERT_LINKED with is_primary=true)
    
    Args:
        request: Contains alert_id to create case from
        current_user: Authenticated user creating the case
        x_correlation_id: Request correlation ID for audit trail
        db: Database session
    
    Returns:
        CaseCreatedResponse with case_id, case_ref, status, etc.
    
    Raises:
        404: Alert not found
    """
    service = CaseService(db)
    
    try:
        case = service.create_case_from_alert(
            alert_id=request.alert_id,
            created_by_user_id=current_user.user_id,
            actor_role=current_user.role,
            correlation_id=x_correlation_id
        )
        
        return CaseCreatedResponse(
            case_id=case.case_id,
            case_ref=case.case_ref,
            primary_alert_id=case.primary_alert_id,
            created_by_user_id=case.created_by_user_id,
            status=case.status,
            created_at_utc=case.created_at_utc
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


class LinkAlertRequest(BaseModel):
    """Request body for linking additional alert to case."""
    alert_id: uuid.UUID


class LinkAlertResponse(BaseModel):
    """Response for alert link creation."""
    case_alert_link_id: uuid.UUID
    case_id: uuid.UUID
    alert_id: uuid.UUID
    is_primary: bool
    linked_at_utc: str


@router.post("/api/v1/cases/{case_id}/alerts", response_model=LinkAlertResponse, status_code=status.HTTP_201_CREATED)
def link_alert_to_case(
    case_id: uuid.UUID,
    request: LinkAlertRequest,
    current_user: User = Depends(get_current_active_user),
    x_correlation_id: str = Header(..., alias="X-Correlation-ID"),
    db: Session = Depends(get_db),
) -> LinkAlertResponse:
    """
    Link an additional alert to an existing case.
    
    Creates a case_alert_link record with is_primary=False and emits
    an ALERT_LINKED audit event.
    
    Args:
        case_id: Case to link alert to
        request: Contains alert_id to link
        current_user: Authenticated user linking the alert
        x_correlation_id: Request correlation ID for audit trail
        db: Database session
    
    Returns:
        LinkAlertResponse with link details
    
    Raises:
        404: Case or alert not found
        409: Alert already linked to this case
    """
    from app.repositories.case_repository import CaseRepository
    from app.repositories.alert_repository import AlertRepository
    from app.services.audit_service import AuditService
    from app.models.case_alert_link import CaseAlertLink
    from sqlalchemy.exc import IntegrityError
    
    case_repo = CaseRepository(db)
    alert_repo = AlertRepository(db)
    audit_service = AuditService(db)
    
    # Validate case exists
    case = case_repo.get_by_id(case_id)
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case {case_id} not found"
        )
    
    # Validate alert exists
    alert = alert_repo.get_by_id(request.alert_id)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert {request.alert_id} not found"
        )
    
    try:
        # Create link
        link = case_repo.add_alert_link(
            case_id=case_id,
            alert_id=request.alert_id,
            linked_by_user_id=current_user.user_id
        )
        
        # Emit audit event
        audit_service.log_event(
            entity_type="CASE",
            entity_id=case_id,
            action_type="ALERT_LINKED",
            actor_user_id=current_user.user_id,
            actor_role=current_user.role,
            correlation_id=x_correlation_id,
            details={
                "alert_id": str(request.alert_id),
                "case_id": str(case_id),
                "is_primary": False
            }
        )
        
        db.commit()
        
        return LinkAlertResponse(
            case_alert_link_id=link.case_alert_link_id,
            case_id=link.case_id,
            alert_id=link.alert_id,
            is_primary=link.is_primary,
            linked_at_utc=link.linked_at_utc.isoformat()
        )
    
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Alert {request.alert_id} is already linked to case {case_id}"
        )


@router.post("/api/v1/cases/{case_id}/notes", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
def add_note(
    case_id: uuid.UUID,
    request: AddNoteRequest,
    current_user: User = Depends(get_current_active_user),
    x_correlation_id: str = Header(..., alias="X-Correlation-ID"),
    db: Session = Depends(get_db),
) -> NoteResponse:
    """
    Add an investigation note to a case.
    
    Captures author identity from auth context and timestamp.
    Creates NOTE_ADDED audit event.
    
    Args:
        case_id: Case to add note to
        request: Contains note_category and note_text
        current_user: Authenticated user authoring the note
        x_correlation_id: Request correlation ID for audit trail
        db: Database session
    
    Returns:
        NoteResponse with note_id, author_user_id, authored_at_utc, etc.
    
    Raises:
        404: Case not found
    """
    service = CaseService(db)
    
    try:
        note = service.add_note(
            case_id=case_id,
            note_category=request.note_category,
            note_text=request.note_text,
            author_user_id=current_user.user_id,
            actor_role=current_user.role,
            correlation_id=x_correlation_id
        )
        
        return NoteResponse(
            note_id=note.note_id,
            case_id=note.case_id,
            note_category=note.note_category,
            note_text=note.note_text,
            author_user_id=note.author_user_id,
            authored_at_utc=note.authored_at_utc
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/api/v1/cases/{case_id}/workspace", response_model=CaseWorkspaceResponse)
def get_case_workspace(
    case_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> CaseWorkspaceResponse:
    """
    Get complete case workspace with progress restoration capability.
    
    Returns:
        CaseWorkspaceResponse aggregating:
        - Case metadata (case_ref, status, blocker_state, timestamps)
        - Linked alerts array (with is_primary flag)
        - Notes array ordered by authored_at_utc DESC
        - Evidence gaps array
        - Timeline entries array (audit events ordered by occurred_at_utc DESC)
        
        All arrays use {items: [...], total: N} structure.
    
    Raises:
        404: Case not found
    """
    from app.repositories.case_repository import CaseRepository
    
    case_repo = CaseRepository(db)
    workspace = case_repo.get_workspace_data(case_id)
    
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case {case_id} not found"
        )
    
    return CaseWorkspaceResponse(**workspace)
