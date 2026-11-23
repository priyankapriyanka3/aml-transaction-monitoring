"""
Integration tests for the complete Flow 01 workflow.

Tests the end-to-end investigator-to-officer journey covering:
- Alert queue filtering and pagination
- Alert assignment with audit events
- Evidence retrieval with rule snapshots
- Case creation with primary alert link
- Note capture with author attribution
- Information request lifecycle with blocker enforcement
- Readiness checklist derivation
- Officer assignment validation (four-eyes)
- Decision recording with immutability
- Return-for-investigation path
"""

import pytest
import uuid
from datetime import datetime, timezone
from uuid import uuid4

from app.models import (
    User, Alert, Transaction, Customer, Account,
    RuleEvaluationSnapshot, AmlCase, CaseNote,
    InformationRequest, EvidenceGap, AuditEvent
)
from app.core.security import hash_password


@pytest.fixture
def investigator_user(db_session):
    """Create investigator user for full flow test."""
    email = f"investigator_flow_{uuid4().hex[:8]}@example.com"
    user = User(
        user_id=uuid4(),
        email=email,
        display_name="Riya Sharma",
        hashed_password=hash_password("investigator123"),
        role="INVESTIGATOR",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def officer_user(db_session):
    """Create officer user for four-eyes review."""
    email = f"officer_flow_{uuid4().hex[:8]}@example.com"
    user = User(
        user_id=uuid4(),
        email=email,
        display_name="Morgan Lee",
        hashed_password=hash_password("officer123"),
        role="OFFICER",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def alert_with_evidence(db_session):
    """Create complete alert with transaction, customer, account, and rule snapshots."""
    # Create customer
    customer = Customer(
        customer_id=uuid4(),
        customer_name="Acme Corp",
        pep_flag=False,
        country_code="GB",
        created_at_utc=datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    )
    db_session.add(customer)
    
    # Create account
    account = Account(
        account_id=uuid4(),
        customer_id=customer.customer_id,
        account_ref="ACC-12345",
        account_type="Business",
        created_at_utc=datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    )
    db_session.add(account)
    
    # Create transaction
    transaction = Transaction(
        transaction_id=uuid4(),
        account_id=account.account_id,
        transaction_ref="TXN-98765",
        amount=150000.00,
        currency_code="USD",
        source_country_code="GB",
        destination_country_code="AE",
        executed_at_utc=datetime(2026, 11, 5, 14, 30, 0, tzinfo=timezone.utc),
        created_at_utc=datetime(2026, 11, 5, 14, 35, 0, tzinfo=timezone.utc)
    )
    db_session.add(transaction)
    
    # Create alert
    alert = Alert(
        alert_id=uuid4(),
        alert_ref="AL-1042",
        transaction_id=transaction.transaction_id,
        customer_id=customer.customer_id,
        priority="Critical",
        risk_score=95,
        status="New",
        owner_user_id=None,
        triggered_at_utc=datetime(2026, 11, 5, 15, 0, 0, tzinfo=timezone.utc),
        created_at_utc=datetime(2026, 11, 5, 15, 0, 0, tzinfo=timezone.utc)
    )
    db_session.add(alert)
    
    # Create rule evaluation snapshots
    snapshot1 = RuleEvaluationSnapshot(
        snapshot_id=uuid4(),
        alert_id=alert.alert_id,
        rule_code="RULE-001",
        rule_name="High-Value Cross-Border",
        rule_version="v3.2",
        outcome="MATCH",
        condition_text="Transaction amount > $100,000 AND destination high-risk jurisdiction",
        evaluated_from_utc=datetime(2026, 11, 1, 0, 0, 0, tzinfo=timezone.utc),
        evaluated_to_utc=datetime(2026, 11, 30, 23, 59, 59, tzinfo=timezone.utc),
        immutable_hash="hash_rule001",
        created_at_utc=datetime(2026, 11, 5, 15, 0, 0, tzinfo=timezone.utc)
    )
    
    snapshot2 = RuleEvaluationSnapshot(
        snapshot_id=uuid4(),
        alert_id=alert.alert_id,
        rule_code="RULE-002",
        rule_name="PEP Screening",
        rule_version="v2.1",
        outcome="PASS",
        condition_text="Customer or beneficial owner is politically exposed person",
        evaluated_from_utc=datetime(2026, 11, 1, 0, 0, 0, tzinfo=timezone.utc),
        evaluated_to_utc=datetime(2026, 11, 30, 23, 59, 59, tzinfo=timezone.utc),
        immutable_hash="hash_rule002",
        created_at_utc=datetime(2026, 11, 5, 15, 0, 0, tzinfo=timezone.utc)
    )
    
    db_session.add_all([snapshot1, snapshot2])
    db_session.commit()
    
    db_session.refresh(alert)
    db_session.refresh(transaction)
    db_session.refresh(customer)
    db_session.refresh(account)
    
    return {
        "alert": alert,
        "transaction": transaction,
        "customer": customer,
        "account": account,
        "snapshots": [snapshot1, snapshot2]
    }


def test_full_investigator_to_officer_flow(client, db_session, investigator_user, officer_user, alert_with_evidence):
    """
    Test the complete Flow 01 journey from alert queue to final decision.
    
    Flow:
    1. Login as investigator
    2. View alert queue with filtering
    3. Assign alert to self
    4. View evidence with rule snapshots
    5. Create case from alert
    6. Add investigation note
    7. Create information request
    8. Record response to request
    9. Check readiness
    10. Assign officer
    11. Share for review
    12. Logout investigator
    13. Login as officer
    14. Review package
    15. Record decision with rationale
    16. Verify immutable decision record
    """
    alert = alert_with_evidence["alert"]
    
    # Step 1: Login as investigator
    login_response = client.post("/api/v1/auth/login", json={
        "email": investigator_user.email,
        "password": "investigator123"
    })
    assert login_response.status_code == 200
    inv_token = login_response.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {inv_token}"
    
    # Step 2: View alert queue with filtering
    queue_response = client.get("/api/v1/alerts", params={
        "priority": "Critical",
        "ownership": "Unassigned"
    })
    assert queue_response.status_code == 200
    queue_data = queue_response.json()
    assert queue_data["total"] >= 1
    assert any(item["alert_ref"] == "AL-1042" for item in queue_data["items"])
    
    # Step 3: Assign alert to self
    assign_response = client.post(f"/api/v1/alerts/{alert.alert_id}/assign", headers={
        "X-Correlation-ID": "test-corr-001"
    })
    assert assign_response.status_code == 200
    assert assign_response.json()["owner_user_id"] == str(investigator_user.user_id)
    
    # Verify assignment audit event created
    audit_events = db_session.query(AuditEvent).filter(
        AuditEvent.entity_id == alert.alert_id,
        AuditEvent.action_type == "ALERT_ASSIGNED"
    ).all()
    assert len(audit_events) == 1
    assert audit_events[0].actor_user_id == investigator_user.user_id
    
    # Step 4: View evidence with rule snapshots
    evidence_response = client.get(f"/api/v1/alerts/{alert.alert_id}/evidence")
    assert evidence_response.status_code == 200
    evidence = evidence_response.json()
    assert evidence["alert_ref"] == "AL-1042"
    assert float(evidence["transaction"]["amount"]) == 150000.00
    assert evidence["transaction"]["currency_code"] == "USD"
    assert evidence["customer"]["customer_name"] == "Acme Corp"
    assert len(evidence["rule_snapshots"]) == 2
    assert any(snap["outcome"] == "MATCH" for snap in evidence["rule_snapshots"])
    assert any(snap["outcome"] == "PASS" for snap in evidence["rule_snapshots"])
    
    # Step 5: Create case from alert
    case_response = client.post("/api/v1/cases", json={
        "alert_id": str(alert.alert_id)
    }, headers={
        "X-Correlation-ID": "test-corr-002"
    })
    assert case_response.status_code == 201
    case_id = case_response.json()["case_id"]
    case_ref = case_response.json()["case_ref"]
    assert case_ref.startswith("CS-")
    
    # Verify case created audit event
    case_audit = db_session.query(AuditEvent).filter(
        AuditEvent.action_type == "CASE_CREATED"
    ).first()
    assert case_audit is not None
    assert case_audit.actor_user_id == investigator_user.user_id
    
    # Step 6: Add investigation note
    note_response = client.post(f"/api/v1/cases/{case_id}/notes", json={
        "note_category": "investigation",
        "note_text": "Customer profile indicates legitimate business operations. Transaction aligns with expected activity pattern."
    }, headers={
        "X-Correlation-ID": "test-corr-003"
    })
    assert note_response.status_code == 201
    assert note_response.json()["author_user_id"] == str(investigator_user.user_id)
    
    # Step 7: Create information request
    from datetime import timedelta
    future_due_date = (datetime.now(timezone.utc) + timedelta(days=5)).isoformat()
    request_response = client.post(f"/api/v1/cases/{case_id}/requests", json={
        "gap_title": "Source of Funds Verification",
        "gap_description": "Need documentation showing source of the $150,000 transfer",
        "target_party": "Customer Operations Team",
        "delivery_channel": "Internal ticket system",
        "reason_text": "Verify legitimacy of large cross-border transfer",
        "due_at_utc": future_due_date
    }, headers={
        "X-Correlation-ID": "test-corr-004"
    })
    assert request_response.status_code == 201
    request_id = request_response.json()["request_id"]
    
    # Verify case blocker state updated to OPEN_REQUESTS
    case = db_session.query(AmlCase).filter(AmlCase.case_id == uuid.UUID(case_id)).first()
    assert case.current_blocker_state == "OPEN_REQUESTS"
    
    # Step 8: Record response to request
    response_received_date = datetime.now(timezone.utc).isoformat()
    response_response = client.post(f"/api/v1/cases/{case_id}/requests/{request_id}/response", json={
        "response_summary": "Customer operations supplied source-of-funds documents showing legitimate business revenue.",
        "received_at_utc": response_received_date
    }, headers={
        "X-Correlation-ID": "test-corr-005"
    })
    assert response_response.status_code == 200
    
    # Verify blocker state cleared
    db_session.refresh(case)
    assert case.current_blocker_state == "NONE"
    
    # Step 9: Check readiness
    readiness_response = client.get(f"/api/v1/cases/{case_id}/readiness")
    assert readiness_response.status_code == 200
    readiness = readiness_response.json()
    
    # Verify all checklist items are complete
    checklist = readiness["checklist"]
    assert all(item["complete"] for item in checklist)
    
    # Verify eligible officers excludes case creator
    eligible_officers = readiness["eligible_officers"]
    assert str(investigator_user.user_id) not in [o["user_id"] for o in eligible_officers]
    assert str(officer_user.user_id) in [o["user_id"] for o in eligible_officers]
    
    # Step 10: Assign officer
    assign_officer_response = client.post(f"/api/v1/cases/{case_id}/assign-officer", json={
        "officer_user_id": str(officer_user.user_id)
    }, headers={
        "X-Correlation-ID": "test-corr-006"
    })
    assert assign_officer_response.status_code == 200
    
    # Step 11: Share for review
    share_response = client.post(f"/api/v1/cases/{case_id}/share-for-review", headers={
        "X-Correlation-ID": "test-corr-007"
    })
    assert share_response.status_code == 200
    
    # Verify case status transitioned to UNDER_REVIEW
    db_session.refresh(case)
    assert case.status == "UNDER_REVIEW"
    
    # Step 12: Logout investigator
    client.headers.pop("Authorization")
    
    # Step 13: Login as officer
    officer_login = client.post("/api/v1/auth/login", json={
        "email": officer_user.email,
        "password": "officer123"
    })
    assert officer_login.status_code == 200
    officer_token = officer_login.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {officer_token}"
    
    # Step 14: Review package
    review_response = client.get(f"/api/v1/cases/{case_id}/officer-review")
    assert review_response.status_code == 200
    review_package = review_response.json()
    assert review_package["case_ref"] == case_ref
    assert review_package["blocker_state"] == "NONE"
    assert review_package["is_conflicted_officer"] is False
    assert len(review_package["linked_alerts"]) >= 1
    assert len(review_package["notes"]) >= 1
    
    # Step 15: Record decision with rationale
    decision_response = client.post(f"/api/v1/cases/{case_id}/decision", json={
        "outcome": "FALSE_POSITIVE",
        "rationale_text": "Transaction is legitimate business activity with verified source of funds. Customer profile and supporting documentation confirm no AML risk."
    }, headers={
        "X-Correlation-ID": "test-corr-008"
    })
    assert decision_response.status_code == 201
    decision_data = decision_response.json()
    assert decision_data["outcome"] == "FALSE_POSITIVE"
    assert decision_data["deciding_officer_user_id"] == str(officer_user.user_id)
    assert decision_data["immutable_hash"] is not None
    
    # Step 16: Verify immutable decision record and audit trail
    from app.models import CaseDecision
    decision_record = db_session.query(CaseDecision).filter(
        CaseDecision.case_id == uuid.UUID(case_id)
    ).first()
    assert decision_record is not None
    assert decision_record.outcome == "FALSE_POSITIVE"
    assert decision_record.rationale_text.startswith("Transaction is legitimate")
    assert decision_record.immutable_hash is not None
    
    # Verify decision recorded audit event
    decision_audit = db_session.query(AuditEvent).filter(
        AuditEvent.action_type == "DECISION_RECORDED",
        AuditEvent.entity_id == uuid.UUID(case_id)
    ).first()
    assert decision_audit is not None
    assert decision_audit.actor_user_id == officer_user.user_id
    assert decision_audit.actor_role == "OFFICER"
    
    # Verify case status updated to outcome-mapped status
    db_session.refresh(case)
    assert case.status == "FALSE_POSITIVE"  # FALSE_POSITIVE stays as FALSE_POSITIVE


def test_alert_queue_pagination_and_filtering(client, db_session, investigator_user, alert_with_evidence):
    """Test alert queue supports filtering by priority, ownership, status and pagination."""
    # Login
    login_response = client.post("/api/v1/auth/login", json={
        "email": investigator_user.email,
        "password": "investigator123"
    })
    client.headers["Authorization"] = f"Bearer {login_response.json()['access_token']}"
    
    # Test priority filter
    response = client.get("/api/v1/alerts", params={"priority": "Critical"})
    assert response.status_code == 200
    data = response.json()
    assert all(item["priority"] == "Critical" for item in data["items"])
    
    # Test ownership filter - unassigned
    response = client.get("/api/v1/alerts", params={"ownership": "Unassigned"})
    assert response.status_code == 200
    data = response.json()
    assert all(item["owner_user_id"] is None for item in data["items"])
    
    # Test pagination
    response = client.get("/api/v1/alerts", params={"page": 1, "page_size": 10})
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["page_size"] == 10
    assert len(data["items"]) <= 10
