"""Pydantic schemas for alert endpoints."""
import uuid
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict


class AlertQueueItem(BaseModel):
    """Alert queue item response DTO."""
    
    alert_id: uuid.UUID
    alert_ref: str
    priority: str
    risk_score: int
    status: str
    owner_user_id: uuid.UUID | None
    triggered_at_utc: datetime
    transaction_amount: Decimal
    transaction_currency_code: str
    source_country_code: str
    destination_country_code: str
    customer_id: uuid.UUID
    customer_name: str
    
    model_config = ConfigDict(from_attributes=True)


class AlertQueueResponse(BaseModel):
    """Paginated alert queue response."""
    
    items: list[AlertQueueItem]
    total: int
    page: int
    page_size: int


class AlertAssignmentRequest(BaseModel):
    """Alert assignment request (empty - user from auth context)."""
    
    pass


class AlertAssignmentResponse(BaseModel):
    """Alert assignment response."""
    
    alert_id: uuid.UUID
    owner_user_id: uuid.UUID
    assigned_at_utc: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ErrorResponse(BaseModel):
    """Standard error response."""
    
    detail: str
