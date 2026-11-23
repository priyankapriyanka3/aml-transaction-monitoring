"""Tests for readiness service checklist derivation."""
import uuid
from datetime import datetime, timezone, timedelta
import pytest
from sqlalchemy.orm import Session
from app.models.case import AmlCase
from app.models.case_alert_link import CaseAlertLink
from app.models.case_note import CaseNote
from app.models.evidence_gap import EvidenceGap
from app.models.information_request import InformationRequest
from app.services.readiness_service import ReadinessService


def test_derive_checklist_all_complete(db_session: Session):
    """Test readiness checklist derivation when all items are complete."""
    # Create test case
    case = AmlCase(
        case_ref="CS-TEST-001",
        primary_alert_id=uuid.uuid4(),
        created_by_user_id=uuid.uuid4(),
        status="INVESTIGATING",
        current_blocker_state="NONE",
        created_at_utc=datetime.now(timezone.utc),
        updated_at_utc=datetime.now(timezone.utc)
    )
    db_session.add(case)
    db_session.flush()
    
    # Add linked alert (checklist item 1)
    link = CaseAlertLink(
        case_id=case.case_id,
        alert_id=uuid.uuid4(),
        is_primary=True,
        linked_by_user_id=case.created_by_user_id,
        linked_at_utc=datetime.now(timezone.utc)
    )
    db_session.add(link)
    
    # Add investigation note (checklist item 2)
    note = CaseNote(
        case_id=case.case_id,
        note_category="investigation",
        note_text="Test note",
        author_user_id=case.created_by_user_id,
        authored_at_utc=datetime.now(timezone.utc)
    )
    db_session.add(note)
    
    # Add evidence gap and RESPONDED request (checklist items 3 & 4)
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
    
    request = InformationRequest(
        request_ref="IR-TEST-001",
        case_id=case.case_id,
        gap_id=gap.gap_id,
        target_party="Test party",
        delivery_channel="Email",
        reason_text="Test reason",
        due_at_utc=datetime.now(timezone.utc) + timedelta(days=3),
        status="RESPONDED",
        created_by_user_id=case.created_by_user_id,
        response_summary="Response received",
        response_received_at_utc=datetime.now(timezone.utc) - timedelta(hours=1),
        created_at_utc=datetime.now(timezone.utc),
        updated_at_utc=datetime.now(timezone.utc)
    )
    db_session.add(request)
    db_session.commit()
    
    # Derive checklist
    service = ReadinessService(db_session)
    readiness = service.derive_checklist(case.case_id)
    
    # Verify all checklist items are complete
    assert len(readiness.checklist) == 4
    
    linked_evidence = next(item for item in readiness.checklist if item.name == "linked_evidence")
    assert linked_evidence.complete is True
    assert "1 alert" in linked_evidence.details
    
    investigation_notes = next(item for item in readiness.checklist if item.name == "investigation_notes")
    assert investigation_notes.complete is True
    assert "1 note" in investigation_notes.details
    
    responses_reviewed = next(item for item in readiness.checklist if item.name == "responses_reviewed")
    assert responses_reviewed.complete is True
    assert "1 of 1" in responses_reviewed.details
    
    no_open_requests = next(item for item in readiness.checklist if item.name == "no_open_requests")
    assert no_open_requests.complete is True
    assert "No open" in no_open_requests.details
    
    # Verify package summary
    assert readiness.package_summary.alert_count == 1
    assert readiness.package_summary.note_count == 1
    assert readiness.package_summary.request_count == 1


def test_derive_checklist_with_blockers(db_session: Session):
    """Test readiness checklist derivation with open requests (blockers)."""
    # Create test case
    case = AmlCase(
        case_ref="CS-TEST-002",
        primary_alert_id=uuid.uuid4(),
        created_by_user_id=uuid.uuid4(),
        status="PENDING_INFORMATION",
        current_blocker_state="OPEN_REQUESTS",
        created_at_utc=datetime.now(timezone.utc),
        updated_at_utc=datetime.now(timezone.utc)
    )
    db_session.add(case)
    db_session.flush()
    
    # Add linked alert
    link = CaseAlertLink(
        case_id=case.case_id,
        alert_id=uuid.uuid4(),
        is_primary=True,
        linked_by_user_id=case.created_by_user_id,
        linked_at_utc=datetime.now(timezone.utc)
    )
    db_session.add(link)
    
    # Add evidence gap and OPEN request (blocker)
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
    
    request = InformationRequest(
        request_ref="IR-TEST-002",
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
    
    # Derive checklist
    service = ReadinessService(db_session)
    readiness = service.derive_checklist(case.case_id)
    
    # Verify checklist items with blockers
    responses_reviewed = next(item for item in readiness.checklist if item.name == "responses_reviewed")
    assert responses_reviewed.complete is False
    assert "0 of 1" in responses_reviewed.details
    
    no_open_requests = next(item for item in readiness.checklist if item.name == "no_open_requests")
    assert no_open_requests.complete is False
    assert "1 open" in no_open_requests.details


def test_derive_checklist_case_not_found(db_session: Session):
    """Test derive checklist for non-existent case raises ValueError."""
    service = ReadinessService(db_session)
    
    with pytest.raises(ValueError, match="not found"):
        service.derive_checklist(uuid.uuid4())
