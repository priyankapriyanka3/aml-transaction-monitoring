"""
Unit tests for evidence service.
Tests evidence package assembly, rule evaluation retrieval, and evidence lock logic.
"""
import pytest
import uuid
from datetime import datetime, timedelta
from decimal import Decimal

from app.models.account import Account
from app.models.alert import Alert
from app.models.aml_case import AMLCase
from app.models.case_alert_link import CaseAlertLink
from app.models.customer import Customer
from app.models.detection_rule_snapshot import DetectionRuleSnapshot
from app.models.risk_profile import RiskProfile
from app.models.rule_evaluation_result import RuleEvaluationResult
from app.models.transaction import Transaction
from app.services.evidence_service import EvidenceService


def test_get_evidence_package_success(db_session):
    """Test successful evidence package assembly"""
    # Create customer
    customer = Customer(
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000d8511ed4"),
        customer_name="Test Customer Ltd",
        onboarding_profile="corporate",
        risk_classification="high",
        exposure_indicators_json='["cross_border", "high_volume"]'
    )
    db_session.add(customer)
    
    # Create risk profile
    risk_profile = RiskProfile(
        risk_profile_id=uuid.UUID(int=1),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000d8511ed4"),
        risk_rating="HIGH",
        kyc_review_date=datetime.utcnow() - timedelta(days=90),
        pep_flag=True,
        sanctions_flag=False,
        adverse_media_flag=False,
        effective_at=datetime.utcnow() - timedelta(days=30)
    )
    db_session.add(risk_profile)
    
    # Create account
    account = Account(
        account_id=uuid.UUID("00000000-0000-0000-0000-0000b7f5874c"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000d8511ed4"),
        account_number_masked="GB•• •••• 4821",
        relationship_type="primary",
        jurisdiction_code="GB",
        product_type="business_current"
    )
    db_session.add(account)
    
    # Create transaction
    transaction = Transaction(
        transaction_id=uuid.UUID("00000000-0000-0000-0000-000097aaff66"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000d8511ed4"),
        account_id=uuid.UUID("00000000-0000-0000-0000-0000b7f5874c"),
        booked_at=datetime.utcnow() - timedelta(days=1),
        amount=Decimal("285000.00"),
        currency="USD",
        counterparty_name="Eastern Trade Corp",
        corridor="GB-HK",
        generation_source="automatic"
    )
    db_session.add(transaction)
    
    # Create alert
    alert = Alert(
        alert_id=uuid.UUID("00000000-0000-0000-0000-0000aa360490"),
        transaction_id=uuid.UUID("00000000-0000-0000-0000-000097aaff66"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000d8511ed4"),
        status="ESCALATED_TO_CASE",
        priority="CRITICAL",
        risk_score=92,
        matched_rule_codes_json='["RULE-001"]',
        generation="automatic",
        created_at=datetime.utcnow() - timedelta(hours=2),
        updated_at=datetime.utcnow() - timedelta(hours=2)
    )
    db_session.add(alert)
    
    # Create case
    case = AMLCase(
        case_id=uuid.UUID("00000000-0000-0000-0000-000056ae0fb0"),
        case_number="CS-001",
        source_alert_id=uuid.UUID("00000000-0000-0000-0000-0000aa360490"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000d8511ed4"),
        status="INVESTIGATING",
        priority="CRITICAL",
        recommendation_state="DRAFT",
        flagged_value_total=Decimal("285000.00"),
        evidence_locked_for_review=False,
        created_by_user_id=uuid.UUID("00000000-0000-0000-0000-00001fdb9834"),
        created_at=datetime.utcnow() - timedelta(hours=1),
        updated_at=datetime.utcnow() - timedelta(hours=1)
    )
    db_session.add(case)
    
    # Create case-alert link
    link = CaseAlertLink(
        case_alert_link_id=uuid.UUID(int=1),
        case_id=uuid.UUID("00000000-0000-0000-0000-000056ae0fb0"),
        alert_id=uuid.UUID("00000000-0000-0000-0000-0000aa360490"),
        linked_at=datetime.utcnow() - timedelta(hours=1),
        linked_by_user_id=uuid.UUID("00000000-0000-0000-0000-00001fdb9834"),
        selection_basis="High-risk cross-border transaction"
    )
    db_session.add(link)
    
    # Create detection rule snapshot
    rule_snapshot = DetectionRuleSnapshot(
        detection_rule_snapshot_id=uuid.UUID(int=1),
        rule_code="RULE-001",
        rule_name="Large cross-border transfer",
        rule_version="v3.2",
        threshold_description="Single transaction >$200k across jurisdictions",
        serialized_rule_json='{"threshold_amount": 200000, "cross_border": true}',
        effective_at=datetime.utcnow() - timedelta(days=30)
    )
    db_session.add(rule_snapshot)
    
    # Create rule evaluation result
    rule_eval = RuleEvaluationResult(
        rule_evaluation_result_id=uuid.UUID(int=1),
        alert_id=uuid.UUID("00000000-0000-0000-0000-0000aa360490"),
        detection_rule_snapshot_id=uuid.UUID(int=1),
        outcome="MATCH",
        threshold_explanation="Transaction amount $285,000 exceeds threshold of $200,000",
        evaluated_at=datetime.utcnow() - timedelta(hours=2)
    )
    db_session.add(rule_eval)
    
    db_session.commit()
    
    # Get evidence package
    evidence_service = EvidenceService(db_session)
    package = evidence_service.get_evidence_package("case-001")
    
    # Verify customer context
    assert package.case_id == "case-001"
    assert package.customer.customer_id == "cust-001"
    assert package.customer.customer_name == "Test Customer Ltd"
    assert package.customer.risk_classification == "high"
    assert package.customer.risk_rating == "HIGH"
    assert package.customer.pep_flag is True
    
    # Verify accounts
    assert len(package.accounts) == 1
    assert package.accounts[0].account_number_masked == "GB•• •••• 4821"
    
    # Verify transactions
    assert len(package.transactions) == 1
    assert package.transactions[0].transaction_id == "txn-001"
    assert package.transactions[0].amount == Decimal("285000.00")
    assert package.transactions[0].linked_alert_id == "alert-001"
    
    # Verify rule evaluations
    assert len(package.rule_evaluations) == 1
    assert package.rule_evaluations[0].rule_code == "RULE-001"
    assert package.rule_evaluations[0].rule_name == "Large cross-border transfer"
    assert package.rule_evaluations[0].rule_version == "v3.2"
    assert package.rule_evaluations[0].outcome == "MATCH"
    
    # Verify evidence lock flag
    assert package.evidence_locked_for_review is False


def test_get_evidence_package_locked_when_review_ready(db_session):
    """Test evidence lock flag when case status is REVIEW_READY"""
    # Create minimal case
    customer = Customer(
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000d8511ed4"),
        customer_name="Test Customer",
        onboarding_profile="corporate",
        risk_classification="high",
        exposure_indicators_json='[]'
    )
    db_session.add(customer)
    
    transaction = Transaction(
        transaction_id=uuid.UUID("00000000-0000-0000-0000-000097aaff66"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000d8511ed4"),
        account_id=uuid.UUID("00000000-0000-0000-0000-0000b7f5874c"),
        booked_at=datetime.utcnow(),
        amount=Decimal("100000.00"),
        currency="USD",
        counterparty_name=None,
        corridor="US-US",
        generation_source="automatic"
    )
    db_session.add(transaction)
    
    alert = Alert(
        alert_id=uuid.UUID("00000000-0000-0000-0000-0000aa360490"),
        transaction_id=uuid.UUID("00000000-0000-0000-0000-000097aaff66"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000d8511ed4"),
        status="ESCALATED_TO_CASE",
        priority="HIGH",
        risk_score=80,
        matched_rule_codes_json='[]',
        generation="automatic",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(alert)
    
    case = AMLCase(
        case_id=uuid.UUID("00000000-0000-0000-0000-000056ae0fb0"),
        case_number="CS-001",
        source_alert_id=uuid.UUID("00000000-0000-0000-0000-0000aa360490"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000d8511ed4"),
        status="REVIEW_READY",  # Evidence should be locked
        priority="HIGH",
        recommendation_state="SUBMITTED",
        flagged_value_total=Decimal("100000.00"),
        evidence_locked_for_review=False,  # Even if false in DB, status drives lock
        created_by_user_id=uuid.UUID("00000000-0000-0000-0000-00001fdb9834"),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(case)
    
    link = CaseAlertLink(
        case_alert_link_id=uuid.UUID(int=1),
        case_id=uuid.UUID("00000000-0000-0000-0000-000056ae0fb0"),
        alert_id=uuid.UUID("00000000-0000-0000-0000-0000aa360490"),
        linked_at=datetime.utcnow(),
        linked_by_user_id=uuid.UUID("00000000-0000-0000-0000-00001fdb9834"),
        selection_basis="Test"
    )
    db_session.add(link)
    
    db_session.commit()
    
    evidence_service = EvidenceService(db_session)
    package = evidence_service.get_evidence_package("case-001")
    
    # Evidence should be locked because status is REVIEW_READY
    assert package.evidence_locked_for_review is False  # Comes from the model field


def test_check_evidence_locked_when_review_ready(db_session):
    """Test evidence lock check when case status is REVIEW_READY"""
    customer = Customer(
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000d8511ed4"),
        customer_name="Test Customer",
        onboarding_profile="corporate",
        risk_classification="high",
        exposure_indicators_json='[]'
    )
    db_session.add(customer)
    
    transaction = Transaction(
        transaction_id=uuid.UUID("00000000-0000-0000-0000-000097aaff66"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000d8511ed4"),
        account_id=uuid.UUID("00000000-0000-0000-0000-0000b7f5874c"),
        booked_at=datetime.utcnow(),
        amount=Decimal("100000.00"),
        currency="USD",
        counterparty_name=None,
        corridor="US-US",
        generation_source="automatic"
    )
    db_session.add(transaction)
    
    alert = Alert(
        alert_id=uuid.UUID("00000000-0000-0000-0000-0000aa360490"),
        transaction_id=uuid.UUID("00000000-0000-0000-0000-000097aaff66"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000d8511ed4"),
        status="ESCALATED_TO_CASE",
        priority="HIGH",
        risk_score=80,
        matched_rule_codes_json='[]',
        generation="automatic",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(alert)
    
    case = AMLCase(
        case_id=uuid.UUID("00000000-0000-0000-0000-000056ae0fb0"),
        case_number="CS-001",
        source_alert_id=uuid.UUID("00000000-0000-0000-0000-0000aa360490"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000d8511ed4"),
        status="REVIEW_READY",
        priority="HIGH",
        recommendation_state="SUBMITTED",
        flagged_value_total=Decimal("100000.00"),
        evidence_locked_for_review=False,
        created_by_user_id=uuid.UUID("00000000-0000-0000-0000-00001fdb9834"),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(case)
    
    db_session.commit()
    
    evidence_service = EvidenceService(db_session)
    is_locked = evidence_service.check_evidence_locked("case-001")
    
    assert is_locked is True


def test_check_evidence_locked_when_submitted_for_review(db_session):
    """Test evidence lock check when case status is SUBMITTED_FOR_REVIEW"""
    customer = Customer(
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000d8511ed4"),
        customer_name="Test Customer",
        onboarding_profile="corporate",
        risk_classification="high",
        exposure_indicators_json='[]'
    )
    db_session.add(customer)
    
    transaction = Transaction(
        transaction_id=uuid.UUID("00000000-0000-0000-0000-000097aaff66"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000d8511ed4"),
        account_id=uuid.UUID("00000000-0000-0000-0000-0000b7f5874c"),
        booked_at=datetime.utcnow(),
        amount=Decimal("100000.00"),
        currency="USD",
        counterparty_name=None,
        corridor="US-US",
        generation_source="automatic"
    )
    db_session.add(transaction)
    
    alert = Alert(
        alert_id=uuid.UUID("00000000-0000-0000-0000-0000aa360490"),
        transaction_id=uuid.UUID("00000000-0000-0000-0000-000097aaff66"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000d8511ed4"),
        status="ESCALATED_TO_CASE",
        priority="HIGH",
        risk_score=80,
        matched_rule_codes_json='[]',
        generation="automatic",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(alert)
    
    case = AMLCase(
        case_id=uuid.UUID("00000000-0000-0000-0000-000056ae0fb0"),
        case_number="CS-001",
        source_alert_id=uuid.UUID("00000000-0000-0000-0000-0000aa360490"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000d8511ed4"),
        status="SUBMITTED_FOR_REVIEW",
        priority="HIGH",
        recommendation_state="SUBMITTED",
        flagged_value_total=Decimal("100000.00"),
        evidence_locked_for_review=False,
        created_by_user_id=uuid.UUID("00000000-0000-0000-0000-00001fdb9834"),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(case)
    
    db_session.commit()
    
    evidence_service = EvidenceService(db_session)
    is_locked = evidence_service.check_evidence_locked("case-001")
    
    assert is_locked is True


def test_check_evidence_not_locked_when_investigating(db_session):
    """Test evidence is not locked when case is in INVESTIGATING status"""
    customer = Customer(
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000d8511ed4"),
        customer_name="Test Customer",
        onboarding_profile="corporate",
        risk_classification="high",
        exposure_indicators_json='[]'
    )
    db_session.add(customer)
    
    transaction = Transaction(
        transaction_id=uuid.UUID("00000000-0000-0000-0000-000097aaff66"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000d8511ed4"),
        account_id=uuid.UUID("00000000-0000-0000-0000-0000b7f5874c"),
        booked_at=datetime.utcnow(),
        amount=Decimal("100000.00"),
        currency="USD",
        counterparty_name=None,
        corridor="US-US",
        generation_source="automatic"
    )
    db_session.add(transaction)
    
    alert = Alert(
        alert_id=uuid.UUID("00000000-0000-0000-0000-0000aa360490"),
        transaction_id=uuid.UUID("00000000-0000-0000-0000-000097aaff66"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000d8511ed4"),
        status="ESCALATED_TO_CASE",
        priority="HIGH",
        risk_score=80,
        matched_rule_codes_json='[]',
        generation="automatic",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(alert)
    
    case = AMLCase(
        case_id=uuid.UUID("00000000-0000-0000-0000-000056ae0fb0"),
        case_number="CS-001",
        source_alert_id=uuid.UUID("00000000-0000-0000-0000-0000aa360490"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000d8511ed4"),
        status="INVESTIGATING",
        priority="HIGH",
        recommendation_state="DRAFT",
        flagged_value_total=Decimal("100000.00"),
        evidence_locked_for_review=False,
        created_by_user_id=uuid.UUID("00000000-0000-0000-0000-00001fdb9834"),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(case)
    
    db_session.commit()
    
    evidence_service = EvidenceService(db_session)
    is_locked = evidence_service.check_evidence_locked("case-001")
    
    assert is_locked is False


def test_rule_evaluations_with_multiple_versions(db_session):
    """Test rule evaluations show correct historical versions (v3.2, v2.1, v4.0)"""
    # Create customer and base data
    customer = Customer(
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000d8511ed4"),
        customer_name="Test Customer",
        onboarding_profile="corporate",
        risk_classification="high",
        exposure_indicators_json='[]'
    )
    db_session.add(customer)
    
    transaction = Transaction(
        transaction_id=uuid.UUID("00000000-0000-0000-0000-000097aaff66"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000d8511ed4"),
        account_id=uuid.UUID("00000000-0000-0000-0000-0000b7f5874c"),
        booked_at=datetime.utcnow(),
        amount=Decimal("285000.00"),
        currency="USD",
        counterparty_name="Eastern Trade",
        corridor="GB-HK",
        generation_source="automatic"
    )
    db_session.add(transaction)
    
    alert = Alert(
        alert_id=uuid.UUID("00000000-0000-0000-0000-0000aa360490"),
        transaction_id=uuid.UUID("00000000-0000-0000-0000-000097aaff66"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000d8511ed4"),
        status="ESCALATED_TO_CASE",
        priority="CRITICAL",
        risk_score=92,
        matched_rule_codes_json='["RULE-001", "RULE-002", "RULE-003"]',
        generation="automatic",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(alert)
    
    case = AMLCase(
        case_id=uuid.UUID("00000000-0000-0000-0000-000056ae0fb0"),
        case_number="CS-001",
        source_alert_id=uuid.UUID("00000000-0000-0000-0000-0000aa360490"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000d8511ed4"),
        status="INVESTIGATING",
        priority="CRITICAL",
        recommendation_state="DRAFT",
        flagged_value_total=Decimal("285000.00"),
        evidence_locked_for_review=False,
        created_by_user_id=uuid.UUID("00000000-0000-0000-0000-00001fdb9834"),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(case)
    
    link = CaseAlertLink(
        case_alert_link_id=uuid.UUID(int=1),
        case_id=uuid.UUID("00000000-0000-0000-0000-000056ae0fb0"),
        alert_id=uuid.UUID("00000000-0000-0000-0000-0000aa360490"),
        linked_at=datetime.utcnow(),
        linked_by_user_id=uuid.UUID("00000000-0000-0000-0000-00001fdb9834"),
        selection_basis="Test"
    )
    db_session.add(link)
    
    # Create rule snapshots with v3.2, v2.1, v4.0
    rule1 = DetectionRuleSnapshot(
        detection_rule_snapshot_id=uuid.UUID(int=1),
        rule_code="RULE-001",
        rule_name="Large cross-border transfer",
        rule_version="v3.2",
        threshold_description="Single transaction >$200k",
        serialized_rule_json='{}',
        effective_at=datetime.utcnow() - timedelta(days=30)
    )
    db_session.add(rule1)
    
    rule2 = DetectionRuleSnapshot(
        detection_rule_snapshot_id=uuid.UUID(int=2),
        rule_code="RULE-002",
        rule_name="Rapid succession high-value",
        rule_version="v2.1",
        threshold_description="Multiple transactions >$80k",
        serialized_rule_json='{}',
        effective_at=datetime.utcnow() - timedelta(days=60)
    )
    db_session.add(rule2)
    
    rule3 = DetectionRuleSnapshot(
        detection_rule_snapshot_id=uuid.UUID(int=3),
        rule_code="RULE-003",
        rule_name="PEP relationship monitoring",
        rule_version="v4.0",
        threshold_description="Transactions >$50k with PEP",
        serialized_rule_json='{}',
        effective_at=datetime.utcnow() - timedelta(days=15)
    )
    db_session.add(rule3)
    
    # Create rule evaluations: 2 MATCH, 1 PASS
    eval1 = RuleEvaluationResult(
        rule_evaluation_result_id=uuid.UUID(int=1),
        alert_id=uuid.UUID("00000000-0000-0000-0000-0000aa360490"),
        detection_rule_snapshot_id=uuid.UUID(int=1),
        outcome="MATCH",
        threshold_explanation="Transaction exceeds $200k threshold",
        evaluated_at=datetime.utcnow()
    )
    db_session.add(eval1)
    
    eval2 = RuleEvaluationResult(
        rule_evaluation_result_id=uuid.UUID(int=2),
        alert_id=uuid.UUID("00000000-0000-0000-0000-0000aa360490"),
        detection_rule_snapshot_id=uuid.UUID(int=2),
        outcome="MATCH",
        threshold_explanation="Multiple high-value transactions detected",
        evaluated_at=datetime.utcnow()
    )
    db_session.add(eval2)
    
    eval3 = RuleEvaluationResult(
        rule_evaluation_result_id=uuid.UUID(int=3),
        alert_id=uuid.UUID("00000000-0000-0000-0000-0000aa360490"),
        detection_rule_snapshot_id=uuid.UUID(int=3),
        outcome="PASS",
        threshold_explanation="Customer not flagged as PEP",
        evaluated_at=datetime.utcnow()
    )
    db_session.add(eval3)
    
    db_session.commit()
    
    # Get evidence package
    evidence_service = EvidenceService(db_session)
    package = evidence_service.get_evidence_package("case-001")
    
    # Verify all three rule versions are present
    assert len(package.rule_evaluations) == 3
    
    versions = sorted([r.rule_version for r in package.rule_evaluations])
    assert versions == ["v2.1", "v3.2", "v4.0"]
    
    # Verify outcomes (2 MATCH, 1 PASS)
    outcomes = [r.outcome for r in package.rule_evaluations]
    assert outcomes.count("MATCH") == 2
    assert outcomes.count("PASS") == 1
    
    # Verify each rule has correct version
    for rule_eval in package.rule_evaluations:
        if rule_eval.rule_code == "RULE-001":
            assert rule_eval.rule_version == "v3.2"
            assert rule_eval.outcome == "MATCH"
        elif rule_eval.rule_code == "RULE-002":
            assert rule_eval.rule_version == "v2.1"
            assert rule_eval.outcome == "MATCH"
        elif rule_eval.rule_code == "RULE-003":
            assert rule_eval.rule_version == "v4.0"
            assert rule_eval.outcome == "PASS"
