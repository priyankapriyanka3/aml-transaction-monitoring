"""Case Review Assignment model for independent officer assignment."""
import uuid
from datetime import datetime, timezone
from sqlalchemy import ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class CaseReviewAssignment(Base):
    """Case review assignment entity tracking independent officer assignment."""
    
    __tablename__ = "case_review_assignments"
    
    assignment_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4
    )
    case_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("aml_cases.case_id"),
        nullable=False,
        unique=True,
        index=True
    )
    officer_user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.user_id"),
        nullable=False
    )
    assigned_by_user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.user_id"),
        nullable=False
    )
    assigned_at_utc: Mapped[datetime] = mapped_column(
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    
    def __repr__(self) -> str:
        return f"<CaseReviewAssignment(assignment_id={self.assignment_id}, case_id={self.case_id}, officer_user_id={self.officer_user_id})>"
