import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class Customer(Base):
    __tablename__ = "customers"
    
    customer_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    customer_name: Mapped[str] = mapped_column(String(255), nullable=False)
    onboarding_profile: Mapped[str] = mapped_column(String(128), nullable=False)
    risk_classification: Mapped[str] = mapped_column(String(32), nullable=False)
    exposure_indicators_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
