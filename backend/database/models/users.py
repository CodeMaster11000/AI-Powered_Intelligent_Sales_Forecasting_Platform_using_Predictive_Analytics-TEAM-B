from datetime import datetime
from sqlalchemy import (BigInteger, CheckConstraint, DateTime, Identity, Text, UniqueConstraint, func,)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from backend.database.database import Base

if TYPE_CHECKING:
    from backend.database.models.leads import Lead
    from backend.database.models.outreach_emails import OutreachEmail
ROLES = ("Sales Representative", "BDR", "Sales Manager", "RevOps")

class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint(
            "role IN (" + ", ".join(f"'{r}'" for r in ROLES) + ")",
            name="ck_users_role",
        ),
        UniqueConstraint("email", name="uq_users_email"),
    )

    user_id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    email: Mapped[str] = mapped_column(Text)
    role: Mapped[str] = mapped_column(Text)
    department: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    leads: Mapped[list["Lead"]] = relationship(back_populates="owner", passive_deletes=True)
    outreach_emails: Mapped[list["OutreachEmail"]] = relationship(
        back_populates="user", passive_deletes=True
    )
    #analytics: Mapped[list["SalesAnalytics"]] = relationship(back_populates="user", passive_deletes=True)