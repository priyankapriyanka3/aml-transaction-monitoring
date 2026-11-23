"""create users and sessions tables

Revision ID: 001
Revises: 
Create Date: 2026-11-22 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('display_name', sa.String(length=120), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=32), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('created_at_utc', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at_utc', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint(
            "role IN ('INVESTIGATOR', 'OFFICER', 'AUDITOR', 'SUPERVISOR')",
            name='valid_user_role'
        ),
        sa.PrimaryKeyConstraint('user_id'),
        sa.UniqueConstraint('email')
    )
    
    # Create index on email
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    
    # Create sessions table
    op.create_table(
        'sessions',
        sa.Column('session_id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('hashed_token', sa.String(length=64), nullable=False),
        sa.Column('issued_at_utc', sa.DateTime(), nullable=False),
        sa.Column('expires_at_utc', sa.DateTime(), nullable=False),
        sa.Column('last_activity_utc', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('session_id'),
        sa.UniqueConstraint('hashed_token')
    )
    
    # Create indexes on sessions
    op.create_index(op.f('ix_sessions_user_id'), 'sessions', ['user_id'], unique=False)
    op.create_index(op.f('ix_sessions_hashed_token'), 'sessions', ['hashed_token'], unique=True)
    op.create_index(op.f('ix_sessions_expires_at_utc'), 'sessions', ['expires_at_utc'], unique=False)


def downgrade() -> None:
    # Drop sessions table
    op.drop_index(op.f('ix_sessions_expires_at_utc'), table_name='sessions')
    op.drop_index(op.f('ix_sessions_hashed_token'), table_name='sessions')
    op.drop_index(op.f('ix_sessions_user_id'), table_name='sessions')
    op.drop_table('sessions')
    
    # Drop users table
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
