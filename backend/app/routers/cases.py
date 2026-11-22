"""
Cases API router.
Handles case overview retrieval, notes, and status transitions.
"""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..database import get_db
from ..middleware.auth_middleware import get_current_user
from ..models.user import User
from ..schemas.case_schemas import CaseNoteRequest, CaseNoteResponse, CaseOverviewResponse
from ..schemas.evidence_schemas import EvidencePackageResponse
from ..schemas.handoff_schemas import (
    HandoffPackageResponse,
    HandoffSubmitRequest,
    HandoffSubmitResponse,
)
from ..services.case_service import CaseService
from ..services.evidence_service import EvidenceService
from ..services.handoff_service import HandoffService


class StatusTransitionRequest(BaseModel):
    """Request to transition case status"""
    new_status: str = Field(..., pattern="^(INVESTIGATING|PENDING_INFORMATION|REVIEW_READY|SUBMITTED_FOR_REVIEW)$")
    reason: str = Field(default="")
    trigger_event: str = Field(default="")


class RecommendationSubmitRequest(BaseModel):
    """Request to submit investigation recommendation"""
    recommendation_outcome: str = Field(..., pattern="^(SUBSTANTIATE|NO_FURTHER_ACTION|ESCALATE_FOR_REVIEW)$")
    findings_summary: str = Field(..., min_length=50)
    supporting_note_ids: list[str] = Field(default_factory=list)


router = APIRouter(prefix="/api/v1/cases", tags=["cases"])


@router.get("/{case_id}", response_model=CaseOverviewResponse)
def get_case_overview(
    case_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get consolidated case overview with aggregated counts and recent activity.
    
    Returns:
    - Case metadata (status, priority, assignment)
    - Recommendation state
    - Linked alert count
    - Flagged value total from linked transactions
    - Open and overdue information request counts
    - Recent activity timeline from audit events
    """
    case_service = CaseService(db)
    
    try:
        overview = case_service.get_case_overview(case_id)
        return overview
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/{case_id}/notes", response_model=list[CaseNoteResponse])
def get_case_notes(
    case_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all notes for a case in chronological order.
    
    Returns notes from oldest to newest (created_at ASC).
    Each note includes author information and supersession tracking.
    """
    case_service = CaseService(db)
    
    try:
        notes = case_service.list_notes(case_id)
        return notes
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/{case_id}/notes", response_model=CaseNoteResponse, status_code=status.HTTP_201_CREATED)
def create_case_note(
    case_id: str,
    request: CaseNoteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new investigation note for a case.
    
    Validates:
    - body is not empty
    - note_type and stage are provided
    
    Creates INVESTIGATION_NOTE_ADDED audit event.
    """
    case_service = CaseService(db)
    
    try:
        note = case_service.create_note(
            case_id=case_id,
            note_type=request.note_type,
            stage=request.stage,
            body=request.body,
            author_user_id=current_user.user_id
        )
        return note
    except ValueError as e:
        error_msg = str(e)
        if "cannot be empty" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=error_msg
            )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_msg
        )


@router.post("/{case_id}/recommendation", response_model=dict)
def submit_recommendation(
    case_id: str,
    request: RecommendationSubmitRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Submit investigation recommendation for review.
    
    Validates:
    - findings_summary minimum 50 characters
    - At least one linked alert exists
    - No open or overdue information requests
    
    Updates case with recommendation_state=SUBMITTED.
    Creates INVESTIGATION_RECOMMENDATION_SUBMITTED audit event.
    
    Returns 422 for validation failures.
    Returns 409 when readiness prerequisites are incomplete.
    """
    case_service = CaseService(db)
    
    try:
        result = case_service.submit_recommendation(
            case_id=case_id,
            recommendation_outcome=request.recommendation_outcome,
            findings_summary=request.findings_summary,
            actor_id=current_user.user_id
        )
        return result
    except ValueError as e:
        error_msg = str(e)
        if "at least 50 characters" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=error_msg
            )
        if "Cannot submit recommendation" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=error_msg
            )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_msg
        )


