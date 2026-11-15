from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, CheckConstraint, DateTime, Identity, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.database import Base

if TYPE_CHECKING:
    from backend.database.models.crm_field_mappings import CRMFieldMapping
    from backend.database.models.crm_records import CRMRecord
    from backend.database.models.crm_sync_logs import CRMSyncLog
    from backend.database.models.sales_interactions import SalesInteraction


class CRMConnection(Base):
    __tablename__ = "crm_connections"
    __table_args__ = (
        CheckConstraint(
            "provider IN ('hubspot', 'salesforce')",
            name="ck_crm_connections_provider",
        ),
        CheckConstraint(
            "status IN ('active', 'disabled', 'error')",
            name="ck_crm_connections_status",
        ),
    )

    connection_id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    provider: Mapped[str] = mapped_column(Text, nullable=False)
    account_identifier: Mapped[str] = mapped_column(Text, nullable=False)
    display_name: Mapped[str | None] = mapped_column(Text)
    credential_ref: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(
        Text, nullable=False, server_default="active"
    )
    scopes: Mapped[list[str] | None] = mapped_column(JSONB)
    last_successful_sync_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    field_mappings: Mapped[list["CRMFieldMapping"]] = relationship(
        back_populates="connection", cascade="all, delete-orphan"
    )
    records: Mapped[list["CRMRecord"]] = relationship(
        back_populates="connection", cascade="all, delete-orphan"
    )
    sync_logs: Mapped[list["CRMSyncLog"]] = relationship(
        back_populates="connection", cascade="all, delete-orphan"
    )
    interactions: Mapped[list["SalesInteraction"]] = relationship(
        back_populates="connection"
    )
