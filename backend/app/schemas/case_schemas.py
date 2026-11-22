"""
Case-related request and response schemas.
Supports case creation from alerts and case overview retrieval.
"""
from datetime import datetime

from pydantic import BaseModel, Field


class CreateCaseFromAlertRequest(BaseModel):
    """Request to create a case from an alert"""
    case_priority: str = Field(..., description="Case priority level")
    initial_rationale: str = Field(..., description="Initial reason for case creation")


class CreateCaseFromAlertResponse(BaseModel):
    """Response from creating a case from an alert"""
    case_id: str
    case_number: str
    source_alert_id: str
    status: str
    created_at: str


class CaseOverviewResponse(BaseModel):
    """Complete case overview with aggregated counts and recent activity"""
    case_id: str
    case_number: str
    status: str
    priority: str
    assigned_user_id: str | None = None
    assigned_user_name: str | None = None
    recommendation_state: str
    recommendation_outcome: str | None = None
    flagged_value_total: float
    currency: str
    linked_alert_count: int
    open_information_request_count: int
    overdue_information_request_count: int
    recent_activity: list[dict]
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class CaseNoteRequest(BaseModel):
    """Request to create a case note"""
    note_type: str = Field(..., description="Type of note (e.g., INVESTIGATION, DECISION)")
    stage: str = Field(..., description="Investigation stage")
    body: str = Field(..., description="Note content")


class CaseNoteResponse(BaseModel):
    """Case note response"""
    note_id: str
    case_id: str
    note_type: str
    stage: str
    body: str
    author_user_id: str
    author_display_name: str | None = None
    created_at: datetime
    superseded_by_note_id: str | None = None
    
    model_config = {"from_attributes": True}