@router.get("/{case_id}/evidence-package", response_model=EvidencePackageResponse)
def get_evidence_package(
    case_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get complete evidence package for case review.
    
    Implements FR-011, FR-012, FR-013, FR-015.
    
    Returns:
    - Customer context (FR-011): customer_name, risk_classification, onboarding_profile,
      exposure_indicators, risk_rating from latest risk_profile
    - Account relationships (FR-011): accounts with masked numbers (e.g., GB•• •••• 4821)
    - Transaction timeline (FR-012): transactions sorted by booked_at DESC with transaction_id,
      account_id, counterparty_name, generation_source, linked alert references
    - Rule evaluations (FR-013): historical rule snapshot context with outcomes and explanations
    - Evidence lock flag (FR-015): evidence_locked_for_review indicating reviewer-ready state
    """
    evidence_service = EvidenceService(db)
    
    try:
        package = evidence_service.get_evidence_package(case_id)
        return package
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/{case_id}/handoff", response_model=HandoffPackageResponse)
def get_handoff_package(
    case_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get handoff package for review preview.
    
    Includes:
    - Case details and recommendation
    - Linked alerts summary
    - Key evidence summary
    - Information request summary
    - Unresolved issues
    - Readiness checklist with pass/fail items
    """
    handoff_service = HandoffService(db)
    
    try:
        package = handoff_service.get_handoff_package(case_id)
        return package
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/{case_id}/handoff", response_model=HandoffSubmitResponse)
def submit_handoff(
    case_id: str,
    request: HandoffSubmitRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Submit case for officer review (handoff).
    
    Validates:
    - Four-eyes: officer_user_id != case.created_by_user_id
    - Readiness passed (all checklist items)
    
    Transitions case status to SUBMITTED_FOR_REVIEW.
    Creates CASE_HANDOFF_SUBMITTED audit event.
    
    Returns 409 when readiness_passed=false.
    """
    from ..services.audit_service import AuditService
    from ..services.readiness_service import ReadinessService
    
    case_service = CaseService(db)
    readiness_service = ReadinessService(db)
    audit_service = AuditService(db)
    
    try:
        # Get case
        from ..repositories.case_repository import CaseRepository
        
        case_repo = CaseRepository(db)
        case = case_repo.get_overview(case_id)
        if not case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Case not found"
            )
        
        # Validate four-eyes: officer != creator
        if request.officer_user_id == case.created_by_user_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Four-eyes violation: officer cannot be the case creator"
            )
        
        # Evaluate readiness
        readiness = readiness_service.evaluate_readiness(case_id)
        if not readiness.is_ready:
            failed_items = [item.label for item in readiness.checklist_items if not item.passed]
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Case not ready for handoff. Failed items: {', '.join(failed_items)}"
            )
        
        # Update case with officer assignment
        case.handoff_officer_user_id = request.officer_user_id
        case.updated_at = datetime.now(timezone.utc)
        db.add(case)
        
        # Transition to SUBMITTED_FOR_REVIEW
        now = datetime.now(timezone.utc)
        result = case_service.transition_status(
            case_id=case_id,
            new_status="SUBMITTED_FOR_REVIEW",
            actor_id=current_user.user_id,
            reason="Handoff to officer for review",
            trigger_event="CASE_HANDOFF_SUBMITTED"
        )
        
        # Create CASE_HANDOFF_SUBMITTED audit event
        from ..repositories.user_repository import UserRepository
        
        user_repo = UserRepository(db)
        actor = user_repo.get_by_id(current_user.user_id)
        
        audit_service.create_event(
            entity_type="case",
            entity_id=case_id,
            action_type="CASE_HANDOFF_SUBMITTED",
            actor_user_id=current_user.user_id,
            actor_role=actor.primary_role if actor else "unknown",
            payload={
                "officer_user_id": request.officer_user_id,
                "submission_comment": request.submission_comment,
                "readiness_passed": True,
                "submitted_at": now.isoformat()
            }
        )
        
        db.commit()
        
        return HandoffSubmitResponse(
            case_id=case_id,
            status="SUBMITTED_FOR_REVIEW",
            handoff_submitted_at=now.isoformat(),
            handoff_submitted_by_user_id=current_user.user_id,
            officer_user_id=request.officer_user_id,
            readiness_passed=True
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/{case_id}/status-transitions", response_model=dict)
def transition_case_status(
    case_id: str,
    request: StatusTransitionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Transition case to a new status with state machine validation.
    
    Valid transitions:
    - INVESTIGATING -> PENDING_INFORMATION (on information request issuance)
    - INVESTIGATING -> REVIEW_READY (on recommendation submission + readiness pass)
    - PENDING_INFORMATION -> INVESTIGATING (on information response received)
    - REVIEW_READY -> SUBMITTED_FOR_REVIEW (on handoff submission)
    
    Returns 409 when transition is invalid for current status.
    Creates CASE_STATUS_CHANGED audit event.
    """
    case_service = CaseService(db)
    
    try:
        result = case_service.transition_status(
            case_id=case_id,
            new_status=request.new_status,
            actor_id=current_user.user_id,
            reason=request.reason,
            trigger_event=request.trigger_event
        )
        return result
    except ValueError as e:
        error_msg = str(e)
        if "Invalid transition" in error_msg or "No valid transitions" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=error_msg
            )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_msg
        )
