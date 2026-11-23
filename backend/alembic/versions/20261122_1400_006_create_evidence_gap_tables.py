"""Create evidence gap and information request tables

Revision ID: 20261122_1400_006
Revises: 20261122_1400_005
Create Date: 2026-11-22 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '006'
down_revision: Union[str, None] = '005'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create evidence_gaps, information_requests, and request_attachments tables."""
    # Create evidence_gaps table
    op.create_table(
        'evidence_gaps',
        sa.Column('gap_id', sa.Uuid(), nullable=False),
        sa.Column('case_id', sa.Uuid(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=24), nullable=False),
        sa.Column('created_by_user_id', sa.Uuid(), nullable=False),
        sa.Column('created_at_utc', sa.DateTime(), nullable=False),
        sa.Column('resolved_at_utc', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['case_id'], ['aml_cases.case_id'], name='fk_evidence_gaps_case_id'),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['users.user_id'], name='fk_evidence_gaps_created_by_user_id'),
        sa.PrimaryKeyConstraint('gap_id', name='pk_evidence_gaps')
    )
    
    # Create index on case_id for evidence_gaps
    with op.batch_alter_table('evidence_gaps', schema=None) as batch_op:
        batch_op.create_index('ix_evidence_gaps_case_id', ['case_id'], unique=False)
    
    # Create information_requests table
    op.create_table(
        'information_requests',
        sa.Column('request_id', sa.Uuid(), nullable=False),
        sa.Column('request_ref', sa.String(length=64), nullable=False),
        sa.Column('case_id', sa.Uuid(), nullable=False),
        sa.Column('gap_id', sa.Uuid(), nullable=False),
        sa.Column('target_party', sa.String(length=255), nullable=False),
        sa.Column('delivery_channel', sa.String(length=64), nullable=False),
        sa.Column('reason_text', sa.Text(), nullable=False),
        sa.Column('due_at_utc', sa.DateTime(), nullable=False),
        sa.Column('status', sa.String(length=24), nullable=False),
        sa.Column('created_by_user_id', sa.Uuid(), nullable=False),
        sa.Column('response_summary', sa.Text(), nullable=True),
        sa.Column('response_received_at_utc', sa.DateTime(), nullable=True),
        sa.Column('created_at_utc', sa.DateTime(), nullable=False),
        sa.Column('updated_at_utc', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['case_id'], ['aml_cases.case_id'], name='fk_information_requests_case_id'),
        sa.ForeignKeyConstraint(['gap_id'], ['evidence_gaps.gap_id'], name='fk_information_requests_gap_id'),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['users.user_id'], name='fk_information_requests_created_by_user_id'),
        sa.PrimaryKeyConstraint('request_id', name='pk_information_requests'),
        sa.UniqueConstraint('request_ref', name='uq_information_requests_request_ref')
    )
    
    # Create indexes on information_requests
    with op.batch_alter_table('information_requests', schema=None) as batch_op:
        batch_op.create_index('ix_information_requests_case_id', ['case_id'], unique=False)
        batch_op.create_index('ix_information_requests_status', ['status'], unique=False)
    
    # Create request_attachments table
    op.create_table(
        'request_attachments',
        sa.Column('request_attachment_id', sa.Uuid(), nullable=False),
        sa.Column('request_id', sa.Uuid(), nullable=False),
        sa.Column('attachment_ref', sa.String(length=64), nullable=False),
        sa.Column('file_name', sa.String(length=255), nullable=False),
        sa.Column('content_type', sa.String(length=128), nullable=False),
        sa.Column('storage_path', sa.String(length=512), nullable=False),
        sa.Column('uploaded_by_user_id', sa.Uuid(), nullable=False),
        sa.Column('uploaded_at_utc', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['request_id'], ['information_requests.request_id'], name='fk_request_attachments_request_id'),
        sa.ForeignKeyConstraint(['uploaded_by_user_id'], ['users.user_id'], name='fk_request_attachments_uploaded_by_user_id'),
        sa.PrimaryKeyConstraint('request_attachment_id', name='pk_request_attachments'),
        sa.UniqueConstraint('attachment_ref', name='uq_request_attachments_attachment_ref')
    )
    
    # Create index on request_id for request_attachments
    with op.batch_alter_table('request_attachments', schema=None) as batch_op:
        batch_op.create_index('ix_request_attachments_request_id', ['request_id'], unique=False)


def downgrade() -> None:
    """Drop evidence gap and information request tables."""
    op.drop_table('request_attachments')
    op.drop_table('information_requests')
    op.drop_table('evidence_gaps')
