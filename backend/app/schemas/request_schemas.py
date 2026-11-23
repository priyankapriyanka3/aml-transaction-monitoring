"""Schemas for information request endpoints."""
import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class RecordResponseRequest(BaseModel):
    """Request body for recording an information request response."""
    
    response_summary: str = Field(..., min_length=1, description="Summary of the response received")
    received_at_utc: datetime = Field(..., description="When the response was received (UTC)")


class InformationRequestDetail(BaseModel):
    """Detailed information request projection."""
    
    request_id: uuid.UUID
    request_ref: str
    case_id: uuid.UUID
    gap_id: uuid.UUID
    target_party: str
    delivery_channel: str
    reason_text: str
    due_at_utc: datetime
    status: str
    created_by_user_id: uuid.UUID
    response_summary: str | None
    response_received_at_utc: datetime | None
    created_at_utc: datetime
    updated_at_utc: datetime
    blocker_state: str
    
    model_config = ConfigDict(from_attributes=True)


class RecordResponseResponse(BaseModel):
    """Response for recording an information request response."""
    
    request_id: uuid.UUID
    status: str
    response_summary: str
    response_received_at_utc: datetime
    
    model_config = ConfigDict(from_attributes=True)
