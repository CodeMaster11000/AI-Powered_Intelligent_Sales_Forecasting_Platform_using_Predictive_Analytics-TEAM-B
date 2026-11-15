from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Identity,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.database import Base

if TYPE_CHECKING:
    from backend.database.models.crm_connections import CRMConnection
    from backend.database.models.leads import Lead


class CRMRecord(Base):
    __tablename__ = "crm_records"
    __table_args__ = (
        CheckConstraint(
            "object_type IN ('lead', 'contact', 'company', 'deal', 'activity')",
            name="ck_crm_records_object_type",
        ),
        CheckConstraint(
            "sync_state IN ('synced', 'pending', 'error')",
            name="ck_crm_records_sync_state",
        ),
        UniqueConstraint(
            "connection_id",
            "object_type",
            "provider_record_id",
            name="uq_crm_records_provider_identity",
        ),
    )

    record_id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    connection_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("crm_connections.connection_id", ondelete="CASCADE"),
        nullable=False,
    )
    lead_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("leads.lead_id", ondelete="SET NULL")
    )
    object_type: Mapped[str] = mapped_column(Text, nullable=False)
    provider_record_id: Mapped[str] = mapped_column(Text, nullable=False)
    sync_state: Mapped[str] = mapped_column(
        Text, nullable=False, server_default="synced"
    )
    provider_payload: Mapped[dict | None] = mapped_column(JSONB)
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    connection: Mapped["CRMConnection"] = relationship(back_populates="records")
    lead: Mapped["Lead | None"] = relationship(back_populates="crm_records")
