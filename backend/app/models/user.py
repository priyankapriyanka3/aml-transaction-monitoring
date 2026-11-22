import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class User(Base):
    __tablename__ = "users"
    
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    username: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(160), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    primary_role: Mapped[str] = mapped_column(String(64), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="1")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
