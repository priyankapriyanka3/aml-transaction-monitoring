"""AML Case model for case management."""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, ForeignKey, CheckConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class AmlCase(Base):
    """AML case entity for investigation and review."""
    
    __tablename__ = "aml_cases"
    
    case_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4
    )
    case_ref: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    primary_alert_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("alerts.alert_id"),
        nullable=False
    )
    created_by_user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.user_id"),
        nullable=False
    )
    assigned_officer_user_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid,
        ForeignKey("users.user_id"),
        nullable=True
    )
    status: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    current_blocker_state: Mapped[str] = mapped_column(
        String(24),
        nullable=False,
        default="NONE"
    )
    created_at_utc: Mapped[datetime] = mapped_column(
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at_utc: Mapped[datetime] = mapped_column(
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
    
    __table_args__ = (
        CheckConstraint(
            "status IN ('OPEN', 'INVESTIGATING', 'PENDING_INFORMATION', 'READY_FOR_REVIEW', 'UNDER_REVIEW', 'RETURNED_FOR_INVESTIGATION', 'APPROVED', 'REJECTED', 'ESCALATED', 'FALSE_POSITIVE')",
            name="valid_case_status"
        ),
        CheckConstraint(
            "current_blocker_state IN ('NONE', 'OPEN_REQUESTS', 'OVERDUE_REQUESTS')",
            name="valid_blocker_state"
        ),
    )
    
    # Relationships
    evidence_gaps = relationship("EvidenceGap", back_populates="case")
    information_requests = relationship("InformationRequest", back_populates="case")
    
    def __repr__(self) -> str:
        return f"<AmlCase(case_id={self.case_id}, case_ref={self.case_ref}, status={self.status})>"
