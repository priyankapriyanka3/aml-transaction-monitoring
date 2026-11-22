import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class RuleEvaluationResult(Base):
    __tablename__ = "rule_evaluation_results"
    
    rule_evaluation_result_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    alert_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("alerts.alert_id"), nullable=False, index=True)
    detection_rule_snapshot_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("detection_rule_snapshots.detection_rule_snapshot_id"), nullable=False)
    outcome: Mapped[str] = mapped_column(String(16), nullable=False)
    threshold_explanation: Mapped[str] = mapped_column(Text, nullable=False)
    evaluated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
