"""
Integration tests for case endpoints.
Tests POST /api/v1/alerts/{alert_id}/cases and GET /api/v1/cases/{case_id}.
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


def test_create_case_from_alert_success(client: TestClient, db_session: Session, auth_client: TestClient):
    """Test successful case creation from alert endpoint"""
    # Create test customer, account, transaction, alert
    customer = Customer(
        customer_id=uuid.UUID("00000000-0000-0000-0000-000074d14194"),
        customer_name="Integration Customer",
        onboarding_profile="corporate",
        risk_classification="high",
        exposure_indicators_json="[]"
    )
    db_session.add(customer)
    
    account = Account(
        account_id=uuid.UUID("00000000-0000-0000-0000-00007994f82c"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-000074d14194"),
        account_number_masked="GB•• •••• 1111",
        relationship_type="primary",
        jurisdiction_code="GB",
        product_type="business_current"
    )
    db_session.add(account)
    
    transaction = Transaction(
        transaction_id=uuid.UUID("00000000-0000-0000-0000-0000b857f7d9"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-000074d14194"),
        account_id=uuid.UUID("00000000-0000-0000-0000-00007994f82c"),
        booked_at=datetime.utcnow(),
        amount=Decimal("150000.00"),
        currency="USD",
        counterparty_name="Test Corp",
        corridor="GB-US",
        generation_source="automatic"
    )
    db_session.add(transaction)
    
    alert = Alert(
        alert_id=uuid.UUID("00000000-0000-0000-0000-0000c507340f"),
        transaction_id=uuid.UUID("00000000-0000-0000-0000-0000b857f7d9"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-000074d14194"),
        status="NEW",
        priority="HIGH",
        risk_score=90,
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
    
    # Create case via endpoint
    response = auth_client.post(
        "/api/v1/alerts/00000000-0000-0000-0000-0000c507340f/cases",
        json={
            "case_priority": "HIGH",
            "initial_rationale": "Integration test case creation"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "case_id" in data
    assert "case_number" in data
    assert data["case_number"].startswith("CS-")
    assert data["source_alert_id"] == "00000000-0000-0000-0000-0000c507340f"
    assert data["status"] == "INVESTIGATING"
    
    # Verify case in database
    case = db_session.query(AMLCase).filter(AMLCase.case_id == uuid.UUID(data["case_id"])).first()
    assert case is not None
    assert case.status == "INVESTIGATING"
    assert case.priority == "HIGH"


def test_create_case_from_nonexistent_alert(client: TestClient, auth_client: TestClient):
    """Test case creation fails for nonexistent alert"""
    response = auth_client.post(
        "/api/v1/alerts/nonexistent-alert/cases",
        json={
            "case_priority": "MEDIUM",
            "initial_rationale": "Should fail"
        }
    )
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_create_case_requires_authentication(client: TestClient, db_session: Session):
    """Test case creation requires authentication"""
    # Create alert
    customer = Customer(
        customer_id=uuid.UUID("00000000-0000-0000-0000-00006a2283b0"),
        customer_name="Customer 2",
        onboarding_profile="corporate",
        risk_classification="medium",
        exposure_indicators_json="[]"
    )
    db_session.add(customer)
    
    account = Account(
        account_id=uuid.UUID("00000000-0000-0000-0000-000093ba0c77"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-00006a2283b0"),
        account_number_masked="US•• •••• 2222",
        relationship_type="primary",
        jurisdiction_code="US",
        product_type="investment"
    )
    db_session.add(account)
    
    transaction = Transaction(
        transaction_id=uuid.UUID("00000000-0000-0000-0000-0000a6fa7868"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-00006a2283b0"),
        account_id=uuid.UUID("00000000-0000-0000-0000-000093ba0c77"),
        booked_at=datetime.utcnow(),
        amount=Decimal("75000.00"),
        currency="USD",
        counterparty_name="Partner LLC",
        corridor="US-CA",
        generation_source="automatic"
    )
    db_session.add(transaction)
    
    alert = Alert(
        alert_id=uuid.UUID("00000000-0000-0000-0000-000022b0fd74"),
        transaction_id=uuid.UUID("00000000-0000-0000-0000-0000a6fa7868"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-00006a2283b0"),
        status="NEW",
        priority="MEDIUM",
        risk_score=65,
        matched_rule_codes_json='["RULE-002"]',
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
    
    # Attempt without auth
    response = client.post(
        "/api/v1/alerts/alert-int-002/cases",
        json={
            "case_priority": "MEDIUM",
            "initial_rationale": "Should require auth"
        }
    )
    
    assert response.status_code == 401


def test_get_case_overview_success(client: TestClient, db_session: Session, auth_client: TestClient):
    """Test successful case overview retrieval"""
    # Get test user created by auth_client fixture
    user = db_session.query(User).filter(User.username == "tester").first()
    assert user is not None, "Test user should exist from auth_client fixture"
    
    # Create test data
    customer = Customer(
        customer_id=uuid.UUID("00000000-0000-0000-0000-000085bb85d1"),
        customer_name="Overview Customer",
        onboarding_profile="corporate",
        risk_classification="low",
        exposure_indicators_json="[]"
    )
    db_session.add(customer)
    
    account = Account(
        account_id=uuid.UUID("00000000-0000-0000-0000-00004558f198"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-000085bb85d1"),
        account_number_masked="CA•• •••• 3333",
        relationship_type="primary",
        jurisdiction_code="CA",
        product_type="business_current"
    )
    db_session.add(account)
    
    transaction = Transaction(
        transaction_id=uuid.UUID("00000000-0000-0000-0000-0000bc8019d1"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-000085bb85d1"),
        account_id=uuid.UUID("00000000-0000-0000-0000-00004558f198"),
        booked_at=datetime.utcnow(),
        amount=Decimal("30000.00"),
        currency="CAD",
        counterparty_name="Northern Inc",
        corridor="CA-US",
        generation_source="automatic"
    )
    db_session.add(transaction)
    
    alert = Alert(
        alert_id=uuid.UUID("00000000-0000-0000-0000-0000eda68818"),
        transaction_id=uuid.UUID("00000000-0000-0000-0000-0000bc8019d1"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-000085bb85d1"),
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
        case_id=uuid.UUID("00000000-0000-0000-0000-00007a607434"),
        case_number="CS-INT-001",
        source_alert_id=uuid.UUID("00000000-0000-0000-0000-0000eda68818"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-000085bb85d1"),
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
        case_alert_link_id="link-int-001",
        case_id=uuid.UUID("00000000-0000-0000-0000-00007a607434"),
        alert_id=uuid.UUID("00000000-0000-0000-0000-0000eda68818"),
        linked_at=datetime.utcnow(),
        linked_by_user_id=user.user_id,
        selection_basis="Integration test link"
    )
    db_session.add(link)
    db_session.commit()
    
    # Get case overview
    response = auth_client.get("/api/v1/cases/case-int-001")
    
    assert response.status_code == 200
    data = response.json()
    assert data["case_id"] == "case-int-001"
    assert data["case_number"] == "CS-INT-001"
    assert data["status"] == "INVESTIGATING"
    assert data["priority"] == "LOW"
    assert data["assigned_user_id"] == user.user_id
    assert data["assigned_user_name"] is not None
    assert data["recommendation_state"] == "DRAFT"
    assert data["linked_alert_count"] == 1
    assert data["flagged_value_total"] == 30000.00
    assert data["open_information_request_count"] == 0
    assert data["overdue_information_request_count"] == 0
    assert isinstance(data["recent_activity"], list)


def test_get_case_overview_not_found(client: TestClient, auth_client: TestClient):
    """Test case overview returns 404 for nonexistent case"""
    response = auth_client.get("/api/v1/cases/nonexistent-case")
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_get_case_overview_requires_authentication(client: TestClient, db_session: Session):
    """Test case overview requires authentication"""
    # Create a test user for this test
    user = User(
        user_id=uuid.UUID("00000000-0000-0000-0000-00001bc604da"),
        username="authtest",
        display_name="Auth Test User",
        email="authtest@example.com",
        password_hash="hashed",
        primary_role="investigator",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    
    customer = Customer(
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000e3773c41"),
        customer_name="Auth Test Customer",
        onboarding_profile="corporate",
        risk_classification="medium",
        exposure_indicators_json="[]"
    )
    db_session.add(customer)
    
    account = Account(
        account_id=uuid.UUID("00000000-0000-0000-0000-000027845f69"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000e3773c41"),
        account_number_masked="GB•• •••• 4444",
        relationship_type="primary",
        jurisdiction_code="GB",
        product_type="investment"
    )
    db_session.add(account)
    
    transaction = Transaction(
        transaction_id=uuid.UUID("00000000-0000-0000-0000-000050dbc47f"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000e3773c41"),
        account_id=uuid.UUID("00000000-0000-0000-0000-000027845f69"),
        booked_at=datetime.utcnow(),
        amount=Decimal("60000.00"),
        currency="GBP",
        counterparty_name="UK Partner",
        corridor="GB-US",
        generation_source="automatic"
    )
    db_session.add(transaction)
    
    alert = Alert(
        alert_id=uuid.UUID("00000000-0000-0000-0000-00008828b30f"),
        transaction_id=uuid.UUID("00000000-0000-0000-0000-000050dbc47f"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000e3773c41"),
        status="ESCALATED_TO_CASE",
        priority="MEDIUM",
        risk_score=70,
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
        case_id=uuid.UUID("00000000-0000-0000-0000-000030475b8c"),
        case_number="CS-INT-002",
        source_alert_id=uuid.UUID("00000000-0000-0000-0000-00008828b30f"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000e3773c41"),
        status="INVESTIGATING",
        priority="MEDIUM",
        assigned_user_id=user.user_id,
        recommendation_state="DRAFT",
        recommendation_outcome=None,
        findings_summary=None,
        flagged_value_total=Decimal("60000.00"),
        evidence_locked_for_review=False,
        created_by_user_id=user.user_id,
        handoff_officer_user_id=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(case)
    db_session.commit()
    
    # Attempt without auth
    response = client.get("/api/v1/cases/case-int-002")
    
    assert response.status_code == 401


def test_post_status_transition_investigating_to_pending(auth_client: TestClient, db_session: Session):
    """Test POST /api/v1/cases/{case_id}/status-transitions with valid transition"""
    # Get test user
    user = db_session.query(User).filter(User.username == "tester").first()
    assert user is not None
    
    # Create case
    case = AMLCase(
        case_id=uuid.UUID("00000000-0000-0000-0000-00004cbbb01d"),
        case_number="CS-TRANS-001",
        source_alert_id=uuid.UUID("00000000-0000-0000-0000-00004cf9edaf"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-00004c1f0964"),
        status="INVESTIGATING",
        priority="HIGH",
        assigned_user_id=user.user_id,
        recommendation_state="DRAFT",
        created_by_user_id=user.user_id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(case)
    db_session.commit()
    
    # Transition status
    response = auth_client.post(
        "/api/v1/cases/case-transition-001/status-transitions",
        json={
            "new_status": "PENDING_INFORMATION",
            "reason": "Information request issued",
            "trigger_event": "IR-001 created"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["previous_status"] == "INVESTIGATING"
    assert data["new_status"] == "PENDING_INFORMATION"
    assert data["case_id"] == "case-transition-001"


def test_post_status_transition_invalid_returns_409(auth_client: TestClient, db_session: Session):
    """Test invalid status transition returns 409 Conflict"""
    # Get test user
    user = db_session.query(User).filter(User.username == "tester").first()
    assert user is not None
    
    # Create case
    case = AMLCase(
        case_id=uuid.UUID("00000000-0000-0000-0000-0000a71bc119"),
        case_number="CS-TRANS-002",
        source_alert_id=uuid.UUID("00000000-0000-0000-0000-0000c6d7d104"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-00004c5499da"),
        status="INVESTIGATING",
        priority="HIGH",
        assigned_user_id=user.user_id,
        recommendation_state="DRAFT",
        created_by_user_id=user.user_id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(case)
    db_session.commit()
    
    # Attempt invalid transition
    response = auth_client.post(
        "/api/v1/cases/case-transition-002/status-transitions",
        json={
            "new_status": "SUBMITTED_FOR_REVIEW",
            "reason": "Skip ahead",
            "trigger_event": "Invalid"
        }
    )
    
    assert response.status_code == 409
    assert "Invalid transition" in response.json()["detail"]


def test_post_recommendation_success(auth_client: TestClient, db_session: Session):
    """Test POST /api/v1/cases/{case_id}/recommendation with valid data"""
    from app.models.case_alert_link import CaseAlertLink
    
    # Get test user
    user = db_session.query(User).filter(User.username == "tester").first()
    assert user is not None
    
    # Create test data
    customer = Customer(
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000ba74eb10"),
        customer_name="Rec Customer",
        onboarding_profile="corporate",
        risk_classification="high",
        exposure_indicators_json="[]"
    )
    db_session.add(customer)
    
    account = Account(
        account_id=uuid.UUID("00000000-0000-0000-0000-0000b31dc292"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000ba74eb10"),
        account_number_masked="GB•• •••• 7777",
        relationship_type="primary",
        jurisdiction_code="GB",
        product_type="business"
    )
    db_session.add(account)
    
    transaction = Transaction(
        transaction_id=uuid.UUID("00000000-0000-0000-0000-0000b8e65a9d"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000ba74eb10"),
        account_id=uuid.UUID("00000000-0000-0000-0000-0000b31dc292"),
        booked_at=datetime.utcnow(),
        amount=Decimal("250000.00"),
        currency="USD",
        counterparty_name="Rec Corp",
        corridor="GB-HK",
        generation_source="automatic"
    )
    db_session.add(transaction)
    
    alert = Alert(
        alert_id=uuid.UUID("00000000-0000-0000-0000-00002abf000c"),
        transaction_id=uuid.UUID("00000000-0000-0000-0000-0000b8e65a9d"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000ba74eb10"),
        status="ESCALATED_TO_CASE",
        priority="HIGH",
        risk_score=87,
        matched_rule_codes_json='["RULE-001"]',
        generation="automatic",
        assigned_user_id=user.user_id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(alert)
    
    case = AMLCase(
        case_id=uuid.UUID("00000000-0000-0000-0000-000053253795"),
        case_number="CS-REC-001",
        source_alert_id=uuid.UUID("00000000-0000-0000-0000-00002abf000c"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000ba74eb10"),
        status="INVESTIGATING",
        priority="HIGH",
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
        case_alert_link_id="link-rec-001",
        case_id=uuid.UUID("00000000-0000-0000-0000-000053253795"),
        alert_id=uuid.UUID("00000000-0000-0000-0000-00002abf000c"),
        linked_at=datetime.utcnow(),
        linked_by_user_id=user.user_id,
        selection_basis="Test recommendation link"
    )
    db_session.add(link)
    db_session.commit()
    
    # Submit recommendation
    findings = "This is a comprehensive findings summary detailing the investigation outcomes with sufficient length to meet validation requirements."
    response = auth_client.post(
        "/api/v1/cases/case-rec-001/recommendation",
        json={
            "recommendation_outcome": "SUBSTANTIATE",
            "findings_summary": findings,
            "supporting_note_ids": []
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["case_id"] == "case-rec-001"
    assert data["recommendation_state"] == "SUBMITTED"
    assert data["recommendation_outcome"] == "SUBSTANTIATE"


def test_post_recommendation_validates_findings_length(auth_client: TestClient, db_session: Session):
    """Test recommendation endpoint validates findings summary minimum length"""
    # Get test user
    user = db_session.query(User).filter(User.username == "tester").first()
    
    # Create minimal case
    case = AMLCase(
        case_id=uuid.UUID("00000000-0000-0000-0000-0000b377a97c"),
        case_number="CS-REC-002",
        source_alert_id=uuid.UUID("00000000-0000-0000-0000-00003df878f5"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000a11f50fa"),
        status="INVESTIGATING",
        priority="MEDIUM",
        assigned_user_id=user.user_id,
        recommendation_state="DRAFT",
        created_by_user_id=user.user_id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(case)
    db_session.commit()
    
    # Attempt with short findings
    response = auth_client.post(
        "/api/v1/cases/case-rec-002/recommendation",
        json={
            "recommendation_outcome": "NO_FURTHER_ACTION",
            "findings_summary": "Too short",
            "supporting_note_ids": []
        }
    )
    
    assert response.status_code == 422


def test_get_handoff_package_success(auth_client: TestClient, db_session: Session):
    """Test GET /api/v1/cases/{case_id}/handoff returns package"""
    from app.models.case_alert_link import CaseAlertLink
    
    # Get test user
    user = db_session.query(User).filter(User.username == "tester").first()
    
    # Create test data with complete recommendation
    customer = Customer(
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000b5bbd8c7"),
        customer_name="Handoff Customer",
        onboarding_profile="corporate",
        risk_classification="high",
        exposure_indicators_json="[]"
    )
    db_session.add(customer)
    
    account = Account(
        account_id=uuid.UUID("00000000-0000-0000-0000-00004bf228e3"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000b5bbd8c7"),
        account_number_masked="US•• •••• 8888",
        relationship_type="primary",
        jurisdiction_code="US",
        product_type="business"
    )
    db_session.add(account)
    
    transaction = Transaction(
        transaction_id=uuid.UUID("00000000-0000-0000-0000-0000c60ad8db"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000b5bbd8c7"),
        account_id=uuid.UUID("00000000-0000-0000-0000-00004bf228e3"),
        booked_at=datetime.utcnow(),
        amount=Decimal("400000.00"),
        currency="USD",
        counterparty_name="Handoff Corp",
        corridor="US-HK",
        generation_source="automatic"
    )
    db_session.add(transaction)
    
    alert = Alert(
        alert_id=uuid.UUID("00000000-0000-0000-0000-0000a17122b9"),
        transaction_id=uuid.UUID("00000000-0000-0000-0000-0000c60ad8db"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000b5bbd8c7"),
        status="ESCALATED_TO_CASE",
        priority="CRITICAL",
        risk_score=93,
        matched_rule_codes_json='["RULE-001"]',
        generation="automatic",
        assigned_user_id=user.user_id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(alert)
    
    case = AMLCase(
        case_id=uuid.UUID("00000000-0000-0000-0000-0000b62a5854"),
        case_number="CS-HANDOFF-001",
        source_alert_id=uuid.UUID("00000000-0000-0000-0000-0000a17122b9"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000b5bbd8c7"),
        status="INVESTIGATING",
        priority="CRITICAL",
        assigned_user_id=user.user_id,
        recommendation_state="SUBMITTED",
        recommendation_outcome="SUBSTANTIATE",
        findings_summary="Complete investigation findings with detailed analysis and sufficient length for handoff readiness validation.",
        flagged_value_total=Decimal("0.00"),
        evidence_locked_for_review=False,
        created_by_user_id=user.user_id,
        handoff_officer_user_id=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(case)
    
    link = CaseAlertLink(
        case_alert_link_id="link-handoff-001",
        case_id=uuid.UUID("00000000-0000-0000-0000-0000b62a5854"),
        alert_id=uuid.UUID("00000000-0000-0000-0000-0000a17122b9"),
        linked_at=datetime.utcnow(),
        linked_by_user_id=user.user_id,
        selection_basis="Handoff test link"
    )
    db_session.add(link)
    db_session.commit()
    
    # Get handoff package
    response = auth_client.get("/api/v1/cases/case-handoff-001/handoff")
    
    assert response.status_code == 200
    data = response.json()
    assert data["case_id"] == "case-handoff-001"
    assert data["case_number"] == "CS-HANDOFF-001"
    assert data["recommendation_outcome"] == "SUBSTANTIATE"
    assert "readiness" in data
    assert "linked_alerts" in data
    assert len(data["linked_alerts"]) == 1


def test_post_handoff_submission_success(auth_client: TestClient, db_session: Session):
    """Test POST /api/v1/cases/{case_id}/handoff succeeds when ready"""
    from app.models.case_alert_link import CaseAlertLink
    
    # Get test user
    user = db_session.query(User).filter(User.username == "tester").first()
    
    # Create officer user (different from creator)
    officer = User(
        user_id=uuid.UUID("00000000-0000-0000-0000-0000c11711d5"),
        username="officer",
        display_name="Officer User",
        email="officer@example.com",
        password_hash="hashed",
        primary_role="officer",
        is_active=True
    )
    db_session.add(officer)
    
    # Create complete ready case
    customer = Customer(
        customer_id=uuid.UUID("00000000-0000-0000-0000-00009ace8128"),
        customer_name="Submit Customer",
        onboarding_profile="corporate",
        risk_classification="high",
        exposure_indicators_json="[]"
    )
    db_session.add(customer)
    
    account = Account(
        account_id=uuid.UUID("00000000-0000-0000-0000-0000900b6b89"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-00009ace8128"),
        account_number_masked="CA•• •••• 9999",
        relationship_type="primary",
        jurisdiction_code="CA",
        product_type="business"
    )
    db_session.add(account)
    
    transaction = Transaction(
        transaction_id=uuid.UUID("00000000-0000-0000-0000-000038a6585c"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-00009ace8128"),
        account_id=uuid.UUID("00000000-0000-0000-0000-0000900b6b89"),
        booked_at=datetime.utcnow(),
        amount=Decimal("500000.00"),
        currency="CAD",
        counterparty_name="Submit Corp",
        corridor="CA-HK",
        generation_source="automatic"
    )
    db_session.add(transaction)
    
    alert = Alert(
        alert_id=uuid.UUID("00000000-0000-0000-0000-00005c48f6f9"),
        transaction_id=uuid.UUID("00000000-0000-0000-0000-000038a6585c"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-00009ace8128"),
        status="ESCALATED_TO_CASE",
        priority="CRITICAL",
        risk_score=96,
        matched_rule_codes_json='["RULE-001"]',
        generation="automatic",
        assigned_user_id=user.user_id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(alert)
    
    case = AMLCase(
        case_id=uuid.UUID("00000000-0000-0000-0000-0000d304ea71"),
        case_number="CS-SUBMIT-001",
        source_alert_id=uuid.UUID("00000000-0000-0000-0000-00005c48f6f9"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-00009ace8128"),
        status="REVIEW_READY",
        priority="CRITICAL",
        assigned_user_id=user.user_id,
        recommendation_state="SUBMITTED",
        recommendation_outcome="ESCALATE_FOR_REVIEW",
        findings_summary="Comprehensive investigation findings documenting all evidence and analysis with sufficient detail for final review determination.",
        flagged_value_total=Decimal("0.00"),
        evidence_locked_for_review=False,
        created_by_user_id=user.user_id,
        handoff_officer_user_id=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(case)
    
    link = CaseAlertLink(
        case_alert_link_id="link-submit-001",
        case_id=uuid.UUID("00000000-0000-0000-0000-0000d304ea71"),
        alert_id=uuid.UUID("00000000-0000-0000-0000-00005c48f6f9"),
        linked_at=datetime.utcnow(),
        linked_by_user_id=user.user_id,
        selection_basis="Submit test link"
    )
    db_session.add(link)
    db_session.commit()
    
    # Submit handoff
    response = auth_client.post(
        "/api/v1/cases/case-submit-001/handoff",
        json={
            "officer_user_id": "officer-001",
            "submission_comment": "Ready for officer review"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["case_id"] == "case-submit-001"
    assert data["status"] == "SUBMITTED_FOR_REVIEW"
    assert data["officer_user_id"] == "officer-001"
    assert data["readiness_passed"] is True
