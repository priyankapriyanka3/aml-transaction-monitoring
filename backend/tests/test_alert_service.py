import pytest
import uuid
from decimal import Decimal
from datetime import datetime, timedelta
from app.services.alert_service import AlertService
from app.models.user import User
from app.models.customer import Customer
from app.models.account import Account
from app.models.transaction import Transaction
from app.models.alert import Alert
from app.models.audit_event import AuditEvent


@pytest.fixture
def test_data(db_session):
    """Create test data for alert service tests"""
    # Users
    investigator = User(
        user_id=uuid.UUID("00000000-0000-0000-0000-0000298819a4"),
        username="investigator1",
        display_name="Test Investigator",
        email="inv@example.com",
        password_hash="hashed",
        primary_role="investigator",
        is_active=True
    )
    officer = User(
        user_id=uuid.UUID("00000000-0000-0000-0000-0000ef31b51d"),
        username="officer1",
        display_name="Test Officer",
        email="off@example.com",
        password_hash="hashed",
        primary_role="officer",
        is_active=True
    )
    db_session.add_all([investigator, officer])
    
    # Customer
    customer = Customer(
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000d8511ed4"),
        customer_name="Test Customer Inc",
        onboarding_profile="corporate",
        risk_classification="high",
        exposure_indicators_json='["cross_border"]'
    )
    db_session.add(customer)
    
    # Account
    account = Account(
        account_id=uuid.UUID("00000000-0000-0000-0000-0000b7f5874c"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000d8511ed4"),
        account_number_masked="GB•• •••• 1234",
        relationship_type="primary",
        jurisdiction_code="GB",
        product_type="business_current"
    )
    db_session.add(account)
    
    # Transaction
    transaction = Transaction(
        transaction_id=uuid.UUID("00000000-0000-0000-0000-000097aaff66"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000d8511ed4"),
        account_id=uuid.UUID("00000000-0000-0000-0000-0000b7f5874c"),
        booked_at=datetime.utcnow(),
        amount=Decimal("100000.00"),
        currency="USD",
        counterparty_name="Test Corp",
        corridor="GB-US",
        generation_source="automatic"
    )
    db_session.add(transaction)
    
    # Alerts
    alert1 = Alert(
        alert_id=uuid.UUID("00000000-0000-0000-0000-0000aa360490"),
        transaction_id=uuid.UUID("00000000-0000-0000-0000-000097aaff66"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000d8511ed4"),
        status="NEW",
        priority="HIGH",
        risk_score=85,
        matched_rule_codes_json='["RULE-001"]',
        generation="automatic",
        assigned_user_id=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    alert2 = Alert(
        alert_id=uuid.UUID("00000000-0000-0000-0000-0000d8253a53"),
        transaction_id=uuid.UUID("00000000-0000-0000-0000-000097aaff66"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000d8511ed4"),
        status="UNDER_REVIEW",
        priority="CRITICAL",
        risk_score=95,
        matched_rule_codes_json='["RULE-001", "RULE-002"]',
        generation="automatic",
        assigned_user_id=uuid.UUID("00000000-0000-0000-0000-0000298819a4"),
        created_at=datetime.utcnow() - timedelta(hours=1),
        updated_at=datetime.utcnow()
    )
    db_session.add_all([alert1, alert2])
    db_session.commit()
    
    return {
        "investigator": investigator,
        "officer": officer,
        "customer": customer,
        "transaction": transaction,
        "alert1": alert1,
        "alert2": alert2
    }


def test_get_queue_all_alerts(db_session, test_data):
    """Test getting all alerts without filters"""
    alert_service = AlertService(db_session)
    alerts, total_count = alert_service.get_queue()
    
    assert total_count == 2
    assert len(alerts) == 2
    
    # Check enrichment
    assert alerts[0].customer_name is not None
    assert alerts[0].transaction_amount is not None
    assert alerts[0].transaction_currency is not None


def test_get_queue_filter_by_status(db_session, test_data):
    """Test filtering alerts by status"""
    alert_service = AlertService(db_session)
    alerts, total_count = alert_service.get_queue(status="NEW")
    
    assert total_count == 1
    assert len(alerts) == 1
    assert alerts[0].status == "NEW"


def test_get_queue_filter_by_priority(db_session, test_data):
    """Test filtering alerts by priority"""
    alert_service = AlertService(db_session)
    alerts, total_count = alert_service.get_queue(priority="CRITICAL")
    
    assert total_count == 1
    assert len(alerts) == 1
    assert alerts[0].priority == "CRITICAL"


def test_get_queue_filter_by_assignee(db_session, test_data):
    """Test filtering alerts by assignee"""
    alert_service = AlertService(db_session)
    
    # Assigned alerts
    alerts, total_count = alert_service.get_queue(assignee_id="inv-001")
    assert total_count == 1
    assert alerts[0].assigned_user_id == "inv-001"
    
    # Unassigned alerts
    alerts, total_count = alert_service.get_queue(assignee_id="UNASSIGNED")
    assert total_count == 1
    assert alerts[0].assigned_user_id is None


def test_get_queue_filter_by_risk_score(db_session, test_data):
    """Test filtering alerts by risk score range"""
    alert_service = AlertService(db_session)
    
    # High risk only
    alerts, total_count = alert_service.get_queue(risk_score_min=90)
    assert total_count == 1
    assert alerts[0].risk_score >= 90
    
    # Medium risk range
    alerts, total_count = alert_service.get_queue(risk_score_min=80, risk_score_max=90)
    assert total_count == 1
    assert 80 <= alerts[0].risk_score <= 90


def test_get_queue_sorting(db_session, test_data):
    """Test sorting alerts"""
    alert_service = AlertService(db_session)
    
    # Sort by risk score descending
    alerts, _ = alert_service.get_queue(sort_by="risk_score", sort_direction="desc")
    assert alerts[0].risk_score >= alerts[1].risk_score
    
    # Sort by risk score ascending
    alerts, _ = alert_service.get_queue(sort_by="risk_score", sort_direction="asc")
    assert alerts[0].risk_score <= alerts[1].risk_score


def test_get_queue_pagination(db_session, test_data):
    """Test alert queue pagination"""
    alert_service = AlertService(db_session)
    
    # First page
    alerts, total_count = alert_service.get_queue(limit=1, offset=0)
    assert len(alerts) == 1
    assert total_count == 2
    
    # Second page
    alerts, total_count = alert_service.get_queue(limit=1, offset=1)
    assert len(alerts) == 1
    assert total_count == 2


def test_claim_alert_success(db_session, test_data):
    """Test successfully claiming an alert"""
    alert_service = AlertService(db_session)
    
    alert_response, assigned_name = alert_service.claim_alert(
        alert_id=uuid.UUID("00000000-0000-0000-0000-0000aa360490"),
        assignee_user_id=uuid.UUID("00000000-0000-0000-0000-0000298819a4"),
        assigned_by_user_id=uuid.UUID("00000000-0000-0000-0000-0000ef31b51d"),
        assignment_reason="Test assignment"
    )
    
    assert alert_response.alert_id == "alert-001"
    assert alert_response.assigned_user_id == "inv-001"
    assert assigned_name == "Test Investigator"
    
    # Verify database was updated
    alert = db_session.query(Alert).filter_by(alert_id=uuid.UUID("00000000-0000-0000-0000-0000aa360490")).first()
    assert alert.assigned_user_id == "inv-001"
    
    # Verify audit event was created
    audit_events = db_session.query(AuditEvent).filter_by(
        entity_type="alert",
        entity_id=uuid.UUID("00000000-0000-0000-0000-0000aa360490"),
        action_type="ALERT_ASSIGNED"
    ).all()
    assert len(audit_events) == 1
    assert audit_events[0].actor_user_id == "off-001"


def test_claim_alert_nonexistent(db_session, test_data):
    """Test claiming a non-existent alert"""
    alert_service = AlertService(db_session)
    
    with pytest.raises(ValueError, match="Alert not found"):
        alert_service.claim_alert(
            alert_id=uuid.UUID("00000000-0000-0000-0000-000053f3c938"),
            assignee_user_id=uuid.UUID("00000000-0000-0000-0000-0000298819a4"),
            assigned_by_user_id=uuid.UUID("00000000-0000-0000-0000-0000ef31b51d")
        )


def test_claim_alert_invalid_assignee(db_session, test_data):
    """Test claiming with invalid assignee user"""
    alert_service = AlertService(db_session)
    
    with pytest.raises(ValueError, match="Assignee user not found or inactive"):
        alert_service.claim_alert(
            alert_id=uuid.UUID("00000000-0000-0000-0000-0000aa360490"),
            assignee_user_id=uuid.UUID("00000000-0000-0000-0000-000095d13ae3"),
            assigned_by_user_id=uuid.UUID("00000000-0000-0000-0000-0000ef31b51d")
        )


def test_claim_alert_reassignment(db_session, test_data):
    """Test reassigning an already assigned alert"""
    alert_service = AlertService(db_session)
    
    # Reassign from investigator to officer
    alert_response, assigned_name = alert_service.claim_alert(
        alert_id=uuid.UUID("00000000-0000-0000-0000-0000d8253a53"),
        assignee_user_id=uuid.UUID("00000000-0000-0000-0000-0000ef31b51d"),
        assigned_by_user_id=uuid.UUID("00000000-0000-0000-0000-0000298819a4")
    )
    
    assert alert_response.assigned_user_id == "off-001"
    assert assigned_name == "Test Officer"
    
    # Verify database was updated
    alert = db_session.query(Alert).filter_by(alert_id=uuid.UUID("00000000-0000-0000-0000-0000d8253a53")).first()
    assert alert.assigned_user_id == "off-001"
