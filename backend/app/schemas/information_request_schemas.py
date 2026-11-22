"""
Information request request and response schemas.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class InformationRequestCreateRequest(BaseModel):
    """Request to create an information request"""
    case_id: str = Field(..., min_length=1)
    recipient_channel: str = Field(..., pattern="^(EMAIL|PORTAL|OPERATIONS_QUEUE)$")
    requested_summary: str = Field(..., min_length=10)
    rationale: str = Field(..., min_length=10)
    due_at: datetime = Field(...)
    
    @field_validator("requested_summary", "rationale")
    @classmethod
    def validate_not_blank(cls, v: str) -> str:
        if not v or len(v.strip()) < 10:
            raise ValueError("Must be at least 10 characters")
        return v


class InformationRequestResponse(BaseModel):
    """Response for information request"""
    information_request_id: str
    case_id: str
    recipient_channel: str
    requested_summary: str
    rationale: str
    status: str
    due_at: datetime
    days_remaining: Optional[int] = None
    is_overdue: bool
    response_summary: Optional[str] = None
    response_channel: Optional[str] = None
    response_received_at: Optional[datetime] = None
    created_by_user_id: str
    created_at: datetime
    
    model_config = {"from_attributes": True}


class RecordResponseRequest(BaseModel):
    """Request to record a response to an information request"""
    response_summary: str = Field(..., min_length=10)
    received_at: datetime = Field(...)
    response_channel: str = Field(..., pattern="^(EMAIL|PORTAL|OPERATIONS_QUEUE|PHONE|FAX|OTHER)$")
    
    @field_validator("response_summary")
    @classmethod
    def validate_response_not_blank(cls, v: str) -> str:
        if not v or len(v.strip()) < 10:
            raise ValueError("Response summary must be at least 10 characters")
        return v
