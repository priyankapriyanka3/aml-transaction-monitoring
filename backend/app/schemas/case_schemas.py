"""Schemas for case creation and management."""
import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class CreateCaseRequest(BaseModel):
    """Request to create a new case from an alert."""
    
    alert_id: uuid.UUID = Field(..., description="Primary alert ID to create case from")


class CaseCreatedResponse(BaseModel):
    """Response after successful case creation."""
    
    case_id: uuid.UUID
    case_ref: str
    primary_alert_id: uuid.UUID
    created_by_user_id: uuid.UUID
    status: str
    created_at_utc: datetime
    
    model_config = ConfigDict(from_attributes=True)


class AddNoteRequest(BaseModel):
    """Request to add an investigation note to a case."""
    
    note_category: str = Field(..., description="Note category: investigation, recommendation, information_request, response, closure")
    note_text: str = Field(..., description="Note content")


class CreateInformationRequestRequest(BaseModel):
    """Request to create an information request."""
    
    gap_id: uuid.UUID | None = Field(None, description="Evidence gap ID (if already exists)")
    gap_title: str | None = Field(None, description="Title for new evidence gap (if creating)")
    gap_description: str | None = Field(None, description="Description for new evidence gap (if creating)")
    target_party: str = Field(..., description="Target party for the request")
    delivery_channel: str = Field(..., description="Delivery channel")
    reason_text: str = Field(..., description="Reason for the request")
    due_at_utc: datetime = Field(..., description="Due date for the request")


class InformationRequestResponse(BaseModel):
    """Response for information request creation."""
    
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
    created_at_utc: datetime
    
    model_config = ConfigDict(from_attributes=True)


class NoteResponse(BaseModel):
    """Response for note creation."""
    
    note_id: uuid.UUID
    case_id: uuid.UUID
    note_category: str
    note_text: str
    author_user_id: uuid.UUID
    authored_at_utc: datetime
    
    model_config = ConfigDict(from_attributes=True)


class LinkedAlertItem(BaseModel):
    """Linked alert item in case workspace."""
    
    alert_id: uuid.UUID
    alert_ref: str
    is_primary: bool
    linked_at_utc: datetime
    
    model_config = ConfigDict(from_attributes=True)


class NoteItem(BaseModel):
    """Note item in case workspace."""
    
    note_id: uuid.UUID
    note_category: str
    note_text: str
    author_user_id: uuid.UUID
    authored_at_utc: datetime
    
    model_config = ConfigDict(from_attributes=True)


class EvidenceGapItem(BaseModel):
    """Evidence gap item in case workspace."""
    
    gap_id: uuid.UUID
    gap_description: str
    status: str
    created_at_utc: datetime
    
    model_config = ConfigDict(from_attributes=True)


class TimelineEntryItem(BaseModel):
    """Timeline entry item in case workspace."""
    
    event_id: uuid.UUID
    action_type: str
    actor_user_id: uuid.UUID
    occurred_at_utc: datetime
    details_json: str
    
    model_config = ConfigDict(from_attributes=True)


class CaseWorkspaceResponse(BaseModel):
    """Complete case workspace with progress restoration capability."""
    
    case_id: uuid.UUID
    case_ref: str
    status: str
    current_blocker_state: str
    created_by_user_id: uuid.UUID
    assigned_officer_user_id: uuid.UUID | None
    created_at_utc: datetime
    updated_at_utc: datetime
    
    # Aggregated arrays with {items, total} structure
    linked_alerts: dict[str, list[LinkedAlertItem] | int]  # {items: [...], total: N}
    notes: dict[str, list[NoteItem] | int]  # {items: [...], total: N}
    evidence_gaps: dict[str, list[EvidenceGapItem] | int]  # {items: [...], total: N}
    timeline_entries: dict[str, list[TimelineEntryItem] | int]  # {items: [...], total: N}
    
    model_config = ConfigDict(from_attributes=True)
