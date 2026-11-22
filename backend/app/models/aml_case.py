import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class AMLCase(Base):
    __tablename__ = "aml_cases"
    
    case_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    case_number: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    source_alert_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("alerts.alert_id"), nullable=False)
    customer_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("customers.customer_id"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    priority: Mapped[str] = mapped_column(String(16), nullable=False)
    assigned_user_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("users.user_id"), nullable=True, index=True)
    recommendation_state: Mapped[str] = mapped_column(String(40), nullable=False, default="DRAFT", server_default="DRAFT")
    recommendation_outcome: Mapped[str | None] = mapped_column(String(40), nullable=True)
    findings_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    flagged_value_total: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=0, server_default="0")
    evidence_locked_for_review: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="0")
    created_by_user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.user_id"), nullable=False)
    handoff_officer_user_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("users.user_id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
