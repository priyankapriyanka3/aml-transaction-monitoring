"""
Acceptance tests for TASK-10: Information Request Response and SLA Tracking
Tests FR-017 and FR-018 acceptance criteria.
"""
import json
import uuid
from datetime import datetime, timedelta

from app.models.aml_case import AMLCase
from app.models.information_request import InformationRequest
from app.models.user import User


def test_fr017_request_issuance_updates_case_state(auth_client, db_session):
    """
    FR-017: Request issuance updates the case state automatically or through a guided confirmation step
    """
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
    
    # Issue information request
    response = auth_client.post(
        "/api/v1/information-requests",
        json={
            "case_id": "case-001",
            "recipient_channel": "EMAIL",
            "requested_summary": "Provide supporting documents for transaction verification",
            "rationale": "Need to verify legitimacy of transaction",
            "due_at": (datetime.utcnow() + timedelta(days=5)).isoformat()
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    
    # Verify case state updated automatically
    assert data["case_status_after_create"] == "PENDING_INFORMATION"


def test_fr017_response_receipt_restores_active_investigation_state(auth_client, db_session):
    """
    FR-017: Response receipt restores the case to an active investigation state
    """
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
    
    # Create case in PENDING_INFORMATION state
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
    
    # Create open information request
    info_request = InformationRequest(
        information_request_id=uuid.uuid4(),
        case_id=uuid.UUID("00000000-0000-0000-0000-000056ae0fb0"),
        recipient_channel="EMAIL",
        requested_summary="Provide documents",
        rationale="Verification needed",
        status="OPEN",
        due_at=datetime.utcnow() + timedelta(days=3),
        response_summary=None,
        response_channel=None,
        response_received_at=None,
        created_by_user_id=uuid.UUID("00000000-0000-0000-0000-00001fdb9834"),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(info_request)
    db_session.commit()
    
    # Record response
    response = auth_client.post(
        "/api/v1/information-requests/IR-001/record-response",
        json={
            "response_summary": "Documents have been provided as requested",
            "received_at": datetime.utcnow().isoformat(),
            "response_channel": "EMAIL"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify case restored to active investigation state
    assert data["case_status_after_response"] == "INVESTIGATING"


def test_fr017_timeline_records_state_changes_with_triggering_events(auth_client, db_session):
    """
    FR-017: The timeline records each state change with its triggering event
    """
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
    
    # Issue request
    auth_client.post(
        "/api/v1/information-requests",
        json={
            "case_id": "case-001",
            "recipient_channel": "EMAIL",
            "requested_summary": "Provide supporting documents",
            "rationale": "Need verification",
            "due_at": (datetime.utcnow() + timedelta(days=5)).isoformat()
        }
    )
    
    # Check audit events
    response = auth_client.get("/api/v1/audit-events?entity_id=case-001")
    assert response.status_code == 200
    
    data = response.json()
    assert data["total_count"] >= 1
    
    # Find INFORMATION_REQUEST_CREATED event
    created_events = [e for e in data["items"] if e["action_type"] == "INFORMATION_REQUEST_CREATED"]
    assert len(created_events) >= 1
    
    event = created_events[0]
    payload = event["payload"]
    assert "previous_status" in payload
    assert "new_status" in payload
    assert payload["previous_status"] == "INVESTIGATING"
    assert payload["new_status"] == "PENDING_INFORMATION"


def test_fr018_open_requests_show_days_remaining_or_overdue_status(auth_client, db_session):
    """
    FR-018: Open requests show days remaining or overdue status
    """
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
    
    # Create open request due in future
    future_request = InformationRequest(
        information_request_id=uuid.uuid4(),
        case_id=uuid.UUID("00000000-0000-0000-0000-000056ae0fb0"),
        recipient_channel="EMAIL",
        requested_summary="Future request",
        rationale="Testing",
        status="OPEN",
        due_at=datetime.utcnow() + timedelta(days=5),
        response_summary=None,
        response_channel=None,
        response_received_at=None,
        created_by_user_id=uuid.UUID("00000000-0000-0000-0000-00001fdb9834"),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(future_request)
    
    # Create overdue request
    overdue_request = InformationRequest(
        information_request_id=uuid.uuid4(),
        case_id=uuid.UUID("00000000-0000-0000-0000-000056ae0fb0"),
        recipient_channel="EMAIL",
        requested_summary="Overdue request",
        rationale="Testing",
        status="OPEN",
        due_at=datetime.utcnow() - timedelta(days=2),
        response_summary=None,
        response_channel=None,
        response_received_at=None,
        created_by_user_id=uuid.UUID("00000000-0000-0000-0000-00001fdb9834"),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(overdue_request)
    db_session.commit()
    
    # Get requests
    response = auth_client.get("/api/v1/information-requests?case_id=case-001")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 2
    
    # Find each request
    future_req_data = next(r for r in data if r["information_request_id"] == "IR-001")
    overdue_req_data = next(r for r in data if r["information_request_id"] == "IR-002")
    
    # Verify days_remaining shown for future request
    assert future_req_data["days_remaining"] is not None
    assert future_req_data["days_remaining"] >= 4  # Due in 5 days, might be 4 depending on timing
    assert future_req_data["is_overdue"] is False
    
    # Verify overdue status shown for overdue request
    assert overdue_req_data["is_overdue"] is True


def test_fr018_late_requests_distinguishable_from_ontime_requests(auth_client, db_session):
    """
    FR-018: Late requests are distinguishable from on-time requests
    """
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
    
    # Create on-time request
    ontime_request = InformationRequest(
        information_request_id=uuid.uuid4(),
        case_id=uuid.UUID("00000000-0000-0000-0000-000056ae0fb0"),
        recipient_channel="EMAIL",
        requested_summary="On-time request",
        rationale="Testing",
        status="OPEN",
        due_at=datetime.utcnow() + timedelta(days=3),
        response_summary=None,
        response_channel=None,
        response_received_at=None,
        created_by_user_id=uuid.UUID("00000000-0000-0000-0000-00001fdb9834"),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(ontime_request)
    
    # Create late request
    late_request = InformationRequest(
        information_request_id=uuid.uuid4(),
        case_id=uuid.UUID("00000000-0000-0000-0000-000056ae0fb0"),
        recipient_channel="EMAIL",
        requested_summary="Late request",
        rationale="Testing",
        status="OPEN",
        due_at=datetime.utcnow() - timedelta(days=1),
        response_summary=None,
        response_channel=None,
        response_received_at=None,
        created_by_user_id=uuid.UUID("00000000-0000-0000-0000-00001fdb9834"),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(late_request)
    db_session.commit()
    
    # Get requests
    response = auth_client.get("/api/v1/information-requests?case_id=case-001")
    assert response.status_code == 200
    
    data = response.json()
    
    ontime_data = next(r for r in data if r["information_request_id"] == "IR-001")
    late_data = next(r for r in data if r["information_request_id"] == "IR-002")
    
    # Verify clear distinction via is_overdue flag
    assert ontime_data["is_overdue"] is False
    assert late_data["is_overdue"] is True


def test_fr018_reviewers_see_request_timeliness_history(auth_client, db_session):
    """
    FR-018: Reviewers can see request timeliness history during decision-making
    """
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
    
    # Create responded request with historical timeliness
    request = InformationRequest(
        information_request_id=uuid.uuid4(),
        case_id=uuid.UUID("00000000-0000-0000-0000-000056ae0fb0"),
        recipient_channel="EMAIL",
        requested_summary="Historical request",
        rationale="Testing",
        status="RESPONDED",
        due_at=datetime.utcnow() + timedelta(days=7),
        response_summary="Response provided",
        response_channel="EMAIL",
        response_received_at=datetime.utcnow() + timedelta(days=3),  # Responded on time
        created_by_user_id=uuid.UUID("00000000-0000-0000-0000-00001fdb9834"),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(request)
    db_session.commit()
    
    # Get request history
    response = auth_client.get("/api/v1/information-requests?case_id=case-001")
    assert response.status_code == 200
    
    data = response.json()
    req_data = data[0]
    
    # Verify historical timeliness visible
    assert req_data["status"] == "RESPONDED"
    assert req_data["due_at"] is not None
    assert req_data["response_received_at"] is not None
    assert req_data["created_at"] is not None
    
    # Verify reviewer can see if response was on-time
    # (response_received_at < due_at indicates on-time response)
    from datetime import datetime as dt
    response_time = dt.fromisoformat(req_data["response_received_at"].replace("Z", "+00:00"))
    due_time = dt.fromisoformat(req_data["due_at"].replace("Z", "+00:00"))
    assert response_time < due_time  # On-time response visible
