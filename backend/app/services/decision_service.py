"""Decision service for officer assignment and decision recording."""
import uuid
import hashlib
import json
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.repositories.decision_repository import DecisionRepository
from app.repositories.readiness_repository import ReadinessRepository
from app.repositories.case_repository import CaseRepository
from app.models.audit_event import AuditEvent
from app.schemas.decision_schemas import (
    AssignOfficerResponse,
    ShareForReviewResponse,
    DecisionResponse,
    OfficerReviewPackage,
    OfficerReviewLinkedAlert,
    OfficerReviewNote,
    OfficerReviewRuleSnapshot
)


class DecisionService:
    """Service for officer assignment and decision recording."""
    
    def __init__(self, db: Session):
        self.db = db
        self.decision_repo = DecisionRepository(db)
        self.readiness_repo = ReadinessRepository(db)
        self.case_repo = CaseRepository(db)
    
    def assign_officer(
        self,
        case_id: uuid.UUID,
        officer_user_id: uuid.UUID,
        assigned_by_user_id: uuid.UUID,
        assigned_by_role: str,
        correlation_id: str
    ) -> AssignOfficerResponse:
        """Assign an independent officer to a case.
        
        Validates officer != case creator (four-eyes enforcement).
        
        Args:
            case_id: Case ID
            officer_user_id: Officer user ID
            assigned_by_user_id: User ID of assigner
            assigned_by_role: Role of assigner
            correlation_id: Correlation ID
        
        Returns:
            AssignOfficerResponse
        
        Raises:
            ValueError: If case not found or validation fails
        """
        # Verify case exists
        case = self.case_repo.get_by_id(case_id)
        if not case:
            raise ValueError(f"Case {case_id} not found")
        
        # Validate officer != case creator
        if officer_user_id == case.created_by_user_id:
            raise ValueError("Officer cannot be the case creator (four-eyes violation)")
        
        # Create or update assignment
        assignment = self.decision_repo.assign_officer(
            case_id=case_id,
            officer_user_id=officer_user_id,
            assigned_by_user_id=assigned_by_user_id
        )
        
        # Update case.assigned_officer_user_id
        self.decision_repo.update_case_officer(case_id, officer_user_id)
        
        # Create audit event
        audit_event = AuditEvent(
            entity_type="CASE",
            entity_id=case_id,
            action_type="OFFICER_ASSIGNED",
            actor_user_id=assigned_by_user_id,
            actor_role=assigned_by_role,
            correlation_id=correlation_id,
            details_json=json.dumps({
                "case_id": str(case_id),
                "officer_user_id": str(officer_user_id),
                "assigned_by_user_id": str(assigned_by_user_id)
            })
        )
        self.db.add(audit_event)
        self.db.commit()
        
        return AssignOfficerResponse(
            assignment_id=assignment.assignment_id,
            case_id=assignment.case_id,
            officer_user_id=assignment.officer_user_id,
            assigned_by_user_id=assignment.assigned_by_user_id,
            assigned_at_utc=assignment.assigned_at_utc
        )
    
    def share_for_review(
        self,
        case_id: uuid.UUID,
        actor_user_id: uuid.UUID,
        actor_role: str,
        correlation_id: str
    ) -> ShareForReviewResponse:
        """Transition case to UNDER_REVIEW after validation.
        
        Validates:
        - All checklist items complete
        - No open/overdue requests
        - Officer assigned
        - Officer != case creator
        
        Args:
            case_id: Case ID
            actor_user_id: Actor user ID
            actor_role: Actor role
            correlation_id: Correlation ID
        
        Returns:
            ShareForReviewResponse
        
        Raises:
            ValueError: If case not found or validation fails
        """
        # Verify case exists
        case = self.case_repo.get_by_id(case_id)
        if not case:
            raise ValueError(f"Case {case_id} not found")
        
        # Get checklist state
        checklist_state = self.readiness_repo.get_checklist_state(case_id)
        
        # Validate all checklist items complete
        if checklist_state["linked_alert_count"] < 1:
            raise ValueError("Cannot share for review: No linked alerts")
        
        if checklist_state["note_count"] < 1:
            raise ValueError("Cannot share for review: No investigation notes")
        
        if checklist_state["open_request_count"] > 0:
            raise ValueError("Cannot share for review: Open information requests remain")
        
        if checklist_state["overdue_request_count"] > 0:
            raise ValueError("Cannot share for review: Overdue information requests remain")
        
        # Validate officer assigned
        if not case.assigned_officer_user_id:
            raise ValueError("Cannot share for review: No officer assigned")
        
        # Validate officer != case creator
        if case.assigned_officer_user_id == case.created_by_user_id:
            raise ValueError("Cannot share for review: Officer cannot be case creator")
        
        # Update case status to UNDER_REVIEW
        self.decision_repo.update_case_status(case_id, "UNDER_REVIEW")
        
        # Create audit event
        shared_at_utc = datetime.now(timezone.utc)
        audit_event = AuditEvent(
            entity_type="CASE",
            entity_id=case_id,
            action_type="SHARED_FOR_REVIEW",
            actor_user_id=actor_user_id,
            actor_role=actor_role,
            correlation_id=correlation_id,
            details_json=json.dumps({
                "case_id": str(case_id),
                "status": "UNDER_REVIEW",
                "shared_at_utc": shared_at_utc.isoformat()
            })
        )
        self.db.add(audit_event)
        self.db.commit()
        
        return ShareForReviewResponse(
            case_id=case_id,
            status="UNDER_REVIEW",
            shared_at_utc=shared_at_utc
        )
    
    def record_decision(
        self,
        case_id: uuid.UUID,
        deciding_officer_user_id: uuid.UUID,
        deciding_officer_role: str,
        outcome: str,
        rationale_text: str,
        correlation_id: str
    ) -> DecisionResponse:
        """Record an immutable final decision.
        
        Validates:
        - Current user != case creator
        - No open/overdue requests
        - Rationale not empty
        
        Args:
            case_id: Case ID
            deciding_officer_user_id: Officer user ID
            deciding_officer_role: Officer role
            outcome: Decision outcome
            rationale_text: Rationale text
            correlation_id: Correlation ID
        
        Returns:
            DecisionResponse
        
        Raises:
            ValueError: If case not found or validation fails
        """
        # Verify case exists
        case = self.case_repo.get_by_id(case_id)
        if not case:
            raise ValueError(f"Case {case_id} not found")
        
        # Validate officer != case creator
        if deciding_officer_user_id == case.created_by_user_id:
            raise ValueError("Officer cannot decide own case (four-eyes violation)")
        
        # Validate no open/overdue requests
        blocker_state = self.readiness_repo.derive_blocker_state(case_id)
        if blocker_state != "NONE":
            # Convert blocker state to human-readable message
            if blocker_state == "OPEN_REQUESTS":
                raise ValueError("Cannot record decision: open requests remain")
            elif blocker_state == "OVERDUE_REQUESTS":
                raise ValueError("Cannot record decision: overdue requests remain")
            else:
                raise ValueError(f"Cannot record decision: {blocker_state}")
        
        # Validate rationale not empty
        if not rationale_text or not rationale_text.strip():
            raise ValueError("Rationale text is required")
        
        # Compute immutable hash
        recorded_at_utc = datetime.now(timezone.utc)
        hash_input = f"{case_id}|{outcome}|{rationale_text}|{recorded_at_utc.isoformat()}"
        immutable_hash = hashlib.sha256(hash_input.encode()).hexdigest()
        
        # Create decision record
        decision = self.decision_repo.create_decision(
            case_id=case_id,
            deciding_officer_user_id=deciding_officer_user_id,
            outcome=outcome,
            rationale_text=rationale_text,
            immutable_hash=immutable_hash
        )
        
        # Map outcome to case status
        outcome_to_status = {
            "APPROVE": "APPROVED",
            "REJECT": "REJECTED",
            "ESCALATE": "ESCALATED",
            "FALSE_POSITIVE": "FALSE_POSITIVE",
            "RETURN_FOR_INVESTIGATION": "RETURNED_FOR_INVESTIGATION"
        }
        new_status = outcome_to_status.get(outcome, "UNDER_REVIEW")
        
        # Update case status
        self.decision_repo.update_case_status(case_id, new_status)
        
        # Create audit event
        audit_event = AuditEvent(
            entity_type="CASE",
            entity_id=case_id,
            action_type="DECISION_RECORDED",
            actor_user_id=deciding_officer_user_id,
            actor_role=deciding_officer_role,
            correlation_id=correlation_id,
            details_json=json.dumps({
                "case_id": str(case_id),
                "decision_id": str(decision.decision_id),
                "outcome": outcome,
                "recorded_at_utc": recorded_at_utc.isoformat()
            })
        )
        self.db.add(audit_event)
        self.db.commit()
        
        return DecisionResponse(
            decision_id=decision.decision_id,
            case_id=decision.case_id,
            deciding_officer_user_id=decision.deciding_officer_user_id,
            outcome=decision.outcome,
            rationale_text=decision.rationale_text,
            recorded_at_utc=decision.recorded_at_utc,
            immutable_hash=decision.immutable_hash
        )
    
    def get_officer_review_package(
        self,
        case_id: uuid.UUID,
        current_user_id: uuid.UUID
    ) -> OfficerReviewPackage:
        """Get officer review package for a case.
        
        Validates current user != case creator.
        
        Args:
            case_id: Case ID
            current_user_id: Current user ID
        
        Returns:
            OfficerReviewPackage
        
        Raises:
            ValueError: If case not found or user is case creator
        """
        # Verify case exists
        case = self.case_repo.get_by_id(case_id)
        if not case:
            raise ValueError(f"Case {case_id} not found")
        
        # Validate current user != case creator
        if current_user_id == case.created_by_user_id:
            raise ValueError("Case creator cannot review own case")
        
        # Get blocker state
        blocker_state = self.readiness_repo.derive_blocker_state(case_id)
        
        # Check if current user is conflicted
        is_conflicted = self.readiness_repo.check_conflicted_officer(case_id, current_user_id)
        
        # Get linked alerts
        from app.models.case_alert_link import CaseAlertLink
        from app.models.alert import Alert
        links = self.db.query(CaseAlertLink).filter(
            CaseAlertLink.case_id == case_id
        ).all()
        
        # Get alert details
        alert_ids = [link.alert_id for link in links]
        alerts_dict = {}
        if alert_ids:
            alerts = self.db.query(Alert).filter(Alert.alert_id.in_(alert_ids)).all()
            alerts_dict = {alert.alert_id: alert for alert in alerts}
        
        linked_alerts = [
            OfficerReviewLinkedAlert(
                alert_id=link.alert_id,
                alert_ref=alerts_dict[link.alert_id].alert_ref if link.alert_id in alerts_dict else f"ALT-{link.alert_id}",
                is_primary=link.is_primary
            )
            for link in links
        ]
        
        # Get notes
        from app.models.case_note import CaseNote
        notes_models = self.db.query(CaseNote).filter(
            CaseNote.case_id == case_id
        ).order_by(CaseNote.authored_at_utc.desc()).all()
        
        notes = [
            OfficerReviewNote(
                note_id=note.note_id,
                note_text=note.note_text,
                author_user_id=note.author_user_id,
                authored_at_utc=note.authored_at_utc
            )
            for note in notes_models
        ]
        
        # Get rule snapshots for linked alerts
        from app.models.rule_snapshot import RuleEvaluationSnapshot
        alert_ids = [link.alert_id for link in links]
        snapshots_models = self.db.query(RuleEvaluationSnapshot).filter(
            RuleEvaluationSnapshot.alert_id.in_(alert_ids)
        ).all() if alert_ids else []
        
        rule_snapshots = [
            OfficerReviewRuleSnapshot(
                snapshot_id=snapshot.snapshot_id,
                rule_name=snapshot.rule_name,
                rule_version=snapshot.rule_version,
                outcome=snapshot.outcome
            )
            for snapshot in snapshots_models
        ]
        
        return OfficerReviewPackage(
            case_id=case.case_id,
            case_ref=case.case_ref,
            status=case.status,
            blocker_state=blocker_state,
            is_conflicted_officer=is_conflicted,
            linked_alerts=linked_alerts,
            notes=notes,
            rule_snapshots=rule_snapshots
        )
