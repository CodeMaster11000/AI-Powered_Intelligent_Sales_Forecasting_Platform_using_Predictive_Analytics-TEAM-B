from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, CheckConstraint, ForeignKey, Identity, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.database import Base

if TYPE_CHECKING:
    from backend.database.models.crm_connections import CRMConnection


class CRMFieldMapping(Base):
    __tablename__ = "crm_field_mappings"
    __table_args__ = (
        CheckConstraint(
            "direction IN ('inbound', 'outbound', 'bidirectional')",
            name="ck_crm_field_mappings_direction",
        ),
        UniqueConstraint(
            "connection_id",
            "object_type",
            "provider_field",
            "internal_field",
            name="uq_crm_field_mappings_field",
        ),
    )

    mapping_id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    connection_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("crm_connections.connection_id", ondelete="CASCADE"),
        nullable=False,
    )
    object_type: Mapped[str] = mapped_column(Text, nullable=False)
    provider_field: Mapped[str] = mapped_column(Text, nullable=False)
    internal_field: Mapped[str] = mapped_column(Text, nullable=False)
    direction: Mapped[str] = mapped_column(
        Text, nullable=False, server_default="bidirectional"
    )
    transform_name: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(
        nullable=False, server_default="true"
    )

    connection: Mapped["CRMConnection"] = relationship(
        back_populates="field_mappings"
    )
