"""
Unit tests for case status transition service.
Tests state machine validation and audit trail creation.
"""
import pytest
import uuid
from datetime import datetime

from app.models.aml_case import AMLCase
from app.models.user import User
from app.services.case_service import CaseService


def test_transition_investigating_to_pending_information(db_session):
    """Test valid transition from INVESTIGATING to PENDING_INFORMATION"""
    # Create user
    user = User(
        user_id=uuid.UUID("00000000-0000-0000-0000-00001fdb9834"),
        username="riya",
        display_name="Riya Sharma",
        email="riya@example.com",
        password_hash="hash",
        primary_role="investigator",
        is_active=True
    )
    db_session.add(user)
    
    # Create case
    case = AMLCase(
        case_id=uuid.UUID("00000000-0000-0000-0000-000056ae0fb0"),
        case_number="CS-001",
        source_alert_id=uuid.UUID("00000000-0000-0000-0000-0000aa360490"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000d8511ed4"),
        status="INVESTIGATING",
        priority="HIGH",
        assigned_user_id=uuid.UUID("00000000-0000-0000-0000-00001fdb9834"),
        recommendation_state="DRAFT",
        created_by_user_id=uuid.UUID("00000000-0000-0000-0000-00001fdb9834"),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(case)
    db_session.commit()
    
    # Transition status
    service = CaseService(db_session)
    result = service.transition_status(
        case_id=uuid.UUID("00000000-0000-0000-0000-000056ae0fb0"),
        new_status="PENDING_INFORMATION",
        actor_id=uuid.UUID("00000000-0000-0000-0000-00001fdb9834"),
        reason="Information request issued",
        trigger_event="IR-001 created"
    )
    
    assert result["previous_status"] == "INVESTIGATING"
    assert result["new_status"] == "PENDING_INFORMATION"
    assert result["case_id"] == "case-001"
    assert result["transitioned_by_user_id"] == str(uuid.UUID(int=1))


def test_transition_investigating_to_review_ready(db_session):
    """Test valid transition from INVESTIGATING to REVIEW_READY"""
    # Create user
    user = User(
        user_id=uuid.UUID("00000000-0000-0000-0000-00001fdb9834"),
        username="riya",
        display_name="Riya Sharma",
        email="riya@example.com",
        password_hash="hash",
        primary_role="investigator",
        is_active=True
    )
    db_session.add(user)
    
    # Create case
    case = AMLCase(
        case_id=uuid.UUID("00000000-0000-0000-0000-000056ae0fb0"),
        case_number="CS-001",
        source_alert_id=uuid.UUID("00000000-0000-0000-0000-0000aa360490"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000d8511ed4"),
        status="INVESTIGATING",
        priority="HIGH",
        assigned_user_id=uuid.UUID("00000000-0000-0000-0000-00001fdb9834"),
        recommendation_state="DRAFT",
        created_by_user_id=uuid.UUID("00000000-0000-0000-0000-00001fdb9834"),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(case)
    db_session.commit()
    
    # Transition status
    service = CaseService(db_session)
    result = service.transition_status(
        case_id=uuid.UUID("00000000-0000-0000-0000-000056ae0fb0"),
        new_status="REVIEW_READY",
        actor_id=uuid.UUID("00000000-0000-0000-0000-00001fdb9834"),
        reason="Recommendation submitted",
        trigger_event="Recommendation complete"
    )
    
    assert result["previous_status"] == "INVESTIGATING"
    assert result["new_status"] == "REVIEW_READY"


def test_transition_pending_information_to_investigating(db_session):
    """Test valid transition from PENDING_INFORMATION to INVESTIGATING"""
    # Create user
    user = User(
        user_id=uuid.UUID("00000000-0000-0000-0000-00001fdb9834"),
        username="riya",
        display_name="Riya Sharma",
        email="riya@example.com",
        password_hash="hash",
        primary_role="investigator",
        is_active=True
    )
    db_session.add(user)
    
    # Create case
    case = AMLCase(
        case_id=uuid.UUID("00000000-0000-0000-0000-000056ae0fb0"),
        case_number="CS-001",
        source_alert_id=uuid.UUID("00000000-0000-0000-0000-0000aa360490"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000d8511ed4"),
        status="PENDING_INFORMATION",
        priority="HIGH",
        assigned_user_id=uuid.UUID("00000000-0000-0000-0000-00001fdb9834"),
        recommendation_state="DRAFT",
        created_by_user_id=uuid.UUID("00000000-0000-0000-0000-00001fdb9834"),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(case)
    db_session.commit()
    
    # Transition status
    service = CaseService(db_session)
    result = service.transition_status(
        case_id=uuid.UUID("00000000-0000-0000-0000-000056ae0fb0"),
        new_status="INVESTIGATING",
        actor_id=uuid.UUID("00000000-0000-0000-0000-00001fdb9834"),
        reason="Information received",
        trigger_event="IR-001 response recorded"
    )
    
    assert result["previous_status"] == "PENDING_INFORMATION"
    assert result["new_status"] == "INVESTIGATING"


def test_transition_review_ready_to_submitted_for_review(db_session):
    """Test valid transition from REVIEW_READY to SUBMITTED_FOR_REVIEW"""
    # Create user
    user = User(
        user_id=uuid.UUID("00000000-0000-0000-0000-00001fdb9834"),
        username="riya",
        display_name="Riya Sharma",
        email="riya@example.com",
        password_hash="hash",
        primary_role="investigator",
        is_active=True
    )
    db_session.add(user)
    
    # Create case
    case = AMLCase(
        case_id=uuid.UUID("00000000-0000-0000-0000-000056ae0fb0"),
        case_number="CS-001",
        source_alert_id=uuid.UUID("00000000-0000-0000-0000-0000aa360490"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000d8511ed4"),
        status="REVIEW_READY",
        priority="HIGH",
        assigned_user_id=uuid.UUID("00000000-0000-0000-0000-00001fdb9834"),
        recommendation_state="SUBMITTED",
        created_by_user_id=uuid.UUID("00000000-0000-0000-0000-00001fdb9834"),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(case)
    db_session.commit()
    
    # Transition status
    service = CaseService(db_session)
    result = service.transition_status(
        case_id=uuid.UUID("00000000-0000-0000-0000-000056ae0fb0"),
        new_status="SUBMITTED_FOR_REVIEW",
        actor_id=uuid.UUID("00000000-0000-0000-0000-00001fdb9834"),
        reason="Handoff submitted",
        trigger_event="Handoff package created"
    )
    
    assert result["previous_status"] == "REVIEW_READY"
    assert result["new_status"] == "SUBMITTED_FOR_REVIEW"


def test_transition_invalid_from_investigating_to_submitted(db_session):
    """Test invalid transition from INVESTIGATING directly to SUBMITTED_FOR_REVIEW"""
    # Create user
    user = User(
        user_id=uuid.UUID("00000000-0000-0000-0000-00001fdb9834"),
        username="riya",
        display_name="Riya Sharma",
        email="riya@example.com",
        password_hash="hash",
        primary_role="investigator",
        is_active=True
    )
    db_session.add(user)
    
    # Create case
    case = AMLCase(
        case_id=uuid.UUID("00000000-0000-0000-0000-000056ae0fb0"),
        case_number="CS-001",
        source_alert_id=uuid.UUID("00000000-0000-0000-0000-0000aa360490"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000d8511ed4"),
        status="INVESTIGATING",
        priority="HIGH",
        assigned_user_id=uuid.UUID("00000000-0000-0000-0000-00001fdb9834"),
        recommendation_state="DRAFT",
        created_by_user_id=uuid.UUID("00000000-0000-0000-0000-00001fdb9834"),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(case)
    db_session.commit()
    
    # Attempt invalid transition
    service = CaseService(db_session)
    with pytest.raises(ValueError) as exc_info:
        service.transition_status(
            case_id=uuid.UUID("00000000-0000-0000-0000-000056ae0fb0"),
            new_status="SUBMITTED_FOR_REVIEW",
            actor_id=uuid.UUID("00000000-0000-0000-0000-00001fdb9834")
        )
    
    assert "Invalid transition" in str(exc_info.value)


def test_transition_invalid_from_pending_information_to_review_ready(db_session):
    """Test invalid transition from PENDING_INFORMATION to REVIEW_READY"""
    # Create user
    user = User(
        user_id=uuid.UUID("00000000-0000-0000-0000-00001fdb9834"),
        username="riya",
        display_name="Riya Sharma",
        email="riya@example.com",
        password_hash="hash",
        primary_role="investigator",
        is_active=True
    )
    db_session.add(user)
    
    # Create case
    case = AMLCase(
        case_id=uuid.UUID("00000000-0000-0000-0000-000056ae0fb0"),
        case_number="CS-001",
        source_alert_id=uuid.UUID("00000000-0000-0000-0000-0000aa360490"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000d8511ed4"),
        status="PENDING_INFORMATION",
        priority="HIGH",
        assigned_user_id=uuid.UUID("00000000-0000-0000-0000-00001fdb9834"),
        recommendation_state="DRAFT",
        created_by_user_id=uuid.UUID("00000000-0000-0000-0000-00001fdb9834"),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(case)
    db_session.commit()
    
    # Attempt invalid transition
    service = CaseService(db_session)
    with pytest.raises(ValueError) as exc_info:
        service.transition_status(
            case_id=uuid.UUID("00000000-0000-0000-0000-000056ae0fb0"),
            new_status="REVIEW_READY",
            actor_id=uuid.UUID("00000000-0000-0000-0000-00001fdb9834")
        )
    
    assert "Invalid transition" in str(exc_info.value)


def test_transition_case_not_found(db_session):
    """Test transition fails when case doesn't exist"""
    # Create user
    user = User(
        user_id=uuid.UUID("00000000-0000-0000-0000-00001fdb9834"),
        username="riya",
        display_name="Riya Sharma",
        email="riya@example.com",
        password_hash="hash",
        primary_role="investigator",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    
    # Attempt transition on non-existent case
    service = CaseService(db_session)
    with pytest.raises(ValueError) as exc_info:
        service.transition_status(
            case_id=uuid.UUID("00000000-0000-0000-0000-00005e5b5a87"),
            new_status="PENDING_INFORMATION",
            actor_id=uuid.UUID("00000000-0000-0000-0000-00001fdb9834")
        )
    
    assert "Case not found" in str(exc_info.value)
