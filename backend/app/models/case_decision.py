"""Case Decision model for immutable final decision recording."""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, ForeignKey, CheckConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class CaseDecision(Base):
    """Case decision entity for immutable final disposition recording."""
    
    __tablename__ = "case_decisions"
    
    decision_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4
    )
    case_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("aml_cases.case_id"),
        nullable=False,
        index=True
    )
    deciding_officer_user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.user_id"),
        nullable=False
    )
    outcome: Mapped[str] = mapped_column(String(40), nullable=False)
    rationale_text: Mapped[str] = mapped_column(Text, nullable=False)
    recorded_at_utc: Mapped[datetime] = mapped_column(
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    immutable_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    
    __table_args__ = (
        CheckConstraint(
            "outcome IN ('APPROVE', 'REJECT', 'ESCALATE', 'FALSE_POSITIVE', 'RETURN_FOR_INVESTIGATION')",
            name="valid_decision_outcome"
        ),
    )
    
    def __repr__(self) -> str:
        return f"<CaseDecision(decision_id={self.decision_id}, case_id={self.case_id}, outcome={self.outcome})>"
