import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class CaseNote(Base):
    __tablename__ = "case_notes"
    
    note_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    case_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("aml_cases.case_id"), nullable=False, index=True)
    note_type: Mapped[str] = mapped_column(String(32), nullable=False)
    stage: Mapped[str] = mapped_column(String(32), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    author_user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.user_id"), nullable=False)
    superseded_by_note_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("case_notes.note_id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
