import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Text, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class CaseAlertLink(Base):
    __tablename__ = "case_alert_links"
    __table_args__ = (
        UniqueConstraint("case_id", "alert_id", name="uq_case_alert_links_case_alert"),
    )
    
    case_alert_link_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    case_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("aml_cases.case_id"), nullable=False, index=True)
    alert_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("alerts.alert_id"), nullable=False, index=True)
    linked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    linked_by_user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.user_id"), nullable=False)
    selection_basis: Mapped[str] = mapped_column(Text, nullable=False)
