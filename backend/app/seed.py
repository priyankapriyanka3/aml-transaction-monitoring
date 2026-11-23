"""Seed data for local development and testing."""
import uuid
import hashlib
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.database import SessionLocal
from app.models.user import User
from app.models.customer import Customer
from app.models.account import Account
from app.models.transaction import Transaction
from app.models.alert import Alert
from app.models.case import AmlCase
from app.models.case_alert_link import CaseAlertLink
from app.models.rule_snapshot import RuleEvaluationSnapshot
from app.models.case_note import CaseNote
from app.models.evidence_gap import EvidenceGap
from app.models.information_request import InformationRequest
from app.models.case_review_assignment import CaseReviewAssignment
from app.models.case_decision import CaseDecision
from app.core.security import hash_password


def seed_users(db: Session) -> None:
    """Seed default users with various roles.
    
    Args:
        db: Database session
    """
    # Check if users already exist
    stmt = select(User).limit(1)
    existing_user = db.scalars(stmt).first()
    
    if existing_user:
        print("Users already seeded, skipping...")
        return
    
    # Seed users
    users_data = [
        {
            "user_id": uuid.UUID("00000000-0000-0000-0000-000000000001"),
            "display_name": "Alice Investigator",
            "email": "investigator@example.com",
            "password": "investigator123",
            "role": "INVESTIGATOR",
            "is_active": True
        },
        {
            "user_id": uuid.UUID("00000000-0000-0000-0000-000000000002"),
            "display_name": "Bob Officer",
            "email": "officer@example.com",
            "password": "officer123",
            "role": "OFFICER",
            "is_active": True
        },
        {
            "user_id": uuid.UUID("00000000-0000-0000-0000-000000000003"),
            "display_name": "Carol Auditor",
            "email": "auditor@example.com",
            "password": "auditor123",
            "role": "AUDITOR",
            "is_active": True
        },
        {
            "user_id": uuid.UUID("00000000-0000-0000-0000-000000000004"),
            "display_name": "Dave Supervisor",
            "email": "supervisor@example.com",
            "password": "supervisor123",
            "role": "SUPERVISOR",
            "is_active": True
        },
        {
            "user_id": uuid.UUID("00000000-0000-0000-0000-000000000005"),
            "display_name": "Eve Investigator 2",
            "email": "investigator2@example.com",
            "password": "investigator123",
            "role": "INVESTIGATOR",
            "is_active": True
        }
    ]
    
    for user_data in users_data:
        password = str(user_data.pop("password"))
        hashed_password = hash_password(password)
        
        user = User(
            **user_data,
            hashed_password=hashed_password
        )
        db.add(user)
    
    db.commit()
    print(f"Seeded {len(users_data)} users")


def seed_customers(db: Session) -> None:
    """Seed customer data."""
    # Check if customers already exist
    stmt = select(Customer).limit(1)
    existing = db.scalars(stmt).first()
    
    if existing:
        print("Customers already seeded, skipping...")
        return
    
    customers_data = [
        {
            "customer_id": uuid.UUID("10000000-0000-0000-0000-000000000001"),
            "customer_name": "John Smith",
            "pep_flag": False,
            "country_code": "GB"
        },
        {
            "customer_id": uuid.UUID("10000000-0000-0000-0000-000000000002"),
            "customer_name": "Maria Garcia",
            "pep_flag": True,
            "country_code": "ES"
        },
        {
            "customer_id": uuid.UUID("10000000-0000-0000-0000-000000000003"),
            "customer_name": "Zhang Wei",
            "pep_flag": False,
            "country_code": "CN"
        },
        {
            "customer_id": uuid.UUID("10000000-0000-0000-0000-000000000004"),
            "customer_name": "Ahmed Hassan",
            "pep_flag": False,
            "country_code": "EG"
        },
        {
            "customer_id": uuid.UUID("10000000-0000-0000-0000-000000000005"),
            "customer_name": "Svetlana Ivanova",
            "pep_flag": True,
            "country_code": "RU"
        }
    ]
    
    for customer_data in customers_data:
        customer = Customer(**customer_data)
        db.add(customer)
    
    db.commit()
    print(f"Seeded {len(customers_data)} customers")


def seed_accounts(db: Session) -> None:
    """Seed account data."""
    # Check if accounts already exist
    stmt = select(Account).limit(1)
    existing = db.scalars(stmt).first()
    
    if existing:
        print("Accounts already seeded, skipping...")
        return
    
    accounts_data = [
        {
            "account_id": uuid.UUID("20000000-0000-0000-0000-000000000001"),
            "customer_id": uuid.UUID("10000000-0000-0000-0000-000000000001"),
            "account_ref": "ACC-GB-001",
            "account_type": "Checking"
        },
        {
            "account_id": uuid.UUID("20000000-0000-0000-0000-000000000002"),
            "customer_id": uuid.UUID("10000000-0000-0000-0000-000000000002"),
            "account_ref": "ACC-ES-001",
            "account_type": "Business"
        },
        {
            "account_id": uuid.UUID("20000000-0000-0000-0000-000000000003"),
            "customer_id": uuid.UUID("10000000-0000-0000-0000-000000000003"),
            "account_ref": "ACC-CN-001",
            "account_type": "Savings"
        },
        {
            "account_id": uuid.UUID("20000000-0000-0000-0000-000000000004"),
            "customer_id": uuid.UUID("10000000-0000-0000-0000-000000000004"),
            "account_ref": "ACC-EG-001",
            "account_type": "Checking"
        },
        {
            "account_id": uuid.UUID("20000000-0000-0000-0000-000000000005"),
            "customer_id": uuid.UUID("10000000-0000-0000-0000-000000000005"),
            "account_ref": "ACC-RU-001",
            "account_type": "Business"
        }
    ]
    
    for account_data in accounts_data:
        account = Account(**account_data)
        db.add(account)
    
    db.commit()
    print(f"Seeded {len(accounts_data)} accounts")


