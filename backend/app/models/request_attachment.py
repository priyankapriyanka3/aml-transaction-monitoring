"""Request attachment model for information request evidence."""
import uuid
from datetime import datetime
from sqlalchemy import Column, ForeignKey, String, DateTime
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class RequestAttachment(Base):
    """Request attachment entity for uploaded evidence."""
    
    __tablename__ = "request_attachments"
    
    request_attachment_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    request_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("information_requests.request_id"), nullable=False, index=True)
    attachment_ref: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(128), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(512), nullable=False)
    uploaded_by_user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.user_id"), nullable=False)
    uploaded_at_utc: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    
    # Relationships
    request = relationship("InformationRequest", back_populates="attachments")
    uploaded_by = relationship("User", foreign_keys=[uploaded_by_user_id])
