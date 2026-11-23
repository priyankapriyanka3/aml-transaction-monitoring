"""Tests for information request service response recording."""
import uuid
from datetime import datetime, timezone, timedelta
import pytest
from sqlalchemy.orm import Session
from app.models.case import AmlCase
from app.models.evidence_gap import EvidenceGap
from app.models.information_request import InformationRequest
from app.services.information_request_service import InformationRequestService


def test_record_response(db_session: Session):
    """Test recording a response to an information request."""
    # Create test case
    case = AmlCase(
        case_ref="CS-TEST-001",
        primary_alert_id=uuid.uuid4(),
        created_by_user_id=uuid.uuid4(),
        status="PENDING_INFORMATION",
        current_blocker_state="OPEN_REQUESTS",
        created_at_utc=datetime.now(timezone.utc),
        updated_at_utc=datetime.now(timezone.utc)
    )
    db_session.add(case)
    db_session.flush()
    
    # Create evidence gap
    gap = EvidenceGap(
        case_id=case.case_id,
        title="Test gap",
        description="Test description",
        status="OPEN",
        created_by_user_id=case.created_by_user_id,
        created_at_utc=datetime.now(timezone.utc)
    )
    db_session.add(gap)
    db_session.flush()
    
    # Create information request with OPEN status
    request = InformationRequest(
        request_ref="IR-TEST-001",
        case_id=case.case_id,
        gap_id=gap.gap_id,
        target_party="Test party",
        delivery_channel="Email",
        reason_text="Test reason",
        due_at_utc=datetime.now(timezone.utc) + timedelta(days=3),
        status="OPEN",
        created_by_user_id=case.created_by_user_id,
        created_at_utc=datetime.now(timezone.utc),
        updated_at_utc=datetime.now(timezone.utc)
    )
    db_session.add(request)
    db_session.commit()
    
    # Record response
    service = InformationRequestService(db_session)
    response_summary = "Customer provided all required documentation including invoices and contracts."
    received_at = datetime.now(timezone.utc) - timedelta(hours=2)
    
    updated_request = service.record_response(
        request_id=request.request_id,
        response_summary=response_summary,
        received_at_utc=received_at,
        actor_user_id=case.created_by_user_id,
        actor_role="INVESTIGATOR",
        correlation_id=str(uuid.uuid4())
    )
    
    # Verify request updated
    assert updated_request.status == "RESPONDED"
    assert updated_request.response_summary == response_summary
    assert updated_request.response_received_at_utc == received_at
    
    # Verify case blocker_state updated (should be NONE now since no OPEN requests remain)
    db_session.refresh(case)
    assert case.current_blocker_state == "NONE"


def test_record_response_not_found(db_session: Session):
    """Test recording response to non-existent request raises ValueError."""
    service = InformationRequestService(db_session)
    
    with pytest.raises(ValueError, match="not found"):
        service.record_response(
            request_id=uuid.uuid4(),
            response_summary="Test summary",
            received_at_utc=datetime.now(timezone.utc),
            actor_user_id=uuid.uuid4(),
            actor_role="INVESTIGATOR",
            correlation_id=str(uuid.uuid4())
        )
