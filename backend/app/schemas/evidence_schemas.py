"""Schemas for alert evidence read models."""
import uuid
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict


class TransactionFactsView(BaseModel):
    """Transaction facts nested in evidence response."""
    
    transaction_id: uuid.UUID
    transaction_ref: str
    amount: Decimal
    currency_code: str
    source_country_code: str
    destination_country_code: str
    executed_at_utc: datetime
    
    model_config = ConfigDict(from_attributes=True)


class CustomerContextView(BaseModel):
    """Customer context nested in evidence response."""
    
    customer_id: uuid.UUID
    customer_name: str
    pep_flag: bool
    country_code: str
    
    model_config = ConfigDict(from_attributes=True)


class AccountContextView(BaseModel):
    """Account context nested in evidence response."""
    
    account_id: uuid.UUID
    account_ref: str
    account_type: str
    
    model_config = ConfigDict(from_attributes=True)


class RuleSnapshotItem(BaseModel):
    """Historical rule evaluation snapshot item."""
    
    snapshot_id: uuid.UUID
    rule_code: str
    rule_name: str
    rule_version: str
    outcome: str
    condition_text: str
    evaluated_from_utc: datetime
    evaluated_to_utc: datetime
    
    model_config = ConfigDict(from_attributes=True)


class AlertEvidenceResponse(BaseModel):
    """Full alert evidence read model for Screen 2."""
    
    alert_id: uuid.UUID
    alert_ref: str
    priority: str
    risk_score: int
    status: str
    triggered_at_utc: datetime
    transaction: TransactionFactsView
    customer: CustomerContextView
    account: AccountContextView
    rule_snapshots: list[RuleSnapshotItem]
    
    model_config = ConfigDict(from_attributes=True)
