"""Transaction model for AML domain entities."""
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import String, ForeignKey, Numeric, Uuid
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class Transaction(Base):
    """Transaction entity for monitoring."""
    
    __tablename__ = "transactions"
    
    transaction_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4
    )
    account_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("accounts.account_id"),
        nullable=False
    )
    transaction_ref: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    currency_code: Mapped[str] = mapped_column(String(3), nullable=False)
    source_country_code: Mapped[str] = mapped_column(String(2), nullable=False)
    destination_country_code: Mapped[str] = mapped_column(String(2), nullable=False)
    executed_at_utc: Mapped[datetime] = mapped_column(nullable=False)
    created_at_utc: Mapped[datetime] = mapped_column(
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    
    def __repr__(self) -> str:
        return f"<Transaction(transaction_id={self.transaction_id}, transaction_ref={self.transaction_ref}, amount={self.amount})>"
