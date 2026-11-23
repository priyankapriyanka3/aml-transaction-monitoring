"""Schemas for readiness checklist endpoints."""
import uuid
from pydantic import BaseModel, ConfigDict


class ReadinessChecklistItem(BaseModel):
    """Individual readiness checklist item."""
    
    name: str
    complete: bool
    details: str


class PackageSummary(BaseModel):
    """Package summary counts."""
    
    alert_count: int
    note_count: int
    request_count: int
    evidence_count: int


class EligibleOfficer(BaseModel):
    """Eligible officer for case review assignment."""
    
    user_id: uuid.UUID
    display_name: str
    email: str
    
    model_config = ConfigDict(from_attributes=True)


class ReadinessProjection(BaseModel):
    """Complete readiness checklist projection."""
    
    checklist: list[ReadinessChecklistItem]
    package_summary: PackageSummary
    eligible_officers: list[EligibleOfficer]
    
    model_config = ConfigDict(from_attributes=True)
