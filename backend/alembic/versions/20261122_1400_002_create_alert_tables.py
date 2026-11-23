"""create alert domain tables

Revision ID: 002
Revises: 001
Create Date: 2026-11-22 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create customers table
    op.create_table(
        'customers',
        sa.Column('customer_id', sa.Uuid(), nullable=False),
        sa.Column('customer_name', sa.String(length=255), nullable=False),
        sa.Column('pep_flag', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('country_code', sa.String(length=2), nullable=False),
        sa.Column('created_at_utc', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('customer_id')
    )
    
    # Create accounts table
    op.create_table(
        'accounts',
        sa.Column('account_id', sa.Uuid(), nullable=False),
        sa.Column('customer_id', sa.Uuid(), nullable=False),
        sa.Column('account_ref', sa.String(length=64), nullable=False),
        sa.Column('account_type', sa.String(length=32), nullable=False),
        sa.Column('created_at_utc', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.customer_id'], ),
        sa.PrimaryKeyConstraint('account_id'),
        sa.UniqueConstraint('account_ref')
    )
    with op.batch_alter_table('accounts', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_accounts_account_ref'), ['account_ref'], unique=True)
    
    # Create transactions table
    op.create_table(
        'transactions',
        sa.Column('transaction_id', sa.Uuid(), nullable=False),
        sa.Column('account_id', sa.Uuid(), nullable=False),
        sa.Column('transaction_ref', sa.String(length=64), nullable=False),
        sa.Column('amount', sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column('currency_code', sa.String(length=3), nullable=False),
        sa.Column('source_country_code', sa.String(length=2), nullable=False),
        sa.Column('destination_country_code', sa.String(length=2), nullable=False),
        sa.Column('executed_at_utc', sa.DateTime(), nullable=False),
        sa.Column('created_at_utc', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['account_id'], ['accounts.account_id'], ),
        sa.PrimaryKeyConstraint('transaction_id'),
        sa.UniqueConstraint('transaction_ref')
    )
    with op.batch_alter_table('transactions', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_transactions_transaction_ref'), ['transaction_ref'], unique=True)
    
    # Create alerts table
    op.create_table(
        'alerts',
        sa.Column('alert_id', sa.Uuid(), nullable=False),
        sa.Column('alert_ref', sa.String(length=64), nullable=False),
        sa.Column('transaction_id', sa.Uuid(), nullable=False),
        sa.Column('customer_id', sa.Uuid(), nullable=False),
        sa.Column('priority', sa.String(length=16), nullable=False),
        sa.Column('risk_score', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('owner_user_id', sa.Uuid(), nullable=True),
        sa.Column('triggered_at_utc', sa.DateTime(), nullable=False),
        sa.Column('created_at_utc', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("priority IN ('Critical', 'High', 'Medium', 'Low')", name='valid_alert_priority'),
        sa.CheckConstraint("status IN ('New', 'Under Review', 'Escalated', 'Resolved')", name='valid_alert_status'),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.customer_id'], ),
        sa.ForeignKeyConstraint(['owner_user_id'], ['users.user_id'], ),
        sa.ForeignKeyConstraint(['transaction_id'], ['transactions.transaction_id'], ),
        sa.PrimaryKeyConstraint('alert_id'),
        sa.UniqueConstraint('alert_ref')
    )
    with op.batch_alter_table('alerts', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_alerts_alert_ref'), ['alert_ref'], unique=True)
        batch_op.create_index(batch_op.f('ix_alerts_priority'), ['priority'], unique=False)
        batch_op.create_index(batch_op.f('ix_alerts_risk_score'), ['risk_score'], unique=False)
        batch_op.create_index(batch_op.f('ix_alerts_status'), ['status'], unique=False)
    
    # Create audit_events table
    op.create_table(
        'audit_events',
        sa.Column('audit_event_id', sa.Uuid(), nullable=False),
        sa.Column('entity_type', sa.String(length=32), nullable=False),
        sa.Column('entity_id', sa.Uuid(), nullable=False),
        sa.Column('action_type', sa.String(length=64), nullable=False),
        sa.Column('actor_user_id', sa.Uuid(), nullable=False),
        sa.Column('actor_role', sa.String(length=32), nullable=False),
        sa.Column('correlation_id', sa.String(length=128), nullable=False),
        sa.Column('details_json', sa.Text(), nullable=False),
        sa.Column('occurred_at_utc', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['actor_user_id'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('audit_event_id')
    )
    with op.batch_alter_table('audit_events', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_audit_events_correlation_id'), ['correlation_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_audit_events_entity_id'), ['entity_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_audit_events_entity_type'), ['entity_type'], unique=False)
        batch_op.create_index(batch_op.f('ix_audit_events_occurred_at_utc'), ['occurred_at_utc'], unique=False)


def downgrade() -> None:
    # Drop audit_events table
    with op.batch_alter_table('audit_events', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_audit_events_occurred_at_utc'))
        batch_op.drop_index(batch_op.f('ix_audit_events_entity_type'))
        batch_op.drop_index(batch_op.f('ix_audit_events_entity_id'))
        batch_op.drop_index(batch_op.f('ix_audit_events_correlation_id'))
    op.drop_table('audit_events')
    
    # Drop alerts table
    with op.batch_alter_table('alerts', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_alerts_status'))
        batch_op.drop_index(batch_op.f('ix_alerts_risk_score'))
        batch_op.drop_index(batch_op.f('ix_alerts_priority'))
        batch_op.drop_index(batch_op.f('ix_alerts_alert_ref'))
    op.drop_table('alerts')
    
    # Drop transactions table
    with op.batch_alter_table('transactions', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_transactions_transaction_ref'))
    op.drop_table('transactions')
    
    # Drop accounts table
    with op.batch_alter_table('accounts', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_accounts_account_ref'))
    op.drop_table('accounts')
    
    # Drop customers table
    op.drop_table('customers')
