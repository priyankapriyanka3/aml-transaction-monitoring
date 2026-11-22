import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class RiskProfile(Base):
    __tablename__ = "risk_profiles"
    
    risk_profile_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    customer_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("customers.customer_id"), nullable=False, index=True)
    risk_rating: Mapped[str] = mapped_column(String(32), nullable=False)
    kyc_review_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    pep_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="0")
    sanctions_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="0")
    adverse_media_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="0")
    effective_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
