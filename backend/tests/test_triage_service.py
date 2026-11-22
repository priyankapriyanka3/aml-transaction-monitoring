"""
Unit tests for alert triage functionality.
Tests save_triage_disposition method in AlertService.
"""
from datetime import datetime
import uuid

import pytest

from app.models.alert import Alert
from app.models.user import User
from app.services.alert_service import AlertService


def test_save_triage_disposition_close_non_actionable(db_session):
    """Test saving triage disposition with CLOSE_NON_ACTIONABLE outcome"""
    # Create user and alert
    user = User(
        user_id=uuid.UUID("00000000-0000-0000-0000-0000291a87a3"),
        username="tester",
        display_name="Test User",
        email="test@example.com",
        password_hash="hash",
        primary_role="investigator",
        is_active=True
    )
    db_session.add(user)
    
    alert = Alert(
        alert_id=uuid.UUID("00000000-0000-0000-0000-00004eeabc29"),
        transaction_id=uuid.UUID("00000000-0000-0000-0000-0000ba355f9b"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-000091c758b7"),
        status="NEW",
        priority="MEDIUM",
        risk_score=50,
        matched_rule_codes_json='["RULE-001"]',
        generation="automatic",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(alert)
    db_session.commit()
    
    # Save triage disposition
    service = AlertService(db_session)
    result = service.save_triage_disposition(
        alert_id=uuid.UUID("00000000-0000-0000-0000-00004eeabc29"),
        outcome="CLOSE_NON_ACTIONABLE",
        rationale="Transaction verified as legitimate with supporting documentation",
        actor_id=uuid.UUID("00000000-0000-0000-0000-0000291a87a3")
    )
    
    assert result.status == "CLOSED_NON_ACTIONABLE"
    assert result.triage_outcome == "CLOSE_NON_ACTIONABLE"
    assert result.triage_rationale == "Transaction verified as legitimate with supporting documentation"
    assert result.triaged_by_user_id == "00000000-0000-0000-0000-0000291a87a3"
    assert result.triaged_at is not None


def test_save_triage_disposition_investigate_keeps_status(db_session):
    """Test INVESTIGATE outcome keeps current alert status"""
    user = User(
        user_id=uuid.UUID("00000000-0000-0000-0000-0000291a87a3"),
        username="tester",
        display_name="Test User",
        email="test@example.com",
        password_hash="hash",
        primary_role="investigator",
        is_active=True
    )
    db_session.add(user)
    
    alert = Alert(
        alert_id=uuid.UUID("00000000-0000-0000-0000-00004eeabc29"),
        transaction_id=uuid.UUID("00000000-0000-0000-0000-0000ba355f9b"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-000091c758b7"),
        status="UNDER_REVIEW",
        priority="HIGH",
        risk_score=75,
        matched_rule_codes_json='["RULE-001"]',
        generation="automatic",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(alert)
    db_session.commit()
    
    service = AlertService(db_session)
    result = service.save_triage_disposition(
        alert_id=uuid.UUID("00000000-0000-0000-0000-00004eeabc29"),
        outcome="INVESTIGATE",
        rationale="Requires detailed investigation of transaction pattern",
        actor_id=uuid.UUID("00000000-0000-0000-0000-0000291a87a3")
    )
    
    # Status should remain UNDER_REVIEW
    assert result.status == "UNDER_REVIEW"
    assert result.triage_outcome == "INVESTIGATE"


def test_save_triage_disposition_merge_existing_case(db_session):
    """Test MERGE_EXISTING_CASE outcome transitions to MERGED_INTO_EXISTING_CASE status"""
    user = User(
        user_id=uuid.UUID("00000000-0000-0000-0000-0000291a87a3"),
        username="tester",
        display_name="Test User",
        email="test@example.com",
        password_hash="hash",
        primary_role="investigator",
        is_active=True
    )
    db_session.add(user)
    
    alert = Alert(
        alert_id=uuid.UUID("00000000-0000-0000-0000-00004eeabc29"),
        transaction_id=uuid.UUID("00000000-0000-0000-0000-0000ba355f9b"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-000091c758b7"),
        status="NEW",
        priority="MEDIUM",
        risk_score=60,
        matched_rule_codes_json='["RULE-001"]',
        generation="automatic",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(alert)
    db_session.commit()
    
    service = AlertService(db_session)
    result = service.save_triage_disposition(
        alert_id=uuid.UUID("00000000-0000-0000-0000-00004eeabc29"),
        outcome="MERGE_EXISTING_CASE",
        rationale="Related to existing case CS-001, same customer and pattern",
        actor_id=uuid.UUID("00000000-0000-0000-0000-0000291a87a3"),
        existing_case_id="case-CS-001"
    )
    
    assert result.status == "MERGED_INTO_EXISTING_CASE"
    assert result.triage_outcome == "MERGE_EXISTING_CASE"


def test_save_triage_disposition_validates_rationale_length(db_session):
    """Test that rationale with less than 10 characters is rejected"""
    user = User(
        user_id=uuid.UUID("00000000-0000-0000-0000-0000291a87a3"),
        username="tester",
        display_name="Test User",
        email="test@example.com",
        password_hash="hash",
        primary_role="investigator",
        is_active=True
    )
    db_session.add(user)
    
    alert = Alert(
        alert_id=uuid.UUID("00000000-0000-0000-0000-00004eeabc29"),
        transaction_id=uuid.UUID("00000000-0000-0000-0000-0000ba355f9b"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-000091c758b7"),
        status="NEW",
        priority="LOW",
        risk_score=40,
        matched_rule_codes_json='["RULE-001"]',
        generation="automatic",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(alert)
    db_session.commit()
    
    service = AlertService(db_session)
    
    # Test blank rationale
    with pytest.raises(ValueError, match="at least 10 characters"):
        service.save_triage_disposition(
            alert_id=uuid.UUID("00000000-0000-0000-0000-00004eeabc29"),
            outcome="CLOSE_NON_ACTIONABLE",
            rationale="",
            actor_id=uuid.UUID("00000000-0000-0000-0000-0000291a87a3")
        )
    
    # Test short rationale
    with pytest.raises(ValueError, match="at least 10 characters"):
        service.save_triage_disposition(
            alert_id=uuid.UUID("00000000-0000-0000-0000-00004eeabc29"),
            outcome="CLOSE_NON_ACTIONABLE",
            rationale="Short",
            actor_id=uuid.UUID("00000000-0000-0000-0000-0000291a87a3")
        )


def test_save_triage_disposition_validates_outcome(db_session):
    """Test that invalid outcome is rejected"""
    user = User(
        user_id=uuid.UUID("00000000-0000-0000-0000-0000291a87a3"),
        username="tester",
        display_name="Test User",
        email="test@example.com",
        password_hash="hash",
        primary_role="investigator",
        is_active=True
    )
    db_session.add(user)
    
    alert = Alert(
        alert_id=uuid.UUID("00000000-0000-0000-0000-00004eeabc29"),
        transaction_id=uuid.UUID("00000000-0000-0000-0000-0000ba355f9b"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-000091c758b7"),
        status="NEW",
        priority="LOW",
        risk_score=40,
        matched_rule_codes_json='["RULE-001"]',
        generation="automatic",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(alert)
    db_session.commit()
    
    service = AlertService(db_session)
    
    with pytest.raises(ValueError, match="Invalid outcome"):
        service.save_triage_disposition(
            alert_id=uuid.UUID("00000000-0000-0000-0000-00004eeabc29"),
            outcome="INVALID_OUTCOME",
            rationale="Valid rationale text here",
            actor_id=uuid.UUID("00000000-0000-0000-0000-0000291a87a3")
        )


def test_save_triage_disposition_validates_existing_case_id_required(db_session):
    """Test that existing_case_id is required when outcome is MERGE_EXISTING_CASE"""
    user = User(
        user_id=uuid.UUID("00000000-0000-0000-0000-0000291a87a3"),
        username="tester",
        display_name="Test User",
        email="test@example.com",
        password_hash="hash",
        primary_role="investigator",
        is_active=True
    )
    db_session.add(user)
    
    alert = Alert(
        alert_id=uuid.UUID("00000000-0000-0000-0000-00004eeabc29"),
        transaction_id=uuid.UUID("00000000-0000-0000-0000-0000ba355f9b"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-000091c758b7"),
        status="NEW",
        priority="MEDIUM",
        risk_score=60,
        matched_rule_codes_json='["RULE-001"]',
        generation="automatic",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(alert)
    db_session.commit()
    
    service = AlertService(db_session)
    
    with pytest.raises(ValueError, match="existing_case_id is required"):
        service.save_triage_disposition(
            alert_id=uuid.UUID("00000000-0000-0000-0000-00004eeabc29"),
            outcome="MERGE_EXISTING_CASE",
            rationale="Should be merged with existing case",
            actor_id=uuid.UUID("00000000-0000-0000-0000-0000291a87a3"),
            existing_case_id=None
        )


def test_save_triage_disposition_alert_not_found(db_session):
    """Test that nonexistent alert raises ValueError"""
    user = User(
        user_id=uuid.UUID("00000000-0000-0000-0000-0000291a87a3"),
        username="tester",
        display_name="Test User",
        email="test@example.com",
        password_hash="hash",
        primary_role="investigator",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    
    service = AlertService(db_session)
    
    with pytest.raises(ValueError, match="Alert not found"):
        service.save_triage_disposition(
            alert_id=uuid.UUID("00000000-0000-0000-0000-0000a4ec8bc5"),
            outcome="CLOSE_NON_ACTIONABLE",
            rationale="Valid rationale text",
            actor_id=uuid.UUID("00000000-0000-0000-0000-0000291a87a3")
        )


def test_save_triage_disposition_creates_audit_event(db_session):
    """Test that triage disposition creates audit event"""
    from app.models.audit_event import AuditEvent
    
    user = User(
        user_id=uuid.UUID("00000000-0000-0000-0000-0000291a87a3"),
        username="tester",
        display_name="Test User",
        email="test@example.com",
        password_hash="hash",
        primary_role="investigator",
        is_active=True
    )
    db_session.add(user)
    
    alert = Alert(
        alert_id=uuid.UUID("00000000-0000-0000-0000-00004eeabc29"),
        transaction_id=uuid.UUID("00000000-0000-0000-0000-0000ba355f9b"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-000091c758b7"),
        status="NEW",
        priority="MEDIUM",
        risk_score=55,
        matched_rule_codes_json='["RULE-001"]',
        generation="automatic",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(alert)
    db_session.commit()
    
    service = AlertService(db_session)
    service.save_triage_disposition(
        alert_id=uuid.UUID("00000000-0000-0000-0000-00004eeabc29"),
        outcome="CLOSE_NON_ACTIONABLE",
        rationale="Verified legitimate transaction",
        actor_id=uuid.UUID("00000000-0000-0000-0000-0000291a87a3")
    )
    
    # Check audit event created
    audit_event = db_session.query(AuditEvent).filter(
        AuditEvent.entity_type == "alert",
        AuditEvent.entity_id == str(uuid.UUID("00000000-0000-0000-0000-00004eeabc29")),
        AuditEvent.action_type == "ALERT_TRIAGE_RECORDED"
    ).first()
    
    assert audit_event is not None
    assert audit_event.actor_user_id == uuid.UUID("00000000-0000-0000-0000-0000291a87a3")
    assert audit_event.actor_role == "investigator"
