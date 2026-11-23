"""Rule evaluation snapshot model for immutable historical rule state."""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, ForeignKey, Text, CheckConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class RuleEvaluationSnapshot(Base):
    """Immutable historical rule evaluation snapshot.
    
    Captures the exact rule state at alert evaluation time.
    Rule versions and outcomes are preserved and never recalculated.
    """
    
    __tablename__ = "rule_evaluation_snapshots"
    
    snapshot_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4
    )
    alert_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("alerts.alert_id"),
        nullable=False,
        index=True
    )
    rule_code: Mapped[str] = mapped_column(String(64), nullable=False)
    rule_name: Mapped[str] = mapped_column(String(255), nullable=False)
    rule_version: Mapped[str] = mapped_column(String(32), nullable=False)
    outcome: Mapped[str] = mapped_column(String(16), nullable=False)
    condition_text: Mapped[str] = mapped_column(Text, nullable=False)
    evaluated_from_utc: Mapped[datetime] = mapped_column(nullable=False)
    evaluated_to_utc: Mapped[datetime] = mapped_column(nullable=False)
    immutable_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    created_at_utc: Mapped[datetime] = mapped_column(
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    
    __table_args__ = (
        CheckConstraint(
            "outcome IN ('MATCH', 'PASS')",
            name="valid_rule_outcome"
        ),
    )
    
    def __repr__(self) -> str:
        return f"<RuleEvaluationSnapshot(snapshot_id={self.snapshot_id}, rule_name={self.rule_name}, version={self.rule_version}, outcome={self.outcome})>"
