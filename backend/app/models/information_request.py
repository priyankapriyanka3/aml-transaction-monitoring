"""Information request model for evidence gap resolution."""
import uuid
from datetime import datetime
from sqlalchemy import Column, ForeignKey, String, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class InformationRequest(Base):
    """Information request entity for requesting missing evidence."""
    
    __tablename__ = "information_requests"
    
    request_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    request_ref: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    case_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("aml_cases.case_id"), nullable=False, index=True)
    gap_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("evidence_gaps.gap_id"), nullable=False)
    target_party: Mapped[str] = mapped_column(String(255), nullable=False)
    delivery_channel: Mapped[str] = mapped_column(String(64), nullable=False)
    reason_text: Mapped[str] = mapped_column(Text, nullable=False)
    due_at_utc: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[str] = mapped_column(String(24), nullable=False, index=True)  # OPEN, OVERDUE, RESPONDED, RESOLVED
    created_by_user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.user_id"), nullable=False)
    response_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    response_received_at_utc: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at_utc: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at_utc: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    
    # Relationships
    case = relationship("AmlCase", back_populates="information_requests")
    gap = relationship("EvidenceGap", back_populates="information_requests")
    created_by = relationship("User", foreign_keys=[created_by_user_id])
    attachments = relationship("RequestAttachment", back_populates="request")