def seed_transactions(db: Session) -> None:
    """Seed transaction data."""
    # Check if transactions already exist
    stmt = select(Transaction).limit(1)
    existing = db.scalars(stmt).first()
    
    if existing:
        print("Transactions already seeded, skipping...")
        return
    
    now = datetime.now(timezone.utc)
    
    transactions_data = [
        {
            "transaction_id": uuid.UUID("30000000-0000-0000-0000-000000000001"),
            "account_id": uuid.UUID("20000000-0000-0000-0000-000000000001"),
            "transaction_ref": "TXN-2026-001",
            "amount": Decimal("95000.00"),
            "currency_code": "USD",
            "source_country_code": "GB",
            "destination_country_code": "VG",
            "executed_at_utc": now - timedelta(hours=2)
        },
        {
            "transaction_id": uuid.UUID("30000000-0000-0000-0000-000000000002"),
            "account_id": uuid.UUID("20000000-0000-0000-0000-000000000002"),
            "transaction_ref": "TXN-2026-002",
            "amount": Decimal("150000.00"),
            "currency_code": "EUR",
            "source_country_code": "ES",
            "destination_country_code": "PA",
            "executed_at_utc": now - timedelta(hours=4)
        },
        {
            "transaction_id": uuid.UUID("30000000-0000-0000-0000-000000000003"),
            "account_id": uuid.UUID("20000000-0000-0000-0000-000000000003"),
            "transaction_ref": "TXN-2026-003",
            "amount": Decimal("25000.00"),
            "currency_code": "USD",
            "source_country_code": "CN",
            "destination_country_code": "US",
            "executed_at_utc": now - timedelta(hours=6)
        },
        {
            "transaction_id": uuid.UUID("30000000-0000-0000-0000-000000000004"),
            "account_id": uuid.UUID("20000000-0000-0000-0000-000000000004"),
            "transaction_ref": "TXN-2026-004",
            "amount": Decimal("180000.00"),
            "currency_code": "USD",
            "source_country_code": "EG",
            "destination_country_code": "CH",
            "executed_at_utc": now - timedelta(hours=8)
        },
        {
            "transaction_id": uuid.UUID("30000000-0000-0000-0000-000000000005"),
            "account_id": uuid.UUID("20000000-0000-0000-0000-000000000005"),
            "transaction_ref": "TXN-2026-005",
            "amount": Decimal("65000.00"),
            "currency_code": "USD",
            "source_country_code": "RU",
            "destination_country_code": "CY",
            "executed_at_utc": now - timedelta(hours=12)
        },
        {
            "transaction_id": uuid.UUID("30000000-0000-0000-0000-000000000006"),
            "account_id": uuid.UUID("20000000-0000-0000-0000-000000000001"),
            "transaction_ref": "TXN-2026-006",
            "amount": Decimal("45000.00"),
            "currency_code": "GBP",
            "source_country_code": "GB",
            "destination_country_code": "KY",
            "executed_at_utc": now - timedelta(hours=16)
        },
        {
            "transaction_id": uuid.UUID("30000000-0000-0000-0000-000000000007"),
            "account_id": uuid.UUID("20000000-0000-0000-0000-000000000002"),
            "transaction_ref": "TXN-2026-007",
            "amount": Decimal("12000.00"),
            "currency_code": "EUR",
            "source_country_code": "ES",
            "destination_country_code": "FR",
            "executed_at_utc": now - timedelta(hours=20)
        },
        {
            "transaction_id": uuid.UUID("30000000-0000-0000-0000-000000000008"),
            "account_id": uuid.UUID("20000000-0000-0000-0000-000000000003"),
            "transaction_ref": "TXN-2026-008",
            "amount": Decimal("88000.00"),
            "currency_code": "USD",
            "source_country_code": "CN",
            "destination_country_code": "HK",
            "executed_at_utc": now - timedelta(hours=24)
        },
        {
            "transaction_id": uuid.UUID("30000000-0000-0000-0000-000000000009"),
            "account_id": uuid.UUID("20000000-0000-0000-0000-000000000004"),
            "transaction_ref": "TXN-2026-009",
            "amount": Decimal("52000.00"),
            "currency_code": "USD",
            "source_country_code": "EG",
            "destination_country_code": "AE",
            "executed_at_utc": now - timedelta(hours=28)
        },
        {
            "transaction_id": uuid.UUID("30000000-0000-0000-0000-000000000010"),
            "account_id": uuid.UUID("20000000-0000-0000-0000-000000000005"),
            "transaction_ref": "TXN-2026-010",
            "amount": Decimal("125000.00"),
            "currency_code": "USD",
            "source_country_code": "RU",
            "destination_country_code": "MT",
            "executed_at_utc": now - timedelta(hours=32)
        }
    ]
    
    for transaction_data in transactions_data:
        transaction = Transaction(**transaction_data)
        db.add(transaction)
    
    db.commit()
    print(f"Seeded {len(transactions_data)} transactions")


def seed_alerts(db: Session) -> None:
    """Seed alert data."""
    # Check if alerts already exist
    stmt = select(Alert).limit(1)
    existing = db.scalars(stmt).first()
    
    if existing:
        print("Alerts already seeded, skipping...")
        return
    
    now = datetime.now(timezone.utc)
    
    # Get user IDs for assignment
    investigator1_id = uuid.UUID("00000000-0000-0000-0000-000000000001")
    investigator2_id = uuid.UUID("00000000-0000-0000-0000-000000000005")
    
    alerts_data = [
        {
            "alert_id": uuid.UUID("40000000-0000-0000-0000-000000000001"),
            "alert_ref": "ALT-2026-001",
            "transaction_id": uuid.UUID("30000000-0000-0000-0000-000000000001"),
            "customer_id": uuid.UUID("10000000-0000-0000-0000-000000000001"),
            "priority": "Critical",
            "risk_score": 95,
            "status": "New",
            "owner_user_id": None,
            "triggered_at_utc": now - timedelta(hours=2)
        },
        {
            "alert_id": uuid.UUID("40000000-0000-0000-0000-000000000002"),
            "alert_ref": "ALT-2026-002",
            "transaction_id": uuid.UUID("30000000-0000-0000-0000-000000000002"),
            "customer_id": uuid.UUID("10000000-0000-0000-0000-000000000002"),
            "priority": "Critical",
            "risk_score": 92,
            "status": "Under Review",
            "owner_user_id": investigator1_id,
            "triggered_at_utc": now - timedelta(hours=4)
        },
        {
            "alert_id": uuid.UUID("40000000-0000-0000-0000-000000000003"),
            "alert_ref": "ALT-2026-003",
            "transaction_id": uuid.UUID("30000000-0000-0000-0000-000000000003"),
            "customer_id": uuid.UUID("10000000-0000-0000-0000-000000000003"),
            "priority": "Medium",
            "risk_score": 65,
            "status": "New",
            "owner_user_id": None,
            "triggered_at_utc": now - timedelta(hours=6)
        },
        {
            "alert_id": uuid.UUID("40000000-0000-0000-0000-000000000004"),
            "alert_ref": "ALT-2026-004",
            "transaction_id": uuid.UUID("30000000-0000-0000-0000-000000000004"),
            "customer_id": uuid.UUID("10000000-0000-0000-0000-000000000004"),
            "priority": "High",
            "risk_score": 88,
            "status": "New",
            "owner_user_id": None,
            "triggered_at_utc": now - timedelta(hours=8)
        },
        {
            "alert_id": uuid.UUID("40000000-0000-0000-0000-000000000005"),
            "alert_ref": "ALT-2026-005",
            "transaction_id": uuid.UUID("30000000-0000-0000-0000-000000000005"),
            "customer_id": uuid.UUID("10000000-0000-0000-0000-000000000005"),
            "priority": "High",
            "risk_score": 82,
            "status": "Under Review",
            "owner_user_id": investigator2_id,
            "triggered_at_utc": now - timedelta(hours=12)
        },
        {
            "alert_id": uuid.UUID("40000000-0000-0000-0000-000000000006"),
            "alert_ref": "ALT-2026-006",
            "transaction_id": uuid.UUID("30000000-0000-0000-0000-000000000006"),
            "customer_id": uuid.UUID("10000000-0000-0000-0000-000000000001"),
            "priority": "Medium",
            "risk_score": 70,
            "status": "New",
            "owner_user_id": None,
            "triggered_at_utc": now - timedelta(hours=16)
        },
        {
            "alert_id": uuid.UUID("40000000-0000-0000-0000-000000000007"),
            "alert_ref": "ALT-2026-007",
            "transaction_id": uuid.UUID("30000000-0000-0000-0000-000000000007"),
            "customer_id": uuid.UUID("10000000-0000-0000-0000-000000000002"),
            "priority": "Low",
            "risk_score": 50,
            "status": "Resolved",
            "owner_user_id": investigator1_id,
            "triggered_at_utc": now - timedelta(hours=20)
        },
        {
            "alert_id": uuid.UUID("40000000-0000-0000-0000-000000000008"),
            "alert_ref": "ALT-2026-008",
            "transaction_id": uuid.UUID("30000000-0000-0000-0000-000000000008"),
            "customer_id": uuid.UUID("10000000-0000-0000-0000-000000000003"),
            "priority": "High",
            "risk_score": 85,
            "status": "New",
            "owner_user_id": None,
            "triggered_at_utc": now - timedelta(hours=24)
        },
        {
            "alert_id": uuid.UUID("40000000-0000-0000-0000-000000000009"),
            "alert_ref": "ALT-2026-009",
            "transaction_id": uuid.UUID("30000000-0000-0000-0000-000000000009"),
            "customer_id": uuid.UUID("10000000-0000-0000-0000-000000000004"),
            "priority": "Medium",
            "risk_score": 68,
            "status": "Escalated",
            "owner_user_id": investigator2_id,
            "triggered_at_utc": now - timedelta(hours=28)
        },
        {
            "alert_id": uuid.UUID("40000000-0000-0000-0000-000000000010"),
            "alert_ref": "ALT-2026-010",
            "transaction_id": uuid.UUID("30000000-0000-0000-0000-000000000010"),
            "customer_id": uuid.UUID("10000000-0000-0000-0000-000000000005"),
            "priority": "Critical",
            "risk_score": 90,
            "status": "Under Review",
            "owner_user_id": investigator1_id,
            "triggered_at_utc": now - timedelta(hours=32)
        }
    ]
    
    for alert_data in alerts_data:
        alert = Alert(**alert_data)
        db.add(alert)
    
    db.commit()
    print(f"Seeded {len(alerts_data)} alerts")


