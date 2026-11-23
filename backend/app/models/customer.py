"""Customer model for AML domain entities."""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, Uuid
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class Customer(Base):
    """Customer entity for AML transaction monitoring."""
    
    __tablename__ = "customers"
    
    customer_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4
    )
    customer_name: Mapped[str] = mapped_column(String(255), nullable=False)
    pep_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    country_code: Mapped[str] = mapped_column(String(2), nullable=False)
    created_at_utc: Mapped[datetime] = mapped_column(
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    
    def __repr__(self) -> str:
        return f"<Customer(customer_id={self.customer_id}, customer_name={self.customer_name})>"
