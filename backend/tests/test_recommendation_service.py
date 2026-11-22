"""
Unit tests for recommendation submission service.
"""
import pytest
import uuid
from datetime import datetime
from decimal import Decimal

from app.services.case_service import CaseService


def test_submit_recommendation_success(db_session):
    """Test successful recommendation submission"""
    # Create test data
    from app.models.user import User
    from app.models.customer import Customer
    from app.models.alert import Alert
    from app.models.transaction import Transaction
    from app.models.account import Account
    from app.models.aml_case import AMLCase
    from app.models.case_alert_link import CaseAlertLink
    import json
    
    # Create user
    user = User(
        user_id=uuid.UUID("00000000-0000-0000-0000-000062c3730f"),
        username="testuser",
        display_name="Test User",
        email="test@example.com",
        password_hash="hashed",
        primary_role="investigator",
        is_active=True
    )
    db_session.add(user)
    
    # Create customer
    customer = Customer(
        customer_id=uuid.UUID("00000000-0000-0000-0000-00002c87ffdf"),
        customer_name="Test Customer",
        onboarding_profile="corporate",
        risk_classification="high",
        exposure_indicators_json=json.dumps(["test"])
    )
    db_session.add(customer)
    
    # Create account
    account = Account(
        account_id=uuid.UUID("00000000-0000-0000-0000-000038e314b7"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-00002c87ffdf"),
        account_number_masked="GB•• •••• 1234",
        relationship_type="primary",
        jurisdiction_code="GB",
        product_type="business"
    )
    db_session.add(account)
    
    # Create transaction
    transaction = Transaction(
        transaction_id=uuid.UUID("00000000-0000-0000-0000-00002b6bf153"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-00002c87ffdf"),
        account_id=uuid.UUID("00000000-0000-0000-0000-000038e314b7"),
        booked_at=datetime.utcnow(),
        amount=Decimal("100000.00"),
        currency="USD",
        counterparty_name="Test Corp",
        corridor="GB-US",
        generation_source="automatic"
    )
    db_session.add(transaction)
    
    # Create alert
    alert = Alert(
        alert_id=uuid.UUID("00000000-0000-0000-0000-000098ffcd13"),
        transaction_id=uuid.UUID("00000000-0000-0000-0000-00002b6bf153"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-00002c87ffdf"),
        status="ESCALATED_TO_CASE",
        priority="HIGH",
        risk_score=85,
        matched_rule_codes_json=json.dumps(["RULE-001"]),
        generation="automatic",
        assigned_user_id=uuid.UUID("00000000-0000-0000-0000-000062c3730f"),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(alert)
    
    # Create case
    case = AMLCase(
        case_id=uuid.UUID("00000000-0000-0000-0000-0000a22a58d5"),
        case_number="CS-TEST-001",
        source_alert_id=uuid.UUID("00000000-0000-0000-0000-000098ffcd13"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-00002c87ffdf"),
        status="INVESTIGATING",
        priority="HIGH",
        assigned_user_id=uuid.UUID("00000000-0000-0000-0000-000062c3730f"),
        recommendation_state="DRAFT",
        recommendation_outcome=None,
        findings_summary=None,
        flagged_value_total=Decimal("0.00"),
        evidence_locked_for_review=False,
        created_by_user_id=uuid.UUID("00000000-0000-0000-0000-000062c3730f"),
        handoff_officer_user_id=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(case)
    
    # Create case-alert link
    link = CaseAlertLink(
        case_alert_link_id="test-link-1",
        case_id=uuid.UUID("00000000-0000-0000-0000-0000a22a58d5"),
        alert_id=uuid.UUID("00000000-0000-0000-0000-000098ffcd13"),
        linked_at=datetime.utcnow(),
        linked_by_user_id=uuid.UUID("00000000-0000-0000-0000-000062c3730f"),
        selection_basis="Test basis"
    )
    db_session.add(link)
    
    db_session.commit()
    
    # Test recommendation submission
    case_service = CaseService(db_session)
    
    findings = "This is a detailed findings summary that meets the minimum 50 character requirement for submission to ensure adequate documentation."
    
    result = case_service.submit_recommendation(
        case_id=uuid.UUID("00000000-0000-0000-0000-0000a22a58d5"),
        recommendation_outcome="SUBSTANTIATE",
        findings_summary=findings,
        actor_id="test-user-1"
    )
    
    assert result["case_id"] == "test-case-1"
    assert result["recommendation_state"] == "SUBMITTED"
    assert result["recommendation_outcome"] == "SUBSTANTIATE"
    assert result["findings_summary"] == findings
    assert result["submitted_by_user_id"] == "test-user-1"


def test_submit_recommendation_validates_findings_length(db_session):
    """Test that findings summary must be at least 50 characters"""
    from app.models.user import User
    from app.models.customer import Customer
    from app.models.alert import Alert
    from app.models.transaction import Transaction
    from app.models.account import Account
    from app.models.aml_case import AMLCase
    from app.models.case_alert_link import CaseAlertLink
    import json
    from decimal import Decimal
    
    # Create minimal test data
    user = User(
        user_id=uuid.UUID("00000000-0000-0000-0000-0000eb304b58"),
        username="testuser2",
        display_name="Test User 2",
        email="test2@example.com",
        password_hash="hashed",
        primary_role="investigator",
        is_active=True
    )
    db_session.add(user)
    
    customer = Customer(
        customer_id=uuid.UUID("00000000-0000-0000-0000-00009be846dc"),
        customer_name="Test Customer 2",
        onboarding_profile="corporate",
        risk_classification="medium",
        exposure_indicators_json=json.dumps([])
    )
    db_session.add(customer)
    
    account = Account(
        account_id=uuid.UUID("00000000-0000-0000-0000-00003132d0cd"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-00009be846dc"),
        account_number_masked="US•• •••• 5678",
        relationship_type="primary",
        jurisdiction_code="US",
        product_type="business"
    )
    db_session.add(account)
    
    transaction = Transaction(
        transaction_id=uuid.UUID("00000000-0000-0000-0000-0000e4296bc5"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-00009be846dc"),
        account_id=uuid.UUID("00000000-0000-0000-0000-00003132d0cd"),
        booked_at=datetime.utcnow(),
        amount=Decimal("50000.00"),
        currency="USD",
        counterparty_name=None,
        corridor="US-US",
        generation_source="automatic"
    )
    db_session.add(transaction)
    
    alert = Alert(
        alert_id=uuid.UUID("00000000-0000-0000-0000-000071a5d515"),
        transaction_id=uuid.UUID("00000000-0000-0000-0000-0000e4296bc5"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-00009be846dc"),
        status="ESCALATED_TO_CASE",
        priority="MEDIUM",
        risk_score=70,
        matched_rule_codes_json=json.dumps(["RULE-002"]),
        generation="automatic",
        assigned_user_id=uuid.UUID("00000000-0000-0000-0000-0000eb304b58"),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(alert)
    
    case = AMLCase(
        case_id=uuid.UUID("00000000-0000-0000-0000-0000c0c7a0bd"),
        case_number="CS-TEST-002",
        source_alert_id=uuid.UUID("00000000-0000-0000-0000-000071a5d515"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-00009be846dc"),
        status="INVESTIGATING",
        priority="MEDIUM",
        assigned_user_id=uuid.UUID("00000000-0000-0000-0000-0000eb304b58"),
        recommendation_state="DRAFT",
        recommendation_outcome=None,
        findings_summary=None,
        flagged_value_total=Decimal("0.00"),
        evidence_locked_for_review=False,
        created_by_user_id=uuid.UUID("00000000-0000-0000-0000-0000eb304b58"),
        handoff_officer_user_id=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(case)
    
    link = CaseAlertLink(
        case_alert_link_id="test-link-2",
        case_id=uuid.UUID("00000000-0000-0000-0000-0000c0c7a0bd"),
        alert_id=uuid.UUID("00000000-0000-0000-0000-000071a5d515"),
        linked_at=datetime.utcnow(),
        linked_by_user_id=uuid.UUID("00000000-0000-0000-0000-0000eb304b58"),
        selection_basis="Test basis"
    )
    db_session.add(link)
    
    db_session.commit()
    
    # Test with short findings (< 50 chars)
    case_service = CaseService(db_session)
    
    with pytest.raises(ValueError, match="at least 50 characters"):
        case_service.submit_recommendation(
            case_id=uuid.UUID("00000000-0000-0000-0000-0000c0c7a0bd"),
            recommendation_outcome="NO_FURTHER_ACTION",
            findings_summary="Too short",
            actor_id="test-user-2"
        )


def test_submit_recommendation_requires_linked_alert(db_session):
    """Test that recommendation cannot be submitted without linked alerts"""
    from app.models.user import User
    from app.models.customer import Customer
    from app.models.aml_case import AMLCase
    import json
    from decimal import Decimal
    
    user = User(
        user_id=uuid.UUID("00000000-0000-0000-0000-00001d635cea"),
        username="testuser3",
        display_name="Test User 3",
        email="test3@example.com",
        password_hash="hashed",
        primary_role="investigator",
        is_active=True
    )
    db_session.add(user)
    
    customer = Customer(
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000be42bf0b"),
        customer_name="Test Customer 3",
        onboarding_profile="corporate",
        risk_classification="low",
        exposure_indicators_json=json.dumps([])
    )
    db_session.add(customer)
    
    # Create case WITHOUT linked alerts
    case = AMLCase(
        case_id=uuid.UUID("00000000-0000-0000-0000-000024e11b95"),
        case_number="CS-TEST-003",
        source_alert_id=uuid.UUID("00000000-0000-0000-0000-0000a4ec8bc5"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000be42bf0b"),
        status="INVESTIGATING",
        priority="LOW",
        assigned_user_id=uuid.UUID("00000000-0000-0000-0000-00001d635cea"),
        recommendation_state="DRAFT",
        recommendation_outcome=None,
        findings_summary=None,
        flagged_value_total=Decimal("0.00"),
        evidence_locked_for_review=False,
        created_by_user_id=uuid.UUID("00000000-0000-0000-0000-00001d635cea"),
        handoff_officer_user_id=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(case)
    db_session.commit()
    
    case_service = CaseService(db_session)
    
    with pytest.raises(ValueError, match="no alerts linked"):
        case_service.submit_recommendation(
            case_id=uuid.UUID("00000000-0000-0000-0000-000024e11b95"),
            recommendation_outcome="SUBSTANTIATE",
            findings_summary="This is a valid findings summary with enough characters to meet the minimum requirement.",
            actor_id="test-user-3"
        )


def test_submit_recommendation_blocked_by_open_requests(db_session):
    """Test that recommendation cannot be submitted when open information requests exist"""
    from app.models.user import User
    from app.models.customer import Customer
    from app.models.alert import Alert
    from app.models.transaction import Transaction
    from app.models.account import Account
    from app.models.aml_case import AMLCase
    from app.models.case_alert_link import CaseAlertLink
    from app.models.information_request import InformationRequest
    import json
    from decimal import Decimal
    from datetime import timedelta
    
    user = User(
        user_id=uuid.UUID("00000000-0000-0000-0000-0000050017e8"),
        username="testuser4",
        display_name="Test User 4",
        email="test4@example.com",
        password_hash="hashed",
        primary_role="investigator",
        is_active=True
    )
    db_session.add(user)
    
    customer = Customer(
        customer_id=uuid.UUID("00000000-0000-0000-0000-000047edfc61"),
        customer_name="Test Customer 4",
        onboarding_profile="corporate",
        risk_classification="medium",
        exposure_indicators_json=json.dumps([])
    )
    db_session.add(customer)
    
    account = Account(
        account_id=uuid.UUID("00000000-0000-0000-0000-000068dedc6f"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-000047edfc61"),
        account_number_masked="CA•• •••• 9012",
        relationship_type="primary",
        jurisdiction_code="CA",
        product_type="business"
    )
    db_session.add(account)
    
    transaction = Transaction(
        transaction_id=uuid.UUID("00000000-0000-0000-0000-000017d8f122"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-000047edfc61"),
        account_id=uuid.UUID("00000000-0000-0000-0000-000068dedc6f"),
        booked_at=datetime.utcnow(),
        amount=Decimal("75000.00"),
        currency="CAD",
        counterparty_name="North Corp",
        corridor="CA-US",
        generation_source="automatic"
    )
    db_session.add(transaction)
    
    alert = Alert(
        alert_id=uuid.UUID("00000000-0000-0000-0000-0000593894e1"),
        transaction_id=uuid.UUID("00000000-0000-0000-0000-000017d8f122"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-000047edfc61"),
        status="ESCALATED_TO_CASE",
        priority="MEDIUM",
        risk_score=72,
        matched_rule_codes_json=json.dumps(["RULE-001"]),
        generation="automatic",
        assigned_user_id=uuid.UUID("00000000-0000-0000-0000-0000050017e8"),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(alert)
    
    case = AMLCase(
        case_id=uuid.UUID("00000000-0000-0000-0000-0000fd438fcd"),
        case_number="CS-TEST-004",
        source_alert_id=uuid.UUID("00000000-0000-0000-0000-0000593894e1"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-000047edfc61"),
        status="INVESTIGATING",
        priority="MEDIUM",
        assigned_user_id=uuid.UUID("00000000-0000-0000-0000-0000050017e8"),
        recommendation_state="DRAFT",
        recommendation_outcome=None,
        findings_summary=None,
        flagged_value_total=Decimal("0.00"),
        evidence_locked_for_review=False,
        created_by_user_id=uuid.UUID("00000000-0000-0000-0000-0000050017e8"),
        handoff_officer_user_id=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(case)
    
    link = CaseAlertLink(
        case_alert_link_id="test-link-4",
        case_id=uuid.UUID("00000000-0000-0000-0000-0000fd438fcd"),
        alert_id=uuid.UUID("00000000-0000-0000-0000-0000593894e1"),
        linked_at=datetime.utcnow(),
        linked_by_user_id=uuid.UUID("00000000-0000-0000-0000-0000050017e8"),
        selection_basis="Test basis"
    )
    db_session.add(link)
    
    # Add OPEN information request
    ir = InformationRequest(
        information_request_id=uuid.UUID("00000000-0000-0000-0000-0000baf903c4"),
        case_id=uuid.UUID("00000000-0000-0000-0000-0000fd438fcd"),
        recipient_channel="EMAIL",
        requested_summary="Test request summary for validation purposes",
        rationale="Test rationale for validation purposes",
        status="OPEN",
        due_at=datetime.utcnow() + timedelta(days=3),
        response_summary=None,
        response_channel=None,
        response_received_at=None,
        created_by_user_id=uuid.UUID("00000000-0000-0000-0000-0000050017e8"),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(ir)
    db_session.commit()
    
    case_service = CaseService(db_session)
    
    with pytest.raises(ValueError, match="open and .* overdue information requests"):
        case_service.submit_recommendation(
            case_id=uuid.UUID("00000000-0000-0000-0000-0000fd438fcd"),
            recommendation_outcome="NO_FURTHER_ACTION",
            findings_summary="Valid findings summary with sufficient length to meet minimum requirement.",
            actor_id="test-user-4"
        )
