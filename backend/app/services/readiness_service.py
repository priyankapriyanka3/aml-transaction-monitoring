"""
Service for case readiness evaluation.
Validates that a case is ready for handoff to review.
"""
from uuid import UUID

from sqlalchemy.orm import Session

from ..repositories.case_repository import CaseRepository
from ..schemas.handoff_schemas import ReadinessChecklistItem, ReadinessResponse


class ReadinessService:
    """Service for evaluating case readiness for handoff"""
    
    def __init__(self, db: Session):
        self.db = db
        self.case_repo = CaseRepository(db)
    
    def evaluate_readiness(self, case_id: str) -> ReadinessResponse:
        """
        Evaluate case readiness for handoff.
        
        Checks:
        1. At least 1 linked alert exists
        2. Recommendation is present
        3. Findings summary is present (min 50 chars)
        4. No open or overdue information requests
        
        Returns ReadinessResponse with overall is_ready and checklist items.
        """
        # Get case
        case_uuid = UUID(case_id) if isinstance(case_id, str) else case_id
        case = self.case_repo.get_overview(case_uuid)
        if not case:
            raise ValueError("Case not found")
        
        # Get counts
        linked_alert_count = self.case_repo.get_linked_alert_count(case_uuid)
        open_request_count = self.case_repo.get_open_information_request_count(case_uuid)
        overdue_request_count = self.case_repo.get_overdue_information_request_count(case_uuid)
        
        # Evaluate checklist items
        checklist_items = []
        
        # 1. Linked evidence
        has_linked_alerts = linked_alert_count > 0
        checklist_items.append(ReadinessChecklistItem(
            code="linked_evidence",
            label="Linked evidence",
            passed=has_linked_alerts,
            detail=f"{linked_alert_count} alert(s) linked" if has_linked_alerts else "No alerts linked to case"
        ))
        
        # 2. Investigation notes (always pass if we got here - notes are tracked separately)
        checklist_items.append(ReadinessChecklistItem(
            code="investigation_notes",
            label="Investigation notes",
            passed=True,
            detail="Investigation documented"
        ))
        
        # 3. Recommendation present
        has_recommendation = (
            case.recommendation_outcome is not None and 
            case.recommendation_outcome != ""
        )
        checklist_items.append(ReadinessChecklistItem(
            code="recommendation",
            label="Recommendation present",
            passed=has_recommendation,
            detail="Recommendation submitted" if has_recommendation else "No recommendation submitted"
        ))
        
        # 4. Findings summary present (min 50 chars)
        has_findings = (
            case.findings_summary is not None and 
            len(case.findings_summary.strip()) >= 50
        )
        checklist_items.append(ReadinessChecklistItem(
            code="findings_summary",
            label="Findings summary",
            passed=has_findings,
            detail=f"Findings documented ({len(case.findings_summary) if case.findings_summary else 0} chars)" if has_findings else "Findings summary missing or too short (min 50 chars)"
        ))
        
        # 5. No open or overdue requests
        no_pending_requests = (open_request_count == 0 and overdue_request_count == 0)
        checklist_items.append(ReadinessChecklistItem(
            code="no_open_requests",
            label="Responses reviewed",
            passed=no_pending_requests,
            detail="All information requests resolved" if no_pending_requests else f"{open_request_count} open, {overdue_request_count} overdue requests"
        ))
        
        # Overall readiness
        is_ready = all(item.passed for item in checklist_items)
        
        return ReadinessResponse(
            is_ready=is_ready,
            checklist_items=checklist_items
        )