def seed_rule_snapshots(db: Session) -> None:
    """Seed rule evaluation snapshots for alerts.
    
    Creates 3-5 rule snapshots per alert with varied outcomes and versions.
    """
    # Check if rule snapshots already exist
    stmt = select(RuleEvaluationSnapshot).limit(1)
    existing = db.scalars(stmt).first()
    
    if existing:
        print("Rule snapshots already seeded, skipping...")
        return
    
    now = datetime.now(timezone.utc)
    
    # Helper to generate immutable hash
    def generate_hash(alert_id: str, rule_code: str, outcome: str, timestamp: str) -> str:
        content = f"{alert_id}:{rule_code}:{outcome}:{timestamp}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    snapshots_data = [
        # Alert 1: ALT-2026-001 (Critical, high-value offshore)
        {
            "snapshot_id": uuid.UUID("70000000-0000-0000-0000-000000000001"),
            "alert_id": uuid.UUID("40000000-0000-0000-0000-000000000001"),
            "rule_code": "AML-HIGH-VALUE-001",
            "rule_name": "High Value Transaction to Offshore Jurisdiction",
            "rule_version": "v3.2",
            "outcome": "MATCH",
            "condition_text": "Transaction amount >= $50,000 AND destination in [VG, KY, PA, BM]",
            "evaluated_from_utc": now - timedelta(hours=3),
            "evaluated_to_utc": now - timedelta(hours=2),
            "immutable_hash": generate_hash("40000000-0000-0000-0000-000000000001", "AML-HIGH-VALUE-001", "MATCH", str(now - timedelta(hours=2)))
        },
        {
            "snapshot_id": uuid.UUID("70000000-0000-0000-0000-000000000002"),
            "alert_id": uuid.UUID("40000000-0000-0000-0000-000000000001"),
            "rule_code": "AML-RAPID-MOVEMENT-001",
            "rule_name": "Rapid Movement of Funds",
            "rule_version": "v2.1",
            "outcome": "PASS",
            "condition_text": "Transaction count in 24h window > 5 with total > $100,000",
            "evaluated_from_utc": now - timedelta(hours=3),
            "evaluated_to_utc": now - timedelta(hours=2),
            "immutable_hash": generate_hash("40000000-0000-0000-0000-000000000001", "AML-RAPID-MOVEMENT-001", "PASS", str(now - timedelta(hours=2)))
        },
        {
            "snapshot_id": uuid.UUID("70000000-0000-0000-0000-000000000003"),
            "alert_id": uuid.UUID("40000000-0000-0000-0000-000000000001"),
            "rule_code": "AML-STRUCT-DETECT-001",
            "rule_name": "Structuring Detection",
            "rule_version": "v4.0",
            "outcome": "PASS",
            "condition_text": "Multiple transactions just below $10,000 threshold in 7-day period",
            "evaluated_from_utc": now - timedelta(hours=3),
            "evaluated_to_utc": now - timedelta(hours=2),
            "immutable_hash": generate_hash("40000000-0000-0000-0000-000000000001", "AML-STRUCT-DETECT-001", "PASS", str(now - timedelta(hours=2)))
        },
        # Alert 2: ALT-2026-002 (Critical, PEP to offshore)
        {
            "snapshot_id": uuid.UUID("70000000-0000-0000-0000-000000000004"),
            "alert_id": uuid.UUID("40000000-0000-0000-0000-000000000002"),
            "rule_code": "AML-PEP-OFFSHORE-001",
            "rule_name": "PEP Transaction to High-Risk Jurisdiction",
            "rule_version": "v3.2",
            "outcome": "MATCH",
            "condition_text": "Customer PEP_FLAG = TRUE AND destination in high-risk jurisdictions",
            "evaluated_from_utc": now - timedelta(hours=5),
            "evaluated_to_utc": now - timedelta(hours=4),
            "immutable_hash": generate_hash("40000000-0000-0000-0000-000000000002", "AML-PEP-OFFSHORE-001", "MATCH", str(now - timedelta(hours=4)))
        },
        {
            "snapshot_id": uuid.UUID("70000000-0000-0000-0000-000000000005"),
            "alert_id": uuid.UUID("40000000-0000-0000-0000-000000000002"),
            "rule_code": "AML-HIGH-VALUE-001",
            "rule_name": "High Value Transaction to Offshore Jurisdiction",
            "rule_version": "v3.2",
            "outcome": "MATCH",
            "condition_text": "Transaction amount >= $50,000 AND destination in [VG, KY, PA, BM]",
            "evaluated_from_utc": now - timedelta(hours=5),
            "evaluated_to_utc": now - timedelta(hours=4),
            "immutable_hash": generate_hash("40000000-0000-0000-0000-000000000002", "AML-HIGH-VALUE-001", "MATCH", str(now - timedelta(hours=4)))
        },
        {
            "snapshot_id": uuid.UUID("70000000-0000-0000-0000-000000000006"),
            "alert_id": uuid.UUID("40000000-0000-0000-0000-000000000002"),
            "rule_code": "AML-UNUSUAL-CURRENCY-001",
            "rule_name": "Unusual Currency for Customer Profile",
            "rule_version": "v2.5",
            "outcome": "PASS",
            "condition_text": "Transaction currency not in customer's typical currency set",
            "evaluated_from_utc": now - timedelta(hours=5),
            "evaluated_to_utc": now - timedelta(hours=4),
            "immutable_hash": generate_hash("40000000-0000-0000-0000-000000000002", "AML-UNUSUAL-CURRENCY-001", "PASS", str(now - timedelta(hours=4)))
        },
        {
            "snapshot_id": uuid.UUID("70000000-0000-0000-0000-000000000007"),
            "alert_id": uuid.UUID("40000000-0000-0000-0000-000000000002"),
            "rule_code": "AML-VELOCITY-SPIKE-001",
            "rule_name": "Transaction Velocity Spike",
            "rule_version": "v1.8",
            "outcome": "PASS",
            "condition_text": "Transaction velocity > 3x customer historical average",
            "evaluated_from_utc": now - timedelta(hours=5),
            "evaluated_to_utc": now - timedelta(hours=4),
            "immutable_hash": generate_hash("40000000-0000-0000-0000-000000000002", "AML-VELOCITY-SPIKE-001", "PASS", str(now - timedelta(hours=4)))
        },
        # Alert 3: ALT-2026-003 (Medium)
        {
            "snapshot_id": uuid.UUID("70000000-0000-0000-0000-000000000008"),
            "alert_id": uuid.UUID("40000000-0000-0000-0000-000000000003"),
            "rule_code": "AML-CROSS-BORDER-001",
            "rule_name": "Cross-Border Medium Value",
            "rule_version": "v2.1",
            "outcome": "MATCH",
            "condition_text": "Amount > $20,000 AND source_country != destination_country",
            "evaluated_from_utc": now - timedelta(hours=7),
            "evaluated_to_utc": now - timedelta(hours=6),
            "immutable_hash": generate_hash("40000000-0000-0000-0000-000000000003", "AML-CROSS-BORDER-001", "MATCH", str(now - timedelta(hours=6)))
        },
        {
            "snapshot_id": uuid.UUID("70000000-0000-0000-0000-000000000009"),
            "alert_id": uuid.UUID("40000000-0000-0000-0000-000000000003"),
            "rule_code": "AML-HIGH-VALUE-001",
            "rule_name": "High Value Transaction to Offshore Jurisdiction",
            "rule_version": "v3.2",
            "outcome": "PASS",
            "condition_text": "Transaction amount >= $50,000 AND destination in [VG, KY, PA, BM]",
            "evaluated_from_utc": now - timedelta(hours=7),
            "evaluated_to_utc": now - timedelta(hours=6),
            "immutable_hash": generate_hash("40000000-0000-0000-0000-000000000003", "AML-HIGH-VALUE-001", "PASS", str(now - timedelta(hours=6)))
        },
        {
            "snapshot_id": uuid.UUID("70000000-0000-0000-0000-000000000010"),
            "alert_id": uuid.UUID("40000000-0000-0000-0000-000000000003"),
            "rule_code": "AML-PEP-OFFSHORE-001",
            "rule_name": "PEP Transaction to High-Risk Jurisdiction",
            "rule_version": "v3.2",
            "outcome": "PASS",
            "condition_text": "Customer PEP_FLAG = TRUE AND destination in high-risk jurisdictions",
            "evaluated_from_utc": now - timedelta(hours=7),
            "evaluated_to_utc": now - timedelta(hours=6),
            "immutable_hash": generate_hash("40000000-0000-0000-0000-000000000003", "AML-PEP-OFFSHORE-001", "PASS", str(now - timedelta(hours=6)))
        },
        # Alert 4: ALT-2026-004 (High)
        {
            "snapshot_id": uuid.UUID("70000000-0000-0000-0000-000000000011"),
            "alert_id": uuid.UUID("40000000-0000-0000-0000-000000000004"),
            "rule_code": "AML-HIGH-VALUE-001",
            "rule_name": "High Value Transaction to Offshore Jurisdiction",
            "rule_version": "v3.2",
            "outcome": "MATCH",
            "condition_text": "Transaction amount >= $50,000 AND destination in [VG, KY, PA, BM]",
            "evaluated_from_utc": now - timedelta(hours=9),
            "evaluated_to_utc": now - timedelta(hours=8),
            "immutable_hash": generate_hash("40000000-0000-0000-0000-000000000004", "AML-HIGH-VALUE-001", "MATCH", str(now - timedelta(hours=8)))
        },
        {
            "snapshot_id": uuid.UUID("70000000-0000-0000-0000-000000000012"),
            "alert_id": uuid.UUID("40000000-0000-0000-0000-000000000004"),
            "rule_code": "AML-UNUSUAL-DEST-001",
            "rule_name": "Unusual Destination Country",
            "rule_version": "v2.3",
            "outcome": "MATCH",
            "condition_text": "Destination country not in customer's historical destinations",
            "evaluated_from_utc": now - timedelta(hours=9),
            "evaluated_to_utc": now - timedelta(hours=8),
            "immutable_hash": generate_hash("40000000-0000-0000-0000-000000000004", "AML-UNUSUAL-DEST-001", "MATCH", str(now - timedelta(hours=8)))
        },
        {
            "snapshot_id": uuid.UUID("70000000-0000-0000-0000-000000000013"),
            "alert_id": uuid.UUID("40000000-0000-0000-0000-000000000004"),
            "rule_code": "AML-PEP-OFFSHORE-001",
            "rule_name": "PEP Transaction to High-Risk Jurisdiction",
            "rule_version": "v3.2",
            "outcome": "PASS",
            "condition_text": "Customer PEP_FLAG = TRUE AND destination in high-risk jurisdictions",
            "evaluated_from_utc": now - timedelta(hours=9),
            "evaluated_to_utc": now - timedelta(hours=8),
            "immutable_hash": generate_hash("40000000-0000-0000-0000-000000000004", "AML-PEP-OFFSHORE-001", "PASS", str(now - timedelta(hours=8)))
        },
        # Alert 5: ALT-2026-005 (High, PEP)
        {
            "snapshot_id": uuid.UUID("70000000-0000-0000-0000-000000000014"),
            "alert_id": uuid.UUID("40000000-0000-0000-0000-000000000005"),
            "rule_code": "AML-PEP-OFFSHORE-001",
            "rule_name": "PEP Transaction to High-Risk Jurisdiction",
            "rule_version": "v3.2",
            "outcome": "MATCH",
            "condition_text": "Customer PEP_FLAG = TRUE AND destination in high-risk jurisdictions",
            "evaluated_from_utc": now - timedelta(hours=13),
            "evaluated_to_utc": now - timedelta(hours=12),
            "immutable_hash": generate_hash("40000000-0000-0000-0000-000000000005", "AML-PEP-OFFSHORE-001", "MATCH", str(now - timedelta(hours=12)))
        },
        {
            "snapshot_id": uuid.UUID("70000000-0000-0000-0000-000000000015"),
            "alert_id": uuid.UUID("40000000-0000-0000-0000-000000000005"),
            "rule_code": "AML-HIGH-VALUE-001",
            "rule_name": "High Value Transaction to Offshore Jurisdiction",
            "rule_version": "v3.2",
            "outcome": "MATCH",
            "condition_text": "Transaction amount >= $50,000 AND destination in [VG, KY, PA, BM]",
            "evaluated_from_utc": now - timedelta(hours=13),
            "evaluated_to_utc": now - timedelta(hours=12),
            "immutable_hash": generate_hash("40000000-0000-0000-0000-000000000005", "AML-HIGH-VALUE-001", "MATCH", str(now - timedelta(hours=12)))
        },
        {
            "snapshot_id": uuid.UUID("70000000-0000-0000-0000-000000000016"),
            "alert_id": uuid.UUID("40000000-0000-0000-0000-000000000005"),
            "rule_code": "AML-RAPID-MOVEMENT-001",
            "rule_name": "Rapid Movement of Funds",
            "rule_version": "v2.1",
            "outcome": "PASS",
            "condition_text": "Transaction count in 24h window > 5 with total > $100,000",
            "evaluated_from_utc": now - timedelta(hours=13),
            "evaluated_to_utc": now - timedelta(hours=12),
            "immutable_hash": generate_hash("40000000-0000-0000-0000-000000000005", "AML-RAPID-MOVEMENT-001", "PASS", str(now - timedelta(hours=12)))
        },
        {
            "snapshot_id": uuid.UUID("70000000-0000-0000-0000-000000000017"),
            "alert_id": uuid.UUID("40000000-0000-0000-0000-000000000005"),
            "rule_code": "AML-STRUCT-DETECT-001",
            "rule_name": "Structuring Detection",
            "rule_version": "v4.0",
            "outcome": "PASS",
            "condition_text": "Multiple transactions just below $10,000 threshold in 7-day period",
            "evaluated_from_utc": now - timedelta(hours=13),
            "evaluated_to_utc": now - timedelta(hours=12),
            "immutable_hash": generate_hash("40000000-0000-0000-0000-000000000005", "AML-STRUCT-DETECT-001", "PASS", str(now - timedelta(hours=12)))
        },
    ]
    
    for snapshot_data in snapshots_data:
        snapshot = RuleEvaluationSnapshot(**snapshot_data)
        db.add(snapshot)
    
    db.commit()
    print(f"Seeded {len(snapshots_data)} rule evaluation snapshots")


