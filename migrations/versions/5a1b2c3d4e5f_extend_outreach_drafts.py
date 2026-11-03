"""extend outreach drafts with lifecycle and generation metadata

Revision ID: 5a1b2c3d4e5f
Revises: 4f8e2c7a1b90
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "5a1b2c3d4e5f"
down_revision: Union[str, Sequence[str], None] = "4f8e2c7a1b90"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint(
        "ck_outreach_emails_status", "outreach_emails", type_="check"
    )
    op.create_check_constraint(
        "ck_outreach_emails_status",
        "outreach_emails",
        "status IN ('draft', 'sent', 'archived')",
    )

    op.add_column("outreach_emails", sa.Column("provider", sa.Text(), nullable=True))
    op.add_column("outreach_emails", sa.Column("model_name", sa.Text(), nullable=True))
    op.add_column("outreach_emails", sa.Column("angle", sa.Text(), nullable=True))
    op.add_column("outreach_emails", sa.Column("tone", sa.Text(), nullable=True))
    op.add_column("outreach_emails", sa.Column("custom_note", sa.Text(), nullable=True))
    op.add_column(
        "outreach_emails",
        sa.Column(
            "subject_options",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
    )
    op.add_column(
        "outreach_emails",
        sa.Column(
            "generation_metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
    )
    op.add_column(
        "outreach_emails",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.add_column(
        "outreach_emails", sa.Column("sent_at", sa.DateTime(timezone=True))
    )
    op.add_column(
        "outreach_emails", sa.Column("archived_at", sa.DateTime(timezone=True))
    )


def downgrade() -> None:
    for column in (
        "archived_at",
        "sent_at",
        "updated_at",
        "generation_metadata",
        "subject_options",
        "custom_note",
        "tone",
        "angle",
        "model_name",
        "provider",
    ):
        op.drop_column("outreach_emails", column)

    op.drop_constraint(
        "ck_outreach_emails_status", "outreach_emails", type_="check"
    )
    op.create_check_constraint(
        "ck_outreach_emails_status",
        "outreach_emails",
        "status IN ('draft', 'sent')",
    )
