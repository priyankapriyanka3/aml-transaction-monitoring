"""Evidence gap model for tracking missing information in cases."""
import uuid
from datetime import datetime
from sqlalchemy import Column, ForeignKey, String, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class EvidenceGap(Base):
    """Evidence gap entity tracking missing information in a case."""
    
    __tablename__ = "evidence_gaps"
    
    gap_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("aml_cases.case_id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(24), nullable=False)  # OPEN, RESOLVED
    created_by_user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.user_id"), nullable=False)
    created_at_utc: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    resolved_at_utc: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    case = relationship("AmlCase", back_populates="evidence_gaps")
    created_by = relationship("User", foreign_keys=[created_by_user_id])
    information_requests = relationship("InformationRequest", back_populates="gap")