def seed_cases(db: Session) -> None:
    """Seed sample cases with alert links.
    
    Args:
        db: Database session
    """
    # Check if cases already exist
    stmt = select(AmlCase).limit(1)
    existing_case = db.scalars(stmt).first()
    
    if existing_case:
        print("Cases already seeded, skipping...")
        return
    
    now = datetime.now(timezone.utc)
    investigator1_id = uuid.UUID("00000000-0000-0000-0000-000000000001")
    investigator2_id = uuid.UUID("00000000-0000-0000-0000-000000000005")
    
    officer_id = uuid.UUID("00000000-0000-0000-0000-000000000002")
    
    # Sample cases
    cases_data = [
        {
            "case_id": uuid.UUID("50000000-0000-0000-0000-000000000001"),
            "case_ref": "CS-201",
            "primary_alert_id": uuid.UUID("40000000-0000-0000-0000-000000000001"),
            "created_by_user_id": investigator1_id,
            "assigned_officer_user_id": None,
            "status": "OPEN",
            "current_blocker_state": "NONE",
            "created_at_utc": now - timedelta(hours=6),
            "updated_at_utc": now - timedelta(hours=6)
        },
        {
            "case_id": uuid.UUID("50000000-0000-0000-0000-000000000002"),
            "case_ref": "CS-202",
            "primary_alert_id": uuid.UUID("40000000-0000-0000-0000-000000000002"),
            "created_by_user_id": investigator2_id,
            "assigned_officer_user_id": None,
            "status": "INVESTIGATING",
            "current_blocker_state": "NONE",
            "created_at_utc": now - timedelta(hours=12),
            "updated_at_utc": now - timedelta(hours=12)
        },
        {
            "case_id": uuid.UUID("50000000-0000-0000-0000-000000000003"),
            "case_ref": "CS-203",
            "primary_alert_id": uuid.UUID("40000000-0000-0000-0000-000000000003"),
            "created_by_user_id": investigator1_id,
            "assigned_officer_user_id": None,
            "status": "PENDING_INFORMATION",
            "current_blocker_state": "OPEN_REQUESTS",
            "created_at_utc": now - timedelta(days=1),
            "updated_at_utc": now - timedelta(hours=18)
        },
        # CS-204: Ready for officer decision (UNDER_REVIEW, assigned to officer, no blockers)
        {
            "case_id": uuid.UUID("50000000-0000-0000-0000-000000000004"),
            "case_ref": "CS-204",
            "primary_alert_id": uuid.UUID("40000000-0000-0000-0000-000000000004"),
            "created_by_user_id": investigator1_id,
            "assigned_officer_user_id": officer_id,
            "status": "UNDER_REVIEW",
            "current_blocker_state": "NONE",
            "created_at_utc": now - timedelta(days=2),
            "updated_at_utc": now - timedelta(hours=2)
        },
        # CS-205: Blocked by open request (for testing blocker enforcement)
        {
            "case_id": uuid.UUID("50000000-0000-0000-0000-000000000005"),
            "case_ref": "CS-205",
            "primary_alert_id": uuid.UUID("40000000-0000-0000-0000-000000000007"),
            "created_by_user_id": investigator2_id,
            "assigned_officer_user_id": officer_id,
            "status": "UNDER_REVIEW",
            "current_blocker_state": "OPEN_REQUESTS",
            "created_at_utc": now - timedelta(days=3),
            "updated_at_utc": now - timedelta(hours=4)
        }
    ]
    
    for case_data in cases_data:
        case = AmlCase(**case_data)
        db.add(case)
    
    db.commit()
    print(f"Seeded {len(cases_data)} cases")
    
    # Create primary alert links and secondary alert links
    links_data = [
        # Primary links
        {
            "case_alert_link_id": uuid.UUID("60000000-0000-0000-0000-000000000001"),
            "case_id": uuid.UUID("50000000-0000-0000-0000-000000000001"),
            "alert_id": uuid.UUID("40000000-0000-0000-0000-000000000001"),
            "is_primary": True,
            "linked_by_user_id": investigator1_id,
            "linked_at_utc": now - timedelta(hours=6)
        },
        {
            "case_alert_link_id": uuid.UUID("60000000-0000-0000-0000-000000000002"),
            "case_id": uuid.UUID("50000000-0000-0000-0000-000000000002"),
            "alert_id": uuid.UUID("40000000-0000-0000-0000-000000000002"),
            "is_primary": True,
            "linked_by_user_id": investigator2_id,
            "linked_at_utc": now - timedelta(hours=12)
        },
        {
            "case_alert_link_id": uuid.UUID("60000000-0000-0000-0000-000000000003"),
            "case_id": uuid.UUID("50000000-0000-0000-0000-000000000003"),
            "alert_id": uuid.UUID("40000000-0000-0000-0000-000000000003"),
            "is_primary": True,
            "linked_by_user_id": investigator1_id,
            "linked_at_utc": now - timedelta(days=1)
        },
        # Secondary links - 2 per case (one primary, one secondary)
        {
            "case_alert_link_id": uuid.UUID("60000000-0000-0000-0000-000000000004"),
            "case_id": uuid.UUID("50000000-0000-0000-0000-000000000001"),
            "alert_id": uuid.UUID("40000000-0000-0000-0000-000000000006"),
            "is_primary": False,
            "linked_by_user_id": investigator1_id,
            "linked_at_utc": now - timedelta(hours=5)
        },
        {
            "case_alert_link_id": uuid.UUID("60000000-0000-0000-0000-000000000005"),
            "case_id": uuid.UUID("50000000-0000-0000-0000-000000000002"),
            "alert_id": uuid.UUID("40000000-0000-0000-0000-000000000005"),
            "is_primary": False,
            "linked_by_user_id": investigator2_id,
            "linked_at_utc": now - timedelta(hours=10)
        },
        {
            "case_alert_link_id": uuid.UUID("60000000-0000-0000-0000-000000000006"),
            "case_id": uuid.UUID("50000000-0000-0000-0000-000000000003"),
            "alert_id": uuid.UUID("40000000-0000-0000-0000-000000000008"),
            "is_primary": False,
            "linked_by_user_id": investigator1_id,
            "linked_at_utc": now - timedelta(hours=20)
        },
        # CS-204 primary link (ready for officer decision)
        {
            "case_alert_link_id": uuid.UUID("60000000-0000-0000-0000-000000000007"),
            "case_id": uuid.UUID("50000000-0000-0000-0000-000000000004"),
            "alert_id": uuid.UUID("40000000-0000-0000-0000-000000000004"),
            "is_primary": True,
            "linked_by_user_id": investigator1_id,
            "linked_at_utc": now - timedelta(days=2)
        },
        # CS-205 primary link (blocked by open request)
        {
            "case_alert_link_id": uuid.UUID("60000000-0000-0000-0000-000000000008"),
            "case_id": uuid.UUID("50000000-0000-0000-0000-000000000005"),
            "alert_id": uuid.UUID("40000000-0000-0000-0000-000000000007"),
            "is_primary": True,
            "linked_by_user_id": investigator2_id,
            "linked_at_utc": now - timedelta(days=3)
        }
    ]
    
    for link_data in links_data:
        link = CaseAlertLink(**link_data)
        db.add(link)
    
    db.commit()
    print(f"Seeded {len(links_data)} case-alert links ({sum(1 for l in links_data if l['is_primary'])} primary, {sum(1 for l in links_data if not l['is_primary'])} secondary)")


