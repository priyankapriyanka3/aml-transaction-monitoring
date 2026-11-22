"""
Unit tests for readiness evaluation service.
"""
import pytest
import uuid
from datetime import datetime, timedelta
from decimal import Decimal

from app.services.readiness_service import ReadinessService


def test_evaluate_readiness_all_passed(db_session):
    """Test readiness evaluation when all criteria pass"""
    from app.models.user import User
    from app.models.customer import Customer
    from app.models.alert import Alert
    from app.models.transaction import Transaction
    from app.models.account import Account
    from app.models.aml_case import AMLCase
    from app.models.case_alert_link import CaseAlertLink
    import json
    
    # Create test data with all readiness criteria met
    user = User(
        user_id=uuid.UUID("00000000-0000-0000-0000-000062cf060d"),
        username="readyuser",
        display_name="Ready User",
        email="ready@example.com",
        password_hash="hashed",
        primary_role="investigator",
        is_active=True
    )
    db_session.add(user)
    
    customer = Customer(
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000df19b652"),
        customer_name="Ready Customer",
        onboarding_profile="corporate",
        risk_classification="high",
        exposure_indicators_json=json.dumps(["test"])
    )
    db_session.add(customer)
    
    account = Account(
        account_id=uuid.UUID("00000000-0000-0000-0000-00001a7ad523"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000df19b652"),
        account_number_masked="GB•• •••• 1111",
        relationship_type="primary",
        jurisdiction_code="GB",
        product_type="business"
    )
    db_session.add(account)
    
    transaction = Transaction(
        transaction_id=uuid.UUID("00000000-0000-0000-0000-0000419fe4bc"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000df19b652"),
        account_id=uuid.UUID("00000000-0000-0000-0000-00001a7ad523"),
        booked_at=datetime.utcnow(),
        amount=Decimal("200000.00"),
        currency="USD",
        counterparty_name="Ready Corp",
        corridor="GB-US",
        generation_source="automatic"
    )
    db_session.add(transaction)
    
    alert = Alert(
        alert_id=uuid.UUID("00000000-0000-0000-0000-00003fae711e"),
        transaction_id=uuid.UUID("00000000-0000-0000-0000-0000419fe4bc"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000df19b652"),
        status="ESCALATED_TO_CASE",
        priority="HIGH",
        risk_score=88,
        matched_rule_codes_json=json.dumps(["RULE-001"]),
        generation="automatic",
        assigned_user_id=uuid.UUID("00000000-0000-0000-0000-000062cf060d"),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(alert)
    
    # Case with recommendation and findings (ready for handoff)
    case = AMLCase(
        case_id=uuid.UUID("00000000-0000-0000-0000-000003613e56"),
        case_number="CS-READY-001",
        source_alert_id=uuid.UUID("00000000-0000-0000-0000-00003fae711e"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000df19b652"),
        status="INVESTIGATING",
        priority="HIGH",
        assigned_user_id=uuid.UUID("00000000-0000-0000-0000-000062cf060d"),
        recommendation_state="SUBMITTED",
        recommendation_outcome="SUBSTANTIATE",
        findings_summary="This is a complete findings summary with sufficient detail and length to meet all requirements for handoff readiness evaluation and submission.",
        flagged_value_total=Decimal("0.00"),
        evidence_locked_for_review=False,
        created_by_user_id=uuid.UUID("00000000-0000-0000-0000-000062cf060d"),
        handoff_officer_user_id=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(case)
    
    link = CaseAlertLink(
        case_alert_link_id="ready-link-1",
        case_id=uuid.UUID("00000000-0000-0000-0000-000003613e56"),
        alert_id=uuid.UUID("00000000-0000-0000-0000-00003fae711e"),
        linked_at=datetime.utcnow(),
        linked_by_user_id=uuid.UUID("00000000-0000-0000-0000-000062cf060d"),
        selection_basis="Ready basis"
    )
    db_session.add(link)
    
    db_session.commit()
    
    # Evaluate readiness
    readiness_service = ReadinessService(db_session)
    result = readiness_service.evaluate_readiness("ready-case-1")
    
    assert result.is_ready is True
    assert len(result.checklist_items) == 5
    assert all(item.passed for item in result.checklist_items)


def test_evaluate_readiness_no_linked_alerts(db_session):
    """Test readiness fails when no alerts linked"""
    from app.models.user import User
    from app.models.customer import Customer
    from app.models.aml_case import AMLCase
    import json
    
    user = User(
        user_id=uuid.UUID("00000000-0000-0000-0000-000020d15fc9"),
        username="noalertuser",
        display_name="No Alert User",
        email="noalert@example.com",
        password_hash="hashed",
        primary_role="investigator",
        is_active=True
    )
    db_session.add(user)
    
    customer = Customer(
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000f499896e"),
        customer_name="No Alert Customer",
        onboarding_profile="corporate",
        risk_classification="medium",
        exposure_indicators_json=json.dumps([])
    )
    db_session.add(customer)
    
    # Case without any linked alerts
    case = AMLCase(
        case_id=uuid.UUID("00000000-0000-0000-0000-00007f2e1f1b"),
        case_number="CS-NOALERT-001",
        source_alert_id=uuid.UUID("00000000-0000-0000-0000-0000e7dc9076"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000f499896e"),
        status="INVESTIGATING",
        priority="MEDIUM",
        assigned_user_id=uuid.UUID("00000000-0000-0000-0000-000020d15fc9"),
        recommendation_state="SUBMITTED",
        recommendation_outcome="SUBSTANTIATE",
        findings_summary="Complete findings summary with sufficient length for validation.",
        flagged_value_total=Decimal("0.00"),
        evidence_locked_for_review=False,
        created_by_user_id=uuid.UUID("00000000-0000-0000-0000-000020d15fc9"),
        handoff_officer_user_id=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(case)
    db_session.commit()
    
    readiness_service = ReadinessService(db_session)
    result = readiness_service.evaluate_readiness("no-alert-case")
    
    assert result.is_ready is False
    linked_evidence_item = next(item for item in result.checklist_items if item.code == "linked_evidence")
    assert linked_evidence_item.passed is False
    assert "No alerts linked" in linked_evidence_item.detail


def test_evaluate_readiness_no_recommendation(db_session):
    """Test readiness fails when recommendation missing"""
    from app.models.user import User
    from app.models.customer import Customer
    from app.models.alert import Alert
    from app.models.transaction import Transaction
    from app.models.account import Account
    from app.models.aml_case import AMLCase
    from app.models.case_alert_link import CaseAlertLink
    import json
    
    user = User(
        user_id=uuid.UUID("00000000-0000-0000-0000-0000b4329ed9"),
        username="norecuser",
        display_name="No Rec User",
        email="norec@example.com",
        password_hash="hashed",
        primary_role="investigator",
        is_active=True
    )
    db_session.add(user)
    
    customer = Customer(
        customer_id=uuid.UUID("00000000-0000-0000-0000-00001af044b5"),
        customer_name="No Rec Customer",
        onboarding_profile="corporate",
        risk_classification="low",
        exposure_indicators_json=json.dumps([])
    )
    db_session.add(customer)
    
    account = Account(
        account_id=uuid.UUID("00000000-0000-0000-0000-00004151032f"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-00001af044b5"),
        account_number_masked="US•• •••• 2222",
        relationship_type="primary",
        jurisdiction_code="US",
        product_type="business"
    )
    db_session.add(account)
    
    transaction = Transaction(
        transaction_id=uuid.UUID("00000000-0000-0000-0000-0000a25c48cb"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-00001af044b5"),
        account_id=uuid.UUID("00000000-0000-0000-0000-00004151032f"),
        booked_at=datetime.utcnow(),
        amount=Decimal("30000.00"),
        currency="USD",
        counterparty_name=None,
        corridor="US-US",
        generation_source="automatic"
    )
    db_session.add(transaction)
    
    alert = Alert(
        alert_id=uuid.UUID("00000000-0000-0000-0000-0000bb7f2334"),
        transaction_id=uuid.UUID("00000000-0000-0000-0000-0000a25c48cb"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-00001af044b5"),
        status="ESCALATED_TO_CASE",
        priority="LOW",
        risk_score=55,
        matched_rule_codes_json=json.dumps(["RULE-002"]),
        generation="automatic",
        assigned_user_id=uuid.UUID("00000000-0000-0000-0000-0000b4329ed9"),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(alert)
    
    # Case without recommendation
    case = AMLCase(
        case_id=uuid.UUID("00000000-0000-0000-0000-0000e23c0c8f"),
        case_number="CS-NOREC-001",
        source_alert_id=uuid.UUID("00000000-0000-0000-0000-0000bb7f2334"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-00001af044b5"),
        status="INVESTIGATING",
        priority="LOW",
        assigned_user_id=uuid.UUID("00000000-0000-0000-0000-0000b4329ed9"),
        recommendation_state="DRAFT",
        recommendation_outcome=None,
        findings_summary=None,
        flagged_value_total=Decimal("0.00"),
        evidence_locked_for_review=False,
        created_by_user_id=uuid.UUID("00000000-0000-0000-0000-0000b4329ed9"),
        handoff_officer_user_id=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(case)
    
    link = CaseAlertLink(
        case_alert_link_id="no-rec-link",
        case_id=uuid.UUID("00000000-0000-0000-0000-0000e23c0c8f"),
        alert_id=uuid.UUID("00000000-0000-0000-0000-0000bb7f2334"),
        linked_at=datetime.utcnow(),
        linked_by_user_id=uuid.UUID("00000000-0000-0000-0000-0000b4329ed9"),
        selection_basis="Test"
    )
    db_session.add(link)
    db_session.commit()
    
    readiness_service = ReadinessService(db_session)
    result = readiness_service.evaluate_readiness("no-rec-case")
    
    assert result.is_ready is False
    recommendation_item = next(item for item in result.checklist_items if item.code == "recommendation")
    assert recommendation_item.passed is False


def test_evaluate_readiness_with_open_requests(db_session):
    """Test readiness fails when open information requests exist"""
    from app.models.user import User
    from app.models.customer import Customer
    from app.models.alert import Alert
    from app.models.transaction import Transaction
    from app.models.account import Account
    from app.models.aml_case import AMLCase
    from app.models.case_alert_link import CaseAlertLink
    from app.models.information_request import InformationRequest
    import json
    
    user = User(
        user_id=uuid.UUID("00000000-0000-0000-0000-0000db2d9d37"),
        username="openrequser",
        display_name="Open Req User",
        email="openreq@example.com",
        password_hash="hashed",
        primary_role="investigator",
        is_active=True
    )
    db_session.add(user)
    
    customer = Customer(
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000e98f6e9e"),
        customer_name="Open Req Customer",
        onboarding_profile="corporate",
        risk_classification="high",
        exposure_indicators_json=json.dumps(["test"])
    )
    db_session.add(customer)
    
    account = Account(
        account_id=uuid.UUID("00000000-0000-0000-0000-00007612befa"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000e98f6e9e"),
        account_number_masked="CA•• •••• 3333",
        relationship_type="primary",
        jurisdiction_code="CA",
        product_type="business"
    )
    db_session.add(account)
    
    transaction = Transaction(
        transaction_id=uuid.UUID("00000000-0000-0000-0000-0000dc46dfa0"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000e98f6e9e"),
        account_id=uuid.UUID("00000000-0000-0000-0000-00007612befa"),
        booked_at=datetime.utcnow(),
        amount=Decimal("150000.00"),
        currency="CAD",
        counterparty_name="Test Corp",
        corridor="CA-US",
        generation_source="automatic"
    )
    db_session.add(transaction)
    
    alert = Alert(
        alert_id=uuid.UUID("00000000-0000-0000-0000-000012f3d0aa"),
        transaction_id=uuid.UUID("00000000-0000-0000-0000-0000dc46dfa0"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000e98f6e9e"),
        status="ESCALATED_TO_CASE",
        priority="HIGH",
        risk_score=80,
        matched_rule_codes_json=json.dumps(["RULE-001"]),
        generation="automatic",
        assigned_user_id=uuid.UUID("00000000-0000-0000-0000-0000db2d9d37"),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(alert)
    
    case = AMLCase(
        case_id=uuid.UUID("00000000-0000-0000-0000-000039c562a0"),
        case_number="CS-OPENREQ-001",
        source_alert_id=uuid.UUID("00000000-0000-0000-0000-000012f3d0aa"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000e98f6e9e"),
        status="PENDING_INFORMATION",
        priority="HIGH",
        assigned_user_id=uuid.UUID("00000000-0000-0000-0000-0000db2d9d37"),
        recommendation_state="SUBMITTED",
        recommendation_outcome="ESCALATE_FOR_REVIEW",
        findings_summary="Complete findings summary meeting all length requirements for validation.",
        flagged_value_total=Decimal("0.00"),
        evidence_locked_for_review=False,
        created_by_user_id=uuid.UUID("00000000-0000-0000-0000-0000db2d9d37"),
        handoff_officer_user_id=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(case)
    
    link = CaseAlertLink(
        case_alert_link_id="open-req-link",
        case_id=uuid.UUID("00000000-0000-0000-0000-000039c562a0"),
        alert_id=uuid.UUID("00000000-0000-0000-0000-000012f3d0aa"),
        linked_at=datetime.utcnow(),
        linked_by_user_id=uuid.UUID("00000000-0000-0000-0000-0000db2d9d37"),
        selection_basis="Test"
    )
    db_session.add(link)
    
    # Add open information request
    ir = InformationRequest(
        information_request_id=uuid.UUID("00000000-0000-0000-0000-0000d288d267"),
        case_id=uuid.UUID("00000000-0000-0000-0000-000039c562a0"),
        recipient_channel="EMAIL",
        requested_summary="Test request for open information request validation",
        rationale="Test rationale for open information request validation",
        status="OPEN",
        due_at=datetime.utcnow() + timedelta(days=5),
        response_summary=None,
        response_channel=None,
        response_received_at=None,
        created_by_user_id=uuid.UUID("00000000-0000-0000-0000-0000db2d9d37"),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(ir)
    db_session.commit()
    
    readiness_service = ReadinessService(db_session)
    result = readiness_service.evaluate_readiness("open-req-case")
    
    assert result.is_ready is False
    no_open_requests_item = next(item for item in result.checklist_items if item.code == "no_open_requests")
    assert no_open_requests_item.passed is False
    assert "1 open" in no_open_requests_item.detail
