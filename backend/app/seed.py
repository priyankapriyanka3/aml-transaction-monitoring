"""
Seed data loader for development and testing.
Creates users, customers, accounts, transactions, detection rules, and alerts.
"""
import json
import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy.orm import Session

from .database import SessionLocal
from .models.account import Account
from .models.alert import Alert
from .models.aml_case import AMLCase
from .models.audit_event import AuditEvent
from .models.case_alert_link import CaseAlertLink
from .models.case_note import CaseNote
from .models.customer import Customer
from .models.detection_rule_snapshot import DetectionRuleSnapshot
from .models.information_request import InformationRequest
from .models.risk_profile import RiskProfile
from .models.rule_evaluation_result import RuleEvaluationResult
from .models.transaction import Transaction
from .models.user import User


def seed_database():
    """
    Seed complete data required for development and testing.
    
    Creates:
    - 2 users (riya investigator, morgan officer)
    - 3 customers with risk profiles
    - 3 accounts
    - 5 transactions
    - 2 detection rule snapshots
    - 10 sample alerts with varying statuses, priorities, and risk scores
    """
    db: Session = SessionLocal()
    
    try:
        # Check if seed data already exists
        existing_users = db.query(User).count()
        if existing_users > 0:
            print(f"Seed data already exists ({existing_users} users found), skipping...")
            return
        
        print("Seeding database...")
        
        # ===== Users =====
        investigator = User(
            user_id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
            username="riya",
            display_name="Riya Sharma",
            email="riya@example.com",
            password_hash="$2b$12$zS.ionuYdvEXgp.IQxoVEemU2YxmzeHmGhabWT3Sq6OHBCxO1knPy",  # password123
            primary_role="investigator",
            is_active=True
        )
        
        officer = User(
            user_id=uuid.UUID("00000000-0000-0000-0000-000000000002"),
            username="morgan",
            display_name="Morgan Chen",
            email="morgan@example.com",
            password_hash="$2b$12$zS.ionuYdvEXgp.IQxoVEemU2YxmzeHmGhabWT3Sq6OHBCxO1knPy",  # password123
            primary_role="officer",
            is_active=True
        )
        
        db.add(investigator)
        db.add(officer)
        
        # ===== Customers =====
        customers_data = [
            {
                "customer_id": "00000000-0000-0000-0000-000000000064",
                "customer_name": "Acme Global Trading Ltd",
                "onboarding_profile": "corporate",
                "risk_classification": "high",
                "exposure_indicators_json": json.dumps(["cross_border", "high_volume", "sanctioned_jurisdiction"])
            },
            {
                "customer_id": "00000000-0000-0000-0000-000000000065",
                "customer_name": "Brighton Investment Partners",
                "onboarding_profile": "institutional",
                "risk_classification": "medium",
                "exposure_indicators_json": json.dumps(["pep_related", "complex_structure"])
            },
            {
                "customer_id": "00000000-0000-0000-0000-000000000066",
                "customer_name": "Clearwater Holdings Inc",
                "onboarding_profile": "corporate",
                "risk_classification": "low",
                "exposure_indicators_json": json.dumps(["domestic_only"])
            }
        ]
        
        for cust_data in customers_data:
            cust_data["customer_id"] = uuid.UUID(cust_data["customer_id"])
            customer = Customer(**cust_data)
            db.add(customer)
        
        # Define base time for all timestamp calculations
        base_time = datetime.now(timezone.utc) - timedelta(days=7)
        
        # ===== Risk Profiles =====
        risk_profiles_data = [
            {
                "risk_profile_id": "00000000-0000-0000-0000-0000000000c8",
                "customer_id": "00000000-0000-0000-0000-000000000064",
                "risk_rating": "HIGH",
                "kyc_review_date": base_time - timedelta(days=90),
                "pep_flag": False,
                "sanctions_flag": False,
                "adverse_media_flag": True,
                "effective_at": base_time - timedelta(days=30)
            },
            {
                "risk_profile_id": "00000000-0000-0000-0000-0000000000c9",
                "customer_id": "00000000-0000-0000-0000-000000000065",
                "risk_rating": "MEDIUM",
                "kyc_review_date": base_time - timedelta(days=180),
                "pep_flag": True,
                "sanctions_flag": False,
                "adverse_media_flag": False,
                "effective_at": base_time - timedelta(days=60)
            },
            {
                "risk_profile_id": "00000000-0000-0000-0000-0000000000ca",
                "customer_id": "00000000-0000-0000-0000-000000000066",
                "risk_rating": "LOW",
                "kyc_review_date": base_time - timedelta(days=365),
                "pep_flag": False,
                "sanctions_flag": False,
                "adverse_media_flag": False,
                "effective_at": base_time - timedelta(days=180)
            }
        ]
        
        for risk_data in risk_profiles_data:
            risk_data["risk_profile_id"] = uuid.UUID(risk_data["risk_profile_id"])
            risk_data["customer_id"] = uuid.UUID(risk_data["customer_id"])
            risk_profile = RiskProfile(**risk_data)
            db.add(risk_profile)
        
        # ===== Accounts =====
        accounts_data = [
            {
                "account_id": "00000000-0000-0000-0000-00000000012c",
                "customer_id": "00000000-0000-0000-0000-000000000064",
                "account_number_masked": "GB•• •••• 4821",
                "relationship_type": "primary",
                "jurisdiction_code": "GB",
                "product_type": "business_current"
            },
            {
                "account_id": "00000000-0000-0000-0000-00000000012d",
                "customer_id": "00000000-0000-0000-0000-000000000065",
                "account_number_masked": "US•• •••• 7392",
                "relationship_type": "primary",
                "jurisdiction_code": "US",
                "product_type": "investment"
            },
            {
                "account_id": "00000000-0000-0000-0000-00000000012e",
                "customer_id": "00000000-0000-0000-0000-000000000066",
                "account_number_masked": "CA•• •••• 1145",
                "relationship_type": "primary",
                "jurisdiction_code": "CA",
                "product_type": "business_current"
            }
        ]
        
        for acc_data in accounts_data:
            acc_data["account_id"] = uuid.UUID(acc_data["account_id"])
            acc_data["customer_id"] = uuid.UUID(acc_data["customer_id"])
            account = Account(**acc_data)
            db.add(account)
        
        # ===== Transactions =====
        transactions_data = [
            {
                "transaction_id": "00000000-0000-0000-0000-000000000190",
                "customer_id": "00000000-0000-0000-0000-000000000064",
                "account_id": "00000000-0000-0000-0000-00000000012c",
                "booked_at": base_time,
                "amount": Decimal("285000.00"),
                "currency": "USD",
                "counterparty_name": "Eastern Trade Corp",
                "corridor": "GB-HK",
                "generation_source": "automatic"
            },
            {
                "transaction_id": "00000000-0000-0000-0000-000000000191",
                "customer_id": "00000000-0000-0000-0000-000000000064",
                "account_id": "00000000-0000-0000-0000-00000000012c",
                "booked_at": base_time + timedelta(days=1),
                "amount": Decimal("450000.00"),
                "currency": "USD",
                "counterparty_name": "Pacific Holdings Ltd",
                "corridor": "GB-SG",
                "generation_source": "automatic"
            },
            {
                "transaction_id": "00000000-0000-0000-0000-000000000192",
                "customer_id": "00000000-0000-0000-0000-000000000065",
                "account_id": "00000000-0000-0000-0000-00000000012d",
                "booked_at": base_time + timedelta(days=2),
                "amount": Decimal("125000.00"),
                "currency": "USD",
                "counterparty_name": None,
                "corridor": "US-US",
                "generation_source": "automatic"
            },
            {
                "transaction_id": "00000000-0000-0000-0000-000000000193",
                "customer_id": "00000000-0000-0000-0000-000000000065",
                "account_id": "00000000-0000-0000-0000-00000000012d",
                "booked_at": base_time + timedelta(days=3),
                "amount": Decimal("95000.00"),
                "currency": "USD",
                "counterparty_name": "Riverside Capital",
                "corridor": "US-CH",
                "generation_source": "manual"
            },
            {
                "transaction_id": "00000000-0000-0000-0000-000000000194",
                "customer_id": "00000000-0000-0000-0000-000000000066",
                "account_id": "00000000-0000-0000-0000-00000000012e",
                "booked_at": base_time + timedelta(days=4),
                "amount": Decimal("45000.00"),
                "currency": "CAD",
                "counterparty_name": "Northern Supply Co",
                "corridor": "CA-CA",
                "generation_source": "automatic"
            }
        ]
        
        for txn_data in transactions_data:
            txn_data["transaction_id"] = uuid.UUID(txn_data["transaction_id"])
            txn_data["customer_id"] = uuid.UUID(txn_data["customer_id"])
            txn_data["account_id"] = uuid.UUID(txn_data["account_id"])
            transaction = Transaction(**txn_data)
            db.add(transaction)
        
        # ===== Detection Rule Snapshots =====
        rules_data = [
            {
                "detection_rule_snapshot_id": "00000000-0000-0000-0000-0000000001f4",
                "rule_code": "RULE-001",
                "rule_name": "Large cross-border transfer",
                "rule_version": "v3.2",
                "threshold_description": "Single transaction >$200k across jurisdictions",
                "serialized_rule_json": json.dumps({
                    "threshold_amount": 200000,
                    "cross_border": True,
                    "lookback_days": 1
                }),
                "effective_at": base_time - timedelta(days=30)
            },
            {
                "detection_rule_snapshot_id": "00000000-0000-0000-0000-0000000001f5",
                "rule_code": "RULE-002",
                "rule_name": "Rapid succession high-value",
                "rule_version": "v2.1",
                "threshold_description": "Multiple transactions >$80k within 48 hours",
                "serialized_rule_json": json.dumps({
                    "threshold_amount": 80000,
                    "transaction_count": 2,
                    "time_window_hours": 48
                }),
                "effective_at": base_time - timedelta(days=60)
            },
            {
                "detection_rule_snapshot_id": "00000000-0000-0000-0000-0000000001f6",
                "rule_code": "RULE-003",
                "rule_name": "PEP relationship monitoring",
                "rule_version": "v4.0",
                "threshold_description": "Transactions >$50k with PEP-flagged customers",
                "serialized_rule_json": json.dumps({
                    "threshold_amount": 50000,
                    "pep_check": True,
                    "lookback_days": 30
                }),
                "effective_at": base_time - timedelta(days=15)
            }
        ]
        
        for rule_data in rules_data:
            rule_data["detection_rule_snapshot_id"] = uuid.UUID(rule_data["detection_rule_snapshot_id"])
            rule = DetectionRuleSnapshot(**rule_data)
            db.add(rule)
        
        # ===== Rule Evaluation Results =====
        # Create rule evaluation results for FR-013 historical rule snapshot visibility
        # Outcome values: MATCH (rule triggered), PASS (rule checked but not triggered)
        rule_evaluations_data = [
            {
                "rule_evaluation_result_id": "00000000-0000-0000-0000-000000000258",
                "alert_id": "00000000-0000-0000-0000-0000000002bc",
                "detection_rule_snapshot_id": "00000000-0000-0000-0000-0000000001f4",
                "outcome": "MATCH",
                "threshold_explanation": "Transaction amount $285,000 exceeds threshold of $200,000 for cross-border corridor GB-HK",
                "evaluated_at": base_time
            },
            {
                "rule_evaluation_result_id": "00000000-0000-0000-0000-000000000259",
                "alert_id": "00000000-0000-0000-0000-0000000002bd",
                "detection_rule_snapshot_id": "00000000-0000-0000-0000-0000000001f4",
                "outcome": "MATCH",
                "threshold_explanation": "Transaction amount $450,000 exceeds threshold of $200,000 for cross-border corridor GB-SG",
                "evaluated_at": base_time + timedelta(hours=2)
            },
            {
                "rule_evaluation_result_id": "00000000-0000-0000-0000-00000000025a",
                "alert_id": "00000000-0000-0000-0000-0000000002bd",
                "detection_rule_snapshot_id": "00000000-0000-0000-0000-0000000001f5",
                "outcome": "MATCH",
                "threshold_explanation": "2 transactions totaling $735,000 detected within 48-hour window, each exceeding $80,000",
                "evaluated_at": base_time + timedelta(hours=2)
            },
            {
                "rule_evaluation_result_id": "00000000-0000-0000-0000-00000000025b",
                "alert_id": "00000000-0000-0000-0000-0000000002be",
                "detection_rule_snapshot_id": "00000000-0000-0000-0000-0000000001f5",
                "outcome": "MATCH",
                "threshold_explanation": "Transaction amount $125,000 exceeds threshold of $80,000",
                "evaluated_at": base_time + timedelta(hours=4)
            },
            {
                "rule_evaluation_result_id": "00000000-0000-0000-0000-00000000025c",
                "alert_id": "00000000-0000-0000-0000-0000000002c3",
                "detection_rule_snapshot_id": "00000000-0000-0000-0000-0000000001f6",
                "outcome": "MATCH",
                "threshold_explanation": "Transaction amount $125,000 with PEP-flagged customer relationship",
                "evaluated_at": base_time + timedelta(hours=13)
            },
            {
                "rule_evaluation_result_id": "00000000-0000-0000-0000-00000000025d",
                "alert_id": "00000000-0000-0000-0000-0000000002c3",
                "detection_rule_snapshot_id": "00000000-0000-0000-0000-0000000001f5",
                "outcome": "MATCH",
                "threshold_explanation": "Multiple high-value transactions detected in rapid succession",
                "evaluated_at": base_time + timedelta(hours=13)
            },
            {
                "rule_evaluation_result_id": "00000000-0000-0000-0000-00000000025e",
                "alert_id": "00000000-0000-0000-0000-0000000002c0",
                "detection_rule_snapshot_id": "00000000-0000-0000-0000-0000000001f4",
                "outcome": "PASS",
                "threshold_explanation": "Transaction amount $45,000 below threshold of $200,000 - no match",
                "evaluated_at": base_time + timedelta(hours=8)
            },
            {
                "rule_evaluation_result_id": "00000000-0000-0000-0000-00000000025f",
                "alert_id": "00000000-0000-0000-0000-0000000002c5",
                "detection_rule_snapshot_id": "00000000-0000-0000-0000-0000000001f6",
                "outcome": "PASS",
                "threshold_explanation": "Customer not flagged as PEP - no match",
                "evaluated_at": base_time + timedelta(hours=16)
            }
        ]
        
        for eval_data in rule_evaluations_data:
            eval_data["rule_evaluation_result_id"] = uuid.UUID(eval_data["rule_evaluation_result_id"])
            eval_data["alert_id"] = uuid.UUID(eval_data["alert_id"])
            eval_data["detection_rule_snapshot_id"] = uuid.UUID(eval_data["detection_rule_snapshot_id"])
            rule_eval = RuleEvaluationResult(**eval_data)
            db.add(rule_eval)
        
        # ===== Alerts =====
        alerts_data = [
            {
                "alert_id": "00000000-0000-0000-0000-0000000002bc",
                "transaction_id": "00000000-0000-0000-0000-000000000190",
                "customer_id": "00000000-0000-0000-0000-000000000064",
                "status": "NEW",
                "priority": "CRITICAL",
                "risk_score": 92,
                "matched_rule_codes_json": json.dumps(["RULE-001"]),
                "generation": "automatic",
                "assigned_user_id": None,
                "triage_outcome": None,
                "triage_rationale": None,
                "triaged_by_user_id": None,
                "triaged_at": None,
                "created_at": base_time,
                "updated_at": base_time
            },
            {
                "alert_id": "00000000-0000-0000-0000-0000000002bd",
                "transaction_id": "00000000-0000-0000-0000-000000000191",
                "customer_id": "00000000-0000-0000-0000-000000000064",
                "status": "NEW",
                "priority": "HIGH",
                "risk_score": 88,
                "matched_rule_codes_json": json.dumps(["RULE-001", "RULE-002"]),
                "generation": "automatic",
                "assigned_user_id": None,
                "triage_outcome": None,
                "triage_rationale": None,
                "triaged_by_user_id": None,
                "triaged_at": None,
                "created_at": base_time + timedelta(hours=2),
                "updated_at": base_time + timedelta(hours=2)
            },
            {
                "alert_id": "00000000-0000-0000-0000-0000000002be",
                "transaction_id": "00000000-0000-0000-0000-000000000192",
                "customer_id": "00000000-0000-0000-0000-000000000065",
                "status": "UNDER_REVIEW",
                "priority": "HIGH",
                "risk_score": 75,
                "matched_rule_codes_json": json.dumps(["RULE-002"]),
                "generation": "automatic",
                "assigned_user_id": "00000000-0000-0000-0000-000000000001",
                "triage_outcome": None,
                "triage_rationale": None,
                "triaged_by_user_id": None,
                "triaged_at": None,
                "created_at": base_time + timedelta(hours=4),
                "updated_at": base_time + timedelta(hours=5)
            },
            {
                "alert_id": "00000000-0000-0000-0000-0000000002bf",
                "transaction_id": "00000000-0000-0000-0000-000000000193",
                "customer_id": "00000000-0000-0000-0000-000000000065",
                "status": "UNDER_REVIEW",
                "priority": "MEDIUM",
                "risk_score": 65,
                "matched_rule_codes_json": json.dumps(["RULE-001"]),
                "generation": "manual",
                "assigned_user_id": "00000000-0000-0000-0000-000000000001",
                "triage_outcome": None,
                "triage_rationale": None,
                "triaged_by_user_id": None,
                "triaged_at": None,
                "created_at": base_time + timedelta(hours=6),
                "updated_at": base_time + timedelta(hours=7)
            },
            {
                "alert_id": "00000000-0000-0000-0000-0000000002c0",
                "transaction_id": "00000000-0000-0000-0000-000000000194",
                "customer_id": "00000000-0000-0000-0000-000000000066",
                "status": "NEW",
                "priority": "LOW",
                "risk_score": 45,
                "matched_rule_codes_json": json.dumps(["RULE-002"]),
                "generation": "automatic",
                "assigned_user_id": None,
                "triage_outcome": None,
                "triage_rationale": None,
                "triaged_by_user_id": None,
                "triaged_at": None,
                "created_at": base_time + timedelta(hours=8),
                "updated_at": base_time + timedelta(hours=8)
            },
            {
                "alert_id": "00000000-0000-0000-0000-0000000002c1",
                "transaction_id": "00000000-0000-0000-0000-000000000190",
                "customer_id": "00000000-0000-0000-0000-000000000064",
                "status": "ESCALATED_TO_CASE",
                "priority": "CRITICAL",
                "risk_score": 95,
                "matched_rule_codes_json": json.dumps(["RULE-001"]),
                "generation": "automatic",
                "assigned_user_id": "00000000-0000-0000-0000-000000000001",
                "triage_outcome": "INVESTIGATE",
                "triage_rationale": "Suspicious pattern detected with high-risk jurisdiction",
                "triaged_by_user_id": "00000000-0000-0000-0000-000000000001",
                "triaged_at": base_time + timedelta(hours=10),
                "created_at": base_time + timedelta(hours=9),
                "updated_at": base_time + timedelta(hours=10)
            },
            {
                "alert_id": "00000000-0000-0000-0000-0000000002c2",
                "transaction_id": "00000000-0000-0000-0000-000000000191",
                "customer_id": "00000000-0000-0000-0000-000000000064",
                "status": "CLOSED_NON_ACTIONABLE",
                "priority": "MEDIUM",
                "risk_score": 58,
                "matched_rule_codes_json": json.dumps(["RULE-002"]),
                "generation": "automatic",
                "assigned_user_id": "00000000-0000-0000-0000-000000000001",
                "triage_outcome": "CLOSE_NON_ACTIONABLE",
                "triage_rationale": "Verified legitimate business transaction with supporting documentation",
                "triaged_by_user_id": "00000000-0000-0000-0000-000000000001",
                "triaged_at": base_time + timedelta(hours=12),
                "created_at": base_time + timedelta(hours=11),
                "updated_at": base_time + timedelta(hours=12)
            },
            {
                "alert_id": "00000000-0000-0000-0000-0000000002c3",
                "transaction_id": "00000000-0000-0000-0000-000000000192",
                "customer_id": "00000000-0000-0000-0000-000000000065",
                "status": "NEW",
                "priority": "HIGH",
                "risk_score": 82,
                "matched_rule_codes_json": json.dumps(["RULE-001", "RULE-002"]),
                "generation": "automatic",
                "assigned_user_id": None,
                "triage_outcome": None,
                "triage_rationale": None,
                "triaged_by_user_id": None,
                "triaged_at": None,
                "created_at": base_time + timedelta(hours=13),
                "updated_at": base_time + timedelta(hours=13)
            },
            {
                "alert_id": "00000000-0000-0000-0000-0000000002c4",
                "transaction_id": "00000000-0000-0000-0000-000000000193",
                "customer_id": "00000000-0000-0000-0000-000000000065",
                "status": "UNDER_REVIEW",
                "priority": "MEDIUM",
                "risk_score": 68,
                "matched_rule_codes_json": json.dumps(["RULE-001"]),
                "generation": "automatic",
                "assigned_user_id": "00000000-0000-0000-0000-000000000002",
                "triage_outcome": None,
                "triage_rationale": None,
                "triaged_by_user_id": None,
                "triaged_at": None,
                "created_at": base_time + timedelta(hours=14),
                "updated_at": base_time + timedelta(hours=15)
            },
            {
                "alert_id": "00000000-0000-0000-0000-0000000002c5",
                "transaction_id": "00000000-0000-0000-0000-000000000194",
                "customer_id": "00000000-0000-0000-0000-000000000066",
                "status": "NEW",
                "priority": "LOW",
                "risk_score": 38,
                "matched_rule_codes_json": json.dumps(["RULE-002"]),
                "generation": "automatic",
                "assigned_user_id": None,
                "triage_outcome": None,
                "triage_rationale": None,
                "triaged_by_user_id": None,
                "triaged_at": None,
                "created_at": base_time + timedelta(hours=16),
                "updated_at": base_time + timedelta(hours=16)
            }
        ]
        
        for alert_data in alerts_data:
            alert_data["alert_id"] = uuid.UUID(alert_data["alert_id"])
            alert_data["transaction_id"] = uuid.UUID(alert_data["transaction_id"])
            alert_data["customer_id"] = uuid.UUID(alert_data["customer_id"])
            if alert_data.get("assigned_user_id"):
                alert_data["assigned_user_id"] = uuid.UUID(alert_data["assigned_user_id"])
            if alert_data.get("triaged_by_user_id"):
                alert_data["triaged_by_user_id"] = uuid.UUID(alert_data["triaged_by_user_id"])
            alert = Alert(**alert_data)
            db.add(alert)
        
        # ===== Cases =====
        # Create 2 sample cases linked to alerts
        cases_data = [
            {
                "case_id": "00000000-0000-0000-0000-000000000320",
                "case_number": "CS-001",
                "source_alert_id": "00000000-0000-0000-0000-0000000002bc",
                "customer_id": "00000000-0000-0000-0000-000000000064",
                "status": "INVESTIGATING",
                "priority": "CRITICAL",
                "assigned_user_id": "00000000-0000-0000-0000-000000000001",
                "recommendation_state": "DRAFT",
                "recommendation_outcome": None,
                "findings_summary": None,
                "flagged_value_total": Decimal("285000.00"),
                "evidence_locked_for_review": False,
                "created_by_user_id": "00000000-0000-0000-0000-000000000001",
                "handoff_officer_user_id": None,
                "created_at": base_time + timedelta(hours=17),
                "updated_at": base_time + timedelta(hours=17)
            },
            {
                "case_id": "00000000-0000-0000-0000-000000000321",
                "case_number": "CS-002",
                "source_alert_id": "00000000-0000-0000-0000-0000000002c3",
                "customer_id": "00000000-0000-0000-0000-000000000065",
                "status": "INVESTIGATING",
                "priority": "HIGH",
                "assigned_user_id": "00000000-0000-0000-0000-000000000001",
                "recommendation_state": "SUBMITTED",
                "recommendation_outcome": "NO_FURTHER_ACTION",
                "findings_summary": "After thorough investigation and review of supporting documentation, Brighton Investment Partners' transaction pattern is consistent with normal institutional fund operations. No PEP or sanctions matches found. Customer provided quarterly investment reports confirming legitimate portfolio rebalancing activity. No further action required at this time. Customer will remain on standard monitoring schedule.",
                "flagged_value_total": Decimal("125000.00"),
                "evidence_locked_for_review": False,
                "created_by_user_id": "00000000-0000-0000-0000-000000000001",
                "handoff_officer_user_id": None,
                "created_at": base_time + timedelta(hours=18),
                "updated_at": base_time + timedelta(days=6)
            }
        ]
        
        for case_data in cases_data:
            case_data["case_id"] = uuid.UUID(case_data["case_id"])
            case_data["source_alert_id"] = uuid.UUID(case_data["source_alert_id"])
            case_data["customer_id"] = uuid.UUID(case_data["customer_id"])
            case_data["assigned_user_id"] = uuid.UUID(case_data["assigned_user_id"])
            case_data["created_by_user_id"] = uuid.UUID(case_data["created_by_user_id"])
            case = AMLCase(**case_data)  # type: ignore[arg-type]
            db.add(case)
        
        # ===== Case Alert Links =====
        links_data = [
            {
                "case_alert_link_id": "00000000-0000-0000-0000-000000000384",
                "case_id": "00000000-0000-0000-0000-000000000320",
                "alert_id": "00000000-0000-0000-0000-0000000002bc",
                "linked_at": base_time + timedelta(hours=17),
                "linked_by_user_id": "00000000-0000-0000-0000-000000000001",
                "selection_basis": "Large cross-border transfer with high risk score requiring investigation"
            },
            {
                "case_alert_link_id": "00000000-0000-0000-0000-000000000385",
                "case_id": "00000000-0000-0000-0000-000000000321",
                "alert_id": "00000000-0000-0000-0000-0000000002c3",
                "linked_at": base_time + timedelta(hours=18),
                "linked_by_user_id": "00000000-0000-0000-0000-000000000001",
                "selection_basis": "Multiple rule hits indicating suspicious pattern"
            }
        ]
        
        for link_data in links_data:
            link_data["case_alert_link_id"] = uuid.UUID(link_data["case_alert_link_id"])
            link_data["case_id"] = uuid.UUID(link_data["case_id"])
            link_data["alert_id"] = uuid.UUID(link_data["alert_id"])
            link_data["linked_by_user_id"] = uuid.UUID(link_data["linked_by_user_id"])
            link = CaseAlertLink(**link_data)
            db.add(link)
        
        # ===== Audit Events for Case Creation =====
        audit_events_data = [
            {
                "audit_event_id": "00000000-0000-0000-0000-0000000003e8",
                "entity_type": "case",
                "entity_id": "00000000-0000-0000-0000-000000000320",
                "action_type": "CASE_CREATED",
                "actor_user_id": "00000000-0000-0000-0000-000000000001",
                "actor_role": "investigator",
                "correlation_id": "00000000-0000-0000-0000-000000000514",
                "payload_json": json.dumps({
                    "case_number": "CS-001",
                    "source_alert_id": "00000000-0000-0000-0000-0000000002bc",
                    "priority": "CRITICAL",
                    "initial_rationale": "Large cross-border transfer with high risk score requiring investigation"
                }),
                "occurred_at": base_time + timedelta(hours=17),
                "created_at": base_time + timedelta(hours=17)
            },
            {
                "audit_event_id": "00000000-0000-0000-0000-0000000003e9",
                "entity_type": "alert",
                "entity_id": "00000000-0000-0000-0000-0000000002bc",
                "action_type": "ALERT_LINKED_TO_CASE",
                "actor_user_id": "00000000-0000-0000-0000-000000000001",
                "actor_role": "investigator",
                "correlation_id": "00000000-0000-0000-0000-000000000514",
                "payload_json": json.dumps({
                    "case_id": "00000000-0000-0000-0000-000000000320",
                    "case_number": "CS-001",
                    "previous_status": "UNDER_REVIEW",
                    "new_status": "ESCALATED_TO_CASE"
                }),
                "occurred_at": base_time + timedelta(hours=17),
                "created_at": base_time + timedelta(hours=17)
            },
            {
                "audit_event_id": "00000000-0000-0000-0000-0000000003ea",
                "entity_type": "case",
                "entity_id": "00000000-0000-0000-0000-000000000321",
                "action_type": "CASE_CREATED",
                "actor_user_id": "00000000-0000-0000-0000-000000000001",
                "actor_role": "investigator",
                "correlation_id": "00000000-0000-0000-0000-000000000515",
                "payload_json": json.dumps({
                    "case_number": "CS-002",
                    "source_alert_id": "00000000-0000-0000-0000-0000000002c3",
                    "priority": "HIGH",
                    "initial_rationale": "Multiple rule hits indicating suspicious pattern"
                }),
                "occurred_at": base_time + timedelta(hours=18),
                "created_at": base_time + timedelta(hours=18)
            },
            {
                "audit_event_id": "00000000-0000-0000-0000-0000000003eb",
                "entity_type": "alert",
                "entity_id": "00000000-0000-0000-0000-0000000002c3",
                "action_type": "ALERT_LINKED_TO_CASE",
                "actor_user_id": "00000000-0000-0000-0000-000000000001",
                "actor_role": "investigator",
                "correlation_id": "00000000-0000-0000-0000-000000000515",
                "payload_json": json.dumps({
                    "case_id": "00000000-0000-0000-0000-000000000321",
                    "case_number": "CS-002",
                    "previous_status": "NEW",
                    "new_status": "ESCALATED_TO_CASE"
                }),
                "occurred_at": base_time + timedelta(hours=18),
                "created_at": base_time + timedelta(hours=18)
            }
        ]
        
        for event_data in audit_events_data:
            event_data["audit_event_id"] = uuid.UUID(event_data["audit_event_id"])
            # entity_id and correlation_id are String columns, not UUID
            event_data["actor_user_id"] = uuid.UUID(event_data["actor_user_id"])
            event = AuditEvent(**event_data)
            db.add(event)
        
        # ===== Case Notes =====
        # Add sample investigation notes for the seed cases
        case_notes_data = [
            {
                "note_id": "00000000-0000-0000-0000-00000000044c",
                "case_id": "00000000-0000-0000-0000-000000000320",
                "note_type": "INVESTIGATION",
                "stage": "INITIAL_REVIEW",
                "body": "Initial review of transaction reveals large cross-border transfer to high-risk jurisdiction. Customer Acme Global Trading has history of similar transactions. Need to verify business purpose and ultimate beneficial owner.",
                "author_user_id": "00000000-0000-0000-0000-000000000001",
                "superseded_by_note_id": None,
                "created_at": base_time + timedelta(hours=17, minutes=15)
            },
            {
                "note_id": "00000000-0000-0000-0000-00000000044d",
                "case_id": "00000000-0000-0000-0000-000000000320",
                "note_type": "ANALYSIS",
                "stage": "DETAILED_ANALYSIS",
                "body": "Reviewed supporting documentation. Transaction appears to be payment for legitimate import/export business. Customer provided invoice and shipping documents. Counterparty Eastern Trade Corp is registered trading company in Hong Kong.",
                "author_user_id": "00000000-0000-0000-0000-000000000001",
                "superseded_by_note_id": None,
                "created_at": base_time + timedelta(hours=18, minutes=30)
            },
            {
                "note_id": "00000000-0000-0000-0000-00000000044e",
                "case_id": "00000000-0000-0000-0000-000000000320",
                "note_type": "INVESTIGATION",
                "stage": "ONGOING_MONITORING",
                "body": "Flagged for enhanced monitoring. Will track subsequent transactions for unusual patterns. Customer risk rating remains HIGH pending additional verification of beneficial ownership structure.",
                "author_user_id": "00000000-0000-0000-0000-000000000001",
                "superseded_by_note_id": None,
                "created_at": base_time + timedelta(hours=19, minutes=45)
            },
            {
                "note_id": "00000000-0000-0000-0000-00000000044f",
                "case_id": "00000000-0000-0000-0000-000000000321",
                "note_type": "INVESTIGATION",
                "stage": "INITIAL_REVIEW",
                "body": "Multiple rule hits on this alert. Brighton Investment Partners shows rapid succession of high-value transactions. Checking against known PEP database and sanctions lists.",
                "author_user_id": "00000000-0000-0000-0000-000000000001",
                "superseded_by_note_id": None,
                "created_at": base_time + timedelta(hours=18, minutes=20)
            },
            {
                "note_id": "00000000-0000-0000-0000-000000000450",
                "case_id": "00000000-0000-0000-0000-000000000321",
                "note_type": "ANALYSIS",
                "stage": "DETAILED_ANALYSIS",
                "body": "No PEP or sanctions matches found. Transaction pattern consistent with normal investment fund operations. Customer has provided quarterly investment reports showing legitimate portfolio rebalancing activity.",
                "author_user_id": "00000000-0000-0000-0000-000000000001",
                "superseded_by_note_id": None,
                "created_at": base_time + timedelta(hours=19, minutes=10)
            }
        ]
        
        for note_data in case_notes_data:
            note_data["note_id"] = uuid.UUID(note_data["note_id"])
            note_data["case_id"] = uuid.UUID(note_data["case_id"])
            note_data["author_user_id"] = uuid.UUID(note_data["author_user_id"])
            note = CaseNote(**note_data)
            db.add(note)
        
        # Add corresponding audit events for note creation
        note_audit_events_data = [
            {
                "audit_event_id": "00000000-0000-0000-0000-0000000003ec",
                "entity_type": "case",
                "entity_id": "00000000-0000-0000-0000-000000000320",
                "action_type": "INVESTIGATION_NOTE_ADDED",
                "actor_user_id": "00000000-0000-0000-0000-000000000001",
                "actor_role": "investigator",
                "correlation_id": "00000000-0000-0000-0000-000000000516",
                "payload_json": json.dumps({
                    "note_id": "00000000-0000-0000-0000-00000000044c",
                    "note_type": "INVESTIGATION",
                    "stage": "INITIAL_REVIEW",
                    "body_length": 234
                }),
                "occurred_at": base_time + timedelta(hours=17, minutes=15),
                "created_at": base_time + timedelta(hours=17, minutes=15)
            },
            {
                "audit_event_id": "00000000-0000-0000-0000-0000000003ed",
                "entity_type": "case",
                "entity_id": "00000000-0000-0000-0000-000000000321",
                "action_type": "INVESTIGATION_NOTE_ADDED",
                "actor_user_id": "00000000-0000-0000-0000-000000000001",
                "actor_role": "investigator",
                "correlation_id": "00000000-0000-0000-0000-000000000517",
                "payload_json": json.dumps({
                    "note_id": "00000000-0000-0000-0000-00000000044f",
                    "note_type": "INVESTIGATION",
                    "stage": "INITIAL_REVIEW",
                    "body_length": 179
                }),
                "occurred_at": base_time + timedelta(hours=18, minutes=20),
                "created_at": base_time + timedelta(hours=18, minutes=20)
            }
        ]
        
        for event_data in note_audit_events_data:
            event_data["audit_event_id"] = uuid.UUID(event_data["audit_event_id"])
            # entity_id and correlation_id are String columns, not UUID
            event_data["actor_user_id"] = uuid.UUID(event_data["actor_user_id"])
            event = AuditEvent(**event_data)
            db.add(event)
        
        # ===== Information Requests =====
        # Add 3 sample information requests: IR-001 responded, IR-002 overdue, IR-003 responded
        information_requests_data = [
            {
                "information_request_id": "00000000-0000-0000-0000-0000000004b0",
                "case_id": "00000000-0000-0000-0000-000000000320",
                "recipient_channel": "EMAIL",
                "requested_summary": "Request copy of invoices and shipping documents for transaction txn-001 dated " + base_time.strftime("%Y-%m-%d"),
                "rationale": "Need to verify legitimacy of large cross-border payment to Eastern Trade Corp",
                "status": "RESPONDED",
                "due_at": base_time + timedelta(days=5),
                "response_summary": "Invoices and shipping documents provided. Transaction confirmed legitimate import/export payment.",
                "response_channel": "EMAIL",
                "response_received_at": base_time + timedelta(days=3),
                "created_by_user_id": "00000000-0000-0000-0000-000000000001",
                "created_at": base_time + timedelta(hours=20),
                "updated_at": base_time + timedelta(days=3)
            },
            {
                "information_request_id": "00000000-0000-0000-0000-0000000004b1",
                "case_id": "00000000-0000-0000-0000-000000000320",
                "recipient_channel": "PORTAL",
                "requested_summary": "Provide detailed breakdown of beneficial ownership structure for Acme Global Trading Ltd",
                "rationale": "Enhanced due diligence required for high-risk customer with cross-border transactions",
                "status": "OPEN",
                "due_at": datetime.now(timezone.utc) - timedelta(days=2),  # Overdue by 2 days
                "response_summary": None,
                "response_channel": None,
                "response_received_at": None,
                "created_by_user_id": "00000000-0000-0000-0000-000000000001",
                "created_at": base_time + timedelta(hours=21),
                "updated_at": base_time + timedelta(hours=21)
            },
            {
                "information_request_id": "00000000-0000-0000-0000-0000000004b2",
                "case_id": "00000000-0000-0000-0000-000000000321",
                "recipient_channel": "EMAIL",
                "requested_summary": "Submit quarterly investment reports and portfolio statements for Q3 and Q4",
                "rationale": "Verify transaction pattern consistency with normal fund operations",
                "status": "RESPONDED",
                "due_at": base_time + timedelta(days=7),
                "response_summary": "Investment reports provided. Confirms portfolio rebalancing activity. All transactions legitimate and consistent with fund strategy.",
                "response_channel": "EMAIL",
                "response_received_at": base_time + timedelta(days=5),
                "created_by_user_id": "00000000-0000-0000-0000-000000000001",
                "created_at": base_time + timedelta(hours=22),
                "updated_at": base_time + timedelta(days=5)
            }
        ]
        
        for request_data in information_requests_data:
            request_data["information_request_id"] = uuid.UUID(request_data["information_request_id"])
            request_data["case_id"] = uuid.UUID(request_data["case_id"])
            request_data["created_by_user_id"] = uuid.UUID(request_data["created_by_user_id"])
            request = InformationRequest(**request_data)
            db.add(request)
        
        # Add corresponding audit events for information request creation and response
        ir_audit_events_data = [
            {
                "audit_event_id": "00000000-0000-0000-0000-0000000003ee",
                "entity_type": "case",
                "entity_id": "00000000-0000-0000-0000-000000000320",
                "action_type": "INFORMATION_REQUEST_CREATED",
                "actor_user_id": "00000000-0000-0000-0000-000000000001",
                "actor_role": "investigator",
                "correlation_id": "00000000-0000-0000-0000-000000000518",
                "payload_json": json.dumps({
                    "information_request_id": "00000000-0000-0000-0000-0000000004b0",
                    "recipient_channel": "EMAIL",
                    "requested_summary": "Request copy of invoices and shipping documents",
                    "due_at": (base_time + timedelta(days=5)).isoformat()
                }),
                "occurred_at": base_time + timedelta(hours=20),
                "created_at": base_time + timedelta(hours=20)
            },
            {
                "audit_event_id": "00000000-0000-0000-0000-0000000003ef",
                "entity_type": "case",
                "entity_id": "00000000-0000-0000-0000-000000000320",
                "action_type": "INFORMATION_REQUEST_RESPONSE_RECORDED",
                "actor_user_id": "00000000-0000-0000-0000-000000000001",
                "actor_role": "investigator",
                "correlation_id": "00000000-0000-0000-0000-000000000519",
                "payload_json": json.dumps({
                    "information_request_id": "00000000-0000-0000-0000-0000000004b0",
                    "response_channel": "EMAIL",
                    "received_at": (base_time + timedelta(days=3)).isoformat(),
                    "previous_status": "PENDING_INFORMATION",
                    "new_status": "INVESTIGATING",
                    "recorded_at": (base_time + timedelta(days=3)).isoformat()
                }),
                "occurred_at": base_time + timedelta(days=3),
                "created_at": base_time + timedelta(days=3)
            },
            {
                "audit_event_id": "00000000-0000-0000-0000-0000000003f0",
                "entity_type": "case",
                "entity_id": "00000000-0000-0000-0000-000000000320",
                "action_type": "INFORMATION_REQUEST_CREATED",
                "actor_user_id": "00000000-0000-0000-0000-000000000001",
                "actor_role": "investigator",
                "correlation_id": "00000000-0000-0000-0000-00000000051a",
                "payload_json": json.dumps({
                    "information_request_id": "00000000-0000-0000-0000-0000000004b1",
                    "recipient_channel": "PORTAL",
                    "requested_summary": "Provide detailed breakdown of beneficial ownership structure",
                    "due_at": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
                }),
                "occurred_at": base_time + timedelta(hours=21),
                "created_at": base_time + timedelta(hours=21)
            },
            {
                "audit_event_id": "00000000-0000-0000-0000-0000000003f1",
                "entity_type": "case",
                "entity_id": "00000000-0000-0000-0000-000000000321",
                "action_type": "INFORMATION_REQUEST_CREATED",
                "actor_user_id": "00000000-0000-0000-0000-000000000001",
                "actor_role": "investigator",
                "correlation_id": "00000000-0000-0000-0000-00000000051b",
                "payload_json": json.dumps({
                    "information_request_id": "00000000-0000-0000-0000-0000000004b2",
                    "recipient_channel": "EMAIL",
                    "requested_summary": "Submit quarterly investment reports and portfolio statements",
                    "due_at": (base_time + timedelta(days=7)).isoformat()
                }),
                "occurred_at": base_time + timedelta(hours=22),
                "created_at": base_time + timedelta(hours=22)
            }
        ]
        
        for event_data in ir_audit_events_data:
            event_data["audit_event_id"] = uuid.UUID(event_data["audit_event_id"])
            # entity_id and correlation_id are String columns, not UUID
            event_data["actor_user_id"] = uuid.UUID(event_data["actor_user_id"])
            event = AuditEvent(**event_data)
            db.add(event)
        
        # ===== Recommendation Submission Audit Event =====
        # Add audit event for CS-002 recommendation submission
        recommendation_audit_event = AuditEvent(
            audit_event_id=uuid.UUID("00000000-0000-0000-0000-0000000003f2"),
            entity_type="case",
            entity_id="00000000-0000-0000-0000-000000000321",  # String, not UUID
            action_type="INVESTIGATION_RECOMMENDATION_SUBMITTED",
            actor_user_id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
            actor_role="investigator",
            correlation_id="00000000-0000-0000-0000-00000000051c",  # String, not UUID
            payload_json=json.dumps({
                "recommendation_outcome": "NO_FURTHER_ACTION",
                "findings_summary_length": 407,
                "recommendation_state": "SUBMITTED",
                "submitted_at": (base_time + timedelta(days=6)).isoformat()
            }),
            occurred_at=base_time + timedelta(days=6),
            created_at=base_time + timedelta(days=6)
        )
        db.add(recommendation_audit_event)
        
        db.commit()
        
        print("✓ Seed data created successfully")
        print("  - Users: 2 (riya investigator, morgan officer)")
        print("  - Customers: 3")
        print("  - Accounts: 3")
        print("  - Transactions: 5")
        print("  - Detection Rules: 3 (v3.2, v2.1, v4.0)")
        print("  - Rule Evaluations: 8 (6 MATCH, 2 PASS)")
        print("  - Alerts: 10 (varying statuses/priorities/risk scores)")
        print("  - Cases: 2 (CS-001 with overdue request IR-002, CS-002 with submitted recommendation)")
        print("  - Case Alert Links: 2")
        print("  - Case Notes: 5 (investigation notes for both cases)")
        print("  - Information Requests: 3 (IR-001 responded, IR-002 overdue, IR-003 responded)")
        print("  - Audit Events: 11 (includes IR-001 response and recommendation submission)")
        print("  - Login credentials: riya/password123, morgan/password123")
        print("  - CS-002 ready for handoff (recommendation submitted, no open requests)")
        print("  - SLA tracking: IR-002 overdue (due 2 days ago), IR-001 and IR-003 responded")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