def seed_case_notes(db: Session) -> None:
    """Seed case notes for investigation narrative.
    
    Args:
        db: Database session
    """
    # Check if notes already exist
    stmt = select(CaseNote).limit(1)
    existing_note = db.scalars(stmt).first()
    
    if existing_note:
        print("Case notes already seeded, skipping...")
        return
    
    now = datetime.now(timezone.utc)
    investigator1_id = uuid.UUID("00000000-0000-0000-0000-000000000001")
    investigator2_id = uuid.UUID("00000000-0000-0000-0000-000000000005")
    officer_id = uuid.UUID("00000000-0000-0000-0000-000000000002")
    
    # Sample notes for 3 cases (2-3 notes per case with different categories and authors)
    notes_data = [
        # Case CS-201 notes
        {
            "note_id": uuid.UUID("80000000-0000-0000-0000-000000000001"),
            "case_id": uuid.UUID("50000000-0000-0000-0000-000000000001"),
            "note_category": "investigation",
            "note_text": "Initial review of alert ALT-2026-001: High-value transaction ($95,000 USD) from GB to VG (offshore jurisdiction). Customer John Smith has no prior PEP flag. Transaction appears to be a one-off large payment. Need to verify business purpose and beneficiary details.",
            "author_user_id": investigator1_id,
            "authored_at_utc": now - timedelta(hours=5)
        },
        {
            "note_id": uuid.UUID("80000000-0000-0000-0000-000000000002"),
            "case_id": uuid.UUID("50000000-0000-0000-0000-000000000001"),
            "note_category": "information_request",
            "note_text": "Requested additional documentation from customer: Invoice or contract supporting this payment, Beneficiary company registration details, Business relationship documentation with recipient entity in VG.",
            "author_user_id": investigator1_id,
            "authored_at_utc": now - timedelta(hours=4)
        },
        {
            "note_id": uuid.UUID("80000000-0000-0000-0000-000000000003"),
            "case_id": uuid.UUID("50000000-0000-0000-0000-000000000001"),
            "note_category": "investigation",
            "note_text": "Customer provided invoice dated 2026-11-20 for consulting services rendered. Beneficiary is registered offshore advisory firm. Payment amount matches invoice. Transaction appears legitimate pending final compliance review.",
            "author_user_id": investigator1_id,
            "authored_at_utc": now - timedelta(hours=2)
        },
        
        # Case CS-202 notes
        {
            "note_id": uuid.UUID("80000000-0000-0000-0000-000000000004"),
            "case_id": uuid.UUID("50000000-0000-0000-0000-000000000002"),
            "note_category": "investigation",
            "note_text": "Alert ALT-2026-002 triggered on PEP customer Maria Garcia (Spain). Transaction amount EUR 150,000 to Panama. Customer is a politically exposed person with prior flag in system. High-risk jurisdiction destination raises additional concern.",
            "author_user_id": investigator2_id,
            "authored_at_utc": now - timedelta(hours=11)
        },
        {
            "note_id": uuid.UUID("80000000-0000-0000-0000-000000000005"),
            "case_id": uuid.UUID("50000000-0000-0000-0000-000000000002"),
            "note_category": "investigation",
            "note_text": "Reviewed customer transaction history over past 12 months. This is the largest single transaction to offshore jurisdiction. Customer has legitimate import/export business, but Panama entity is new counterparty. Enhanced due diligence recommended.",
            "author_user_id": investigator2_id,
            "authored_at_utc": now - timedelta(hours=9)
        },
        {
            "note_id": uuid.UUID("80000000-0000-0000-0000-000000000006"),
            "case_id": uuid.UUID("50000000-0000-0000-0000-000000000002"),
            "note_category": "recommendation",
            "note_text": "Recommend independent officer review before final disposition. PEP status + high-risk jurisdiction + large value warrants additional oversight. All supporting documentation has been collected and reviewed. Case ready for officer assignment.",
            "author_user_id": investigator2_id,
            "authored_at_utc": now - timedelta(hours=8)
        },
        
        # Case CS-203 notes
        {
            "note_id": uuid.UUID("80000000-0000-0000-0000-000000000007"),
            "case_id": uuid.UUID("50000000-0000-0000-0000-000000000003"),
            "note_category": "investigation",
            "note_text": "Alert ALT-2026-003: Cross-border transaction USD 25,000 from CN to US. Customer Zhang Wei, account ACC-CN-001. Medium risk score (65). Transaction appears routine for this customer profile.",
            "author_user_id": investigator1_id,
            "authored_at_utc": now - timedelta(hours=23)
        },
        {
            "note_id": uuid.UUID("80000000-0000-0000-0000-000000000008"),
            "case_id": uuid.UUID("50000000-0000-0000-0000-000000000003"),
            "note_category": "information_request",
            "note_text": "Open information request issued 2026-11-21: Requested beneficiary bank details and purpose of payment from customer. Due date: 2026-11-25. Status: Pending customer response.",
            "author_user_id": investigator1_id,
            "authored_at_utc": now - timedelta(hours=18)
        },
    ]
    
    for note_data in notes_data:
        note = CaseNote(**note_data)
        db.add(note)
    
    db.commit()
    print(f"Seeded {len(notes_data)} case notes")


