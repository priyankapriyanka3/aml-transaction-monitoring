"""Case Note model for investigation notes."""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class CaseNote(Base):
    """Investigation note with category, author, and timestamp."""
    
    __tablename__ = "case_notes"
    
    note_id: Mapped[uuid.UUID] = mapped_column(
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
    note_category: Mapped[str] = mapped_column(
        String(32),
        nullable=False
    )
    note_text: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    author_user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.user_id"),
        nullable=False
    )
    authored_at_utc: Mapped[datetime] = mapped_column(
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    
    def __repr__(self) -> str:
        return f"<CaseNote(note_id={self.note_id}, case_id={self.case_id}, category={self.note_category})>"
