"""
Unit tests for handoff package service.
"""
import pytest
import uuid
from datetime import datetime, timedelta
from decimal import Decimal

from app.services.handoff_service import HandoffService


def test_get_handoff_package_success(db_session):
    """Test successful handoff package assembly"""
    from app.models.user import User
    from app.models.customer import Customer
    from app.models.alert import Alert
    from app.models.transaction import Transaction
    from app.models.account import Account
    from app.models.aml_case import AMLCase
    from app.models.case_alert_link import CaseAlertLink
    import json
    
    # Create test data
    user = User(
        user_id=uuid.UUID("00000000-0000-0000-0000-0000eaee0647"),
        username="handoffuser",
        display_name="Handoff User",
        email="handoff@example.com",
        password_hash="hashed",
        primary_role="investigator",
        is_active=True
    )
    db_session.add(user)
    
    customer = Customer(
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000e774d62a"),
        customer_name="Handoff Customer",
        onboarding_profile="corporate",
        risk_classification="high",
        exposure_indicators_json=json.dumps(["test"])
    )
    db_session.add(customer)
    
    account = Account(
        account_id=uuid.UUID("00000000-0000-0000-0000-000085c38af3"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000e774d62a"),
        account_number_masked="GB•• •••• 4444",
        relationship_type="primary",
        jurisdiction_code="GB",
        product_type="business"
    )
    db_session.add(account)
    
    transaction = Transaction(
        transaction_id=uuid.UUID("00000000-0000-0000-0000-000075246276"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000e774d62a"),
        account_id=uuid.UUID("00000000-0000-0000-0000-000085c38af3"),
        booked_at=datetime.utcnow(),
        amount=Decimal("300000.00"),
        currency="USD",
        counterparty_name="Handoff Corp",
        corridor="GB-HK",
        generation_source="automatic"
    )
    db_session.add(transaction)
    
    alert = Alert(
        alert_id=uuid.UUID("00000000-0000-0000-0000-00004eb4ec60"),
        transaction_id=uuid.UUID("00000000-0000-0000-0000-000075246276"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000e774d62a"),
        status="ESCALATED_TO_CASE",
        priority="CRITICAL",
        risk_score=95,
        matched_rule_codes_json=json.dumps(["RULE-001"]),
        generation="automatic",
        assigned_user_id=uuid.UUID("00000000-0000-0000-0000-0000eaee0647"),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(alert)
    
    case = AMLCase(
        case_id=uuid.UUID("00000000-0000-0000-0000-0000c9c9724b"),
        case_number="CS-HANDOFF-001",
        source_alert_id=uuid.UUID("00000000-0000-0000-0000-00004eb4ec60"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000e774d62a"),
        status="INVESTIGATING",
        priority="CRITICAL",
        assigned_user_id=uuid.UUID("00000000-0000-0000-0000-0000eaee0647"),
        recommendation_state="SUBMITTED",
        recommendation_outcome="SUBSTANTIATE",
        findings_summary="This is a complete and detailed findings summary with sufficient length and detail to meet all handoff readiness requirements.",
        flagged_value_total=Decimal("0.00"),
        evidence_locked_for_review=False,
        created_by_user_id=uuid.UUID("00000000-0000-0000-0000-0000eaee0647"),
        handoff_officer_user_id=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(case)
    
    link = CaseAlertLink(
        case_alert_link_id="handoff-link-1",
        case_id=uuid.UUID("00000000-0000-0000-0000-0000c9c9724b"),
        alert_id=uuid.UUID("00000000-0000-0000-0000-00004eb4ec60"),
        linked_at=datetime.utcnow(),
        linked_by_user_id=uuid.UUID("00000000-0000-0000-0000-0000eaee0647"),
        selection_basis="Handoff test basis"
    )
    db_session.add(link)
    
    db_session.commit()
    
    # Get handoff package
    handoff_service = HandoffService(db_session)
    package = handoff_service.get_handoff_package("handoff-case-1")
    
    assert package.case_id == "handoff-case-1"
    assert package.case_number == "CS-HANDOFF-001"
    assert package.recommendation_outcome == "SUBSTANTIATE"
    assert len(package.linked_alerts) == 1
    assert package.linked_alerts[0].alert_id == "handoff-alert-1"
    assert package.linked_alerts[0].priority == "CRITICAL"
    assert package.linked_alerts[0].risk_score == 95
    assert package.readiness.is_ready is True


def test_get_handoff_package_with_unresolved_issues(db_session):
    """Test handoff package shows unresolved issues when readiness fails"""
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
        user_id=uuid.UUID("00000000-0000-0000-0000-00009d03d0af"),
        username="unresolveduser",
        display_name="Unresolved User",
        email="unresolved@example.com",
        password_hash="hashed",
        primary_role="investigator",
        is_active=True
    )
    db_session.add(user)
    
    customer = Customer(
        customer_id=uuid.UUID("00000000-0000-0000-0000-00007de5be29"),
        customer_name="Unresolved Customer",
        onboarding_profile="corporate",
        risk_classification="medium",
        exposure_indicators_json=json.dumps([])
    )
    db_session.add(customer)
    
    account = Account(
        account_id=uuid.UUID("00000000-0000-0000-0000-0000581f610c"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-00007de5be29"),
        account_number_masked="US•• •••• 5555",
        relationship_type="primary",
        jurisdiction_code="US",
        product_type="business"
    )
    db_session.add(account)
    
    transaction = Transaction(
        transaction_id=uuid.UUID("00000000-0000-0000-0000-0000b151ef9d"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-00007de5be29"),
        account_id=uuid.UUID("00000000-0000-0000-0000-0000581f610c"),
        booked_at=datetime.utcnow(),
        amount=Decimal("80000.00"),
        currency="USD",
        counterparty_name="Unresolved Corp",
        corridor="US-CH",
        generation_source="automatic"
    )
    db_session.add(transaction)
    
    alert = Alert(
        alert_id=uuid.UUID("00000000-0000-0000-0000-000053289fa5"),
        transaction_id=uuid.UUID("00000000-0000-0000-0000-0000b151ef9d"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-00007de5be29"),
        status="ESCALATED_TO_CASE",
        priority="HIGH",
        risk_score=78,
        matched_rule_codes_json=json.dumps(["RULE-001"]),
        generation="automatic",
        assigned_user_id=uuid.UUID("00000000-0000-0000-0000-00009d03d0af"),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(alert)
    
    # Case with open request and short findings
    case = AMLCase(
        case_id=uuid.UUID("00000000-0000-0000-0000-0000cd15472f"),
        case_number="CS-UNRESOLVED-001",
        source_alert_id=uuid.UUID("00000000-0000-0000-0000-000053289fa5"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-00007de5be29"),
        status="PENDING_INFORMATION",
        priority="HIGH",
        assigned_user_id=uuid.UUID("00000000-0000-0000-0000-00009d03d0af"),
        recommendation_state="DRAFT",
        recommendation_outcome="NO_FURTHER_ACTION",
        findings_summary="Too short",
        flagged_value_total=Decimal("0.00"),
        evidence_locked_for_review=False,
        created_by_user_id=uuid.UUID("00000000-0000-0000-0000-00009d03d0af"),
        handoff_officer_user_id=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(case)
    
    link = CaseAlertLink(
        case_alert_link_id="unresolved-link-1",
        case_id=uuid.UUID("00000000-0000-0000-0000-0000cd15472f"),
        alert_id=uuid.UUID("00000000-0000-0000-0000-000053289fa5"),
        linked_at=datetime.utcnow(),
        linked_by_user_id=uuid.UUID("00000000-0000-0000-0000-00009d03d0af"),
        selection_basis="Unresolved test"
    )
    db_session.add(link)
    
    # Add open request
    ir = InformationRequest(
        information_request_id=uuid.UUID("00000000-0000-0000-0000-00007f9201ac"),
        case_id=uuid.UUID("00000000-0000-0000-0000-0000cd15472f"),
        recipient_channel="EMAIL",
        requested_summary="Test unresolved information request for validation",
        rationale="Test unresolved rationale for validation purposes",
        status="OPEN",
        due_at=datetime.utcnow() + timedelta(days=2),
        response_summary=None,
        response_channel=None,
        response_received_at=None,
        created_by_user_id=uuid.UUID("00000000-0000-0000-0000-00009d03d0af"),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(ir)
    db_session.commit()
    
    handoff_service = HandoffService(db_session)
    package = handoff_service.get_handoff_package("unresolved-case-1")
    
    assert package.readiness.is_ready is False
    assert len(package.unresolved_issues) > 0
    assert any("open information request" in issue.lower() for issue in package.unresolved_issues)
    assert any("findings summary" in issue.lower() for issue in package.unresolved_issues)


def test_get_handoff_package_with_multiple_alerts(db_session):
    """Test handoff package correctly aggregates multiple linked alerts"""
    from app.models.user import User
    from app.models.customer import Customer
    from app.models.alert import Alert
    from app.models.transaction import Transaction
    from app.models.account import Account
    from app.models.aml_case import AMLCase
    from app.models.case_alert_link import CaseAlertLink
    import json
    
    user = User(
        user_id=uuid.UUID("00000000-0000-0000-0000-0000768bbf67"),
        username="multialertuser",
        display_name="Multi Alert User",
        email="multialert@example.com",
        password_hash="hashed",
        primary_role="investigator",
        is_active=True
    )
    db_session.add(user)
    
    customer = Customer(
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000bea423c0"),
        customer_name="Multi Alert Customer",
        onboarding_profile="corporate",
        risk_classification="high",
        exposure_indicators_json=json.dumps([])
    )
    db_session.add(customer)
    
    account = Account(
        account_id=uuid.UUID("00000000-0000-0000-0000-00004900e311"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000bea423c0"),
        account_number_masked="CA•• •••• 6666",
        relationship_type="primary",
        jurisdiction_code="CA",
        product_type="business"
    )
    db_session.add(account)
    
    # Create two transactions and alerts
    for i in range(2):
        transaction = Transaction(
            transaction_id=f"multi-txn-{i}",
            customer_id=uuid.UUID("00000000-0000-0000-0000-0000bea423c0"),
            account_id=uuid.UUID("00000000-0000-0000-0000-00004900e311"),
            booked_at=datetime.utcnow() + timedelta(hours=i),
            amount=Decimal(f"{100000 + i * 50000}.00"),
            currency="CAD",
            counterparty_name=f"Multi Corp {i}",
            corridor="CA-US",
            generation_source="automatic"
        )
        db_session.add(transaction)
        
        alert = Alert(
            alert_id=f"multi-alert-{i}",
            transaction_id=f"multi-txn-{i}",
            customer_id=uuid.UUID("00000000-0000-0000-0000-0000bea423c0"),
            status="ESCALATED_TO_CASE",
            priority="HIGH" if i == 0 else "CRITICAL",
            risk_score=85 + i * 5,
            matched_rule_codes_json=json.dumps(["RULE-001", "RULE-002"]),
            generation="automatic",
            assigned_user_id=uuid.UUID("00000000-0000-0000-0000-0000768bbf67"),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db_session.add(alert)
    
    case = AMLCase(
        case_id=uuid.UUID("00000000-0000-0000-0000-00003c507e2d"),
        case_number="CS-MULTI-001",
        source_alert_id=uuid.UUID("00000000-0000-0000-0000-0000ece602a5"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000bea423c0"),
        status="INVESTIGATING",
        priority="CRITICAL",
        assigned_user_id=uuid.UUID("00000000-0000-0000-0000-0000768bbf67"),
        recommendation_state="SUBMITTED",
        recommendation_outcome="ESCALATE_FOR_REVIEW",
        findings_summary="Multiple suspicious transactions identified requiring escalation to senior review team for final determination.",
        flagged_value_total=Decimal("0.00"),
        evidence_locked_for_review=False,
        created_by_user_id=uuid.UUID("00000000-0000-0000-0000-0000768bbf67"),
        handoff_officer_user_id=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(case)
    
    # Link both alerts
    for i in range(2):
        link = CaseAlertLink(
            case_alert_link_id=f"multi-link-{i}",
            case_id=uuid.UUID("00000000-0000-0000-0000-00003c507e2d"),
            alert_id=f"multi-alert-{i}",
            linked_at=datetime.utcnow(),
            linked_by_user_id=uuid.UUID("00000000-0000-0000-0000-0000768bbf67"),
            selection_basis=f"Alert {i} linked"
        )
        db_session.add(link)
    
    db_session.commit()
    
    handoff_service = HandoffService(db_session)
    package = handoff_service.get_handoff_package("multi-alert-case")
    
    assert len(package.linked_alerts) == 2
    assert package.linked_alerts[0].alert_id == "multi-alert-0"
    assert package.linked_alerts[1].alert_id == "multi-alert-1"
    assert "2 alert(s)" in package.key_evidence_summary[0]