def seed_evidence_gaps_and_requests(db: Session) -> None:
    """Seed evidence gaps and information requests for cases."""
    # Check if evidence gaps already exist
    stmt = select(EvidenceGap).limit(1)
    existing = db.scalars(stmt).first()
    
    if existing:
        print("Evidence gaps and requests already seeded, skipping...")
        return
    
    now = datetime.now(timezone.utc)
    
    # User IDs
    investigator1_id = uuid.UUID("00000000-0000-0000-0000-000000000001")
    investigator2_id = uuid.UUID("00000000-0000-0000-0000-000000000005")
    
    # Seed evidence gaps for each case
    evidence_gaps_data = [
        # CS-201: 1 OPEN gap
        {
            "gap_id": uuid.UUID("90000000-0000-0000-0000-000000000001"),
            "case_id": uuid.UUID("50000000-0000-0000-0000-000000000001"),
            "title": "Source of funds documentation",
            "description": "Missing documentation on the source of funds for the $95,000 transaction to British Virgin Islands.",
            "status": "OPEN",
            "created_by_user_id": investigator1_id,
            "created_at_utc": now - timedelta(days=2),
            "resolved_at_utc": None
        },
        # CS-202: 1 OPEN gap
        {
            "gap_id": uuid.UUID("90000000-0000-0000-0000-000000000002"),
            "case_id": uuid.UUID("50000000-0000-0000-0000-000000000002"),
            "title": "Beneficiary identity verification",
            "description": "Need to verify the identity and business relationship with the beneficiary in Panama.",
            "status": "OPEN",
            "created_by_user_id": investigator2_id,
            "created_at_utc": now - timedelta(days=1),
            "resolved_at_utc": None
        },
        # CS-203: 2 gaps (1 OPEN, 1 RESOLVED for context)
        {
            "gap_id": uuid.UUID("90000000-0000-0000-0000-000000000003"),
            "case_id": uuid.UUID("50000000-0000-0000-0000-000000000003"),
            "title": "Transaction purpose clarification",
            "description": "Customer needs to provide clear business justification for the payment structure.",
            "status": "OPEN",
            "created_by_user_id": investigator1_id,
            "created_at_utc": now - timedelta(days=3),
            "resolved_at_utc": None
        },
        {
            "gap_id": uuid.UUID("90000000-0000-0000-0000-000000000004"),
            "case_id": uuid.UUID("50000000-0000-0000-0000-000000000003"),
            "title": "Previous transaction history",
            "description": "Historical pattern analysis for the customer.",
            "status": "RESOLVED",
            "created_by_user_id": investigator1_id,
            "created_at_utc": now - timedelta(days=5),
            "resolved_at_utc": now - timedelta(days=4)
        },
        # CS-205: OPEN gap (for blocker testing)
        {
            "gap_id": uuid.UUID("90000000-0000-0000-0000-000000000005"),
            "case_id": uuid.UUID("50000000-0000-0000-0000-000000000005"),
            "title": "Enhanced due diligence documentation",
            "description": "Missing enhanced due diligence documentation for high-risk jurisdiction transaction.",
            "status": "OPEN",
            "created_by_user_id": investigator2_id,
            "created_at_utc": now - timedelta(days=2),
            "resolved_at_utc": None
        }
    ]
    
    for gap_data in evidence_gaps_data:
        gap = EvidenceGap(**gap_data)
        db.add(gap)
    
    db.commit()
    
    # Seed information requests (1 per case)
    information_requests_data = [
        # CS-201: OPEN request with future due date
        {
            "request_id": uuid.UUID("a0000000-0000-0000-0000-000000000001"),
            "request_ref": "IR-001",
            "case_id": uuid.UUID("50000000-0000-0000-0000-000000000001"),
            "gap_id": uuid.UUID("90000000-0000-0000-0000-000000000001"),
            "target_party": "Customer: John Smith",
            "delivery_channel": "Email",
            "reason_text": "Request source of funds documentation for the $95,000 offshore transaction. Need bank statements, invoices, or contracts supporting the transfer.",
            "due_at_utc": now + timedelta(days=3),
            "status": "OPEN",
            "created_by_user_id": investigator1_id,
            "response_summary": None,
            "response_received_at_utc": None,
            "created_at_utc": now - timedelta(days=2),
            "updated_at_utc": now - timedelta(days=2)
        },
        # CS-202: OVERDUE request (due date in past)
        {
            "request_id": uuid.UUID("a0000000-0000-0000-0000-000000000002"),
            "request_ref": "IR-002",
            "case_id": uuid.UUID("50000000-0000-0000-0000-000000000002"),
            "gap_id": uuid.UUID("90000000-0000-0000-0000-000000000002"),
            "target_party": "Compliance team",
            "delivery_channel": "Internal system",
            "reason_text": "Verify beneficiary identity and relationship through internal KYC database.",
            "due_at_utc": now - timedelta(days=1),
            "status": "OVERDUE",
            "created_by_user_id": investigator2_id,
            "response_summary": None,
            "response_received_at_utc": None,
            "created_at_utc": now - timedelta(days=2),
            "updated_at_utc": now - timedelta(days=2)
        },
        # CS-203: OPEN request with near-future due date
        {
            "request_id": uuid.UUID("a0000000-0000-0000-0000-000000000003"),
            "request_ref": "IR-003",
            "case_id": uuid.UUID("50000000-0000-0000-0000-000000000003"),
            "gap_id": uuid.UUID("90000000-0000-0000-0000-000000000003"),
            "target_party": "Customer operations team",
            "delivery_channel": "Phone call",
            "reason_text": "Follow up with customer to clarify business purpose and expected payment patterns.",
            "due_at_utc": now + timedelta(days=1),
            "status": "OPEN",
            "created_by_user_id": investigator1_id,
            "response_summary": None,
            "response_received_at_utc": None,
            "created_at_utc": now - timedelta(days=3),
            "updated_at_utc": now - timedelta(days=3)
        },
        # CS-205: OPEN request (for blocker testing - blocks officer decision)
        {
            "request_id": uuid.UUID("a0000000-0000-0000-0000-000000000004"),
            "request_ref": "IR-004",
            "case_id": uuid.UUID("50000000-0000-0000-0000-000000000005"),
            "gap_id": uuid.UUID("90000000-0000-0000-0000-000000000005"),
            "target_party": "Risk department",
            "delivery_channel": "Internal system",
            "reason_text": "Request enhanced due diligence package for jurisdiction with elevated risk profile.",
            "due_at_utc": now + timedelta(days=2),
            "status": "OPEN",
            "created_by_user_id": investigator2_id,
            "response_summary": None,
            "response_received_at_utc": None,
            "created_at_utc": now - timedelta(days=2),
            "updated_at_utc": now - timedelta(days=2)
        },
        # CS-204: RESPONDED request (response received, showcases response recording feature)
        {
            "request_id": uuid.UUID("a0000000-0000-0000-0000-000000000005"),
            "request_ref": "IR-005",
            "case_id": uuid.UUID("50000000-0000-0000-0000-000000000004"),
            "gap_id": uuid.UUID("90000000-0000-0000-0000-000000000001"),
            "target_party": "Customer operations",
            "delivery_channel": "Email",
            "reason_text": "Request additional supporting documentation for transaction justification and beneficiary relationship.",
            "due_at_utc": now + timedelta(days=5),
            "status": "RESPONDED",
            "created_by_user_id": investigator1_id,
            "response_summary": "Customer provided comprehensive documentation including signed contracts, invoices, and beneficiary company registration. All materials have been reviewed and appear legitimate. Business relationship is established and ongoing.",
            "response_received_at_utc": now - timedelta(hours=6),
            "created_at_utc": now - timedelta(days=4),
            "updated_at_utc": now - timedelta(hours=6)
        }
    ]
    
    for request_data in information_requests_data:
        request = InformationRequest(**request_data)
        db.add(request)
    
    db.commit()
    print(f"Seeded {len(evidence_gaps_data)} evidence gaps and {len(information_requests_data)} information requests")


