"""enforce unique lead email addresses

Revision ID: 8e4f1a2b3c5d
Revises: 7d3e8f901234
"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import text


revision: str = "8e4f1a2b3c5d"
down_revision: Union[str, Sequence[str], None] = "7d3e8f901234"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    connection = op.get_bind()
    duplicates = connection.execute(
        text(
            "SELECT lower(trim(email)) AS normalized_email "
            "FROM leads GROUP BY lower(trim(email)) HAVING count(*) > 1"
        )
    ).fetchall()
    if duplicates:
        emails = ", ".join(row[0] for row in duplicates[:5])
        raise RuntimeError(
            "Cannot enforce unique lead emails; duplicate normalized addresses "
            f"exist: {emails}. Merge these leads before migrating."
        )
    op.execute("UPDATE leads SET email = lower(trim(email))")
    op.create_unique_constraint("uq_leads_email", "leads", ["email"])


def downgrade() -> None:
    op.drop_constraint("uq_leads_email", "leads", type_="unique")
