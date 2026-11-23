"""Create case notes table

Revision ID: 005
Revises: 004
Create Date: 2026-11-22 14:00:05

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create case_notes table for investigation notes."""
    op.create_table(
        'case_notes',
        sa.Column('note_id', sa.Uuid(), nullable=False),
        sa.Column('case_id', sa.Uuid(), nullable=False),
        sa.Column('note_category', sa.String(length=32), nullable=False),
        sa.Column('note_text', sa.Text(), nullable=False),
        sa.Column('author_user_id', sa.Uuid(), nullable=False),
        sa.Column('authored_at_utc', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['case_id'], ['aml_cases.case_id'], ),
        sa.ForeignKeyConstraint(['author_user_id'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('note_id')
    )
    
    # Create index on case_id for workspace queries
    op.create_index('ix_case_notes_case_id', 'case_notes', ['case_id'])


def downgrade() -> None:
    """Drop case_notes table."""
    op.drop_index('ix_case_notes_case_id', table_name='case_notes')
    op.drop_table('case_notes')
