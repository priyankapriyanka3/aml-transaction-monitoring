import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class Transaction(Base):
    __tablename__ = "transactions"
    
    transaction_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    customer_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("customers.customer_id"), nullable=False, index=True)
    account_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("accounts.account_id"), nullable=False, index=True)
    booked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    counterparty_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    corridor: Mapped[str] = mapped_column(String(32), nullable=False)
    generation_source: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
