"""add Module 4 lead score components

Revision ID: 4f8e2c7a1b90
Revises: 2d3f6b8a4c91
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "4f8e2c7a1b90"
down_revision: Union[str, Sequence[str], None] = "2d3f6b8a4c91"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    for column in (
        sa.Column("engagement_score", sa.Integer(), server_default="0", nullable=False),
        sa.Column("fit_score", sa.Integer(), server_default="0", nullable=False),
        sa.Column("intent_score", sa.Integer(), server_default="0", nullable=False),
        sa.Column(
            "decision_readiness_score",
            sa.Integer(),
            server_default="0",
            nullable=False,
        ),
        sa.Column(
            "scoring_version",
            sa.Text(),
            server_default="module4-v1",
            nullable=False,
        ),
        sa.Column(
            "scoring_factors",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
    ):
        op.add_column("lead_scores", column)

    for name in (
        "engagement_score",
        "fit_score",
        "intent_score",
        "decision_readiness_score",
    ):
        op.create_check_constraint(
            f"ck_lead_scores_{name}",
            "lead_scores",
            f"{name} BETWEEN 0 AND 100",
        )


def downgrade() -> None:
    for name in (
        "decision_readiness_score",
        "intent_score",
        "fit_score",
        "engagement_score",
        "scoring_version",
        "scoring_factors",
    ):
        op.drop_column("lead_scores", name)
