"""Account model for AML domain entities."""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class Account(Base):
    """Account entity linked to customers."""
    
    __tablename__ = "accounts"
    
    account_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4
    )
    customer_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("customers.customer_id"),
        nullable=False
    )
    account_ref: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    account_type: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at_utc: Mapped[datetime] = mapped_column(
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    
    def __repr__(self) -> str:
        return f"<Account(account_id={self.account_id}, account_ref={self.account_ref})>"
