"""create rule_evaluation_snapshots table

Revision ID: 004
Revises: 003
Create Date: 2026-11-22 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '004'
down_revision: Union[str, None] = '003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create rule_evaluation_snapshots table for immutable historical rule state."""
    op.create_table(
        'rule_evaluation_snapshots',
        sa.Column('snapshot_id', sa.Uuid(), nullable=False),
        sa.Column('alert_id', sa.Uuid(), nullable=False),
        sa.Column('rule_code', sa.String(length=64), nullable=False),
        sa.Column('rule_name', sa.String(length=255), nullable=False),
        sa.Column('rule_version', sa.String(length=32), nullable=False),
        sa.Column('outcome', sa.String(length=16), nullable=False),
        sa.Column('condition_text', sa.Text(), nullable=False),
        sa.Column('evaluated_from_utc', sa.DateTime(), nullable=False),
        sa.Column('evaluated_to_utc', sa.DateTime(), nullable=False),
        sa.Column('immutable_hash', sa.String(length=128), nullable=False),
        sa.Column('created_at_utc', sa.DateTime(), nullable=False),
        sa.CheckConstraint("outcome IN ('MATCH', 'PASS')", name='valid_rule_outcome'),
        sa.ForeignKeyConstraint(['alert_id'], ['alerts.alert_id'], ),
        sa.PrimaryKeyConstraint('snapshot_id')
    )
    
    # Create index for efficient lookup by alert - use the same name SQLAlchemy auto-generates
    with op.batch_alter_table('rule_evaluation_snapshots') as batch_op:
        batch_op.create_index(
            'ix_rule_evaluation_snapshots_alert_id',
            ['alert_id']
        )


def downgrade() -> None:
    """Drop rule_evaluation_snapshots table."""
    with op.batch_alter_table('rule_evaluation_snapshots') as batch_op:
        batch_op.drop_index('ix_rule_evaluation_snapshots_alert_id')
    
    op.drop_table('rule_evaluation_snapshots')