def seed_officer_assignments_and_decisions(db: Session) -> None:
    """Seed officer assignments and completed decision for demonstration."""
    # Check if assignments already exist
    stmt = select(CaseReviewAssignment).limit(1)
    existing = db.scalars(stmt).first()
    
    if existing:
        print("Officer assignments and decisions already seeded, skipping...")
        return
    
    now = datetime.now(timezone.utc)
    
    # User IDs
    investigator1_id = uuid.UUID("00000000-0000-0000-0000-000000000001")
    officer_id = uuid.UUID("00000000-0000-0000-0000-000000000002")
    
    # Seed officer assignment for CS-204 (ready for decision)
    assignment_data = {
        "assignment_id": uuid.UUID("b0000000-0000-0000-0000-000000000001"),
        "case_id": uuid.UUID("50000000-0000-0000-0000-000000000004"),
        "officer_user_id": officer_id,
        "assigned_by_user_id": investigator1_id,
        "assigned_at_utc": now - timedelta(hours=3)
    }
    
    assignment = CaseReviewAssignment(**assignment_data)
    db.add(assignment)
    
    # Add one more case that's complete with a decision (CS-206)
    # First create the case
    case_complete = AmlCase(
        case_id=uuid.UUID("50000000-0000-0000-0000-000000000006"),
        case_ref="CS-206",
        primary_alert_id=uuid.UUID("40000000-0000-0000-0000-000000000005"),
        created_by_user_id=investigator1_id,
        assigned_officer_user_id=officer_id,
        status="APPROVED",
        current_blocker_state="NONE",
        created_at_utc=now - timedelta(days=4),
        updated_at_utc=now - timedelta(hours=1)
    )
    db.add(case_complete)
    
    # Create primary alert link for CS-206
    link_complete = CaseAlertLink(
        case_alert_link_id=uuid.UUID("60000000-0000-0000-0000-000000000009"),
        case_id=uuid.UUID("50000000-0000-0000-0000-000000000006"),
        alert_id=uuid.UUID("40000000-0000-0000-0000-000000000005"),
        is_primary=True,
        linked_by_user_id=investigator1_id,
        linked_at_utc=now - timedelta(days=4)
    )
    db.add(link_complete)
    
    # Create officer assignment for CS-206
    assignment_complete = CaseReviewAssignment(
        assignment_id=uuid.UUID("b0000000-0000-0000-0000-000000000002"),
        case_id=uuid.UUID("50000000-0000-0000-0000-000000000006"),
        officer_user_id=officer_id,
        assigned_by_user_id=investigator1_id,
        assigned_at_utc=now - timedelta(hours=24)
    )
    db.add(assignment_complete)
    
    # Create decision record for CS-206
    recorded_at = now - timedelta(hours=1)
    outcome = "APPROVE"
    rationale = "After comprehensive review of all supporting documentation, transaction history, and risk assessment, this case is approved. The transaction appears legitimate, all enhanced due diligence requirements have been met, and business relationship is well-documented. Customer has provided satisfactory evidence of source of funds and beneficiary relationship. Risk profile is acceptable within institutional risk appetite."
    
    # Compute immutable hash
    hash_input = f"{uuid.UUID('50000000-0000-0000-0000-000000000006')}|{outcome}|{rationale}|{recorded_at.isoformat()}"
    immutable_hash = hashlib.sha256(hash_input.encode()).hexdigest()
    
    decision = CaseDecision(
        decision_id=uuid.UUID("c0000000-0000-0000-0000-000000000001"),
        case_id=uuid.UUID("50000000-0000-0000-0000-000000000006"),
        deciding_officer_user_id=officer_id,
        outcome=outcome,
        rationale_text=rationale,
        recorded_at_utc=recorded_at,
        immutable_hash=immutable_hash
    )
    db.add(decision)
    
    db.commit()
    print(f"Seeded 2 officer assignments and 1 completed decision")


