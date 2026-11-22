import uuid
from datetime import datetime

from sqlalchemy import DateTime, Index, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class DetectionRuleSnapshot(Base):
    __tablename__ = "detection_rule_snapshots"
    __table_args__ = (
        Index("ix_detection_rule_snapshots_rule_code_version", "rule_code", "rule_version"),
    )
    
    detection_rule_snapshot_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    rule_code: Mapped[str] = mapped_column(String(32), nullable=False)
    rule_name: Mapped[str] = mapped_column(String(255), nullable=False)
    rule_version: Mapped[str] = mapped_column(String(32), nullable=False)
    threshold_description: Mapped[str] = mapped_column(Text, nullable=False)
    serialized_rule_json: Mapped[str] = mapped_column(Text, nullable=False)
    effective_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
