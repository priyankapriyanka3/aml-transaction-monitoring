"""
Audit Events API router.
Handles audit event retrieval with filtering and pagination.
"""
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..middleware.auth_middleware import get_current_user
from ..models.user import User
from ..repositories.audit_event_repository import AuditEventRepository

router = APIRouter(prefix="/api/v1/audit-events", tags=["audit-events"])


@router.get("", response_model=dict, status_code=status.HTTP_200_OK)
def get_audit_events(
    entity_type: str | None = Query(None, description="Filter by entity type (e.g., case, alert)"),
    entity_id: str | None = Query(None, description="Filter by entity ID"),
    action_type: str | None = Query(None, description="Filter by action type"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of events to return"),
    offset: int = Query(0, ge=0, description="Number of events to skip"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve audit events with optional filtering and pagination.
    
    Supports filtering by:
    - entity_type: Filter events for specific entity type (case, alert, etc.)
    - entity_id: Filter events for specific entity
    - action_type: Filter events by action type
    
    Returns paginated results with total count.
    """
    repo = AuditEventRepository(db)
    
    events, total_count = repo.list_events(
        entity_type=entity_type,
        entity_id=entity_id,
        action_type=action_type,
        limit=limit,
        offset=offset
    )
    
    import json
    
    items = []
    for event in events:
        # Parse payload_json from string to dict
        try:
            payload = json.loads(event.payload_json)
        except (json.JSONDecodeError, TypeError):
            payload = {}
        
        items.append({
            "audit_event_id": event.audit_event_id,
            "entity_type": event.entity_type,
            "entity_id": event.entity_id,
            "action_type": event.action_type,
            "actor_user_id": event.actor_user_id,
            "actor_role": event.actor_role,
            "correlation_id": event.correlation_id,
            "occurred_at": event.occurred_at.isoformat(),
            "payload": payload
        })
    
    return {
        "items": items,
        "total_count": total_count,
        "limit": limit,
        "offset": offset
    }
