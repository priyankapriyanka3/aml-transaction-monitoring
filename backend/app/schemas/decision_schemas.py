"""Schemas for decision and officer assignment endpoints."""
import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, model_serializer
from typing import Any


class AssignOfficerRequest(BaseModel):
    """Request schema for officer assignment."""
    
    officer_user_id: uuid.UUID


class AssignOfficerResponse(BaseModel):
    """Response schema for officer assignment."""
    
    assignment_id: uuid.UUID
    case_id: uuid.UUID
    officer_user_id: uuid.UUID
    assigned_by_user_id: uuid.UUID
    assigned_at_utc: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ShareForReviewResponse(BaseModel):
    """Response schema for share-for-review action."""
    
    case_id: uuid.UUID
    status: str
    shared_at_utc: datetime


class RecordDecisionRequest(BaseModel):
    """Request schema for decision recording."""
    
    outcome: str  # APPROVE, REJECT, ESCALATE, FALSE_POSITIVE
    rationale_text: str | None = None
    rationale: str | None = None  # Backward compatibility
    
    def get_rationale(self) -> str:
        """Get rationale from either field for backward compatibility."""
        return self.rationale_text or self.rationale or ""


class DecisionResponse(BaseModel):
    """Response schema for decision recording."""
    
    decision_id: uuid.UUID
    case_id: uuid.UUID
    deciding_officer_user_id: uuid.UUID
    outcome: str
    rationale_text: str
    recorded_at_utc: datetime
    immutable_hash: str
    
    model_config = ConfigDict(from_attributes=True)
    
    @model_serializer
    def serialize_model(self) -> dict[str, Any]:
        """Add backward compatibility field 'rationale' as alias for 'rationale_text'."""
        return {
            "decision_id": self.decision_id,
            "case_id": self.case_id,
            "deciding_officer_user_id": self.deciding_officer_user_id,
            "outcome": self.outcome,
            "rationale_text": self.rationale_text,
            "rationale": self.rationale_text,  # Backward compatibility
            "recorded_at_utc": self.recorded_at_utc,
            "immutable_hash": self.immutable_hash
        }


class OfficerReviewLinkedAlert(BaseModel):
    """Linked alert in officer review package."""
    
    alert_id: uuid.UUID
    alert_ref: str
    is_primary: bool
    
    model_config = ConfigDict(from_attributes=True)


class OfficerReviewNote(BaseModel):
    """Note in officer review package."""
    
    note_id: uuid.UUID
    note_text: str
    author_user_id: uuid.UUID
    authored_at_utc: datetime
    
    model_config = ConfigDict(from_attributes=True)


class OfficerReviewRuleSnapshot(BaseModel):
    """Rule snapshot in officer review package."""
    
    snapshot_id: uuid.UUID
    rule_name: str
    rule_version: str
    outcome: str
    
    model_config = ConfigDict(from_attributes=True)


class OfficerReviewPackage(BaseModel):
    """Officer review package response."""
    
    case_id: uuid.UUID
    case_ref: str
    status: str
    blocker_state: str
    is_conflicted_officer: bool
    linked_alerts: list[OfficerReviewLinkedAlert]
    notes: list[OfficerReviewNote]
    rule_snapshots: list[OfficerReviewRuleSnapshot]
