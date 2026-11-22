"""
Evidence service for assembling customer and transaction evidence packages.
Implements FR-011, FR-012, FR-013, FR-015.
"""
from uuid import UUID

from sqlalchemy.orm import Session

from ..repositories.case_repository import CaseRepository
from ..repositories.evidence_repository import EvidenceRepository
from ..schemas.evidence_schemas import (
    AccountResponse,
    CustomerContextResponse,
    EvidencePackageResponse,
    RuleEvaluationResponse,
    TransactionResponse,
)


class EvidenceService:
    """Service for evidence package assembly"""
    
    def __init__(self, db: Session):
        self.db = db
        self.evidence_repo = EvidenceRepository(db)
        self.case_repo = CaseRepository(db)
    
    def check_evidence_locked(self, case_id: str) -> bool:
        """
        Check if evidence is locked for review.
        
        Evidence is locked when case status is REVIEW_READY or SUBMITTED_FOR_REVIEW.
        
        Args:
            case_id: Case identifier
            
        Returns:
            True if evidence is locked, False otherwise
            
        Raises:
            ValueError: If case not found
        """
        case_uuid = UUID(case_id) if isinstance(case_id, str) else case_id
        case = self.case_repo.get_overview(case_uuid)
        if not case:
            raise ValueError("Case not found")
        
        # Evidence is locked when status indicates reviewer-ready state (FR-015)
        locked_statuses = ["REVIEW_READY", "SUBMITTED_FOR_REVIEW"]
        return case.status in locked_statuses or case.evidence_locked_for_review
    
    def get_evidence_package(self, case_id: str) -> EvidencePackageResponse:
        """
        Assemble complete evidence package for case review.
        
        Implements:
        - FR-011: Customer context with risk indicators
        - FR-012: Transaction timeline sorted by booked_at DESC
        - FR-013: Rule evaluation outcomes with historical snapshot context
        - FR-015: Evidence lock status for reviewer-ready context
        
        Args:
            case_id: Case identifier
            
        Returns:
            EvidencePackageResponse with all evidence components
            
        Raises:
            ValueError: If case not found
        """
        # Get case to verify existence and get customer_id
        case_uuid = UUID(case_id) if isinstance(case_id, str) else case_id
        case = self.case_repo.get_overview(case_uuid)
        if not case:
            raise ValueError("Case not found")
        
        # Get customer context (FR-011)
        customer, risk_profile = self.evidence_repo.get_customer_context(case.customer_id)
        if not customer:
            raise ValueError("Customer not found for case")
        
        # Build customer context response with risk profile enrichment
        customer_context = CustomerContextResponse(
            customer_id=str(customer.customer_id),
            customer_name=customer.customer_name,
            onboarding_profile=customer.onboarding_profile,
            risk_classification=customer.risk_classification,
            exposure_indicators_json=customer.exposure_indicators_json,
            risk_rating=risk_profile.risk_rating if risk_profile else None,
            kyc_review_date=risk_profile.kyc_review_date if risk_profile else None,
            pep_flag=risk_profile.pep_flag if risk_profile else False,
            sanctions_flag=risk_profile.sanctions_flag if risk_profile else False,
            adverse_media_flag=risk_profile.adverse_media_flag if risk_profile else False
        )
        
        # Get accounts (FR-011)
        accounts = self.evidence_repo.get_accounts_by_customer(case.customer_id)
        account_responses = [
            AccountResponse(
                account_id=str(acc.account_id),
                customer_id=str(acc.customer_id),
                account_number_masked=acc.account_number_masked,
                relationship_type=acc.relationship_type,
                jurisdiction_code=acc.jurisdiction_code,
                product_type=acc.product_type
            )
            for acc in accounts
        ]
        
        # Get transactions sorted by booked_at DESC (FR-012)
        transaction_tuples = self.evidence_repo.get_transactions_by_case(case_uuid)
        transaction_responses = [
            TransactionResponse(
                transaction_id=str(txn.transaction_id),
                customer_id=str(txn.customer_id),
                account_id=str(txn.account_id),
                booked_at=txn.booked_at,
                amount=txn.amount,
                currency=txn.currency,
                counterparty_name=txn.counterparty_name,
                corridor=txn.corridor,
                generation_source=txn.generation_source,
                linked_alert_id=str(alert_id) if alert_id else None
            )
            for txn, alert_id in transaction_tuples
        ]
        
        # Get rule evaluations with historical snapshot context (FR-013)
        rule_evaluations = self.evidence_repo.get_rule_evaluations_by_case(case_uuid)
        rule_evaluation_responses = []
        
        for evaluation in rule_evaluations:
            # Get rule snapshot for historical context
            snapshot = self.evidence_repo.get_rule_snapshot(
                evaluation.detection_rule_snapshot_id
            )
            
            if snapshot:
                rule_evaluation_responses.append(
                    RuleEvaluationResponse(
                        rule_evaluation_id=str(evaluation.rule_evaluation_result_id),
                        alert_id=str(evaluation.alert_id),
                        rule_code=snapshot.rule_code,
                        rule_name=snapshot.rule_name,
                        rule_version=snapshot.rule_version,
                        outcome=evaluation.outcome,
                        threshold_explanation=evaluation.threshold_explanation,
                        evaluated_at=evaluation.evaluated_at
                    )
                )
        
        # Assemble complete evidence package
        return EvidencePackageResponse(
            case_id=case_id,
            customer=customer_context,
            accounts=account_responses,
            transactions=transaction_responses,
            rule_evaluations=rule_evaluation_responses,
            evidence_locked_for_review=case.evidence_locked_for_review
        )
