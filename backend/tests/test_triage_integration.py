"""
Integration tests for triage and notes endpoints.
Tests POST /api/v1/alerts/{alert_id}/triage-disposition
Tests GET /api/v1/cases/{case_id}/notes
Tests POST /api/v1/cases/{case_id}/notes
"""
import json
import uuid
from datetime import datetime

from app.models.alert import Alert
from app.models.aml_case import AMLCase
from app.models.case_note import CaseNote
from app.models.customer import Customer
from app.models.transaction import Transaction


def test_post_triage_disposition_close_non_actionable(auth_client, db_session):
    """Test POST /api/v1/alerts/{alert_id}/triage-disposition with CLOSE_NON_ACTIONABLE"""
    # Create test data
    customer = Customer(
        customer_id=uuid.UUID("00000000-0000-0000-0000-000091c758b7"),
        customer_name="Test Customer",
        onboarding_profile="corporate",
        risk_classification="medium",
        exposure_indicators_json=json.dumps([])
    )
    db_session.add(customer)
    
    transaction = Transaction(
        transaction_id=uuid.UUID("00000000-0000-0000-0000-0000ba355f9b"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-000091c758b7"),
        account_id=uuid.UUID("00000000-0000-0000-0000-00002c24fd24"),
        booked_at=datetime.utcnow(),
        amount=50000,
        currency="USD",
        corridor="US-US",
        generation_source="automatic"
    )
    db_session.add(transaction)
    
    alert = Alert(
        alert_id=uuid.UUID("00000000-0000-0000-0000-00004eeabc29"),
        transaction_id=uuid.UUID("00000000-0000-0000-0000-0000ba355f9b"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-000091c758b7"),
        status="NEW",
        priority="MEDIUM",
        risk_score=60,
        matched_rule_codes_json=json.dumps(["RULE-001"]),
        generation="automatic",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(alert)
    db_session.commit()
    
    # Make request
    response = auth_client.post(
        "/api/v1/alerts/00000000-0000-0000-0000-00004eeabc29/triage-disposition",
        json={
            "outcome": "CLOSE_NON_ACTIONABLE",
            "rationale": "Transaction verified as legitimate with supporting documentation"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["alert_id"] == "alert-test"
    assert data["status"] == "CLOSED_NON_ACTIONABLE"
    assert data["triage_outcome"] == "CLOSE_NON_ACTIONABLE"
    assert data["triaged_by_user_id"] == "tester-user-001"


def test_post_triage_disposition_investigate(auth_client, db_session):
    """Test POST triage disposition with INVESTIGATE keeps status"""
    customer = Customer(
        customer_id=uuid.UUID("00000000-0000-0000-0000-000091c758b7"),
        customer_name="Test Customer",
        onboarding_profile="corporate",
        risk_classification="high",
        exposure_indicators_json=json.dumps([])
    )
    db_session.add(customer)
    
    transaction = Transaction(
        transaction_id=uuid.UUID("00000000-0000-0000-0000-0000ba355f9b"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-000091c758b7"),
        account_id=uuid.UUID("00000000-0000-0000-0000-00002c24fd24"),
        booked_at=datetime.utcnow(),
        amount=250000,
        currency="USD",
        corridor="US-HK",
        generation_source="automatic"
    )
    db_session.add(transaction)
    
    alert = Alert(
        alert_id=uuid.UUID("00000000-0000-0000-0000-00004eeabc29"),
        transaction_id=uuid.UUID("00000000-0000-0000-0000-0000ba355f9b"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-000091c758b7"),
        status="UNDER_REVIEW",
        priority="HIGH",
        risk_score=85,
        matched_rule_codes_json=json.dumps(["RULE-001", "RULE-002"]),
        generation="automatic",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(alert)
    db_session.commit()
    
    response = auth_client.post(
        "/api/v1/alerts/00000000-0000-0000-0000-00004eeabc29/triage-disposition",
        json={
            "outcome": "INVESTIGATE",
            "rationale": "Complex transaction pattern requires detailed investigation"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "UNDER_REVIEW"  # Status should remain unchanged
    assert data["triage_outcome"] == "INVESTIGATE"


def test_post_triage_disposition_merge_existing_case(auth_client, db_session):
    """Test POST triage disposition with MERGE_EXISTING_CASE"""
    customer = Customer(
        customer_id=uuid.UUID("00000000-0000-0000-0000-000091c758b7"),
        customer_name="Test Customer",
        onboarding_profile="corporate",
        risk_classification="medium",
        exposure_indicators_json=json.dumps([])
    )
    db_session.add(customer)
    
    transaction = Transaction(
        transaction_id=uuid.UUID("00000000-0000-0000-0000-0000ba355f9b"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-000091c758b7"),
        account_id=uuid.UUID("00000000-0000-0000-0000-00002c24fd24"),
        booked_at=datetime.utcnow(),
        amount=75000,
        currency="USD",
        corridor="US-US",
        generation_source="automatic"
    )
    db_session.add(transaction)
    
    alert = Alert(
        alert_id=uuid.UUID("00000000-0000-0000-0000-00004eeabc29"),
        transaction_id=uuid.UUID("00000000-0000-0000-0000-0000ba355f9b"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-000091c758b7"),
        status="NEW",
        priority="MEDIUM",
        risk_score=65,
        matched_rule_codes_json=json.dumps(["RULE-001"]),
        generation="automatic",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(alert)
    db_session.commit()
    
    response = auth_client.post(
        "/api/v1/alerts/00000000-0000-0000-0000-00004eeabc29/triage-disposition",
        json={
            "outcome": "MERGE_EXISTING_CASE",
            "rationale": "Same customer and transaction pattern as case CS-001",
            "existing_case_id": "case-CS-001"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "MERGED_INTO_EXISTING_CASE"
    assert data["triage_outcome"] == "MERGE_EXISTING_CASE"


def test_post_triage_disposition_validates_rationale_length(auth_client, db_session):
    """Test that short rationale returns 422"""
    customer = Customer(
        customer_id=uuid.UUID("00000000-0000-0000-0000-000091c758b7"),
        customer_name="Test Customer",
        onboarding_profile="corporate",
        risk_classification="low",
        exposure_indicators_json=json.dumps([])
    )
    db_session.add(customer)
    
    transaction = Transaction(
        transaction_id=uuid.UUID("00000000-0000-0000-0000-0000ba355f9b"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-000091c758b7"),
        account_id=uuid.UUID("00000000-0000-0000-0000-00002c24fd24"),
        booked_at=datetime.utcnow(),
        amount=30000,
        currency="USD",
        corridor="US-US",
        generation_source="automatic"
    )
    db_session.add(transaction)
    
    alert = Alert(
        alert_id=uuid.UUID("00000000-0000-0000-0000-00004eeabc29"),
        transaction_id=uuid.UUID("00000000-0000-0000-0000-0000ba355f9b"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-000091c758b7"),
        status="NEW",
        priority="LOW",
        risk_score=40,
        matched_rule_codes_json=json.dumps(["RULE-001"]),
        generation="automatic",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(alert)
    db_session.commit()
    
    # Test blank rationale
    response = auth_client.post(
        "/api/v1/alerts/00000000-0000-0000-0000-00004eeabc29/triage-disposition",
        json={
            "outcome": "CLOSE_NON_ACTIONABLE",
            "rationale": ""
        }
    )
    assert response.status_code == 422
    
    # Test short rationale
    response = auth_client.post(
        "/api/v1/alerts/00000000-0000-0000-0000-00004eeabc29/triage-disposition",
        json={
            "outcome": "CLOSE_NON_ACTIONABLE",
            "rationale": "Short"
        }
    )
    assert response.status_code == 422


def test_post_triage_disposition_alert_not_found(auth_client):
    """Test that nonexistent alert returns 404"""
    response = auth_client.post(
        "/api/v1/alerts/nonexistent-alert/triage-disposition",
        json={
            "outcome": "CLOSE_NON_ACTIONABLE",
            "rationale": "Valid rationale text"
        }
    )
    assert response.status_code == 404


def test_get_case_notes_returns_chronological_order(auth_client, db_session):
    """Test GET /api/v1/cases/{case_id}/notes returns notes in chronological order"""
    # Create case
    customer = Customer(
        customer_id=uuid.UUID("00000000-0000-0000-0000-000091c758b7"),
        customer_name="Test Customer",
        onboarding_profile="corporate",
        risk_classification="medium",
        exposure_indicators_json=json.dumps([])
    )
    db_session.add(customer)
    
    transaction = Transaction(
        transaction_id=uuid.UUID("00000000-0000-0000-0000-0000ba355f9b"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-000091c758b7"),
        account_id=uuid.UUID("00000000-0000-0000-0000-00002c24fd24"),
        booked_at=datetime.utcnow(),
        amount=100000,
        currency="USD",
        corridor="US-US",
        generation_source="automatic"
    )
    db_session.add(transaction)
    
    alert = Alert(
        alert_id=uuid.UUID("00000000-0000-0000-0000-00004eeabc29"),
        transaction_id=uuid.UUID("00000000-0000-0000-0000-0000ba355f9b"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-000091c758b7"),
        status="ESCALATED_TO_CASE",
        priority="HIGH",
        risk_score=80,
        matched_rule_codes_json=json.dumps(["RULE-001"]),
        generation="automatic",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(alert)
    
    case = AMLCase(
        case_id=uuid.UUID("00000000-0000-0000-0000-0000d6d80c83"),
        case_number="CS-TEST",
        source_alert_id=uuid.UUID("00000000-0000-0000-0000-00004eeabc29"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-000091c758b7"),
        status="INVESTIGATING",
        priority="HIGH",
        recommendation_state="DRAFT",
        flagged_value_total=100000,
        evidence_locked_for_review=False,
        created_by_user_id=uuid.UUID("00000000-0000-0000-0000-0000cdac1e4f"),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(case)
    
    # Create notes with different timestamps
    base_time = datetime.utcnow()
    note1 = CaseNote(
        note_id=uuid.uuid4(),
        case_id=uuid.UUID("00000000-0000-0000-0000-0000d6d80c83"),
        note_type="INVESTIGATION",
        stage="INITIAL_REVIEW",
        body="First note - initial review",
        author_user_id=uuid.UUID("00000000-0000-0000-0000-0000cdac1e4f"),
        created_at=base_time
    )
    note2 = CaseNote(
        note_id=uuid.uuid4(),
        case_id=uuid.UUID("00000000-0000-0000-0000-0000d6d80c83"),
        note_type="ANALYSIS",
        stage="DETAILED_ANALYSIS",
        body="Second note - detailed analysis",
        author_user_id=uuid.UUID("00000000-0000-0000-0000-0000cdac1e4f"),
        created_at=base_time.replace(hour=base_time.hour + 1)
    )
    note3 = CaseNote(
        note_id=uuid.uuid4(),
        case_id=uuid.UUID("00000000-0000-0000-0000-0000d6d80c83"),
        note_type="INVESTIGATION",
        stage="ONGOING_MONITORING",
        body="Third note - monitoring",
        author_user_id=uuid.UUID("00000000-0000-0000-0000-0000cdac1e4f"),
        created_at=base_time.replace(hour=base_time.hour + 2)
    )
    db_session.add_all([note1, note2, note3])
    db_session.commit()
    
    # Get notes
    response = auth_client.get("/api/v1/cases/case-test/notes")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert data[0]["note_id"] == "note-1"
    assert data[1]["note_id"] == "note-2"
    assert data[2]["note_id"] == "note-3"
    assert data[0]["body"] == "First note - initial review"
    assert data[1]["body"] == "Second note - detailed analysis"


def test_get_case_notes_includes_author_info(auth_client, db_session):
    """Test that GET notes includes author display name"""
    customer = Customer(
        customer_id=uuid.UUID("00000000-0000-0000-0000-000091c758b7"),
        customer_name="Test Customer",
        onboarding_profile="corporate",
        risk_classification="medium",
        exposure_indicators_json=json.dumps([])
    )
    db_session.add(customer)
    
    transaction = Transaction(
        transaction_id=uuid.UUID("00000000-0000-0000-0000-0000ba355f9b"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-000091c758b7"),
        account_id=uuid.UUID("00000000-0000-0000-0000-00002c24fd24"),
        booked_at=datetime.utcnow(),
        amount=100000,
        currency="USD",
        corridor="US-US",
        generation_source="automatic"
    )
    db_session.add(transaction)
    
    alert = Alert(
        alert_id=uuid.UUID("00000000-0000-0000-0000-00004eeabc29"),
        transaction_id=uuid.UUID("00000000-0000-0000-0000-0000ba355f9b"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-000091c758b7"),
        status="ESCALATED_TO_CASE",
        priority="HIGH",
        risk_score=80,
        matched_rule_codes_json=json.dumps(["RULE-001"]),
        generation="automatic",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(alert)
    
    case = AMLCase(
        case_id=uuid.UUID("00000000-0000-0000-0000-0000d6d80c83"),
        case_number="CS-TEST",
        source_alert_id=uuid.UUID("00000000-0000-0000-0000-00004eeabc29"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-000091c758b7"),
        status="INVESTIGATING",
        priority="HIGH",
        recommendation_state="DRAFT",
        flagged_value_total=100000,
        evidence_locked_for_review=False,
        created_by_user_id="tester@example.com",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(case)
    
    note = CaseNote(
        note_id=uuid.uuid4(),
        case_id=uuid.UUID("00000000-0000-0000-0000-0000d6d80c83"),
        note_type="INVESTIGATION",
        stage="INITIAL_REVIEW",
        body="Test note",
        author_user_id=uuid.UUID("00000000-0000-0000-0000-0000cdac1e4f"),
        created_at=datetime.utcnow()
    )
    db_session.add(note)
    db_session.commit()
    
    response = auth_client.get("/api/v1/cases/case-test/notes")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["author_user_id"] == "tester-user-001"
    assert data[0]["author_display_name"] == "Test User"


def test_post_case_note_creates_note(auth_client, db_session):
    """Test POST /api/v1/cases/{case_id}/notes creates note"""
    customer = Customer(
        customer_id=uuid.UUID("00000000-0000-0000-0000-000091c758b7"),
        customer_name="Test Customer",
        onboarding_profile="corporate",
        risk_classification="medium",
        exposure_indicators_json=json.dumps([])
    )
    db_session.add(customer)
    
    transaction = Transaction(
        transaction_id=uuid.UUID("00000000-0000-0000-0000-0000ba355f9b"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-000091c758b7"),
        account_id=uuid.UUID("00000000-0000-0000-0000-00002c24fd24"),
        booked_at=datetime.utcnow(),
        amount=100000,
        currency="USD",
        corridor="US-US",
        generation_source="automatic"
    )
    db_session.add(transaction)
    
    alert = Alert(
        alert_id=uuid.UUID("00000000-0000-0000-0000-00004eeabc29"),
        transaction_id=uuid.UUID("00000000-0000-0000-0000-0000ba355f9b"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-000091c758b7"),
        status="ESCALATED_TO_CASE",
        priority="HIGH",
        risk_score=80,
        matched_rule_codes_json=json.dumps(["RULE-001"]),
        generation="automatic",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(alert)
    
    case = AMLCase(
        case_id=uuid.UUID("00000000-0000-0000-0000-0000d6d80c83"),
        case_number="CS-TEST",
        source_alert_id=uuid.UUID("00000000-0000-0000-0000-00004eeabc29"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-000091c758b7"),
        status="INVESTIGATING",
        priority="HIGH",
        recommendation_state="DRAFT",
        flagged_value_total=100000,
        evidence_locked_for_review=False,
        created_by_user_id="tester@example.com",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(case)
    db_session.commit()
    
    response = auth_client.post(
        "/api/v1/cases/case-test/notes",
        json={
            "note_type": "INVESTIGATION",
            "stage": "INITIAL_REVIEW",
            "body": "Initial review completed. Transaction appears suspicious."
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["case_id"] == "case-test"
    assert data["note_type"] == "INVESTIGATION"
    assert data["stage"] == "INITIAL_REVIEW"
    assert data["body"] == "Initial review completed. Transaction appears suspicious."
    assert data["author_user_id"] == "tester-user-001"
    assert data["author_display_name"] == "Test User"
    assert "note_id" in data
    assert "created_at" in data


def test_post_case_note_validates_empty_body(auth_client, db_session):
    """Test that empty note body returns 422"""
    customer = Customer(
        customer_id=uuid.UUID("00000000-0000-0000-0000-000091c758b7"),
        customer_name="Test Customer",
        onboarding_profile="corporate",
        risk_classification="medium",
        exposure_indicators_json=json.dumps([])
    )
    db_session.add(customer)
    
    transaction = Transaction(
        transaction_id=uuid.UUID("00000000-0000-0000-0000-0000ba355f9b"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-000091c758b7"),
        account_id=uuid.UUID("00000000-0000-0000-0000-00002c24fd24"),
        booked_at=datetime.utcnow(),
        amount=100000,
        currency="USD",
        corridor="US-US",
        generation_source="automatic"
    )
    db_session.add(transaction)
    
    alert = Alert(
        alert_id=uuid.UUID("00000000-0000-0000-0000-00004eeabc29"),
        transaction_id=uuid.UUID("00000000-0000-0000-0000-0000ba355f9b"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-000091c758b7"),
        status="ESCALATED_TO_CASE",
        priority="HIGH",
        risk_score=80,
        matched_rule_codes_json=json.dumps(["RULE-001"]),
        generation="automatic",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(alert)
    
    case = AMLCase(
        case_id=uuid.UUID("00000000-0000-0000-0000-0000d6d80c83"),
        case_number="CS-TEST",
        source_alert_id=uuid.UUID("00000000-0000-0000-0000-00004eeabc29"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-000091c758b7"),
        status="INVESTIGATING",
        priority="HIGH",
        recommendation_state="DRAFT",
        flagged_value_total=100000,
        evidence_locked_for_review=False,
        created_by_user_id="tester@example.com",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(case)
    db_session.commit()
    
    response = auth_client.post(
        "/api/v1/cases/case-test/notes",
        json={
            "note_type": "INVESTIGATION",
            "stage": "INITIAL_REVIEW",
            "body": ""
        }
    )
    
    assert response.status_code == 422


def test_post_case_note_case_not_found(auth_client):
    """Test that nonexistent case returns 404"""
    response = auth_client.post(
        "/api/v1/cases/nonexistent-case/notes",
        json={
            "note_type": "INVESTIGATION",
            "stage": "INITIAL_REVIEW",
            "body": "Test note"
        }
    )
    assert response.status_code == 404
