"""Audit event model for immutable audit trail."""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, ForeignKey, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class AuditEvent(Base):
    """Audit event entity for immutable audit trail."""
    
    __tablename__ = "audit_events"
    
    audit_event_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4
    )
    entity_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    entity_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, index=True)
    action_type: Mapped[str] = mapped_column(String(64), nullable=False)
    actor_user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.user_id"),
        nullable=False
    )
    actor_role: Mapped[str] = mapped_column(String(32), nullable=False)
    correlation_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    details_json: Mapped[str] = mapped_column(Text, nullable=False)
    occurred_at_utc: Mapped[datetime] = mapped_column(
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True
    )
    
    def __repr__(self) -> str:
        return f"<AuditEvent(audit_event_id={self.audit_event_id}, entity_type={self.entity_type}, action_type={self.action_type})>"
