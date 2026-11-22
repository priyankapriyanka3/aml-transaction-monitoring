"""Fix UUID and DateTime types

Revision ID: 20261121_160128
Revises: 70e3a29542df
Create Date: 2026-11-21 16:01:28.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20261121_160128'
down_revision = '70e3a29542df'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Use Uuid type that works across SQLite and PostgreSQL
    from sqlalchemy import Uuid
    
    # Fix customers table
    with op.batch_alter_table('customers', schema=None) as batch_op:
        batch_op.alter_column('customer_id', type_=Uuid(), existing_type=sa.String(36), existing_nullable=False)
        batch_op.alter_column('created_at', type_=sa.DateTime(timezone=True), existing_type=sa.DateTime(), existing_nullable=False)
        batch_op.alter_column('updated_at', type_=sa.DateTime(timezone=True), existing_type=sa.DateTime(), existing_nullable=False)
    
    # Fix detection_rule_snapshots table
    with op.batch_alter_table('detection_rule_snapshots', schema=None) as batch_op:
        batch_op.alter_column('detection_rule_snapshot_id', type_=Uuid(), existing_type=sa.String(36), existing_nullable=False)
        batch_op.alter_column('effective_at', type_=sa.DateTime(timezone=True), existing_type=sa.DateTime(), existing_nullable=False)
        batch_op.alter_column('created_at', type_=sa.DateTime(timezone=True), existing_type=sa.DateTime(), existing_nullable=False)
    
    # Fix users table
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('user_id', type_=Uuid(), existing_type=sa.String(36), existing_nullable=False)
        batch_op.alter_column('created_at', type_=sa.DateTime(timezone=True), existing_type=sa.DateTime(), existing_nullable=False)
        batch_op.alter_column('updated_at', type_=sa.DateTime(timezone=True), existing_type=sa.DateTime(), existing_nullable=False)
    
    # Fix accounts table
    with op.batch_alter_table('accounts', schema=None) as batch_op:
        batch_op.alter_column('account_id', type_=Uuid(), existing_type=sa.String(36), existing_nullable=False)
        batch_op.alter_column('customer_id', type_=Uuid(), existing_type=sa.String(36), existing_nullable=False)
        batch_op.alter_column('created_at', type_=sa.DateTime(timezone=True), existing_type=sa.DateTime(), existing_nullable=False)
        batch_op.alter_column('updated_at', type_=sa.DateTime(timezone=True), existing_type=sa.DateTime(), existing_nullable=False)
    
    # Fix audit_events table
    with op.batch_alter_table('audit_events', schema=None) as batch_op:
        batch_op.alter_column('audit_event_id', type_=Uuid(), existing_type=sa.String(36), existing_nullable=False)
        batch_op.alter_column('actor_user_id', type_=Uuid(), existing_type=sa.String(36), existing_nullable=False)
        batch_op.alter_column('occurred_at', type_=sa.DateTime(timezone=True), existing_type=sa.DateTime(), existing_nullable=False)
        batch_op.alter_column('created_at', type_=sa.DateTime(timezone=True), existing_type=sa.DateTime(), existing_nullable=False)
    
    # Fix risk_profiles table
    with op.batch_alter_table('risk_profiles', schema=None) as batch_op:
        batch_op.alter_column('risk_profile_id', type_=Uuid(), existing_type=sa.String(36), existing_nullable=False)
        batch_op.alter_column('customer_id', type_=Uuid(), existing_type=sa.String(36), existing_nullable=False)
        batch_op.alter_column('kyc_review_date', type_=sa.DateTime(timezone=True), existing_type=sa.DateTime(), existing_nullable=True)
        batch_op.alter_column('effective_at', type_=sa.DateTime(timezone=True), existing_type=sa.DateTime(), existing_nullable=False)
        batch_op.alter_column('created_at', type_=sa.DateTime(timezone=True), existing_type=sa.DateTime(), existing_nullable=False)
    
    # Fix session_records table
    with op.batch_alter_table('session_records', schema=None) as batch_op:
        batch_op.alter_column('session_id', type_=Uuid(), existing_type=sa.String(36), existing_nullable=False)
        batch_op.alter_column('user_id', type_=Uuid(), existing_type=sa.String(36), existing_nullable=False)
        batch_op.alter_column('issued_at', type_=sa.DateTime(timezone=True), existing_type=sa.DateTime(), existing_nullable=False)
        batch_op.alter_column('expires_at', type_=sa.DateTime(timezone=True), existing_type=sa.DateTime(), existing_nullable=False)
        batch_op.alter_column('last_activity_at', type_=sa.DateTime(timezone=True), existing_type=sa.DateTime(), existing_nullable=False)
        batch_op.alter_column('revoked_at', type_=sa.DateTime(timezone=True), existing_type=sa.DateTime(), existing_nullable=True)
        batch_op.alter_column('created_at', type_=sa.DateTime(timezone=True), existing_type=sa.DateTime(), existing_nullable=False)
    
    # Fix transactions table
    with op.batch_alter_table('transactions', schema=None) as batch_op:
        batch_op.alter_column('transaction_id', type_=Uuid(), existing_type=sa.String(36), existing_nullable=False)
        batch_op.alter_column('customer_id', type_=Uuid(), existing_type=sa.String(36), existing_nullable=False)
        batch_op.alter_column('account_id', type_=Uuid(), existing_type=sa.String(36), existing_nullable=False)
        batch_op.alter_column('booked_at', type_=sa.DateTime(timezone=True), existing_type=sa.DateTime(), existing_nullable=False)
        batch_op.alter_column('created_at', type_=sa.DateTime(timezone=True), existing_type=sa.DateTime(), existing_nullable=False)
    
    # Fix alerts table
    with op.batch_alter_table('alerts', schema=None) as batch_op:
        batch_op.alter_column('alert_id', type_=Uuid(), existing_type=sa.String(36), existing_nullable=False)
        batch_op.alter_column('transaction_id', type_=Uuid(), existing_type=sa.String(36), existing_nullable=False)
        batch_op.alter_column('customer_id', type_=Uuid(), existing_type=sa.String(36), existing_nullable=False)
        batch_op.alter_column('assigned_user_id', type_=Uuid(), existing_type=sa.String(36), existing_nullable=True)
        batch_op.alter_column('triaged_by_user_id', type_=Uuid(), existing_type=sa.String(36), existing_nullable=True)
        batch_op.alter_column('triaged_at', type_=sa.DateTime(timezone=True), existing_type=sa.DateTime(), existing_nullable=True)
        batch_op.alter_column('created_at', type_=sa.DateTime(timezone=True), existing_type=sa.DateTime(), existing_nullable=False)
        batch_op.alter_column('updated_at', type_=sa.DateTime(timezone=True), existing_type=sa.DateTime(), existing_nullable=False)
    
    # Fix aml_cases table
    with op.batch_alter_table('aml_cases', schema=None) as batch_op:
        batch_op.alter_column('case_id', type_=Uuid(), existing_type=sa.String(36), existing_nullable=False)
        batch_op.alter_column('source_alert_id', type_=Uuid(), existing_type=sa.String(36), existing_nullable=False)
        batch_op.alter_column('customer_id', type_=Uuid(), existing_type=sa.String(36), existing_nullable=False)
        batch_op.alter_column('assigned_user_id', type_=Uuid(), existing_type=sa.String(36), existing_nullable=True)
        batch_op.alter_column('created_by_user_id', type_=Uuid(), existing_type=sa.String(36), existing_nullable=False)
        batch_op.alter_column('handoff_officer_user_id', type_=Uuid(), existing_type=sa.String(36), existing_nullable=True)
        batch_op.alter_column('created_at', type_=sa.DateTime(timezone=True), existing_type=sa.DateTime(), existing_nullable=False)
        batch_op.alter_column('updated_at', type_=sa.DateTime(timezone=True), existing_type=sa.DateTime(), existing_nullable=False)
    
    # Fix rule_evaluation_results table
    with op.batch_alter_table('rule_evaluation_results', schema=None) as batch_op:
        batch_op.alter_column('rule_evaluation_result_id', type_=Uuid(), existing_type=sa.String(36), existing_nullable=False)
        batch_op.alter_column('alert_id', type_=Uuid(), existing_type=sa.String(36), existing_nullable=False)
        batch_op.alter_column('detection_rule_snapshot_id', type_=Uuid(), existing_type=sa.String(36), existing_nullable=False)
        batch_op.alter_column('evaluated_at', type_=sa.DateTime(timezone=True), existing_type=sa.DateTime(), existing_nullable=False)
        batch_op.alter_column('created_at', type_=sa.DateTime(timezone=True), existing_type=sa.DateTime(), existing_nullable=False)
    
    # Fix case_alert_links table
    with op.batch_alter_table('case_alert_links', schema=None) as batch_op:
        batch_op.alter_column('case_alert_link_id', type_=Uuid(), existing_type=sa.String(36), existing_nullable=False)
        batch_op.alter_column('case_id', type_=Uuid(), existing_type=sa.String(36), existing_nullable=False)
        batch_op.alter_column('alert_id', type_=Uuid(), existing_type=sa.String(36), existing_nullable=False)
        batch_op.alter_column('linked_by_user_id', type_=Uuid(), existing_type=sa.String(36), existing_nullable=False)
        batch_op.alter_column('linked_at', type_=sa.DateTime(timezone=True), existing_type=sa.DateTime(), existing_nullable=False)
    
    # Fix case_decisions table
    with op.batch_alter_table('case_decisions', schema=None) as batch_op:
        batch_op.alter_column('case_decision_id', type_=Uuid(), existing_type=sa.String(36), existing_nullable=False)
        batch_op.alter_column('case_id', type_=Uuid(), existing_type=sa.String(36), existing_nullable=False)
        batch_op.alter_column('decided_by_user_id', type_=Uuid(), existing_type=sa.String(36), existing_nullable=False)
        batch_op.alter_column('decided_at', type_=sa.DateTime(timezone=True), existing_type=sa.DateTime(), existing_nullable=False)
    
    # Fix case_notes table
    with op.batch_alter_table('case_notes', schema=None) as batch_op:
        batch_op.alter_column('note_id', type_=Uuid(), existing_type=sa.String(36), existing_nullable=False)
        batch_op.alter_column('case_id', type_=Uuid(), existing_type=sa.String(36), existing_nullable=False)
        batch_op.alter_column('author_user_id', type_=Uuid(), existing_type=sa.String(36), existing_nullable=False)
        batch_op.alter_column('superseded_by_note_id', type_=Uuid(), existing_type=sa.String(36), existing_nullable=True)
        batch_op.alter_column('created_at', type_=sa.DateTime(timezone=True), existing_type=sa.DateTime(), existing_nullable=False)
    
    # Fix information_requests table
    with op.batch_alter_table('information_requests', schema=None) as batch_op:
        batch_op.alter_column('information_request_id', type_=Uuid(), existing_type=sa.String(36), existing_nullable=False)
        batch_op.alter_column('case_id', type_=Uuid(), existing_type=sa.String(36), existing_nullable=False)
        batch_op.alter_column('created_by_user_id', type_=Uuid(), existing_type=sa.String(36), existing_nullable=False)
        batch_op.alter_column('due_at', type_=sa.DateTime(timezone=True), existing_type=sa.DateTime(), existing_nullable=False)
        batch_op.alter_column('response_received_at', type_=sa.DateTime(timezone=True), existing_type=sa.DateTime(), existing_nullable=True)
        batch_op.alter_column('created_at', type_=sa.DateTime(timezone=True), existing_type=sa.DateTime(), existing_nullable=False)
        batch_op.alter_column('updated_at', type_=sa.DateTime(timezone=True), existing_type=sa.DateTime(), existing_nullable=False)


def downgrade() -> None:
    # Revert information_requests table
    with op.batch_alter_table('information_requests', schema=None) as batch_op:
        batch_op.alter_column('updated_at', type_=sa.DateTime(), existing_type=sa.DateTime(timezone=True), existing_nullable=False)
        batch_op.alter_column('created_at', type_=sa.DateTime(), existing_type=sa.DateTime(timezone=True), existing_nullable=False)
        batch_op.alter_column('response_received_at', type_=sa.DateTime(), existing_type=sa.DateTime(timezone=True), existing_nullable=True)
        batch_op.alter_column('due_at', type_=sa.DateTime(), existing_type=sa.DateTime(timezone=True), existing_nullable=False)
        batch_op.alter_column('created_by_user_id', type_=sa.String(36), existing_type=sa.Uuid(), existing_nullable=False)
        batch_op.alter_column('case_id', type_=sa.String(36), existing_type=sa.Uuid(), existing_nullable=False)
        batch_op.alter_column('information_request_id', type_=sa.String(36), existing_type=sa.Uuid(), existing_nullable=False)
    
    # Revert case_notes table
    with op.batch_alter_table('case_notes', schema=None) as batch_op:
        batch_op.alter_column('created_at', type_=sa.DateTime(), existing_type=sa.DateTime(timezone=True), existing_nullable=False)
        batch_op.alter_column('superseded_by_note_id', type_=sa.String(36), existing_type=sa.Uuid(), existing_nullable=True)
        batch_op.alter_column('author_user_id', type_=sa.String(36), existing_type=sa.Uuid(), existing_nullable=False)
        batch_op.alter_column('case_id', type_=sa.String(36), existing_type=sa.Uuid(), existing_nullable=False)
        batch_op.alter_column('note_id', type_=sa.String(36), existing_type=sa.Uuid(), existing_nullable=False)
    
    # Revert case_decisions table
    with op.batch_alter_table('case_decisions', schema=None) as batch_op:
        batch_op.alter_column('decided_at', type_=sa.DateTime(), existing_type=sa.DateTime(timezone=True), existing_nullable=False)
        batch_op.alter_column('decided_by_user_id', type_=sa.String(36), existing_type=sa.Uuid(), existing_nullable=False)
        batch_op.alter_column('case_id', type_=sa.String(36), existing_type=sa.Uuid(), existing_nullable=False)
        batch_op.alter_column('case_decision_id', type_=sa.String(36), existing_type=sa.Uuid(), existing_nullable=False)
    
    # Revert case_alert_links table
    with op.batch_alter_table('case_alert_links', schema=None) as batch_op:
        batch_op.alter_column('linked_at', type_=sa.DateTime(), existing_type=sa.DateTime(timezone=True), existing_nullable=False)
        batch_op.alter_column('linked_by_user_id', type_=sa.String(36), existing_type=sa.Uuid(), existing_nullable=False)
        batch_op.alter_column('alert_id', type_=sa.String(36), existing_type=sa.Uuid(), existing_nullable=False)
        batch_op.alter_column('case_id', type_=sa.String(36), existing_type=sa.Uuid(), existing_nullable=False)
        batch_op.alter_column('case_alert_link_id', type_=sa.String(36), existing_type=sa.Uuid(), existing_nullable=False)
    
    # Revert rule_evaluation_results table
    with op.batch_alter_table('rule_evaluation_results', schema=None) as batch_op:
        batch_op.alter_column('created_at', type_=sa.DateTime(), existing_type=sa.DateTime(timezone=True), existing_nullable=False)
        batch_op.alter_column('evaluated_at', type_=sa.DateTime(), existing_type=sa.DateTime(timezone=True), existing_nullable=False)
        batch_op.alter_column('detection_rule_snapshot_id', type_=sa.String(36), existing_type=sa.Uuid(), existing_nullable=False)
        batch_op.alter_column('alert_id', type_=sa.String(36), existing_type=sa.Uuid(), existing_nullable=False)
        batch_op.alter_column('rule_evaluation_result_id', type_=sa.String(36), existing_type=sa.Uuid(), existing_nullable=False)
    
    # Revert aml_cases table
    with op.batch_alter_table('aml_cases', schema=None) as batch_op:
        batch_op.alter_column('updated_at', type_=sa.DateTime(), existing_type=sa.DateTime(timezone=True), existing_nullable=False)
        batch_op.alter_column('created_at', type_=sa.DateTime(), existing_type=sa.DateTime(timezone=True), existing_nullable=False)
        batch_op.alter_column('handoff_officer_user_id', type_=sa.String(36), existing_type=sa.Uuid(), existing_nullable=True)
        batch_op.alter_column('created_by_user_id', type_=sa.String(36), existing_type=sa.Uuid(), existing_nullable=False)
        batch_op.alter_column('assigned_user_id', type_=sa.String(36), existing_type=sa.Uuid(), existing_nullable=True)
        batch_op.alter_column('customer_id', type_=sa.String(36), existing_type=sa.Uuid(), existing_nullable=False)
        batch_op.alter_column('source_alert_id', type_=sa.String(36), existing_type=sa.Uuid(), existing_nullable=False)
        batch_op.alter_column('case_id', type_=sa.String(36), existing_type=sa.Uuid(), existing_nullable=False)
    
    # Revert alerts table
    with op.batch_alter_table('alerts', schema=None) as batch_op:
        batch_op.alter_column('updated_at', type_=sa.DateTime(), existing_type=sa.DateTime(timezone=True), existing_nullable=False)
        batch_op.alter_column('created_at', type_=sa.DateTime(), existing_type=sa.DateTime(timezone=True), existing_nullable=False)
        batch_op.alter_column('triaged_at', type_=sa.DateTime(), existing_type=sa.DateTime(timezone=True), existing_nullable=True)
        batch_op.alter_column('triaged_by_user_id', type_=sa.String(36), existing_type=sa.Uuid(), existing_nullable=True)
        batch_op.alter_column('assigned_user_id', type_=sa.String(36), existing_type=sa.Uuid(), existing_nullable=True)
        batch_op.alter_column('customer_id', type_=sa.String(36), existing_type=sa.Uuid(), existing_nullable=False)
        batch_op.alter_column('transaction_id', type_=sa.String(36), existing_type=sa.Uuid(), existing_nullable=False)
        batch_op.alter_column('alert_id', type_=sa.String(36), existing_type=sa.Uuid(), existing_nullable=False)
    
    # Revert transactions table
    with op.batch_alter_table('transactions', schema=None) as batch_op:
        batch_op.alter_column('created_at', type_=sa.DateTime(), existing_type=sa.DateTime(timezone=True), existing_nullable=False)
        batch_op.alter_column('booked_at', type_=sa.DateTime(), existing_type=sa.DateTime(timezone=True), existing_nullable=False)
        batch_op.alter_column('account_id', type_=sa.String(36), existing_type=sa.Uuid(), existing_nullable=False)
        batch_op.alter_column('customer_id', type_=sa.String(36), existing_type=sa.Uuid(), existing_nullable=False)
        batch_op.alter_column('transaction_id', type_=sa.String(36), existing_type=sa.Uuid(), existing_nullable=False)
    
    # Revert session_records table
    with op.batch_alter_table('session_records', schema=None) as batch_op:
        batch_op.alter_column('created_at', type_=sa.DateTime(), existing_type=sa.DateTime(timezone=True), existing_nullable=False)
        batch_op.alter_column('revoked_at', type_=sa.DateTime(), existing_type=sa.DateTime(timezone=True), existing_nullable=True)
        batch_op.alter_column('last_activity_at', type_=sa.DateTime(), existing_type=sa.DateTime(timezone=True), existing_nullable=False)
        batch_op.alter_column('expires_at', type_=sa.DateTime(), existing_type=sa.DateTime(timezone=True), existing_nullable=False)
        batch_op.alter_column('issued_at', type_=sa.DateTime(), existing_type=sa.DateTime(timezone=True), existing_nullable=False)
        batch_op.alter_column('user_id', type_=sa.String(36), existing_type=sa.Uuid(), existing_nullable=False)
        batch_op.alter_column('session_id', type_=sa.String(36), existing_type=sa.Uuid(), existing_nullable=False)
    
    # Revert risk_profiles table
    with op.batch_alter_table('risk_profiles', schema=None) as batch_op:
        batch_op.alter_column('created_at', type_=sa.DateTime(), existing_type=sa.DateTime(timezone=True), existing_nullable=False)
        batch_op.alter_column('effective_at', type_=sa.DateTime(), existing_type=sa.DateTime(timezone=True), existing_nullable=False)
        batch_op.alter_column('kyc_review_date', type_=sa.DateTime(), existing_type=sa.DateTime(timezone=True), existing_nullable=True)
        batch_op.alter_column('customer_id', type_=sa.String(36), existing_type=sa.Uuid(), existing_nullable=False)
        batch_op.alter_column('risk_profile_id', type_=sa.String(36), existing_type=sa.Uuid(), existing_nullable=False)
    
    # Revert audit_events table
    with op.batch_alter_table('audit_events', schema=None) as batch_op:
        batch_op.alter_column('created_at', type_=sa.DateTime(), existing_type=sa.DateTime(timezone=True), existing_nullable=False)
        batch_op.alter_column('occurred_at', type_=sa.DateTime(), existing_type=sa.DateTime(timezone=True), existing_nullable=False)
        batch_op.alter_column('actor_user_id', type_=sa.String(36), existing_type=sa.Uuid(), existing_nullable=False)
        batch_op.alter_column('audit_event_id', type_=sa.String(36), existing_type=sa.Uuid(), existing_nullable=False)
    
    # Revert accounts table
    with op.batch_alter_table('accounts', schema=None) as batch_op:
        batch_op.alter_column('updated_at', type_=sa.DateTime(), existing_type=sa.DateTime(timezone=True), existing_nullable=False)
        batch_op.alter_column('created_at', type_=sa.DateTime(), existing_type=sa.DateTime(timezone=True), existing_nullable=False)
        batch_op.alter_column('customer_id', type_=sa.String(36), existing_type=sa.Uuid(), existing_nullable=False)
        batch_op.alter_column('account_id', type_=sa.String(36), existing_type=sa.Uuid(), existing_nullable=False)
    
    # Revert users table
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('updated_at', type_=sa.DateTime(), existing_type=sa.DateTime(timezone=True), existing_nullable=False)
        batch_op.alter_column('created_at', type_=sa.DateTime(), existing_type=sa.DateTime(timezone=True), existing_nullable=False)
        batch_op.alter_column('user_id', type_=sa.String(36), existing_type=sa.Uuid(), existing_nullable=False)
    
    # Revert detection_rule_snapshots table
    with op.batch_alter_table('detection_rule_snapshots', schema=None) as batch_op:
        batch_op.alter_column('created_at', type_=sa.DateTime(), existing_type=sa.DateTime(timezone=True), existing_nullable=False)
        batch_op.alter_column('effective_at', type_=sa.DateTime(), existing_type=sa.DateTime(timezone=True), existing_nullable=False)
        batch_op.alter_column('detection_rule_snapshot_id', type_=sa.String(36), existing_type=sa.Uuid(), existing_nullable=False)
    
    # Revert customers table
    with op.batch_alter_table('customers', schema=None) as batch_op:
        batch_op.alter_column('updated_at', type_=sa.DateTime(), existing_type=sa.DateTime(timezone=True), existing_nullable=False)
        batch_op.alter_column('created_at', type_=sa.DateTime(), existing_type=sa.DateTime(timezone=True), existing_nullable=False)
        batch_op.alter_column('customer_id', type_=sa.String(36), existing_type=sa.Uuid(), existing_nullable=False)
