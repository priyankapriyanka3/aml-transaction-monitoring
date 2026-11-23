"""User model for authentication and authorization."""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, CheckConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class User(Base):
    """User entity with role-based access control."""
    
    __tablename__ = "users"
    
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4
    )
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(32), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at_utc: Mapped[datetime] = mapped_column(
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at_utc: Mapped[datetime] = mapped_column(
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
    
    __table_args__ = (
        CheckConstraint(
            "role IN ('INVESTIGATOR', 'OFFICER', 'AUDITOR', 'SUPERVISOR')",
            name="valid_user_role"
        ),
    )
    
    def __repr__(self) -> str:
        return f"<User(user_id={self.user_id}, email={self.email}, role={self.role})>"
