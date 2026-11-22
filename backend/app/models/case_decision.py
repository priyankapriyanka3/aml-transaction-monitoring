import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class CaseDecision(Base):
    __tablename__ = "case_decisions"
    
    case_decision_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    case_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("aml_cases.case_id"), nullable=False, index=True)
    decision_code: Mapped[str] = mapped_column(String(40), nullable=False)
    rationale: Mapped[str] = mapped_column(Text, nullable=False)
    decided_by_user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.user_id"), nullable=False)
    decided_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
