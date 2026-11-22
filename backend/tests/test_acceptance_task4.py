"""
Acceptance tests for TASK-4: Backend Feature B2 - Case Creation and Overview.
Verifies all acceptance criteria defined in the task.
"""
import pytest
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.customer import Customer
from app.models.account import Account
from app.models.transaction import Transaction
from app.models.alert import Alert
from app.models.aml_case import AMLCase
from app.models.case_alert_link import CaseAlertLink
from app.models.audit_event import AuditEvent
from app.models.information_request import InformationRequest


def test_fr003_case_creation_preserves_alert_identifier(auth_client: TestClient, db_session: Session):
    """
    FR-003: Case creation from an alert preserves the original alert identifier and risk context.
    """
    # Setup test data
    customer = Customer(
        customer_id=uuid.UUID("00000000-0000-0000-0000-00001d9c47f8"),
        customer_name="FR003 Customer",
        onboarding_profile="corporate",
        risk_classification="high",
        exposure_indicators_json="[]"
    )
    db_session.add(customer)
    
    account = Account(
        account_id=uuid.UUID("00000000-0000-0000-0000-0000a117a764"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-00001d9c47f8"),
        account_number_masked="XX•• •••• 0001",
        relationship_type="primary",
        jurisdiction_code="US",
        product_type="business_current"
    )
    db_session.add(account)
    
    transaction = Transaction(
        transaction_id=uuid.UUID("00000000-0000-0000-0000-0000e7ca0bd6"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-00001d9c47f8"),
        account_id=uuid.UUID("00000000-0000-0000-0000-0000a117a764"),
        booked_at=datetime.utcnow(),
        amount=Decimal("200000.00"),
        currency="USD",
        counterparty_name="Test Corp",
        corridor="US-GB",
        generation_source="automatic"
    )
    db_session.add(transaction)
    
    alert = Alert(
        alert_id=uuid.UUID("00000000-0000-0000-0000-00003dacebca"),
        transaction_id=uuid.UUID("00000000-0000-0000-0000-0000e7ca0bd6"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-00001d9c47f8"),
        status="NEW",
        priority="CRITICAL",
        risk_score=95,
        matched_rule_codes_json='["RULE-001"]',
        generation="automatic",
        assigned_user_id=None,
        triage_outcome=None,
        triage_rationale=None,
        triaged_by_user_id=None,
        triaged_at=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(alert)
    db_session.commit()
    
    # Create case from alert
    alert_uuid = "00000000-0000-0000-0000-00003dacebca"
    response = auth_client.post(
        f"/api/v1/alerts/{alert_uuid}/cases",
        json={
            "case_priority": "CRITICAL",
            "initial_rationale": "High-risk cross-border transfer requiring investigation"
        }
    )
    
    assert response.status_code == 200
    case_data = response.json()
    case_id = case_data["case_id"]
    
    # Verify alert identifier preserved in case_alert_link
    link = db_session.query(CaseAlertLink).filter(
        CaseAlertLink.case_id == case_id,
        CaseAlertLink.alert_id == uuid.UUID(alert_uuid)
    ).first()
    
    assert link is not None, "Case-alert link should exist"
    assert str(link.alert_id) == alert_uuid, "Alert identifier should be preserved"
    assert "High-risk cross-border transfer" in link.selection_basis, "Risk context should be preserved in selection basis"


def test_fr003_case_shows_linked_alert(auth_client: TestClient, db_session: Session):
    """
    FR-003: The resulting case shows the linked alert in its investigation record.
    """
    # Get test user
    user = db_session.query(User).filter(User.username == "tester").first()
    
    # Create case with linked alert
    customer = Customer(
        customer_id=uuid.UUID("00000000-0000-0000-0000-000096c458c9"),
        customer_name="FR003b Customer",
        onboarding_profile="corporate",
        risk_classification="medium",
        exposure_indicators_json="[]"
    )
    db_session.add(customer)
    
    account = Account(
        account_id=uuid.UUID("00000000-0000-0000-0000-0000d1dde5ff"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-000096c458c9"),
        account_number_masked="XX•• •••• 0002",
        relationship_type="primary",
        jurisdiction_code="GB",
        product_type="investment"
    )
    db_session.add(account)
    
    transaction = Transaction(
        transaction_id=uuid.UUID("00000000-0000-0000-0000-00003f8705eb"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-000096c458c9"),
        account_id=uuid.UUID("00000000-0000-0000-0000-0000d1dde5ff"),
        booked_at=datetime.utcnow(),
        amount=Decimal("100000.00"),
        currency="GBP",
        counterparty_name="Partner LLC",
        corridor="GB-US",
        generation_source="automatic"
    )
    db_session.add(transaction)
    
    alert = Alert(
        alert_id=uuid.UUID("00000000-0000-0000-0000-0000a4d71411"),
        transaction_id=uuid.UUID("00000000-0000-0000-0000-00003f8705eb"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-000096c458c9"),
        status="ESCALATED_TO_CASE",
        priority="HIGH",
        risk_score=85,
        matched_rule_codes_json='["RULE-002"]',
        generation="automatic",
        assigned_user_id=user.user_id,
        triage_outcome=None,
        triage_rationale=None,
        triaged_by_user_id=None,
        triaged_at=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(alert)
    
    case = AMLCase(
        case_id=uuid.UUID("00000000-0000-0000-0000-00009b5299f9"),
        case_number="CS-FR003B",
        source_alert_id=uuid.UUID("00000000-0000-0000-0000-0000a4d71411"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-000096c458c9"),
        status="INVESTIGATING",
        priority="HIGH",
        assigned_user_id=user.user_id,
        recommendation_state="DRAFT",
        recommendation_outcome=None,
        findings_summary=None,
        flagged_value_total=Decimal("100000.00"),
        evidence_locked_for_review=False,
        created_by_user_id=user.user_id,
        handoff_officer_user_id=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(case)
    
    link = CaseAlertLink(
        case_alert_link_id=uuid.uuid4(),
        case_id=uuid.UUID("00000000-0000-0000-0000-00009b5299f9"),
        alert_id=uuid.UUID("00000000-0000-0000-0000-0000a4d71411"),
        linked_at=datetime.utcnow(),
        linked_by_user_id=user.user_id,
        selection_basis="Test link"
    )
    db_session.add(link)
    db_session.commit()
    
    # Get case overview
    case_uuid = "00000000-0000-0000-0000-00009b5299f9"
    response = auth_client.get(f"/api/v1/cases/{case_uuid}")
    assert response.status_code == 200
    
    overview = response.json()
    assert overview["linked_alert_count"] == 1, "Case overview should show linked alert count"


def test_fr003_triage_stores_auditable_rationale(auth_client: TestClient, db_session: Session):
    """
    FR-003: The triage action stores an auditable rationale or status basis for the escalation.
    """
    # Setup
    customer = Customer(
        customer_id=uuid.UUID("00000000-0000-0000-0000-00003da648b9"),
        customer_name="FR003c Customer",
        onboarding_profile="corporate",
        risk_classification="low",
        exposure_indicators_json="[]"
    )
    db_session.add(customer)
    
    account = Account(
        account_id=uuid.UUID("00000000-0000-0000-0000-0000084435ea"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-00003da648b9"),
        account_number_masked="XX•• •••• 0003",
        relationship_type="primary",
        jurisdiction_code="CA",
        product_type="business_current"
    )
    db_session.add(account)
    
    transaction = Transaction(
        transaction_id=uuid.UUID("00000000-0000-0000-0000-0000f7773fa4"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-00003da648b9"),
        account_id=uuid.UUID("00000000-0000-0000-0000-0000084435ea"),
        booked_at=datetime.utcnow(),
        amount=Decimal("50000.00"),
        currency="CAD",
        counterparty_name="Northern Inc",
        corridor="CA-US",
        generation_source="automatic"
    )
    db_session.add(transaction)
    
    alert = Alert(
        alert_id=uuid.UUID("00000000-0000-0000-0000-00008c54b4e2"),
        transaction_id=uuid.UUID("00000000-0000-0000-0000-0000f7773fa4"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-00003da648b9"),
        status="NEW",
        priority="MEDIUM",
        risk_score=70,
        matched_rule_codes_json='["RULE-001"]',
        generation="automatic",
        assigned_user_id=None,
        triage_outcome=None,
        triage_rationale=None,
        triaged_by_user_id=None,
        triaged_at=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(alert)
    db_session.commit()
    
    # Create case with rationale
    rationale = "Suspicious pattern detected requiring deeper investigation"
    alert_uuid = "00000000-0000-0000-0000-00008c54b4e2"
    response = auth_client.post(
        f"/api/v1/alerts/{alert_uuid}/cases",
        json={
            "case_priority": "MEDIUM",
            "initial_rationale": rationale
        }
    )
    
    assert response.status_code == 200
    case_data = response.json()
    
    # Verify audit event created with rationale
    audit_event = db_session.query(AuditEvent).filter(
        AuditEvent.entity_type == "alert",
        AuditEvent.entity_id == alert_uuid,
        AuditEvent.action_type == "ALERT_LINKED_TO_CASE"
    ).first()
    
    assert audit_event is not None, "Audit event should exist"
    assert audit_event.actor_user_id is not None, "Actor should be recorded"
    
    # Verify rationale stored in case_alert_link
    link = db_session.query(CaseAlertLink).filter(
        CaseAlertLink.alert_id == uuid.UUID(alert_uuid)
    ).first()
    assert link is not None
    assert link.selection_basis == rationale, "Rationale should be stored in selection_basis"


def test_fr006_overview_shows_metadata_and_counts(auth_client: TestClient, db_session: Session):
    """
    FR-006: The overview shows case metadata and linked alert count on first load.
    """
    user = db_session.query(User).filter(User.username == "tester").first()
    
    # Create case with metadata
    customer = Customer(
        customer_id=uuid.UUID("00000000-0000-0000-0000-000061b2662c"),
        customer_name="FR006 Customer",
        onboarding_profile="corporate",
        risk_classification="high",
        exposure_indicators_json="[]"
    )
    db_session.add(customer)
    
    account = Account(
        account_id=uuid.UUID("00000000-0000-0000-0000-00004db51e62"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-000061b2662c"),
        account_number_masked="XX•• •••• 0004",
        relationship_type="primary",
        jurisdiction_code="US",
        product_type="investment"
    )
    db_session.add(account)
    
    transaction = Transaction(
        transaction_id=uuid.UUID("00000000-0000-0000-0000-0000a38fe0df"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-000061b2662c"),
        account_id=uuid.UUID("00000000-0000-0000-0000-00004db51e62"),
        booked_at=datetime.utcnow(),
        amount=Decimal("150000.00"),
        currency="USD",
        counterparty_name="Global Corp",
        corridor="US-SG",
        generation_source="automatic"
    )
    db_session.add(transaction)
    
    alert = Alert(
        alert_id=uuid.UUID("00000000-0000-0000-0000-0000cf4d6749"),
        transaction_id=uuid.UUID("00000000-0000-0000-0000-0000a38fe0df"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-000061b2662c"),
        status="ESCALATED_TO_CASE",
        priority="HIGH",
        risk_score=88,
        matched_rule_codes_json='["RULE-001", "RULE-002"]',
        generation="automatic",
        assigned_user_id=user.user_id,
        triage_outcome=None,
        triage_rationale=None,
        triaged_by_user_id=None,
        triaged_at=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(alert)
    
    case = AMLCase(
        case_id=uuid.UUID("00000000-0000-0000-0000-0000c0ae9c71"),
        case_number="CS-FR006",
        source_alert_id=uuid.UUID("00000000-0000-0000-0000-0000cf4d6749"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-000061b2662c"),
        status="INVESTIGATING",
        priority="HIGH",
        assigned_user_id=user.user_id,
        recommendation_state="DRAFT",
        recommendation_outcome=None,
        findings_summary=None,
        flagged_value_total=Decimal("150000.00"),
        evidence_locked_for_review=False,
        created_by_user_id=user.user_id,
        handoff_officer_user_id=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(case)
    
    link = CaseAlertLink(
        case_alert_link_id=uuid.uuid4(),
        case_id=uuid.UUID("00000000-0000-0000-0000-0000c0ae9c71"),
        alert_id=uuid.UUID("00000000-0000-0000-0000-0000cf4d6749"),
        linked_at=datetime.utcnow(),
        linked_by_user_id=user.user_id,
        selection_basis="FR006 test"
    )
    db_session.add(link)
    db_session.commit()
    
    # Get overview
    case_uuid = "00000000-0000-0000-0000-0000c0ae9c71"
    response = auth_client.get(f"/api/v1/cases/{case_uuid}")
    assert response.status_code == 200
    
    overview = response.json()
    assert overview["case_id"] == case_uuid
    assert overview["case_number"] == "CS-FR006"
    assert overview["status"] == "INVESTIGATING"
    assert overview["priority"] == "HIGH"
    assert overview["assigned_user_id"] == user.user_id
    assert overview["linked_alert_count"] == 1


def test_fr006_aggregated_flagged_value_calculated(auth_client: TestClient, db_session: Session):
    """
    FR-006: Aggregated flagged value is calculated from linked alert or transaction data.
    """
    user = db_session.query(User).filter(User.username == "tester").first()
    
    # Create case with transaction
    customer = Customer(
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000153cef72"),
        customer_name="FR006b Customer",
        onboarding_profile="corporate",
        risk_classification="medium",
        exposure_indicators_json="[]"
    )
    db_session.add(customer)
    
    account = Account(
        account_id=uuid.UUID("00000000-0000-0000-0000-0000e9b7cea3"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000153cef72"),
        account_number_masked="XX•• •••• 0005",
        relationship_type="primary",
        jurisdiction_code="GB",
        product_type="business_current"
    )
    db_session.add(account)
    
    transaction = Transaction(
        transaction_id=uuid.UUID("00000000-0000-0000-0000-00005d3d31da"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000153cef72"),
        account_id=uuid.UUID("00000000-0000-0000-0000-0000e9b7cea3"),
        booked_at=datetime.utcnow(),
        amount=Decimal("75000.50"),
        currency="GBP",
        counterparty_name="UK Partner",
        corridor="GB-US",
        generation_source="automatic"
    )
    db_session.add(transaction)
    
    alert = Alert(
        alert_id=uuid.UUID("00000000-0000-0000-0000-000040086e2b"),
        transaction_id=uuid.UUID("00000000-0000-0000-0000-00005d3d31da"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000153cef72"),
        status="ESCALATED_TO_CASE",
        priority="MEDIUM",
        risk_score=72,
        matched_rule_codes_json='["RULE-002"]',
        generation="automatic",
        assigned_user_id=user.user_id,
        triage_outcome=None,
        triage_rationale=None,
        triaged_by_user_id=None,
        triaged_at=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(alert)
    
    case = AMLCase(
        case_id=uuid.UUID("00000000-0000-0000-0000-0000bb5afa0d"),
        case_number="CS-FR006B",
        source_alert_id=uuid.UUID("00000000-0000-0000-0000-000040086e2b"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000153cef72"),
        status="INVESTIGATING",
        priority="MEDIUM",
        assigned_user_id=user.user_id,
        recommendation_state="DRAFT",
        recommendation_outcome=None,
        findings_summary=None,
        flagged_value_total=Decimal("0.00"),
        evidence_locked_for_review=False,
        created_by_user_id=user.user_id,
        handoff_officer_user_id=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(case)
    
    link = CaseAlertLink(
        case_alert_link_id=uuid.uuid4(),
        case_id=uuid.UUID("00000000-0000-0000-0000-0000bb5afa0d"),
        alert_id=uuid.UUID("00000000-0000-0000-0000-000040086e2b"),
        linked_at=datetime.utcnow(),
        linked_by_user_id=user.user_id,
        selection_basis="FR006b test"
    )
    db_session.add(link)
    db_session.commit()
    
    # Get overview
    case_uuid = "00000000-0000-0000-0000-0000bb5afa0d"
    response = auth_client.get(f"/api/v1/cases/{case_uuid}")
    assert response.status_code == 200
    
    overview = response.json()
    # Flagged value should be calculated from linked transaction
    assert overview["flagged_value_total"] == 75000.50


def test_fr006_recent_activity_includes_workflow_events(auth_client: TestClient, db_session: Session):
    """
    FR-006: Recent activity includes the latest notes, assignment changes, and workflow events.
    """
    user = db_session.query(User).filter(User.username == "tester").first()
    
    # Create case with audit events
    customer = Customer(
        customer_id=uuid.UUID("00000000-0000-0000-0000-000063f56d3e"),
        customer_name="FR006c Customer",
        onboarding_profile="corporate",
        risk_classification="low",
        exposure_indicators_json="[]"
    )
    db_session.add(customer)
    
    account = Account(
        account_id=uuid.UUID("00000000-0000-0000-0000-00005f5614e2"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-000063f56d3e"),
        account_number_masked="XX•• •••• 0006",
        relationship_type="primary",
        jurisdiction_code="CA",
        product_type="investment"
    )
    db_session.add(account)
    
    transaction = Transaction(
        transaction_id=uuid.UUID("00000000-0000-0000-0000-0000c66ea1ba"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-000063f56d3e"),
        account_id=uuid.UUID("00000000-0000-0000-0000-00005f5614e2"),
        booked_at=datetime.utcnow(),
        amount=Decimal("30000.00"),
        currency="CAD",
        counterparty_name="Northern LLC",
        corridor="CA-US",
        generation_source="automatic"
    )
    db_session.add(transaction)
    
    alert = Alert(
        alert_id=uuid.UUID("00000000-0000-0000-0000-0000c3edf886"),
        transaction_id=uuid.UUID("00000000-0000-0000-0000-0000c66ea1ba"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-000063f56d3e"),
        status="ESCALATED_TO_CASE",
        priority="LOW",
        risk_score=55,
        matched_rule_codes_json='["RULE-001"]',
        generation="automatic",
        assigned_user_id=user.user_id,
        triage_outcome=None,
        triage_rationale=None,
        triaged_by_user_id=None,
        triaged_at=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(alert)
    
    case = AMLCase(
        case_id=uuid.UUID("00000000-0000-0000-0000-0000a52749fb"),
        case_number="CS-FR006C",
        source_alert_id=uuid.UUID("00000000-0000-0000-0000-0000c3edf886"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-000063f56d3e"),
        status="INVESTIGATING",
        priority="LOW",
        assigned_user_id=user.user_id,
        recommendation_state="DRAFT",
        recommendation_outcome=None,
        findings_summary=None,
        flagged_value_total=Decimal("30000.00"),
        evidence_locked_for_review=False,
        created_by_user_id=user.user_id,
        handoff_officer_user_id=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(case)
    
    link = CaseAlertLink(
        case_alert_link_id="link-fr006c",
        case_id=uuid.UUID("00000000-0000-0000-0000-0000a52749fb"),
        alert_id=uuid.UUID("00000000-0000-0000-0000-0000c3edf886"),
        linked_at=datetime.utcnow(),
        linked_by_user_id=user.user_id,
        selection_basis="FR006c test"
    )
    db_session.add(link)
    
    # Add audit events
    event1 = AuditEvent(
        audit_event_id=uuid.uuid4(),
        entity_type="case",
        entity_id="00000000-0000-0000-0000-0000a52749fb",
        action_type="CASE_CREATED",
        actor_user_id=str(user.user_id),
        actor_role="investigator",
        correlation_id=str(uuid.uuid4()),
        payload_json='{"test": "data"}',
        occurred_at=datetime.utcnow(),
        created_at=datetime.utcnow()
    )
    db_session.add(event1)
    
    event2 = AuditEvent(
        audit_event_id=uuid.uuid4(),
        entity_type="case",
        entity_id="00000000-0000-0000-0000-0000a52749fb",
        action_type="CASE_ASSIGNED",
        actor_user_id=str(user.user_id),
        actor_role="investigator",
        correlation_id=str(uuid.uuid4()),
        payload_json='{"assigned_to": "' + str(user.user_id) + '"}',
        occurred_at=datetime.utcnow(),
        created_at=datetime.utcnow()
    )
    db_session.add(event2)
    db_session.commit()
    
    # Get overview
    case_uuid = "00000000-0000-0000-0000-0000a52749fb"
    response = auth_client.get(f"/api/v1/cases/{case_uuid}")
    assert response.status_code == 200
    
    overview = response.json()
    assert "recent_activity" in overview
    assert len(overview["recent_activity"]) >= 1
    
    # Verify activity structure
    for activity in overview["recent_activity"]:
        assert "event_id" in activity
        assert "event_type" in activity
        assert "occurred_at" in activity
        assert "actor_display" in activity
        assert "summary" in activity
