"""
Unit tests for information request service.
Tests request creation, response recording, and SLA tracking.
"""
import pytest
import uuid
from datetime import datetime, timedelta

from app.models.aml_case import AMLCase
from app.models.information_request import InformationRequest
from app.models.user import User
from app.services.information_request_service import InformationRequestService


def test_create_request_success(db_session):
    """Test successful information request creation"""
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
    
    # Create request
    service = InformationRequestService(db_session)
    due_at = datetime.utcnow() + timedelta(days=7)
    response, case_status = service.create_request(
        case_id=uuid.UUID("00000000-0000-0000-0000-000056ae0fb0"),
        recipient_channel="EMAIL",
        requested_summary="Provide supporting documents",
        rationale="Need verification of transaction purpose",
        due_at=due_at,
        actor_id=uuid.UUID("00000000-0000-0000-0000-00001fdb9834")
    )
    
    assert response.information_request_id == "IR-001"
    assert response.status == "OPEN"
    assert response.case_id == "case-001"
    assert case_status == "PENDING_INFORMATION"
    assert response.days_remaining == 6  # Due in 7 days, rounds down


def test_create_request_validates_due_at_future(db_session):
    """Test that due_at must be in future"""
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
    
    # Attempt to create request with past due_at
    service = InformationRequestService(db_session)
    due_at = datetime.utcnow() - timedelta(days=1)
    
    with pytest.raises(ValueError) as exc_info:
        service.create_request(
            case_id=uuid.UUID("00000000-0000-0000-0000-000056ae0fb0"),
            recipient_channel="EMAIL",
            requested_summary="Provide documents",
            rationale="Need verification",
            due_at=due_at,
            actor_id=uuid.UUID("00000000-0000-0000-0000-00001fdb9834")
        )
    
    assert "must be a future timestamp" in str(exc_info.value)


def test_create_request_transitions_case_to_pending(db_session):
    """Test that request creation transitions case to PENDING_INFORMATION"""
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
    
    # Create request
    service = InformationRequestService(db_session)
    due_at = datetime.utcnow() + timedelta(days=5)
    response, case_status = service.create_request(
        case_id=uuid.UUID("00000000-0000-0000-0000-000056ae0fb0"),
        recipient_channel="PORTAL",
        requested_summary="Submit ownership documents",
        rationale="Enhanced due diligence required",
        due_at=due_at,
        actor_id=uuid.UUID("00000000-0000-0000-0000-00001fdb9834")
    )
    
    # Verify case status changed
    assert case_status == "PENDING_INFORMATION"
    
    # Verify in database
    db_case = db_session.query(AMLCase).filter_by(case_id=uuid.UUID("00000000-0000-0000-0000-000056ae0fb0")).first()
    assert db_case.status == "PENDING_INFORMATION"


