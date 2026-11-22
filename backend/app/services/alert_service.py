from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from ..repositories.alert_repository import AlertRepository
from ..repositories.user_repository import UserRepository
from ..schemas.alert_schemas import AlertResponse
from ..services.audit_service import AuditService


class AlertService:
    """Service for alert queue and assignment operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.alert_repo = AlertRepository(db)
        self.user_repo = UserRepository(db)
        self.audit_service = AuditService(db)
    
    def get_queue(
        self,
        status: str | None = None,
        priority: str | None = None,
        assignee_id: str | None = None,
        risk_score_min: int | None = None,
        risk_score_max: int | None = None,
        generation: str | None = None,
        search: str | None = None,
        sort_by: str = "priority",
        sort_direction: str = "desc",
        limit: int = 20,
        offset: int = 0
    ) -> tuple[list[AlertResponse], int]:
        """
        Get paginated alert queue with filters and enrichment.
        Returns (enriched_alerts, total_count)
        """
        assignee_uuid = None
        if assignee_id:
            assignee_uuid = UUID(assignee_id) if isinstance(assignee_id, str) else assignee_id
        
        alerts, total_count = self.alert_repo.list_queue(
            status=status,
            priority=priority,
            assignee_id=assignee_uuid,
            risk_score_min=risk_score_min,
            risk_score_max=risk_score_max,
            generation=generation,
            search=search,
            sort_by=sort_by,
            sort_direction=sort_direction,
            limit=limit,
            offset=offset
        )
        
        # Enrich alerts with customer, transaction, and user data
        enriched: list[AlertResponse] = []
        for alert in alerts:
            alert_dict: dict[str, object] = {
                "alert_id": str(alert.alert_id),
                "transaction_id": str(alert.transaction_id),
                "customer_id": str(alert.customer_id),
                "status": alert.status,
                "priority": alert.priority,
                "risk_score": alert.risk_score,
                "matched_rule_codes_json": alert.matched_rule_codes_json,
                "generation": alert.generation,
                "assigned_user_id": str(alert.assigned_user_id) if alert.assigned_user_id else None,
                "triage_outcome": alert.triage_outcome,
                "triage_rationale": alert.triage_rationale,
                "triaged_by_user_id": str(alert.triaged_by_user_id) if alert.triaged_by_user_id else None,
                "triaged_at": alert.triaged_at,
                "created_at": alert.created_at,
                "updated_at": alert.updated_at
            }
            
            # Add customer name
            customer = self.alert_repo.get_customer_by_id(alert.customer_id)
            if customer:
                alert_dict["customer_name"] = customer.customer_name
            
            # Add transaction amount and currency
            transaction = self.alert_repo.get_transaction_by_id(alert.transaction_id)
            if transaction:
                alert_dict["transaction_amount"] = float(transaction.amount)
                alert_dict["transaction_currency"] = transaction.currency
            
            # Add assigned user name
            if alert.assigned_user_id:
                user = self.alert_repo.get_user_by_id(alert.assigned_user_id)
                if user:
                    alert_dict["assigned_user_name"] = user.display_name
            
            enriched.append(AlertResponse(**alert_dict))  # type: ignore[arg-type]
        
        return enriched, total_count
    
    def claim_alert(
        self,
        alert_id: str,
        assignee_user_id: str,
        assigned_by_user_id: str,
        assignment_reason: str | None = None
    ) -> tuple[AlertResponse, str]:
        """
        Claim or reassign an alert.
        Returns (enriched_alert_response, assigned_user_name)
        """
        # Get alert
        alert_uuid = UUID(alert_id) if isinstance(alert_id, str) else alert_id
        alert = self.alert_repo.get_by_id(alert_uuid)
        if not alert:
            raise ValueError("Alert not found")
        
        # Validate assignee exists
        assignee_uuid = UUID(assignee_user_id) if isinstance(assignee_user_id, str) else assignee_user_id
        assignee = self.user_repo.get_by_id(assignee_uuid)
        if not assignee or not assignee.is_active:
            raise ValueError("Assignee user not found or inactive")
        
        # Get assigning user for role
        assigned_by_uuid = UUID(assigned_by_user_id) if isinstance(assigned_by_user_id, str) else assigned_by_user_id
        assigning_user = self.user_repo.get_by_id(assigned_by_uuid)
        if not assigning_user:
            raise ValueError("Assigning user not found")
        
        # Update alert
        alert = self.alert_repo.claim(alert, assignee_uuid, assigned_by_uuid)
        
        # Create audit event
        self.audit_service.create_event(
            entity_type="alert",
            entity_id=alert_id,
            action_type="ALERT_ASSIGNED",
            actor_user_id=assigned_by_uuid,
            actor_role=assigning_user.primary_role,
            payload={
                "assignee_user_id": assignee_user_id,
                "assignee_username": assignee.username,
                "assignment_reason": assignment_reason,
                "assigned_at": datetime.now(timezone.utc).isoformat()
            }
        )
        
        # Build enriched response
        alert_dict: dict[str, object] = {
            "alert_id": str(alert.alert_id),
            "transaction_id": str(alert.transaction_id),
            "customer_id": str(alert.customer_id),
            "status": alert.status,
            "priority": alert.priority,
            "risk_score": alert.risk_score,
            "matched_rule_codes_json": alert.matched_rule_codes_json,
            "generation": alert.generation,
            "assigned_user_id": str(alert.assigned_user_id),
            "triage_outcome": alert.triage_outcome,
            "triage_rationale": alert.triage_rationale,
            "triaged_by_user_id": str(alert.triaged_by_user_id),
            "triaged_at": alert.triaged_at,
            "created_at": alert.created_at,
            "updated_at": alert.updated_at,
            "assigned_user_name": assignee.display_name
        }
        
        return AlertResponse(**alert_dict), assignee.display_name  # type: ignore[arg-type]
    
    def save_triage_disposition(
        self,
        alert_id: str,
        outcome: str,
        rationale: str,
        actor_id: str,
        existing_case_id: str | None = None
    ) -> AlertResponse:
        """
        Save triage disposition with validation.
        
        Validates:
        - Rationale is not blank and has minimum 10 characters
        - Outcome is valid (INVESTIGATE, CLOSE_NON_ACTIONABLE, MERGE_EXISTING_CASE)
        - existing_case_id is provided when outcome is MERGE_EXISTING_CASE
        
        Creates ALERT_TRIAGE_RECORDED audit event.
        Updates alert status based on outcome.
        """
        # Validate rationale
        if not rationale or len(rationale.strip()) < 10:
            raise ValueError("Rationale must be at least 10 characters")
        
        # Validate outcome
        valid_outcomes = ["INVESTIGATE", "CLOSE_NON_ACTIONABLE", "MERGE_EXISTING_CASE"]
        if outcome not in valid_outcomes:
            raise ValueError(f"Invalid outcome. Must be one of: {', '.join(valid_outcomes)}")
        
        # Validate existing_case_id for MERGE_EXISTING_CASE
        if outcome == "MERGE_EXISTING_CASE" and not existing_case_id:
            raise ValueError("existing_case_id is required when outcome is MERGE_EXISTING_CASE")
        
        # Get alert
        alert_uuid = UUID(alert_id) if isinstance(alert_id, str) else alert_id
        alert = self.alert_repo.get_by_id(alert_uuid)
        if not alert:
            raise ValueError("Alert not found")
        
        # Get actor for role
        actor_uuid = UUID(actor_id) if isinstance(actor_id, str) else actor_id
        actor = self.user_repo.get_by_id(actor_uuid)
        if not actor:
            raise ValueError("Actor user not found")
        
        # Save disposition
        alert = self.alert_repo.save_triage_disposition(alert, outcome, rationale, actor_uuid)
        
        # Create audit event
        self.audit_service.create_event(
            entity_type="alert",
            entity_id=alert_id,
            action_type="ALERT_TRIAGE_RECORDED",
            actor_user_id=actor_uuid,
            actor_role=actor.primary_role,
            payload={
                "outcome": outcome,
                "rationale": rationale,
                "existing_case_id": existing_case_id,
                "status_after_triage": alert.status,
                "triaged_at": alert.triaged_at.isoformat() if alert.triaged_at else None
            }
        )
        
        # Commit transaction
        self.db.commit()
        
        # Build response
        alert_dict: dict[str, object] = {
            "alert_id": str(alert.alert_id),
            "transaction_id": str(alert.transaction_id),
            "customer_id": str(alert.customer_id),
            "status": alert.status,
            "priority": alert.priority,
            "risk_score": alert.risk_score,
            "matched_rule_codes_json": alert.matched_rule_codes_json,
            "generation": alert.generation,
            "assigned_user_id": str(alert.assigned_user_id),
            "triage_outcome": alert.triage_outcome,
            "triage_rationale": alert.triage_rationale,
            "triaged_by_user_id": str(alert.triaged_by_user_id),
            "triaged_at": alert.triaged_at,
            "created_at": alert.created_at,
            "updated_at": alert.updated_at
        }
        
        return AlertResponse(**alert_dict)  # type: ignore[arg-type]
