import pytest
import uuid
from decimal import Decimal
from datetime import datetime
from app.models.user import User
from app.models.customer import Customer
from app.models.account import Account
from app.models.transaction import Transaction
from app.models.alert import Alert
from app.services.auth_service import AuthService


@pytest.fixture
def auth_headers(client, db_session):
    """Create user and return auth headers"""
    user = User(
        user_id=uuid.UUID("00000000-0000-0000-0000-000026d3b272"),
        username="alerttester",
        display_name="Alert Tester",
        email="alerttest@example.com",
        password_hash=AuthService.hash_password("testpass"),
        primary_role="investigator",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    
    # Login
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "alerttester", "password": "testpass"}
    )
    token = response.json()["auth_token"]
    
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_alerts(db_session):
    """Create test alerts and related data"""
    # User for assignment
    user = User(
        user_id=uuid.UUID("00000000-0000-0000-0000-00004dc4d9cf"),
        username="assignee",
        display_name="Test Assignee",
        email="assignee@example.com",
        password_hash="hashed",
        primary_role="investigator",
        is_active=True
    )
    db_session.add(user)
    
    # Customer
    customer = Customer(
        customer_id=uuid.UUID("00000000-0000-0000-0000-00008a040de0"),
        customer_name="Alert Test Customer",
        onboarding_profile="corporate",
        risk_classification="high",
        exposure_indicators_json='["test"]'
    )
    db_session.add(customer)
    
    # Account
    account = Account(
        account_id=uuid.UUID("00000000-0000-0000-0000-000084c0f643"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-00008a040de0"),
        account_number_masked="XX•• •••• 9999",
        relationship_type="primary",
        jurisdiction_code="US",
        product_type="test"
    )
    db_session.add(account)
    
    # Transaction
    transaction = Transaction(
        transaction_id=uuid.UUID("00000000-0000-0000-0000-0000d051dc6a"),
        customer_id=uuid.UUID("00000000-0000-0000-0000-00008a040de0"),
        account_id=uuid.UUID("00000000-0000-0000-0000-000084c0f643"),
        booked_at=datetime.utcnow(),
        amount=Decimal("50000.00"),
        currency="USD",
        counterparty_name="Test Corp",
        corridor="US-US",
        generation_source="automatic"
    )
    db_session.add(transaction)
    
    # Alerts
    alerts = [
        Alert(
            alert_id=uuid.UUID("00000000-0000-0000-0000-0000547c3353"),
            transaction_id=uuid.UUID("00000000-0000-0000-0000-0000d051dc6a"),
            customer_id=uuid.UUID("00000000-0000-0000-0000-00008a040de0"),
            status="NEW",
            priority="HIGH",
            risk_score=85,
            matched_rule_codes_json='["RULE-001"]',
            generation="automatic",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        Alert(
            alert_id=uuid.UUID("00000000-0000-0000-0000-000045d6dc77"),
            transaction_id=uuid.UUID("00000000-0000-0000-0000-0000d051dc6a"),
            customer_id=uuid.UUID("00000000-0000-0000-0000-00008a040de0"),
            status="UNDER_REVIEW",
            priority="CRITICAL",
            risk_score=95,
            matched_rule_codes_json='["RULE-002"]',
            generation="automatic",
            assigned_user_id=uuid.UUID("00000000-0000-0000-0000-00004dc4d9cf"),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        Alert(
            alert_id=uuid.UUID("00000000-0000-0000-0000-00006faa08ba"),
            transaction_id=uuid.UUID("00000000-0000-0000-0000-0000d051dc6a"),
            customer_id=uuid.UUID("00000000-0000-0000-0000-00008a040de0"),
            status="NEW",
            priority="MEDIUM",
            risk_score=65,
            matched_rule_codes_json='["RULE-001"]',
            generation="automatic",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    ]
    
    for alert in alerts:
        db_session.add(alert)
    
    db_session.commit()
    return alerts


def test_get_alerts_endpoint(client, auth_headers, test_alerts):
    """Test GET /api/v1/alerts"""
    response = client.get("/api/v1/alerts", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    
    assert "items" in data
    assert "total_count" in data
    assert "limit" in data
    assert "offset" in data
    assert data["total_count"] == 3
    assert len(data["items"]) == 3


def test_get_alerts_filter_by_status(client, auth_headers, test_alerts):
    """Test GET /api/v1/alerts with status filter"""
    response = client.get(
        "/api/v1/alerts?status=NEW",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["total_count"] == 2
    for item in data["items"]:
        assert item["status"] == "NEW"


def test_get_alerts_filter_by_priority(client, auth_headers, test_alerts):
    """Test GET /api/v1/alerts with priority filter"""
    response = client.get(
        "/api/v1/alerts?priority=CRITICAL",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["total_count"] == 1
    assert data["items"][0]["priority"] == "CRITICAL"


def test_get_alerts_filter_by_assignee(client, auth_headers, test_alerts):
    """Test GET /api/v1/alerts with assignee filter"""
    # Unassigned
    response = client.get(
        "/api/v1/alerts?assignee_id=UNASSIGNED",
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["total_count"] == 2
    
    # Assigned to specific user
    response = client.get(
        "/api/v1/alerts?assignee_id=assignee-001",
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["total_count"] == 1


def test_get_alerts_filter_by_risk_score(client, auth_headers, test_alerts):
    """Test GET /api/v1/alerts with risk score filter"""
    response = client.get(
        "/api/v1/alerts?risk_score_min=90",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["total_count"] == 1
    assert data["items"][0]["risk_score"] >= 90


def test_get_alerts_pagination(client, auth_headers, test_alerts):
    """Test GET /api/v1/alerts with pagination"""
    # Page 1
    response = client.get(
        "/api/v1/alerts?limit=2&offset=0",
        headers=auth_headers
    )
    assert response.status_code == 200
    assert len(response.json()["items"]) == 2
    
    # Page 2
    response = client.get(
        "/api/v1/alerts?limit=2&offset=2",
        headers=auth_headers
    )
    assert response.status_code == 200
    assert len(response.json()["items"]) == 1


def test_get_alerts_sorting(client, auth_headers, test_alerts):
    """Test GET /api/v1/alerts with sorting"""
    # Sort by risk_score descending
    response = client.get(
        "/api/v1/alerts?sort_by=risk_score&sort_direction=desc",
        headers=auth_headers
    )
    assert response.status_code == 200
    items = response.json()["items"]
    assert items[0]["risk_score"] >= items[1]["risk_score"]
    
    # Sort by risk_score ascending
    response = client.get(
        "/api/v1/alerts?sort_by=risk_score&sort_direction=asc",
        headers=auth_headers
    )
    assert response.status_code == 200
    items = response.json()["items"]
    assert items[0]["risk_score"] <= items[1]["risk_score"]


def test_get_alerts_enrichment(client, auth_headers, test_alerts):
    """Test that alerts are enriched with customer and transaction data"""
    response = client.get("/api/v1/alerts", headers=auth_headers)
    
    assert response.status_code == 200
    items = response.json()["items"]
    
    # Check enriched fields are present
    assert items[0]["customer_name"] is not None
    assert items[0]["transaction_amount"] is not None
    assert items[0]["transaction_currency"] is not None


def test_claim_alert_endpoint(client, auth_headers, test_alerts, db_session):
    """Test POST /api/v1/alerts/{alert_id}/claim"""
    response = client.post(
        "/api/v1/alerts/int-alert-001/claim",
        headers=auth_headers,
        json={
            "assignee_user_id": "assignee-001",
            "assignment_reason": "Test assignment"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["alert_id"] == "int-alert-001"
    assert data["assigned_user_id"] == "assignee-001"
    assert data["assigned_user_name"] == "Test Assignee"
    assert "assigned_at" in data
    assert "assigned_by_user_id" in data


def test_claim_alert_nonexistent(client, auth_headers):
    """Test POST /api/v1/alerts/{alert_id}/claim with non-existent alert"""
    response = client.post(
        "/api/v1/alerts/nonexistent/claim",
        headers=auth_headers,
        json={
            "assignee_user_id": "assignee-001",
            "assignment_reason": "Test assignment"
        }
    )
    
    assert response.status_code == 404


def test_claim_alert_invalid_assignee(client, auth_headers, test_alerts):
    """Test POST /api/v1/alerts/{alert_id}/claim with invalid assignee"""
    response = client.post(
        "/api/v1/alerts/int-alert-001/claim",
        headers=auth_headers,
        json={
            "assignee_user_id": "nonexistent-user",
            "assignment_reason": "Test assignment"
        }
    )
    
    assert response.status_code == 404


def test_claim_alert_without_auth(client, test_alerts):
    """Test POST /api/v1/alerts/{alert_id}/claim without authentication"""
    response = client.post(
        "/api/v1/alerts/int-alert-001/claim",
        json={
            "assignee_user_id": "assignee-001",
            "assignment_reason": "Test assignment"
        }
    )
    
    assert response.status_code == 401  # HTTPBearer returns 401 for missing credentials


def test_alert_workflow_integration(client, auth_headers, test_alerts):
    """Test complete alert workflow: list -> filter -> claim"""
    # 1. List all alerts
    response = client.get("/api/v1/alerts", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["total_count"] == 3
    
    # 2. Filter for unassigned alerts
    response = client.get(
        "/api/v1/alerts?assignee_id=UNASSIGNED",
        headers=auth_headers
    )
    assert response.status_code == 200
    unassigned = response.json()["items"]
    assert len(unassigned) == 2
    
    # 3. Claim one of the unassigned alerts
    alert_to_claim = unassigned[0]["alert_id"]
    response = client.post(
        f"/api/v1/alerts/{alert_to_claim}/claim",
        headers=auth_headers,
        json={"assignee_user_id": "assignee-001", "assignment_reason": "Claiming for investigation"}
    )
    assert response.status_code == 200
    
    # 4. Verify unassigned count decreased
    response = client.get(
        "/api/v1/alerts?assignee_id=UNASSIGNED",
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["total_count"] == 1