def test_list_requests_computes_days_remaining(db_session):
    """Test that list_requests computes days_remaining correctly"""
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
    
    # Create request
    request = InformationRequest(
        information_request_id=uuid.uuid4(),
        case_id=uuid.UUID("00000000-0000-0000-0000-000056ae0fb0"),
        recipient_channel="EMAIL",
        requested_summary="Provide documents",
        rationale="Verification needed",
        status="OPEN",
        due_at=datetime.utcnow() + timedelta(days=3),
        created_by_user_id=uuid.UUID("00000000-0000-0000-0000-00001fdb9834"),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(request)
    db_session.commit()
    
    # List requests
    service = InformationRequestService(db_session)
    requests = service.list_requests_for_case("case-001")
    
    assert len(requests) == 1
    assert requests[0].days_remaining == 2  # Due in 3 days, rounds down
    assert requests[0].is_overdue is False


def test_list_requests_identifies_overdue(db_session):
    """Test that list_requests identifies overdue requests"""
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
    
    # Create overdue request
    request = InformationRequest(
        information_request_id=uuid.uuid4(),
        case_id=uuid.UUID("00000000-0000-0000-0000-000056ae0fb0"),
        recipient_channel="EMAIL",
        requested_summary="Provide documents",
        rationale="Verification needed",
        status="OPEN",
        due_at=datetime.utcnow() - timedelta(days=2),  # Overdue by 2 days
        created_by_user_id=uuid.UUID("00000000-0000-0000-0000-00001fdb9834"),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(request)
    db_session.commit()
    
    # List requests
    service = InformationRequestService(db_session)
    requests = service.list_requests_for_case("case-001")
    
    assert len(requests) == 1
    assert requests[0].is_overdue is True
    assert requests[0].days_remaining == -3  # Overdue by 2 days, rounds down


def test_record_response_success(db_session):
    """Test successful response recording"""
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
    
    # Create request
    request = InformationRequest(
        information_request_id=uuid.uuid4(),
        case_id=uuid.UUID("00000000-0000-0000-0000-000056ae0fb0"),
        recipient_channel="EMAIL",
        requested_summary="Provide documents",
        rationale="Verification needed",
        status="OPEN",
        due_at=datetime.utcnow() + timedelta(days=3),
        created_by_user_id=uuid.UUID("00000000-0000-0000-0000-00001fdb9834"),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(request)
    db_session.commit()
    
    # Record response
    service = InformationRequestService(db_session)
    received_at = datetime.utcnow() - timedelta(hours=1)
    response, case_status = service.record_response(
        information_request_id=uuid.uuid4(),
        response_summary="Documents provided as requested",
        received_at=received_at,
        response_channel="EMAIL",
        actor_id=uuid.UUID("00000000-0000-0000-0000-00001fdb9834")
    )
    
    assert response.status == "RESPONDED"
    assert response.response_summary == "Documents provided as requested"
    assert case_status == "INVESTIGATING"


def test_record_response_validates_received_at_not_future(db_session):
    """Test that received_at cannot be in future"""
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
    
    # Create request
    request = InformationRequest(
        information_request_id=uuid.uuid4(),
        case_id=uuid.UUID("00000000-0000-0000-0000-000056ae0fb0"),
        recipient_channel="EMAIL",
        requested_summary="Provide documents",
        rationale="Verification needed",
        status="OPEN",
        due_at=datetime.utcnow() + timedelta(days=3),
        created_by_user_id=uuid.UUID("00000000-0000-0000-0000-00001fdb9834"),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(request)
    db_session.commit()
    
    # Attempt to record response with future received_at
    service = InformationRequestService(db_session)
    received_at = datetime.utcnow() + timedelta(days=1)
    
    with pytest.raises(ValueError) as exc_info:
        service.record_response(
            information_request_id=uuid.uuid4(),
            response_summary="Documents provided",
            received_at=received_at,
            response_channel="EMAIL",
            actor_id=uuid.UUID("00000000-0000-0000-0000-00001fdb9834")
        )
    
    assert "cannot be in the future" in str(exc_info.value)


def test_record_response_transitions_case_to_investigating(db_session):
    """Test that response recording transitions case back to INVESTIGATING"""
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
    
    # Create request
    request = InformationRequest(
        information_request_id=uuid.uuid4(),
        case_id=uuid.UUID("00000000-0000-0000-0000-000056ae0fb0"),
        recipient_channel="EMAIL",
        requested_summary="Provide documents",
        rationale="Verification needed",
        status="OPEN",
        due_at=datetime.utcnow() + timedelta(days=3),
        created_by_user_id=uuid.UUID("00000000-0000-0000-0000-00001fdb9834"),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(request)
    db_session.commit()
    
    # Record response
    service = InformationRequestService(db_session)
    received_at = datetime.utcnow()
    response, case_status = service.record_response(
        information_request_id=uuid.uuid4(),
        response_summary="All documents received",
        received_at=received_at,
        response_channel="PORTAL",
        actor_id=uuid.UUID("00000000-0000-0000-0000-00001fdb9834")
    )
    
    # Verify case status changed
    assert case_status == "INVESTIGATING"
    
    # Verify in database
    db_case = db_session.query(AMLCase).filter_by(case_id=uuid.UUID("00000000-0000-0000-0000-000056ae0fb0")).first()
    assert db_case.status == "INVESTIGATING"


def test_record_response_rejects_non_open_requests(db_session):
    """Test that response recording fails for non-OPEN requests"""
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
    
    # Create already-responded request
    request = InformationRequest(
        information_request_id=uuid.uuid4(),
        case_id=uuid.UUID("00000000-0000-0000-0000-000056ae0fb0"),
        recipient_channel="EMAIL",
        requested_summary="Provide documents",
        rationale="Verification needed",
        status="RESPONDED",
        due_at=datetime.utcnow() + timedelta(days=3),
        response_summary="Already responded",
        response_channel="EMAIL",
        response_received_at=datetime.utcnow() - timedelta(days=1),
        created_by_user_id=uuid.UUID("00000000-0000-0000-0000-00001fdb9834"),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(request)
    db_session.commit()
    
    # Attempt to record response again
    service = InformationRequestService(db_session)
    
    with pytest.raises(ValueError) as exc_info:
        service.record_response(
            information_request_id=uuid.uuid4(),
            response_summary="Duplicate response",
            received_at=datetime.utcnow(),
            response_channel="EMAIL",
            actor_id=uuid.UUID("00000000-0000-0000-0000-00001fdb9834")
        )
    
    assert "Cannot record response" in str(exc_info.value)
