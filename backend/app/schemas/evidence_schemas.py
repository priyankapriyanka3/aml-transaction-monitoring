"""
Evidence package schemas for customer and transaction evidence.
Implements FR-011, FR-012, FR-013, FR-015.
"""
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class CustomerContextResponse(BaseModel):
    """Customer profile context for case evidence review"""
    customer_id: str
    customer_name: str
    onboarding_profile: str
    risk_classification: str
    exposure_indicators_json: str  # JSON string from model
    risk_rating: str | None = None  # From latest risk_profile
    kyc_review_date: datetime | None = None
    pep_flag: bool = False
    sanctions_flag: bool = False
    adverse_media_flag: bool = False
    
    model_config = ConfigDict(from_attributes=True)


class AccountResponse(BaseModel):
    """Account relationship context"""
    account_id: str
    customer_id: str
    account_number_masked: str
    relationship_type: str
    jurisdiction_code: str
    product_type: str
    
    model_config = ConfigDict(from_attributes=True)


class TransactionResponse(BaseModel):
    """Transaction evidence for case timeline"""
    transaction_id: str
    customer_id: str
    account_id: str
    booked_at: datetime
    amount: Decimal
    currency: str
    counterparty_name: str | None
    corridor: str
    generation_source: str
    linked_alert_id: str | None = None  # Alert that triggered this transaction's inclusion
    
    model_config = ConfigDict(from_attributes=True)


class RuleEvaluationResponse(BaseModel):
    """Rule evaluation outcome and rationale for FR-013"""
    rule_evaluation_id: str
    alert_id: str
    rule_code: str
    rule_name: str
    rule_version: str
    outcome: str
    threshold_explanation: str
    evaluated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class EvidencePackageResponse(BaseModel):
    """Complete evidence package for case review (FR-011, FR-012, FR-013, FR-015)"""
    case_id: str
    customer: CustomerContextResponse
    accounts: list[AccountResponse]
    transactions: list[TransactionResponse]
    rule_evaluations: list[RuleEvaluationResponse]
    evidence_locked_for_review: bool
    
    model_config = ConfigDict(from_attributes=True)
