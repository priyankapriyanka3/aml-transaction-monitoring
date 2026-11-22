"""
Alert schemas for request/response validation.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class AlertQueueFilters(BaseModel):
    """Filters for alert queue query"""
    status: str | None = None
    priority: str | None = None
    assignee_id: str | None = None
    risk_score_min: int | None = Field(None, ge=0, le=100)
    risk_score_max: int | None = Field(None, ge=0, le=100)
    generation: str | None = None
    search: str | None = None
    sort_by: str = "priority"
    sort_direction: str = "desc"
    limit: int = Field(20, ge=1, le=100)
    offset: int = Field(0, ge=0)


class AlertResponse(BaseModel):
    """Alert response with enriched data"""
    alert_id: str
    transaction_id: str
    customer_id: str
    status: str
    priority: str
    risk_score: int
    matched_rule_codes_json: str
    generation: str
    assigned_user_id: str | None = None
    assigned_user_name: str | None = None
    triage_outcome: str | None = None
    triage_rationale: str | None = None
    triaged_by_user_id: str | None = None
    triaged_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    customer_name: str | None = None
    transaction_amount: float | None = None
    transaction_currency: str | None = None
    
    model_config = {"from_attributes": True}


class AlertQueueResponse(BaseModel):
    """Paginated alert queue response"""
    items: list[AlertResponse]
    total_count: int
    limit: int
    offset: int


class ClaimRequest(BaseModel):
    """Request to claim or reassign an alert"""
    assignee_user_id: str
    assignment_reason: str


class ClaimResponse(BaseModel):
    """Response after claiming an alert"""
    alert_id: str
    status: str
    assigned_user_id: str
    assigned_user_name: str
    assigned_at: datetime
    assigned_by_user_id: str


class TriageDispositionRequest(BaseModel):
    """Request to save triage disposition"""
    outcome: str = Field(..., description="INVESTIGATE, CLOSE_NON_ACTIONABLE, or MERGE_EXISTING_CASE")
    rationale: str = Field(..., min_length=10, description="Rationale for triage decision, minimum 10 characters")
    existing_case_id: str | None = None


class TriageDispositionResponse(BaseModel):
    """Response after saving triage disposition"""
    alert_id: str
    status: str
    triage_outcome: str
    triage_rationale: str
    triaged_by_user_id: str
    triaged_at: datetime
