from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Identity,
    Integer,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.database import Base

if TYPE_CHECKING:
    from backend.database.models.crm_connections import CRMConnection


class CRMSyncLog(Base):
    __tablename__ = "crm_sync_logs"
    __table_args__ = (
        CheckConstraint(
            "operation IN ('pull', 'push', 'test_connection')",
            name="ck_crm_sync_logs_operation",
        ),
        CheckConstraint(
            "status IN ('running', 'succeeded', 'partial', 'failed')",
            name="ck_crm_sync_logs_status",
        ),
    )

    sync_log_id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    connection_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("crm_connections.connection_id", ondelete="CASCADE"),
        nullable=False,
    )
    sync_run_id: Mapped[str] = mapped_column(Text, nullable=False)
    operation: Mapped[str] = mapped_column(Text, nullable=False)
    object_type: Mapped[str | None] = mapped_column(Text)
    internal_record_id: Mapped[int | None] = mapped_column(BigInteger)
    external_record_id: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(
        Text, nullable=False, server_default="running"
    )
    records_read: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    records_created: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="0"
    )
    records_updated: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="0"
    )
    records_failed: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="0"
    )
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    error_code: Mapped[str | None] = mapped_column(Text)
    error_message: Mapped[str | None] = mapped_column(Text)
    details: Mapped[dict | None] = mapped_column(JSONB)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    connection: Mapped["CRMConnection"] = relationship(back_populates="sync_logs")
