"""Create case_review_assignments and case_decisions tables

Revision ID: 006
Revises: 005
Create Date: 2026-11-22 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '007'
down_revision: Union[str, None] = '006'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create case_review_assignments table
    op.create_table(
        'case_review_assignments',
        sa.Column('assignment_id', sa.Uuid(), nullable=False),
        sa.Column('case_id', sa.Uuid(), nullable=False),
        sa.Column('officer_user_id', sa.Uuid(), nullable=False),
        sa.Column('assigned_by_user_id', sa.Uuid(), nullable=False),
        sa.Column('assigned_at_utc', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['assigned_by_user_id'], ['users.user_id'], ),
        sa.ForeignKeyConstraint(['case_id'], ['aml_cases.case_id'], ),
        sa.ForeignKeyConstraint(['officer_user_id'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('assignment_id'),
        sa.UniqueConstraint('case_id')
    )
    
    with op.batch_alter_table('case_review_assignments', schema=None) as batch_op:
        batch_op.create_index('ix_case_review_assignments_case_id', ['case_id'], unique=True)
    
    # Create case_decisions table
    op.create_table(
        'case_decisions',
        sa.Column('decision_id', sa.Uuid(), nullable=False),
        sa.Column('case_id', sa.Uuid(), nullable=False),
        sa.Column('deciding_officer_user_id', sa.Uuid(), nullable=False),
        sa.Column('outcome', sa.String(length=40), nullable=False),
        sa.Column('rationale_text', sa.Text(), nullable=False),
        sa.Column('recorded_at_utc', sa.DateTime(), nullable=False),
        sa.Column('immutable_hash', sa.String(length=128), nullable=False),
        sa.CheckConstraint("outcome IN ('APPROVE', 'REJECT', 'ESCALATE', 'FALSE_POSITIVE', 'RETURN_FOR_INVESTIGATION')", name='valid_decision_outcome'),
        sa.ForeignKeyConstraint(['case_id'], ['aml_cases.case_id'], ),
        sa.ForeignKeyConstraint(['deciding_officer_user_id'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('decision_id')
    )
    
    with op.batch_alter_table('case_decisions', schema=None) as batch_op:
        batch_op.create_index('ix_case_decisions_case_id', ['case_id'], unique=False)


def downgrade() -> None:
    with op.batch_alter_table('case_decisions', schema=None) as batch_op:
        batch_op.drop_index('ix_case_decisions_case_id')
    
    op.drop_table('case_decisions')
    
    with op.batch_alter_table('case_review_assignments', schema=None) as batch_op:
        batch_op.drop_index('ix_case_review_assignments_case_id')
    
    op.drop_table('case_review_assignments')
