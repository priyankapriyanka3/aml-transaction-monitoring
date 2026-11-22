"""
Service for handoff package assembly and submission.
"""
from uuid import UUID

from sqlalchemy.orm import Session

from ..repositories.case_repository import CaseRepository
from ..repositories.information_request_repository import InformationRequestRepository
from ..repositories.user_repository import UserRepository
from ..schemas.handoff_schemas import (
    HandoffPackageResponse,
    InformationRequestSummary,
    LinkedAlertSummary,
)
from ..services.readiness_service import ReadinessService


class HandoffService:
    """Service for assembling and submitting handoff packages"""
    
    def __init__(self, db: Session):
        self.db = db
        self.case_repo = CaseRepository(db)
        self.ir_repo = InformationRequestRepository(db)
        self.user_repo = UserRepository(db)
        self.readiness_service = ReadinessService(db)
    
    def get_handoff_package(self, case_id: str) -> HandoffPackageResponse:
        """
        Assemble complete handoff package for preview.
        
        Includes:
        - Case details
        - Linked alerts summary
        - Key evidence summary
        - Information request summary
        - Unresolved issues
        - Readiness checklist
        """
        # Get case
        case_uuid = UUID(case_id) if isinstance(case_id, str) else case_id
        case = self.case_repo.get_overview(case_uuid)
        if not case:
            raise ValueError("Case not found")
        
        # Get readiness evaluation
        readiness = self.readiness_service.evaluate_readiness(case_id)
        
        # Get linked alerts
        from ..models.case_alert_link import CaseAlertLink
        
        links = self.db.query(CaseAlertLink).filter(
            CaseAlertLink.case_id == case_uuid
        ).all()
        
        linked_alerts = []
        for link in links:
            from ..models.alert import Alert
            
            alert = self.db.query(Alert).filter(Alert.alert_id == link.alert_id).first()
            if alert:
                linked_alerts.append(LinkedAlertSummary(
                    alert_id=str(alert.alert_id),
                    priority=alert.priority,
                    risk_score=alert.risk_score
                ))
        
        # Get information requests
        information_requests = self.ir_repo.list_by_case(case_uuid)
        ir_summary = []
        for ir in information_requests:
            ir_summary.append(InformationRequestSummary(
                information_request_id=ir.information_request_id,
                status=ir.status,
                due_at=ir.due_at.isoformat(),
                resolved_at=ir.response_received_at.isoformat() if ir.response_received_at else None
            ))
        
        # Key evidence summary (simplified - in production would aggregate from evidence package)
        key_evidence_summary = [
            f"{len(linked_alerts)} alert(s) investigated",
            f"Risk score range: {min([a.risk_score for a in linked_alerts])} - {max([a.risk_score for a in linked_alerts])}" if linked_alerts else "No alerts"
        ]
        
        # Unresolved issues
        unresolved_issues = []
        open_count = self.case_repo.get_open_information_request_count(case_uuid)
        overdue_count = self.case_repo.get_overdue_information_request_count(case_uuid)
        
        if open_count > 0:
            unresolved_issues.append(f"{open_count} open information request(s)")
        if overdue_count > 0:
            unresolved_issues.append(f"{overdue_count} overdue information request(s)")
        if not case.recommendation_outcome:
            unresolved_issues.append("No recommendation submitted")
        if not case.findings_summary or len(case.findings_summary.strip()) < 50:
            unresolved_issues.append("Findings summary incomplete")
        
        # Officer assignment (if already assigned)
        officer_assignment = None
        if case.handoff_officer_user_id:
            officer = self.user_repo.get_by_id(case.handoff_officer_user_id)
            if officer:
                officer_assignment = {
                    "officer_user_id": str(officer.user_id),
                    "officer_display_name": officer.display_name
                }
        
        return HandoffPackageResponse(
            case_id=str(case.case_id),
            case_number=case.case_number,
            recommendation_outcome=case.recommendation_outcome,
            findings_summary=case.findings_summary,
            linked_alerts=linked_alerts,
            key_evidence_summary=key_evidence_summary,
            information_request_summary=ir_summary,
            unresolved_issues=unresolved_issues,
            readiness=readiness,
            officer_assignment=officer_assignment
        )
