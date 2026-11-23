"""Session model for server-side session tracking."""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class Session(Base):
    """Server-side session record for JWT token revocation and tracking."""
    
    __tablename__ = "sessions"
    
    session_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    hashed_token: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    issued_at_utc: Mapped[datetime] = mapped_column(nullable=False)
    expires_at_utc: Mapped[datetime] = mapped_column(nullable=False, index=True)
    last_activity_utc: Mapped[datetime] = mapped_column(nullable=False)
    
    def __repr__(self) -> str:
        return f"<Session(session_id={self.session_id}, user_id={self.user_id})>"
