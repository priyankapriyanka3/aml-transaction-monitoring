"""
Repository for case operations.
Handles case creation, overview retrieval, and aggregations.
"""
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import func
from sqlalchemy.orm import Session

from ..models.alert import Alert
from ..models.aml_case import AMLCase
from ..models.audit_event import AuditEvent
from ..models.case_alert_link import CaseAlertLink
from ..models.information_request import InformationRequest


class CaseRepository:
    """Repository for case data operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_from_alert(
        self,
        case_number: str,
        source_alert: Alert,
        actor_id: UUID | str,
        priority: str,
        initial_rationale: str
    ) -> AMLCase:
        """
        Create a new case from an alert.
        Sets initial status to INVESTIGATING, assigns to actor.
        """
        now = datetime.now(timezone.utc)
        actor_uuid = UUID(actor_id) if isinstance(actor_id, str) else actor_id
        
        case = AMLCase(
            case_id=uuid4(),
            case_number=case_number,
            source_alert_id=source_alert.alert_id,
            customer_id=source_alert.customer_id,
            status="INVESTIGATING",
            priority=priority,
            assigned_user_id=actor_uuid,
            recommendation_state="DRAFT",
            recommendation_outcome=None,
            findings_summary=None,
            flagged_value_total=Decimal("0.00"),
            evidence_locked_for_review=False,
            created_by_user_id=actor_uuid,
            handoff_officer_user_id=None,
            created_at=now,
            updated_at=now
        )
        
        self.db.add(case)
        self.db.flush()  # Get case_id for linking
        
        return case
    
    def get_by_number(self, case_number: str) -> AMLCase | None:
        """
        Get case by case number (e.g., 'CS-001').
        """
        return self.db.query(AMLCase).filter(AMLCase.case_number == case_number).first()
    
    def get_overview(self, case_id: UUID | str) -> AMLCase | None:
        """
        Get case by ID.
        Does not include aggregations - those are computed by service layer.
        """
        case_uuid = UUID(case_id) if isinstance(case_id, str) else case_id
        return self.db.query(AMLCase).filter(AMLCase.case_id == case_uuid).first()
    
    def get_linked_alert_count(self, case_id: UUID | str) -> int:
        """Count of alerts linked to this case"""
        case_uuid = UUID(case_id) if isinstance(case_id, str) else case_id
        return self.db.query(CaseAlertLink).filter(
            CaseAlertLink.case_id == case_uuid
        ).count()
    
    def get_flagged_value_total(self, case_id: UUID | str) -> Decimal:
        """
        Sum of transaction amounts from linked alerts.
        Returns Decimal for precision.
        """
        from sqlalchemy import select

        from ..models.transaction import Transaction
        
        case_uuid = UUID(case_id) if isinstance(case_id, str) else case_id
        # Get all alert IDs linked to this case
        alert_ids = select(CaseAlertLink.alert_id).where(
            CaseAlertLink.case_id == case_uuid
        ).subquery()
        
        # Get transaction IDs from those alerts
        transaction_ids = select(Alert.transaction_id).where(
            Alert.alert_id.in_(select(alert_ids.c.alert_id))
        ).subquery()
        
        # Sum transaction amounts
        result = self.db.query(
            func.coalesce(func.sum(Transaction.amount), 0)
        ).filter(
            Transaction.transaction_id.in_(select(transaction_ids.c.transaction_id))
        ).scalar()
        
        return Decimal(str(result))
    
    def get_open_information_request_count(self, case_id: UUID | str) -> int:
        """Count of open information requests for this case"""
        case_uuid = UUID(case_id) if isinstance(case_id, str) else case_id
        return self.db.query(InformationRequest).filter(
            InformationRequest.case_id == case_uuid,
            InformationRequest.status == "OPEN"
        ).count()
    
    def get_overdue_information_request_count(self, case_id: UUID | str) -> int:
        """
        Count of overdue information requests.
        Overdue means due_at < now and status is still OPEN.
        """
        case_uuid = UUID(case_id) if isinstance(case_id, str) else case_id
        now = datetime.now(timezone.utc)
        return self.db.query(InformationRequest).filter(
            InformationRequest.case_id == case_uuid,
            InformationRequest.status == "OPEN",
            InformationRequest.due_at < now
        ).count()
    
    def get_recent_activity(self, case_id: UUID | str, limit: int = 10) -> list[AuditEvent]:
        """
        Get recent audit events for this case.
        Returns most recent events first.
        """
        case_id_str = str(case_id)  # AuditEvent stores entity_id as string
        return self.db.query(AuditEvent).filter(
            AuditEvent.entity_type == "case",
            AuditEvent.entity_id == case_id_str
        ).order_by(AuditEvent.occurred_at.desc()).limit(limit).all()
    
    def transition_status(self, case: AMLCase, new_status: str, actor_id: str) -> AMLCase:
        """
        Transition case to new status.
        Updates case status and updated_at timestamp.
        Does not validate state machine - that's done by service layer.
        """
        case.status = new_status
        case.updated_at = datetime.now(timezone.utc)
        self.db.add(case)
        self.db.flush()
        return case
    
    def save_recommendation(
        self,
        case: AMLCase,
        recommendation_outcome: str,
        findings_summary: str,
        actor_id: str
    ) -> AMLCase:
        """
        Save recommendation to case.
        Updates recommendation_state to SUBMITTED, sets outcome and findings.
        Does not validate readiness - that's done by service layer.
        """
        now = datetime.now(timezone.utc)
        case.recommendation_state = "SUBMITTED"
        case.recommendation_outcome = recommendation_outcome
        case.findings_summary = findings_summary
        case.updated_at = now
        self.db.add(case)
        self.db.flush()
        return case
