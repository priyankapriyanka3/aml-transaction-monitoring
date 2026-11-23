"""Case Alert Link model for linking alerts to cases."""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, ForeignKey, Boolean, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class CaseAlertLink(Base):
    """Link between cases and alerts with primary flag."""
    
    __tablename__ = "case_alert_links"
    
    case_alert_link_id: Mapped[uuid.UUID] = mapped_column(
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
    alert_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("alerts.alert_id"),
        nullable=False,
        index=True
    )
    is_primary: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False
    )
    linked_by_user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.user_id"),
        nullable=False
    )
    linked_at_utc: Mapped[datetime] = mapped_column(
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    
    __table_args__ = (
        UniqueConstraint("case_id", "alert_id", name="unique_case_alert"),
    )
    
    def __repr__(self) -> str:
        return f"<CaseAlertLink(case_id={self.case_id}, alert_id={self.alert_id}, is_primary={self.is_primary})>"
