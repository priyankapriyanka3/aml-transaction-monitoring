"""Schemas for officer review and decision recording."""
import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class AlertSummaryItem(BaseModel):
    """Alert summary in officer review package."""
    
    alert_id: uuid.UUID
    alert_ref: str
    priority: str
    risk_score: int
    is_primary: bool
    linked_at_utc: datetime
    
    model_config = ConfigDict(from_attributes=True)


class NoteSummaryItem(BaseModel):
    """Note summary in officer review package."""
    
    note_id: uuid.UUID
    note_category: str
    note_text: str
    author_user_id: uuid.UUID
    authored_at_utc: datetime
    
    model_config = ConfigDict(from_attributes=True)


class RequestSummaryItem(BaseModel):
    """Information request summary in officer review package."""
    
    request_id: uuid.UUID
    request_ref: str
    status: str
    target_party: str
    reason_text: str
    due_at_utc: datetime
    response_summary: str | None
    response_received_at_utc: datetime | None
    
    model_config = ConfigDict(from_attributes=True)


class RuleSnapshotSummaryItem(BaseModel):
    """Rule snapshot summary in officer review package."""
    
    snapshot_id: uuid.UUID
    rule_code: str
    rule_name: str
    rule_version: str
    outcome: str
    condition_text: str
    
    model_config = ConfigDict(from_attributes=True)


class OfficerReviewPackageResponse(BaseModel):
    """Complete officer review package with blocker state."""
    
    # Case summary
    case_id: uuid.UUID
    case_ref: str
    status: str
    current_blocker_state: str
    created_by_user_id: uuid.UUID
    assigned_officer_user_id: uuid.UUID | None
    created_at_utc: datetime
    updated_at_utc: datetime
    
    # Aggregated arrays
    linked_alerts: list[AlertSummaryItem]
    notes: list[NoteSummaryItem]
    requests: list[RequestSummaryItem]
    rule_snapshots: list[RuleSnapshotSummaryItem]
    
    # Blocker state (includes conflicted officer check)
    blocker_state: str  # NONE, OPEN_REQUESTS, OVERDUE_REQUESTS, or combination
    is_conflicted_officer: bool  # True if current user is case creator
    
    model_config = ConfigDict(from_attributes=True)


class RecordDecisionRequest(BaseModel):
    """Request to record a final officer decision."""
    
    outcome: str = Field(
        ...,
        description="Decision outcome: APPROVE, REJECT, ESCALATE, or FALSE_POSITIVE"
    )
    rationale: str = Field(..., description="Mandatory rationale text")


class DecisionRecordedResponse(BaseModel):
    """Response after decision recorded."""
    
    decision_id: uuid.UUID
    case_id: uuid.UUID
    outcome: str
    rationale: str
    deciding_officer_user_id: uuid.UUID
    recorded_at_utc: datetime
    immutable_hash: str
    
    model_config = ConfigDict(from_attributes=True)
