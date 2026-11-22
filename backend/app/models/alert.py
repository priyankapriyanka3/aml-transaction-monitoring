import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class Alert(Base):
    __tablename__ = "alerts"
    
    alert_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    transaction_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("transactions.transaction_id"), nullable=False)
    customer_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("customers.customer_id"), nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    priority: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    risk_score: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    matched_rule_codes_json: Mapped[str] = mapped_column(Text, nullable=False)
    generation: Mapped[str] = mapped_column(String(32), nullable=False)
    assigned_user_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("users.user_id"), nullable=True, index=True)
    triage_outcome: Mapped[str | None] = mapped_column(String(40), nullable=True)
    triage_rationale: Mapped[str | None] = mapped_column(Text, nullable=True)
    triaged_by_user_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("users.user_id"), nullable=True)
    triaged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