def seed_all() -> None:
    """Seed all data."""
    db = SessionLocal()
    try:
        print("Starting database seeding...")
        seed_users(db)
        seed_customers(db)
        seed_accounts(db)
        seed_transactions(db)
        seed_alerts(db)
        seed_rule_snapshots(db)
        seed_cases(db)
        seed_case_notes(db)
        seed_evidence_gaps_and_requests(db)
        seed_officer_assignments_and_decisions(db)
        print("\nDatabase seeding completed!")
        print("\nDefault credentials:")
        print("  Investigator: investigator@example.com / investigator123")
        print("  Officer:      officer@example.com / officer123")
        print("  Auditor:      auditor@example.com / auditor123")
        print("  Supervisor:   supervisor@example.com / supervisor123")
        print("\nSample alert IDs:")
        print("  ALT-2026-001 (Critical, 95): 40000000-0000-0000-0000-000000000001")
        print("  ALT-2026-002 (Critical, 92): 40000000-0000-0000-0000-000000000002")
        print("  ALT-2026-004 (High, 88):     40000000-0000-0000-0000-000000000004")
        print("\nSample case IDs:")
        print("  CS-201 (OPEN):                50000000-0000-0000-0000-000000000001")
        print("  CS-202 (INVESTIGATING):       50000000-0000-0000-0000-000000000002")
        print("  CS-203 (PENDING_INFORMATION): 50000000-0000-0000-0000-000000000003")
        print("\nRule snapshot examples:")
        print("  Each alert has 3-5 rule snapshots with MATCH/PASS outcomes")
        print("  Rule versions: v2.1, v2.3, v2.5, v3.2, v4.0")
        print("\nInformation requests:")
        print("  IR-001 (OPEN, future due):    a0000000-0000-0000-0000-000000000001")
        print("  IR-002 (OVERDUE):             a0000000-0000-0000-0000-000000000002")
        print("  IR-003 (OPEN, near due):      a0000000-0000-0000-0000-000000000003")
        print("  IR-005 (RESPONDED):           a0000000-0000-0000-0000-000000000005")
    finally:
        db.close()


if __name__ == "__main__":
    seed_all()
