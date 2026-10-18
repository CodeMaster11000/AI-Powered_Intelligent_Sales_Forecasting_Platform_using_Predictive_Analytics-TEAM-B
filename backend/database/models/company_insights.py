from datetime import datetime
from sqlalchemy import (BigInteger, CheckConstraint, DateTime, ForeignKey, Identity, Integer, Text, func,)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.database.database import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from backend.database.models.leads import Lead


class CompanyInsight(Base):
    __tablename__ = "company_insights"
    __table_args__ = (
        CheckConstraint(
            "qualification_score IS NULL OR qualification_score BETWEEN 0 AND 100",
            name="ck_company_insights_score",
        ),
    )

    insight_id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    lead_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("leads.lead_id", ondelete="CASCADE"))

    business_needs: Mapped[str | None] = mapped_column(Text)
    opportunities: Mapped[str | None] = mapped_column(Text)
    industry_analysis: Mapped[str | None] = mapped_column(Text)
    qualification_score: Mapped[int | None] = mapped_column(Integer)
    growth_indicators: Mapped[str | None] = mapped_column(Text)
    tech_alignment: Mapped[str | None] = mapped_column(Text)
    decision_maker_summary: Mapped[str | None] = mapped_column(Text)

    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    lead: Mapped["Lead"] = relationship(back_populates="insights")