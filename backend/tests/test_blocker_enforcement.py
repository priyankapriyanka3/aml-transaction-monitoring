"""Tests for decision blocker enforcement."""
import uuid
from datetime import datetime, timedelta, timezone
from app.models.case import AmlCase
from app.models.evidence_gap import EvidenceGap
from app.models.information_request import InformationRequest
from app.repositories.readiness_repository import ReadinessRepository


def test_derive_blocker_state_open_requests(db_session):
    """Test blocker state derivation when OPEN requests exist."""
    # Create case
    case = AmlCase(
        case_ref="CS-TEST-001",
        primary_alert_id=uuid.uuid4(),
        created_by_user_id=uuid.uuid4(),
        status="UNDER_REVIEW",
        current_blocker_state="NONE"
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
    
    # Create OPEN request
    request = InformationRequest(
        request_ref="IR-TEST-001",
        case_id=case.case_id,
        gap_id=gap.gap_id,
        target_party="Test party",
        delivery_channel="Email",
        reason_text="Test reason",
        due_at_utc=datetime.now(timezone.utc) + timedelta(days=1),
        status="OPEN",
        created_by_user_id=case.created_by_user_id,
        created_at_utc=datetime.now(timezone.utc),
        updated_at_utc=datetime.now(timezone.utc)
    )
    db_session.add(request)
    db_session.commit()
    
    # Derive blocker state
    repo = ReadinessRepository(db_session)
    blocker_state = repo.derive_blocker_state(case.case_id)
    
    assert blocker_state == "OPEN_REQUESTS"


def test_derive_blocker_state_overdue_requests(db_session):
    """Test blocker state derivation when overdue requests exist."""
    # Create case
    case = AmlCase(
        case_ref="CS-TEST-002",
        primary_alert_id=uuid.uuid4(),
        created_by_user_id=uuid.uuid4(),
        status="UNDER_REVIEW",
        current_blocker_state="NONE"
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
    
    # Create overdue request (status != RESOLVED and due_at_utc < now)
    request = InformationRequest(
        request_ref="IR-TEST-002",
        case_id=case.case_id,
        gap_id=gap.gap_id,
        target_party="Test party",
        delivery_channel="Email",
        reason_text="Test reason",
        due_at_utc=datetime.now(timezone.utc) - timedelta(days=1),
        status="RESPONDED",  # Not RESOLVED
        created_by_user_id=case.created_by_user_id,
        created_at_utc=datetime.now(timezone.utc),
        updated_at_utc=datetime.now(timezone.utc)
    )
    db_session.add(request)
    db_session.commit()
    
    # Derive blocker state
    repo = ReadinessRepository(db_session)
    blocker_state = repo.derive_blocker_state(case.case_id)
    
    assert blocker_state == "OVERDUE_REQUESTS"


def test_derive_blocker_state_none(db_session):
    """Test blocker state derivation when no blockers exist."""
    # Create case
    case = AmlCase(
        case_ref="CS-TEST-003",
        primary_alert_id=uuid.uuid4(),
        created_by_user_id=uuid.uuid4(),
        status="UNDER_REVIEW",
        current_blocker_state="NONE"
    )
    db_session.add(case)
    db_session.flush()
    
    # Create evidence gap
    gap = EvidenceGap(
        case_id=case.case_id,
        title="Test gap",
        description="Test description",
        status="RESOLVED",
        created_by_user_id=case.created_by_user_id,
        created_at_utc=datetime.now(timezone.utc),
        resolved_at_utc=datetime.now(timezone.utc)
    )
    db_session.add(gap)
    db_session.flush()
    
    # Create RESOLVED request
    request = InformationRequest(
        request_ref="IR-TEST-003",
        case_id=case.case_id,
        gap_id=gap.gap_id,
        target_party="Test party",
        delivery_channel="Email",
        reason_text="Test reason",
        due_at_utc=datetime.now(timezone.utc) - timedelta(days=1),
        status="RESOLVED",
        created_by_user_id=case.created_by_user_id,
        created_at_utc=datetime.now(timezone.utc),
        updated_at_utc=datetime.now(timezone.utc)
    )
    db_session.add(request)
    db_session.commit()
    
    # Derive blocker state
    repo = ReadinessRepository(db_session)
    blocker_state = repo.derive_blocker_state(case.case_id)
    
    assert blocker_state == "NONE"


def test_check_conflicted_officer(db_session):
    """Test four-eyes conflict check."""
    investigator_id = uuid.uuid4()
    officer_id = uuid.uuid4()
    
    # Create case with investigator as creator
    case = AmlCase(
        case_ref="CS-TEST-004",
        primary_alert_id=uuid.uuid4(),
        created_by_user_id=investigator_id,
        status="UNDER_REVIEW",
        current_blocker_state="NONE"
    )
    db_session.add(case)
    db_session.commit()
    
    repo = ReadinessRepository(db_session)
    
    # Check with same user (conflicted)
    is_conflicted = repo.check_conflicted_officer(case.case_id, investigator_id)
    assert is_conflicted is True
    
    # Check with different user (not conflicted)
    is_conflicted = repo.check_conflicted_officer(case.case_id, officer_id)
    assert is_conflicted is False
