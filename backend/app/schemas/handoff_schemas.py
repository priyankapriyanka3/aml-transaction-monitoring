"""
Schemas for handoff package and readiness evaluation.
"""
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ReadinessChecklistItem(BaseModel):
    """Single readiness checklist item"""
    code: str
    label: str
    passed: bool
    detail: str
    
    model_config = ConfigDict(from_attributes=True)


class ReadinessResponse(BaseModel):
    """Readiness evaluation result"""
    is_ready: bool
    checklist_items: list[ReadinessChecklistItem]
    
    model_config = ConfigDict(from_attributes=True)


class LinkedAlertSummary(BaseModel):
    """Summary of linked alert for handoff package"""
    alert_id: str
    priority: str
    risk_score: int
    
    model_config = ConfigDict(from_attributes=True)


class InformationRequestSummary(BaseModel):
    """Summary of information request for handoff package"""
    information_request_id: str
    status: str
    due_at: str
    resolved_at: str | None
    
    model_config = ConfigDict(from_attributes=True)


class HandoffPackageResponse(BaseModel):
    """Complete handoff package for review"""
    case_id: str
    case_number: str
    recommendation_outcome: str | None
    findings_summary: str | None
    linked_alerts: list[LinkedAlertSummary]
    key_evidence_summary: list[str]
    information_request_summary: list[InformationRequestSummary]
    unresolved_issues: list[str]
    readiness: ReadinessResponse
    officer_assignment: dict[str, Any] | None
    
    model_config = ConfigDict(from_attributes=True)


class HandoffSubmitRequest(BaseModel):
    """Request to submit case for officer review"""
    officer_user_id: str = Field(..., description="Officer who will review the case")
    submission_comment: str | None = Field(None, description="Optional comment from investigator")
    
    model_config = ConfigDict(from_attributes=True)


class HandoffSubmitResponse(BaseModel):
    """Response after handoff submission"""
    case_id: str
    status: str
    handoff_submitted_at: str
    handoff_submitted_by_user_id: str
    officer_user_id: str
    readiness_passed: bool
    
    model_config = ConfigDict(from_attributes=True)
