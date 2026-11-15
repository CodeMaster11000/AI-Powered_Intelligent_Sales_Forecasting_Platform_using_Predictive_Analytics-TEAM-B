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
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.database import Base

if TYPE_CHECKING:
    from backend.database.models.crm_connections import CRMConnection
    from backend.database.models.leads import Lead


class SalesInteraction(Base):
    __tablename__ = "sales_interactions"
    __table_args__ = (
        CheckConstraint(
            "interaction_type IN ('meeting', 'call', 'email', 'note')",
            name="ck_sales_interactions_type",
        ),
        CheckConstraint(
            "processing_status IN ('pending', 'completed', 'failed')",
            name="ck_sales_interactions_processing_status",
        ),
        UniqueConstraint(
            "connection_id",
            "provider_activity_id",
            name="uq_sales_interactions_provider_activity",
        ),
    )

    interaction_id: Mapped[int] = mapped_column(
        BigInteger, Identity(), primary_key=True
    )
    lead_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("leads.lead_id", ondelete="SET NULL")
    )
    connection_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("crm_connections.connection_id", ondelete="SET NULL")
    )
    provider_activity_id: Mapped[str | None] = mapped_column(Text)
    interaction_type: Mapped[str] = mapped_column(Text, nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    subject: Mapped[str | None] = mapped_column(Text)
    transcript_text: Mapped[str | None] = mapped_column(Text)
    transcript_ref: Mapped[str | None] = mapped_column(Text)
    summary: Mapped[str | None] = mapped_column(Text)
    discussion_points: Mapped[list[str] | None] = mapped_column(JSONB)
    action_items: Mapped[list[dict] | None] = mapped_column(JSONB)
    risks: Mapped[list[str] | None] = mapped_column(JSONB)
    next_step: Mapped[str | None] = mapped_column(Text)
    processing_status: Mapped[str] = mapped_column(
        Text, nullable=False, server_default="pending"
    )
    ai_provider: Mapped[str | None] = mapped_column(Text)
    ai_model: Mapped[str | None] = mapped_column(Text)
    prompt_version: Mapped[str | None] = mapped_column(Text)
    input_tokens: Mapped[int | None] = mapped_column(Integer)
    output_tokens: Mapped[int | None] = mapped_column(Integer)
    error_message: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    lead: Mapped["Lead | None"] = relationship(back_populates="sales_interactions")
    connection: Mapped["CRMConnection | None"] = relationship(
        back_populates="interactions"
    )
