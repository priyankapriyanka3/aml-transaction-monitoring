"""Create case tables

Revision ID: 003
Revises: 002
Create Date: 2026-11-22 14:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import Uuid


# revision identifiers, used by Alembic.
revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create aml_cases table
    with op.batch_alter_table('aml_cases', schema=None) as batch_op:
        pass
    
    op.create_table(
        'aml_cases',
        sa.Column('case_id', Uuid(), nullable=False),
        sa.Column('case_ref', sa.String(length=64), nullable=False),
        sa.Column('primary_alert_id', Uuid(), nullable=False),
        sa.Column('created_by_user_id', Uuid(), nullable=False),
        sa.Column('assigned_officer_user_id', Uuid(), nullable=True),
        sa.Column('status', sa.String(length=40), nullable=False),
        sa.Column('current_blocker_state', sa.String(length=24), nullable=False, server_default='NONE'),
        sa.Column('created_at_utc', sa.DateTime(), nullable=False),
        sa.Column('updated_at_utc', sa.DateTime(), nullable=False),
        sa.CheckConstraint(
            "status IN ('OPEN', 'INVESTIGATING', 'PENDING_INFORMATION', 'READY_FOR_REVIEW', 'UNDER_REVIEW', 'RETURNED_FOR_INVESTIGATION', 'APPROVED', 'REJECTED', 'ESCALATED', 'FALSE_POSITIVE')",
            name='valid_case_status'
        ),
        sa.CheckConstraint(
            "current_blocker_state IN ('NONE', 'OPEN_REQUESTS', 'OVERDUE_REQUESTS')",
            name='valid_blocker_state'
        ),
        sa.ForeignKeyConstraint(['primary_alert_id'], ['alerts.alert_id'], name='fk_case_primary_alert'),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['users.user_id'], name='fk_case_created_by'),
        sa.ForeignKeyConstraint(['assigned_officer_user_id'], ['users.user_id'], name='fk_case_officer'),
        sa.PrimaryKeyConstraint('case_id'),
        sa.UniqueConstraint('case_ref')
    )
    
    # Create indexes for aml_cases
    with op.batch_alter_table('aml_cases', schema=None) as batch_op:
        batch_op.create_index('ix_aml_cases_case_ref', ['case_ref'], unique=True)
        batch_op.create_index('ix_aml_cases_status', ['status'], unique=False)
    
    # Create case_alert_links table
    op.create_table(
        'case_alert_links',
        sa.Column('case_alert_link_id', Uuid(), nullable=False),
        sa.Column('case_id', Uuid(), nullable=False),
        sa.Column('alert_id', Uuid(), nullable=False),
        sa.Column('is_primary', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('linked_by_user_id', Uuid(), nullable=False),
        sa.Column('linked_at_utc', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['case_id'], ['aml_cases.case_id'], name='fk_case_alert_link_case'),
        sa.ForeignKeyConstraint(['alert_id'], ['alerts.alert_id'], name='fk_case_alert_link_alert'),
        sa.ForeignKeyConstraint(['linked_by_user_id'], ['users.user_id'], name='fk_case_alert_link_user'),
        sa.PrimaryKeyConstraint('case_alert_link_id'),
        sa.UniqueConstraint('case_id', 'alert_id', name='unique_case_alert')
    )
    
    # Create indexes for case_alert_links
    with op.batch_alter_table('case_alert_links', schema=None) as batch_op:
        batch_op.create_index('ix_case_alert_links_case_id', ['case_id'], unique=False)
        batch_op.create_index('ix_case_alert_links_alert_id', ['alert_id'], unique=False)


def downgrade() -> None:
    # Drop indexes and tables in reverse order
    with op.batch_alter_table('case_alert_links', schema=None) as batch_op:
        batch_op.drop_index('ix_case_alert_links_alert_id')
        batch_op.drop_index('ix_case_alert_links_case_id')
    
    op.drop_table('case_alert_links')
    
    with op.batch_alter_table('aml_cases', schema=None) as batch_op:
        batch_op.drop_index('ix_aml_cases_status')
        batch_op.drop_index('ix_aml_cases_case_ref')
    
    op.drop_table('aml_cases')
