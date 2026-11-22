"""
Integration tests for information request API endpoints.
Tests complete request/response workflows with authentication.
"""
from datetime import datetime, timedelta
import uuid

from app.models.aml_case import AMLCase
from app.models.information_request import InformationRequest


def test_create_information_request_success(auth_client, db_session):
    """Test POST /api/v1/information-requests creates request and transitions case"""
    # Create case
    case = AMLCase(
        case_id=uuid.UUID("00000000-0000-0000-0000-000056ae0fb0"),
        case_number="CS-001",
        source_alert_id=uuid.UUID("00000000-0000-0000-0000-0000aa360490"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000d8511ed4"),
        status="INVESTIGATING",
        priority="HIGH",
        assigned_user_id=uuid.UUID("00000000-0000-0000-0000-0000291a87a3"),
        recommendation_state="DRAFT",
        created_by_user_id=uuid.UUID("00000000-0000-0000-0000-0000291a87a3"),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(case)
    db_session.commit()
    
    # Create request
    due_at = datetime.utcnow() + timedelta(days=7)
    response = auth_client.post(
        "/api/v1/information-requests",
        json={
            "case_id": "case-001",
            "recipient_channel": "EMAIL",
            "requested_summary": "Please provide supporting invoices and shipping documents",
            "rationale": "Need to verify legitimacy of large cross-border transaction",
            "due_at": due_at.isoformat()
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["information_request_id"] == "IR-001"
    assert data["status"] == "OPEN"
    assert data["case_id"] == "case-001"
    assert data["case_status_after_create"] == "PENDING_INFORMATION"


def test_create_information_request_validates_requested_summary(auth_client, db_session):
    """Test validation of requested_summary minimum length"""
    # Create case
    case = AMLCase(
        case_id=uuid.UUID("00000000-0000-0000-0000-000056ae0fb0"),
        case_number="CS-001",
        source_alert_id=uuid.UUID("00000000-0000-0000-0000-0000aa360490"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000d8511ed4"),
        status="INVESTIGATING",
        priority="HIGH",
        assigned_user_id=uuid.UUID("00000000-0000-0000-0000-0000291a87a3"),
        recommendation_state="DRAFT",
        created_by_user_id=uuid.UUID("00000000-0000-0000-0000-0000291a87a3"),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(case)
    db_session.commit()
    
    # Attempt with short requested_summary
    response = auth_client.post(
        "/api/v1/information-requests",
        json={
            "case_id": "case-001",
            "recipient_channel": "EMAIL",
            "requested_summary": "Short",  # Less than 10 chars
            "rationale": "Need verification documents",
            "due_at": (datetime.utcnow() + timedelta(days=5)).isoformat()
        }
    )
    
    assert response.status_code == 422


def test_create_information_request_validates_due_at_future(auth_client, db_session):
    """Test validation of due_at being in future"""
    # Create case
    case = AMLCase(
        case_id=uuid.UUID("00000000-0000-0000-0000-000056ae0fb0"),
        case_number="CS-001",
        source_alert_id=uuid.UUID("00000000-0000-0000-0000-0000aa360490"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000d8511ed4"),
        status="INVESTIGATING",
        priority="HIGH",
        assigned_user_id=uuid.UUID("00000000-0000-0000-0000-0000291a87a3"),
        recommendation_state="DRAFT",
        created_by_user_id=uuid.UUID("00000000-0000-0000-0000-0000291a87a3"),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(case)
    db_session.commit()
    
    # Attempt with past due_at
    response = auth_client.post(
        "/api/v1/information-requests",
        json={
            "case_id": "case-001",
            "recipient_channel": "EMAIL",
            "requested_summary": "Provide supporting documents",
            "rationale": "Need verification",
            "due_at": (datetime.utcnow() - timedelta(days=1)).isoformat()
        }
    )
    
    assert response.status_code == 422
    assert "must be a future timestamp" in response.json()["detail"]


def test_list_information_requests_by_case(auth_client, db_session):
    """Test GET /api/v1/information-requests?case_id=X returns requests"""
    # Create case
    case = AMLCase(
        case_id=uuid.UUID("00000000-0000-0000-0000-000056ae0fb0"),
        case_number="CS-001",
        source_alert_id=uuid.UUID("00000000-0000-0000-0000-0000aa360490"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000d8511ed4"),
        status="PENDING_INFORMATION",
        priority="HIGH",
        assigned_user_id=uuid.UUID("00000000-0000-0000-0000-0000291a87a3"),
        recommendation_state="DRAFT",
        created_by_user_id=uuid.UUID("00000000-0000-0000-0000-0000291a87a3"),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(case)
    
    # Create requests
    request1 = InformationRequest(
        information_request_id=uuid.uuid4(),
        case_id=uuid.UUID("00000000-0000-0000-0000-000056ae0fb0"),
        recipient_channel="EMAIL",
        requested_summary="Provide documents for review",
        rationale="Initial document request",
        status="OPEN",
        due_at=datetime.utcnow() + timedelta(days=5),
        created_by_user_id=uuid.UUID("00000000-0000-0000-0000-0000291a87a3"),
        created_at=datetime.utcnow() - timedelta(hours=2),
        updated_at=datetime.utcnow() - timedelta(hours=2)
    )
    request2 = InformationRequest(
        information_request_id=uuid.uuid4(),
        case_id=uuid.UUID("00000000-0000-0000-0000-000056ae0fb0"),
        recipient_channel="PORTAL",
        requested_summary="Submit ownership structure information",
        rationale="Enhanced due diligence",
        status="OPEN",
        due_at=datetime.utcnow() - timedelta(days=1),  # Overdue
        created_by_user_id=uuid.UUID("00000000-0000-0000-0000-0000291a87a3"),
        created_at=datetime.utcnow() - timedelta(hours=1),
        updated_at=datetime.utcnow() - timedelta(hours=1)
    )
    db_session.add(request1)
    db_session.add(request2)
    db_session.commit()
    
    # List requests
    response = auth_client.get("/api/v1/information-requests?case_id=case-001")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    
    # Verify newest first
    assert data[0]["information_request_id"] == "IR-002"
    assert data[1]["information_request_id"] == "IR-001"
    
    # Verify overdue detection
    assert data[0]["is_overdue"] is True
    assert data[1]["is_overdue"] is False


def test_record_response_success(auth_client, db_session):
    """Test POST /api/v1/information-requests/{id}/record-response"""
    # Create case
    case = AMLCase(
        case_id=uuid.UUID("00000000-0000-0000-0000-000056ae0fb0"),
        case_number="CS-001",
        source_alert_id=uuid.UUID("00000000-0000-0000-0000-0000aa360490"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000d8511ed4"),
        status="PENDING_INFORMATION",
        priority="HIGH",
        assigned_user_id=uuid.UUID("00000000-0000-0000-0000-0000291a87a3"),
        recommendation_state="DRAFT",
        created_by_user_id=uuid.UUID("00000000-0000-0000-0000-0000291a87a3"),
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
        due_at=datetime.utcnow() + timedelta(days=5),
        created_by_user_id=uuid.UUID("00000000-0000-0000-0000-0000291a87a3"),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(request)
    db_session.commit()
    
    # Record response
    received_at = datetime.utcnow() - timedelta(hours=2)
    response = auth_client.post(
        "/api/v1/information-requests/IR-001/record-response",
        json={
            "response_summary": "All requested documents have been provided via secure portal",
            "received_at": received_at.isoformat(),
            "response_channel": "PORTAL"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "RESPONDED"
    assert data["case_status_after_response"] == "INVESTIGATING"


def test_record_response_validates_response_summary(auth_client, db_session):
    """Test validation of response_summary minimum length"""
    # Create case
    case = AMLCase(
        case_id=uuid.UUID("00000000-0000-0000-0000-000056ae0fb0"),
        case_number="CS-001",
        source_alert_id=uuid.UUID("00000000-0000-0000-0000-0000aa360490"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000d8511ed4"),
        status="PENDING_INFORMATION",
        priority="HIGH",
        assigned_user_id=uuid.UUID("00000000-0000-0000-0000-0000291a87a3"),
        recommendation_state="DRAFT",
        created_by_user_id=uuid.UUID("00000000-0000-0000-0000-0000291a87a3"),
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
        due_at=datetime.utcnow() + timedelta(days=5),
        created_by_user_id=uuid.UUID("00000000-0000-0000-0000-0000291a87a3"),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(request)
    db_session.commit()
    
    # Attempt with short response_summary
    response = auth_client.post(
        "/api/v1/information-requests/IR-001/record-response",
        json={
            "response_summary": "Done",  # Less than 10 chars
            "received_at": datetime.utcnow().isoformat(),
            "response_channel": "EMAIL"
        }
    )
    
    assert response.status_code == 422


def test_post_status_transition_investigating_to_pending(auth_client, db_session):
    """Test POST /api/v1/cases/{id}/status-transitions"""
    # Create case
    case = AMLCase(
        case_id=uuid.UUID("00000000-0000-0000-0000-000056ae0fb0"),
        case_number="CS-001",
        source_alert_id=uuid.UUID("00000000-0000-0000-0000-0000aa360490"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000d8511ed4"),
        status="INVESTIGATING",
        priority="HIGH",
        assigned_user_id=uuid.UUID("00000000-0000-0000-0000-0000291a87a3"),
        recommendation_state="DRAFT",
        created_by_user_id=uuid.UUID("00000000-0000-0000-0000-0000291a87a3"),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(case)
    db_session.commit()
    
    # Transition status
    response = auth_client.post(
        "/api/v1/cases/case-001/status-transitions",
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
    assert data["case_id"] == "case-001"


def test_post_status_transition_invalid_returns_409(auth_client, db_session):
    """Test invalid status transition returns 409 Conflict"""
    # Create case
    case = AMLCase(
        case_id=uuid.UUID("00000000-0000-0000-0000-000056ae0fb0"),
        case_number="CS-001",
        source_alert_id=uuid.UUID("00000000-0000-0000-0000-0000aa360490"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000d8511ed4"),
        status="INVESTIGATING",
        priority="HIGH",
        assigned_user_id=uuid.UUID("00000000-0000-0000-0000-0000291a87a3"),
        recommendation_state="DRAFT",
        created_by_user_id=uuid.UUID("00000000-0000-0000-0000-0000291a87a3"),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(case)
    db_session.commit()
    
    # Attempt invalid transition
    response = auth_client.post(
        "/api/v1/cases/case-001/status-transitions",
        json={
            "new_status": "SUBMITTED_FOR_REVIEW",
            "reason": "Skip ahead",
            "trigger_event": "Invalid"
        }
    )
    
    assert response.status_code == 409
    assert "Invalid transition" in response.json()["detail"]


def test_complete_workflow_request_to_response(auth_client, db_session):
    """Test complete workflow: create request, list it, record response"""
    # Create case
    case = AMLCase(
        case_id=uuid.UUID("00000000-0000-0000-0000-000056ae0fb0"),
        case_number="CS-001",
        source_alert_id=uuid.UUID("00000000-0000-0000-0000-0000aa360490"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-0000d8511ed4"),
        status="INVESTIGATING",
        priority="HIGH",
        assigned_user_id=uuid.UUID("00000000-0000-0000-0000-0000291a87a3"),
        recommendation_state="DRAFT",
        created_by_user_id=uuid.UUID("00000000-0000-0000-0000-0000291a87a3"),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(case)
    db_session.commit()
    
    # Step 1: Create request
    due_at = datetime.utcnow() + timedelta(days=7)
    create_response = auth_client.post(
        "/api/v1/information-requests",
        json={
            "case_id": "case-001",
            "recipient_channel": "EMAIL",
            "requested_summary": "Submit detailed transaction breakdown",
            "rationale": "Need comprehensive transaction analysis",
            "due_at": due_at.isoformat()
        }
    )
    assert create_response.status_code == 201
    request_id = create_response.json()["information_request_id"]
    
    # Step 2: List requests
    list_response = auth_client.get("/api/v1/information-requests?case_id=case-001")
    assert list_response.status_code == 200
    requests = list_response.json()
    assert len(requests) == 1
    assert requests[0]["status"] == "OPEN"
    assert requests[0]["is_overdue"] is False
    
    # Step 3: Record response
    received_at = datetime.utcnow() - timedelta(hours=1)
    response_response = auth_client.post(
        f"/api/v1/information-requests/{request_id}/record-response",
        json={
            "response_summary": "Complete transaction breakdown provided with supporting documentation",
            "received_at": received_at.isoformat(),
            "response_channel": "EMAIL"
        }
    )
    assert response_response.status_code == 200
    assert response_response.json()["status"] == "RESPONDED"
    assert response_response.json()["case_status_after_response"] == "INVESTIGATING"
    
    # Step 4: Verify case status
    db_session.refresh(case)
    assert case.status == "INVESTIGATING"
