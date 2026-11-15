"""allow Salesforce Lead provider records

Revision ID: 7d3e8f901234
Revises: 6c2d7e8f9012
"""

from typing import Sequence, Union

from alembic import op


revision: str = "7d3e8f901234"
down_revision: Union[str, Sequence[str], None] = "6c2d7e8f9012"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint(
        "ck_crm_records_object_type", "crm_records", type_="check"
    )
    op.create_check_constraint(
        "ck_crm_records_object_type",
        "crm_records",
        "object_type IN ('lead', 'contact', 'company', 'deal', 'activity')",
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_crm_records_object_type", "crm_records", type_="check"
    )
    op.create_check_constraint(
        "ck_crm_records_object_type",
        "crm_records",
        "object_type IN ('contact', 'company', 'deal', 'activity')",
    )
