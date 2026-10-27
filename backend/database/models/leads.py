from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (BigInteger, CheckConstraint, DateTime, ForeignKey, Identity, Text, func,)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.database import Base

if TYPE_CHECKING:
    from backend.database.models.company_insights import CompanyInsight
    from backend.database.models.lead_scores import LeadScore
    from backend.database.models.lead_analysis_runs import LeadAnalysisRun
    from backend.database.models.users import User


LEAD_STATUSES = ("New Leads", "Qualified", "Proposal", "Negotiation", "Closed Won")
SOURCES = ("CRM", "Website Form", "LinkedIn", "Sales Entry", "CSV")


class Lead(Base):
    __tablename__ = "leads"
    __table_args__ = (
        CheckConstraint(
            "lead_status IN (" + ", ".join(f"'{s}'" for s in LEAD_STATUSES) + ")",
            name="ck_leads_lead_status",
        ),
        CheckConstraint(
            "source IN (" + ", ".join(f"'{s}'" for s in SOURCES) + ")",
            name="ck_leads_source",
        ),
    )

    lead_id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    owner_user_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("users.user_id", ondelete="SET NULL")
    )
    company_name: Mapped[str] = mapped_column(Text)
    industry: Mapped[str | None] = mapped_column(Text)
    contact_name: Mapped[str | None] = mapped_column(Text)
    contact_title: Mapped[str | None] = mapped_column(Text)
    email: Mapped[str] = mapped_column(Text)
    phone: Mapped[str | None] = mapped_column(Text)
    lead_status: Mapped[str] = mapped_column(Text, server_default="New Leads")
    source: Mapped[str] = mapped_column(Text)
    company_size: Mapped[str | None] = mapped_column(Text)
    annual_revenue: Mapped[str | None] = mapped_column(Text)
    funding_stage: Mapped[str | None] = mapped_column(Text)
    funding_raised: Mapped[str | None] = mapped_column(Text)
    location: Mapped[str | None] = mapped_column(Text)
    tech_stack: Mapped[list[str] | None] = mapped_column(JSONB)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    owner: Mapped["User | None"] = relationship(back_populates="leads")
    insights: Mapped[list["CompanyInsight"]] = relationship(
        back_populates="lead", cascade="all, delete-orphan", passive_deletes=True
    )
    scores: Mapped[list["LeadScore"]] = relationship(
        back_populates="lead", cascade="all, delete-orphan", passive_deletes=True
    )
    analysis_runs: Mapped[list["LeadAnalysisRun"]] = relationship(
        back_populates="lead", cascade="all, delete-orphan", passive_deletes=True
    )