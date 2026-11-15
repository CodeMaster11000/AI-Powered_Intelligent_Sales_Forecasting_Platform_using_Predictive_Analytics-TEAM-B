"""add Milestone 3 Phase A CRM and interaction models

Revision ID: 6c2d7e8f9012
Revises: 5a1b2c3d4e5f
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "6c2d7e8f9012"
down_revision: Union[str, Sequence[str], None] = "5a1b2c3d4e5f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "crm_connections",
        sa.Column("connection_id", sa.BigInteger(), sa.Identity(), nullable=False),
        sa.Column("provider", sa.Text(), nullable=False),
        sa.Column("account_identifier", sa.Text(), nullable=False),
        sa.Column("display_name", sa.Text(), nullable=True),
        sa.Column("credential_ref", sa.Text(), nullable=True),
        sa.Column("status", sa.Text(), server_default="active", nullable=False),
        sa.Column("scopes", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("last_successful_sync_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint(
            "provider IN ('hubspot', 'salesforce')",
            name="ck_crm_connections_provider",
        ),
        sa.CheckConstraint(
            "status IN ('active', 'disabled', 'error')",
            name="ck_crm_connections_status",
        ),
        sa.PrimaryKeyConstraint("connection_id"),
    )

    op.create_table(
        "crm_field_mappings",
        sa.Column("mapping_id", sa.BigInteger(), sa.Identity(), nullable=False),
        sa.Column("connection_id", sa.BigInteger(), nullable=False),
        sa.Column("object_type", sa.Text(), nullable=False),
        sa.Column("provider_field", sa.Text(), nullable=False),
        sa.Column("internal_field", sa.Text(), nullable=False),
        sa.Column("direction", sa.Text(), server_default="bidirectional", nullable=False),
        sa.Column("transform_name", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.CheckConstraint(
            "direction IN ('inbound', 'outbound', 'bidirectional')",
            name="ck_crm_field_mappings_direction",
        ),
        sa.ForeignKeyConstraint(
            ["connection_id"],
            ["crm_connections.connection_id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("mapping_id"),
        sa.UniqueConstraint(
            "connection_id",
            "object_type",
            "provider_field",
            "internal_field",
            name="uq_crm_field_mappings_field",
        ),
    )

    op.create_table(
        "crm_records",
        sa.Column("record_id", sa.BigInteger(), sa.Identity(), nullable=False),
        sa.Column("connection_id", sa.BigInteger(), nullable=False),
        sa.Column("lead_id", sa.BigInteger(), nullable=True),
        sa.Column("object_type", sa.Text(), nullable=False),
        sa.Column("provider_record_id", sa.Text(), nullable=False),
        sa.Column("sync_state", sa.Text(), server_default="synced", nullable=False),
        sa.Column("provider_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint(
            "object_type IN ('contact', 'company', 'deal', 'activity')",
            name="ck_crm_records_object_type",
        ),
        sa.CheckConstraint(
            "sync_state IN ('synced', 'pending', 'error')",
            name="ck_crm_records_sync_state",
        ),
        sa.ForeignKeyConstraint(
            ["connection_id"],
            ["crm_connections.connection_id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["lead_id"], ["leads.lead_id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("record_id"),
        sa.UniqueConstraint(
            "connection_id",
            "object_type",
            "provider_record_id",
            name="uq_crm_records_provider_identity",
        ),
    )
    op.create_index("ix_crm_records_lead_id", "crm_records", ["lead_id"])

    op.create_table(
        "crm_sync_logs",
        sa.Column("sync_log_id", sa.BigInteger(), sa.Identity(), nullable=False),
        sa.Column("connection_id", sa.BigInteger(), nullable=False),
        sa.Column("sync_run_id", sa.Text(), nullable=False),
        sa.Column("operation", sa.Text(), nullable=False),
        sa.Column("object_type", sa.Text(), nullable=True),
        sa.Column("internal_record_id", sa.BigInteger(), nullable=True),
        sa.Column("external_record_id", sa.Text(), nullable=True),
        sa.Column("status", sa.Text(), server_default="running", nullable=False),
        sa.Column("records_read", sa.Integer(), server_default="0", nullable=False),
        sa.Column("records_created", sa.Integer(), server_default="0", nullable=False),
        sa.Column("records_updated", sa.Integer(), server_default="0", nullable=False),
        sa.Column("records_failed", sa.Integer(), server_default="0", nullable=False),
        sa.Column("retry_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("error_code", sa.Text(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("details", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "operation IN ('pull', 'push', 'test_connection')",
            name="ck_crm_sync_logs_operation",
        ),
        sa.CheckConstraint(
            "status IN ('running', 'succeeded', 'partial', 'failed')",
            name="ck_crm_sync_logs_status",
        ),
        sa.ForeignKeyConstraint(
            ["connection_id"],
            ["crm_connections.connection_id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("sync_log_id"),
    )
    op.create_index(
        "ix_crm_sync_logs_connection_started",
        "crm_sync_logs",
        ["connection_id", "started_at"],
    )
    op.create_index(
        "ix_crm_sync_logs_sync_run_id", "crm_sync_logs", ["sync_run_id"]
    )

    op.create_table(
        "sales_interactions",
        sa.Column("interaction_id", sa.BigInteger(), sa.Identity(), nullable=False),
        sa.Column("lead_id", sa.BigInteger(), nullable=True),
        sa.Column("connection_id", sa.BigInteger(), nullable=True),
        sa.Column("provider_activity_id", sa.Text(), nullable=True),
        sa.Column("interaction_type", sa.Text(), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("subject", sa.Text(), nullable=True),
        sa.Column("transcript_text", sa.Text(), nullable=True),
        sa.Column("transcript_ref", sa.Text(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("discussion_points", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("action_items", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("risks", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("next_step", sa.Text(), nullable=True),
        sa.Column("processing_status", sa.Text(), server_default="pending", nullable=False),
        sa.Column("ai_provider", sa.Text(), nullable=True),
        sa.Column("ai_model", sa.Text(), nullable=True),
        sa.Column("prompt_version", sa.Text(), nullable=True),
        sa.Column("input_tokens", sa.Integer(), nullable=True),
        sa.Column("output_tokens", sa.Integer(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint(
            "interaction_type IN ('meeting', 'call', 'email', 'note')",
            name="ck_sales_interactions_type",
        ),
        sa.CheckConstraint(
            "processing_status IN ('pending', 'completed', 'failed')",
            name="ck_sales_interactions_processing_status",
        ),
        sa.ForeignKeyConstraint(
            ["connection_id"],
            ["crm_connections.connection_id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["lead_id"], ["leads.lead_id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("interaction_id"),
        sa.UniqueConstraint(
            "connection_id",
            "provider_activity_id",
            name="uq_sales_interactions_provider_activity",
        ),
    )
    op.create_index(
        "ix_sales_interactions_lead_occurred",
        "sales_interactions",
        ["lead_id", "occurred_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_sales_interactions_lead_occurred", table_name="sales_interactions")
    op.drop_table("sales_interactions")
    op.drop_index("ix_crm_sync_logs_sync_run_id", table_name="crm_sync_logs")
    op.drop_index("ix_crm_sync_logs_connection_started", table_name="crm_sync_logs")
    op.drop_table("crm_sync_logs")
    op.drop_index("ix_crm_records_lead_id", table_name="crm_records")
    op.drop_table("crm_records")
    op.drop_table("crm_field_mappings")
    op.drop_table("crm_connections")
