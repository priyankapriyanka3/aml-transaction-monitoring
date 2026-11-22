"""
Unit tests for CaseService.
Tests case creation and overview assembly.
"""
import pytest
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from app.services.case_service import CaseService
from app.models.user import User
from app.models.customer import Customer
from app.models.account import Account
from app.models.transaction import Transaction
from app.models.alert import Alert
from app.models.aml_case import AMLCase
from app.models.case_alert_link import CaseAlertLink
from app.models.information_request import InformationRequest
from app.models.audit_event import AuditEvent


def test_create_case_from_alert_success(db_session: Session):
    """Test successful case creation from alert"""
    # Create test user
    user = User(
        user_id=uuid.UUID("00000000-0000-0000-0000-000037c27b2e"),
        username="testuser",
        display_name="Test User",
        email="test@example.com",
        password_hash="hashed",
        primary_role="investigator",
        is_active=True
    )
    db_session.add(user)
    
    # Create test customer
    customer = Customer(
        customer_id=uuid.UUID("00000000-0000-0000-0000-00003b75abcd"),
        customer_name="Test Customer",
        onboarding_profile="corporate",
        risk_classification="high",
        exposure_indicators_json="[]"
    )
    db_session.add(customer)
    
    # Create test account
    account = Account(
        account_id=uuid.UUID("00000000-0000-0000-0000-00001e6716ef"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-00003b75abcd"),
        account_number_masked="GB•• •••• 1234",
        relationship_type="primary",
        jurisdiction_code="GB",
        product_type="business_current"
    )
    db_session.add(account)
    
    # Create test transaction
    transaction = Transaction(
        transaction_id=uuid.UUID("00000000-0000-0000-0000-000099fefac0"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-00003b75abcd"),
        account_id=uuid.UUID("00000000-0000-0000-0000-00001e6716ef"),
        booked_at=datetime.utcnow(),
        amount=Decimal("100000.00"),
        currency="USD",
        counterparty_name="Test Counterparty",
        corridor="GB-US",
        generation_source="automatic"
    )
    db_session.add(transaction)
    
    # Create test alert
    alert = Alert(
        alert_id=uuid.UUID("00000000-0000-0000-0000-000026d3b272"),
        transaction_id=uuid.UUID("00000000-0000-0000-0000-000099fefac0"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-00003b75abcd"),
        status="NEW",
        priority="HIGH",
        risk_score=85,
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
    service = CaseService(db_session)
    case_id, case_number = service.create_case_from_alert(
        alert_id=uuid.UUID("00000000-0000-0000-0000-000026d3b272"),
        case_priority="HIGH",
        initial_rationale="Test rationale",
        actor_id=uuid.UUID("00000000-0000-0000-0000-000037c27b2e")
    )
    
    # Verify case created
    assert case_id is not None
    assert case_number is not None
    assert case_number.startswith("CS-")
    
    # Verify case in database
    case = db_session.query(AMLCase).filter(AMLCase.case_id == uuid.UUID(case_id)).first()
    assert case is not None
    assert case.case_number == case_number
    assert case.source_alert_id == uuid.UUID("00000000-0000-0000-0000-000026d3b272")
    assert case.customer_id == uuid.UUID("00000000-0000-0000-0000-00003b75abcd")
    assert case.status == "INVESTIGATING"
    assert case.priority == "HIGH"
    assert case.assigned_user_id == uuid.UUID("00000000-0000-0000-0000-000037c27b2e")
    assert case.created_by_user_id == uuid.UUID("00000000-0000-0000-0000-000037c27b2e")
    
    # Verify case-alert link created
    link = db_session.query(CaseAlertLink).filter(
        CaseAlertLink.case_id == uuid.UUID(case_id),
        CaseAlertLink.alert_id == uuid.UUID("00000000-0000-0000-0000-000026d3b272")
    ).first()
    assert link is not None
    assert link.selection_basis == "Test rationale"
    
    # Verify alert status updated
    updated_alert = db_session.query(Alert).filter(Alert.alert_id == uuid.UUID("00000000-0000-0000-0000-000026d3b272")).first()
    assert updated_alert.status == "ESCALATED_TO_CASE"
    
    # Verify audit events created
    case_created_event = db_session.query(AuditEvent).filter(
        AuditEvent.entity_type == "case",
        AuditEvent.entity_id == case_id,
        AuditEvent.action_type == "CASE_CREATED"
    ).first()
    assert case_created_event is not None
    assert case_created_event.actor_user_id == uuid.UUID("00000000-0000-0000-0000-000037c27b2e")
    
    alert_linked_event = db_session.query(AuditEvent).filter(
        AuditEvent.entity_type == "alert",
        AuditEvent.entity_id == str(uuid.UUID("00000000-0000-0000-0000-000026d3b272")),
        AuditEvent.action_type == "ALERT_LINKED_TO_CASE"
    ).first()
    assert alert_linked_event is not None


def test_create_case_from_alert_alert_not_found(db_session: Session):
    """Test case creation fails when alert doesn't exist"""
    # Create test user
    user = User(
        user_id=uuid.UUID("00000000-0000-0000-0000-000000d5f49c"),
        username="testuser2",
        display_name="Test User 2",
        email="test2@example.com",
        password_hash="hashed",
        primary_role="investigator",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    
    service = CaseService(db_session)
    
    with pytest.raises(ValueError, match="Alert not found"):
        service.create_case_from_alert(
            alert_id=uuid.UUID("00000000-0000-0000-0000-0000a4ec8bc5"),
            case_priority="HIGH",
            initial_rationale="Test rationale",
            actor_id=uuid.UUID("00000000-0000-0000-0000-000037c27b2e")
        )


def test_get_case_overview_success(db_session: Session):
    """Test successful case overview retrieval with aggregations"""
    # Create test data
    user = User(
        user_id=uuid.UUID("00000000-0000-0000-0000-0000bc346d48"),
        username="testuser3",
        display_name="Test User 3",
        email="test3@example.com",
        password_hash="hashed",
        primary_role="investigator",
        is_active=True
    )
    db_session.add(user)
    
    customer = Customer(
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000a3908d6f"),
        customer_name="Test Customer 2",
        onboarding_profile="corporate",
        risk_classification="medium",
        exposure_indicators_json="[]"
    )
    db_session.add(customer)
    
    account = Account(
        account_id=uuid.UUID("00000000-0000-0000-0000-0000a15b3a46"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000a3908d6f"),
        account_number_masked="US•• •••• 5678",
        relationship_type="primary",
        jurisdiction_code="US",
        product_type="investment"
    )
    db_session.add(account)
    
    transaction = Transaction(
        transaction_id=uuid.UUID("00000000-0000-0000-0000-000026679522"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000a3908d6f"),
        account_id=uuid.UUID("00000000-0000-0000-0000-0000a15b3a46"),
        booked_at=datetime.utcnow(),
        amount=Decimal("50000.00"),
        currency="USD",
        counterparty_name="Test Corp",
        corridor="US-CA",
        generation_source="automatic"
    )
    db_session.add(transaction)
    
    alert = Alert(
        alert_id=uuid.UUID("00000000-0000-0000-0000-0000587a1a9c"),
        transaction_id=uuid.UUID("00000000-0000-0000-0000-000026679522"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000a3908d6f"),
        status="ESCALATED_TO_CASE",
        priority="MEDIUM",
        risk_score=70,
        matched_rule_codes_json='["RULE-002"]',
        generation="automatic",
        assigned_user_id=uuid.UUID("00000000-0000-0000-0000-0000bc346d48"),
        triage_outcome=None,
        triage_rationale=None,
        triaged_by_user_id=None,
        triaged_at=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(alert)
    
    case = AMLCase(
        case_id=uuid.UUID("00000000-0000-0000-0000-0000d8da0809"),
        case_number="CS-TEST-001",
        source_alert_id=uuid.UUID("00000000-0000-0000-0000-0000587a1a9c"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000a3908d6f"),
        status="INVESTIGATING",
        priority="MEDIUM",
        assigned_user_id=uuid.UUID("00000000-0000-0000-0000-0000bc346d48"),
        recommendation_state="DRAFT",
        recommendation_outcome=None,
        findings_summary=None,
        flagged_value_total=Decimal("50000.00"),
        evidence_locked_for_review=False,
        created_by_user_id=uuid.UUID("00000000-0000-0000-0000-0000bc346d48"),
        handoff_officer_user_id=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(case)
    
    link = CaseAlertLink(
        case_alert_link_id="link-test-001",
        case_id=uuid.UUID("00000000-0000-0000-0000-0000d8da0809"),
        alert_id=uuid.UUID("00000000-0000-0000-0000-0000587a1a9c"),
        linked_at=datetime.utcnow(),
        linked_by_user_id=uuid.UUID("00000000-0000-0000-0000-0000bc346d48"),
        selection_basis="Test link"
    )
    db_session.add(link)
    
    # Add an audit event
    event = AuditEvent(
        audit_event_id=uuid.uuid4(),
        entity_type="case",
        entity_id=uuid.UUID("00000000-0000-0000-0000-0000d8da0809"),
        action_type="CASE_CREATED",
        actor_user_id=uuid.UUID("00000000-0000-0000-0000-0000bc346d48"),
        actor_role="investigator",
        correlation_id=str(uuid.uuid4()),
        payload_json='{"test": "data"}',
        occurred_at=datetime.utcnow(),
        created_at=datetime.utcnow()
    )
    db_session.add(event)
    
    db_session.commit()
    
    # Get case overview
    service = CaseService(db_session)
    overview = service.get_case_overview("case-test-001")
    
    # Verify overview data
    assert overview.case_id == "case-test-001"
    assert overview.case_number == "CS-TEST-001"
    assert overview.status == "INVESTIGATING"
    assert overview.priority == "MEDIUM"
    assert overview.assigned_user_id == "usr-test-003"
    assert overview.assigned_user_name == "Test User 3"
    assert overview.recommendation_state == "DRAFT"
    assert overview.linked_alert_count == 1
    assert overview.flagged_value_total == 50000.00
    assert overview.open_information_request_count == 0
    assert overview.overdue_information_request_count == 0
    assert len(overview.recent_activity) == 1
    assert overview.recent_activity[0]["event_type"] == "CASE_CREATED"


def test_get_case_overview_case_not_found(db_session: Session):
    """Test case overview fails when case doesn't exist"""
    service = CaseService(db_session)
    
    with pytest.raises(ValueError, match="Case not found"):
        service.get_case_overview("nonexistent-case")


def test_case_overview_with_information_requests(db_session: Session):
    """Test case overview correctly counts open and overdue requests"""
    # Create minimal test data
    user = User(
        user_id=uuid.UUID("00000000-0000-0000-0000-00007d29b7d7"),
        username="testuser4",
        display_name="Test User 4",
        email="test4@example.com",
        password_hash="hashed",
        primary_role="investigator",
        is_active=True
    )
    db_session.add(user)
    
    customer = Customer(
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000c142d0e8"),
        customer_name="Test Customer 3",
        onboarding_profile="corporate",
        risk_classification="low",
        exposure_indicators_json="[]"
    )
    db_session.add(customer)
    
    account = Account(
        account_id=uuid.UUID("00000000-0000-0000-0000-0000e9bf5496"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000c142d0e8"),
        account_number_masked="CA•• •••• 9012",
        relationship_type="primary",
        jurisdiction_code="CA",
        product_type="business_current"
    )
    db_session.add(account)
    
    transaction = Transaction(
        transaction_id=uuid.UUID("00000000-0000-0000-0000-0000dab8951a"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000c142d0e8"),
        account_id=uuid.UUID("00000000-0000-0000-0000-0000e9bf5496"),
        booked_at=datetime.utcnow(),
        amount=Decimal("25000.00"),
        currency="CAD",
        counterparty_name="Test Partner",
        corridor="CA-US",
        generation_source="automatic"
    )
    db_session.add(transaction)
    
    alert = Alert(
        alert_id=uuid.UUID("00000000-0000-0000-0000-0000c0c43f8c"),
        transaction_id=uuid.UUID("00000000-0000-0000-0000-0000dab8951a"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000c142d0e8"),
        status="ESCALATED_TO_CASE",
        priority="LOW",
        risk_score=50,
        matched_rule_codes_json='["RULE-001"]',
        generation="automatic",
        assigned_user_id=uuid.UUID("00000000-0000-0000-0000-00007d29b7d7"),
        triage_outcome=None,
        triage_rationale=None,
        triaged_by_user_id=None,
        triaged_at=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(alert)
    
    case = AMLCase(
        case_id=uuid.UUID("00000000-0000-0000-0000-00007119b227"),
        case_number="CS-TEST-002",
        source_alert_id=uuid.UUID("00000000-0000-0000-0000-0000c0c43f8c"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000c142d0e8"),
        status="PENDING_INFORMATION",
        priority="LOW",
        assigned_user_id=uuid.UUID("00000000-0000-0000-0000-00007d29b7d7"),
        recommendation_state="DRAFT",
        recommendation_outcome=None,
        findings_summary=None,
        flagged_value_total=Decimal("25000.00"),
        evidence_locked_for_review=False,
        created_by_user_id=uuid.UUID("00000000-0000-0000-0000-00007d29b7d7"),
        handoff_officer_user_id=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(case)
    
    link = CaseAlertLink(
        case_alert_link_id="link-test-002",
        case_id=uuid.UUID("00000000-0000-0000-0000-00007119b227"),
        alert_id=uuid.UUID("00000000-0000-0000-0000-0000c0c43f8c"),
        linked_at=datetime.utcnow(),
        linked_by_user_id=uuid.UUID("00000000-0000-0000-0000-00007d29b7d7"),
        selection_basis="Test link"
    )
    db_session.add(link)
    
    # Add open request
    open_request = InformationRequest(
        information_request_id=uuid.UUID("00000000-0000-0000-0000-0000e8e3824f"),
        case_id=uuid.UUID("00000000-0000-0000-0000-00007119b227"),
        recipient_channel="EMAIL",
        requested_summary="Need more info",
        rationale="Investigation requires additional details",
        status="OPEN",
        due_at=datetime.utcnow() + timedelta(days=3),
        response_summary=None,
        response_channel=None,
        response_received_at=None,
        created_by_user_id=uuid.UUID("00000000-0000-0000-0000-00007d29b7d7"),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(open_request)
    
    # Add overdue request
    overdue_request = InformationRequest(
        information_request_id=uuid.UUID("00000000-0000-0000-0000-0000d7939a8d"),
        case_id=uuid.UUID("00000000-0000-0000-0000-00007119b227"),
        recipient_channel="PORTAL",
        requested_summary="Overdue info",
        rationale="Urgent information needed",
        status="OPEN",
        due_at=datetime.utcnow() - timedelta(days=2),
        response_summary=None,
        response_channel=None,
        response_received_at=None,
        created_by_user_id=uuid.UUID("00000000-0000-0000-0000-00007d29b7d7"),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(overdue_request)
    
    db_session.commit()
    
    # Get case overview
    service = CaseService(db_session)
    overview = service.get_case_overview("case-test-002")
    
    # Verify request counts
    assert overview.open_information_request_count == 2
    assert overview.overdue_information_request_count == 1
