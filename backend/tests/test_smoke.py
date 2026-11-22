"""Smoke test to verify basic app functionality."""


def test_health_endpoint(client):
    """Test that the health endpoint returns 200."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["app"] == "aml-backend"


def test_database_connection(db_session):
    """Test that the database session is available."""
    from sqlalchemy import text
    assert db_session is not None
    # Verify we can execute a simple query
    result = db_session.execute(text("SELECT 1"))
    assert result.scalar() == 1


def test_models_imported():
    """Test that all models are importable."""
    from app.models import (
        User, SessionRecord, Customer, RiskProfile, Account,
        Transaction, Alert, AMLCase, CaseAlertLink,
        DetectionRuleSnapshot, RuleEvaluationResult, CaseNote,
        InformationRequest, CaseDecision, AuditEvent
    )
    # All models should be importable
    assert User is not None
    assert SessionRecord is not None
    assert Customer is not None
    assert RiskProfile is not None
    assert Account is not None
    assert Transaction is not None
    assert Alert is not None
    assert AMLCase is not None
    assert CaseAlertLink is not None
    assert DetectionRuleSnapshot is not None
    assert RuleEvaluationResult is not None
    assert CaseNote is not None
    assert InformationRequest is not None
    assert CaseDecision is not None
    assert AuditEvent is not None
