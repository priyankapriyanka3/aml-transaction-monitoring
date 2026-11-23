"""Alert model for AML domain entities."""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, ForeignKey, Integer, CheckConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class Alert(Base):
    """Alert entity for transaction monitoring."""
    
    __tablename__ = "alerts"
    
    alert_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4
    )
    alert_ref: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    transaction_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("transactions.transaction_id"),
        nullable=False
    )
    customer_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("customers.customer_id"),
        nullable=False
    )
    priority: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    risk_score: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    owner_user_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid,
        ForeignKey("users.user_id"),
        nullable=True
    )
    triggered_at_utc: Mapped[datetime] = mapped_column(nullable=False)
    created_at_utc: Mapped[datetime] = mapped_column(
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    
    __table_args__ = (
        CheckConstraint(
            "priority IN ('Critical', 'High', 'Medium', 'Low')",
            name="valid_alert_priority"
        ),
        CheckConstraint(
            "status IN ('New', 'Under Review', 'Escalated', 'Resolved')",
            name="valid_alert_status"
        ),
    )
    
    def __repr__(self) -> str:
        return f"<Alert(alert_id={self.alert_id}, alert_ref={self.alert_ref}, priority={self.priority}, risk_score={self.risk_score})>"
