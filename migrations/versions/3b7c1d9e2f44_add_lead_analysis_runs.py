"""store complete structured multi-agent analysis output

Revision ID: 3b7c1d9e2f44
Revises: 9ca4d0d53e32
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "3b7c1d9e2f44"
down_revision: Union[str, Sequence[str], None] = "9ca4d0d53e32"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "lead_analysis_runs",
        sa.Column("analysis_id", sa.BigInteger(), sa.Identity(always=False), nullable=False),
        sa.Column("lead_id", sa.BigInteger(), nullable=False),
        sa.Column("qualification_score", sa.Integer(), nullable=False),
        sa.Column("high_growth_potential", sa.Boolean(), nullable=True),
        sa.Column("funding_analysis", sa.Text(), nullable=True),
        sa.Column("overall_tech_compatibility_score", sa.Integer(), nullable=True),
        sa.Column("industry_domain_analysis", sa.Text(), nullable=True),
        sa.Column("business_needs_summary", sa.Text(), nullable=True),
        sa.Column("strategic_recommendation", sa.Text(), nullable=True),
        sa.Column("growth_indicators", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("tech_stack_components", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("transformation_opportunities", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("tech_alignment_metrics", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("decision_makers", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("execution_trace", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("errors", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("execution_latency_seconds", sa.Float(), nullable=True),
        sa.Column(
            "generated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["lead_id"], ["leads.lead_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("analysis_id"),
    )
    op.create_index("ix_lead_analysis_runs_lead_id", "lead_analysis_runs", ["lead_id"])
    op.create_index(
        "ix_lead_analysis_runs_generated_at",
        "lead_analysis_runs",
        ["generated_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_lead_analysis_runs_generated_at",
        table_name="lead_analysis_runs",
    )
    op.drop_index("ix_lead_analysis_runs_lead_id", table_name="lead_analysis_runs")
    op.drop_table("lead_analysis_runs")
