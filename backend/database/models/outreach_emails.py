from datetime import datetime
from typing import TYPE_CHECKING, Literal

from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, Identity, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.database import Base

if TYPE_CHECKING:
    from backend.database.models.leads import Lead
    from backend.database.models.users import User


OutreachEmailStatus = Literal["draft", "sent"]


class OutreachEmail(Base):
    __tablename__ = "outreach_emails"
    __table_args__ = (
        CheckConstraint(
            "status IN ('draft', 'sent')",
            name="ck_outreach_emails_status",
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    lead_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("leads.lead_id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("users.user_id", ondelete="SET NULL"),
        nullable=True,
    )
    subject: Mapped[str] = mapped_column(Text, nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(Text, server_default="draft", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    lead: Mapped["Lead"] = relationship(back_populates="outreach_emails")
    user: Mapped["User | None"] = relationship(back_populates="outreach_emails")
