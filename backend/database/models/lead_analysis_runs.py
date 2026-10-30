from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Boolean, DateTime, Float, ForeignKey, Identity, Integer, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.database import Base

if TYPE_CHECKING:
    from backend.database.models.leads import Lead


class LeadAnalysisRun(Base):
    """Immutable structured output from one multi-agent lead analysis."""

    __tablename__ = "lead_analysis_runs"

    analysis_id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    lead_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("leads.lead_id", ondelete="CASCADE"), index=True
    )
    qualification_score: Mapped[int] = mapped_column(Integer)
    high_growth_potential: Mapped[bool | None] = mapped_column(Boolean)
    funding_analysis: Mapped[str | None] = mapped_column(Text)
    overall_tech_compatibility_score: Mapped[int | None] = mapped_column(Integer)
    industry_domain_analysis: Mapped[str | None] = mapped_column(Text)
    business_needs_summary: Mapped[str | None] = mapped_column(Text)
    strategic_recommendation: Mapped[str | None] = mapped_column(Text)
    growth_indicators: Mapped[list[str] | None] = mapped_column(JSONB)
    tech_stack_components: Mapped[dict[str, list[str]] | None] = mapped_column(JSONB)
    transformation_opportunities: Mapped[list[dict] | None] = mapped_column(JSONB)
    tech_alignment_metrics: Mapped[list[dict] | None] = mapped_column(JSONB)
    decision_makers: Mapped[list[dict] | None] = mapped_column(JSONB)
    execution_trace: Mapped[list[str] | None] = mapped_column(JSONB)
    errors: Mapped[list[str] | None] = mapped_column(JSONB)
    execution_latency_seconds: Mapped[float | None] = mapped_column(Float)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )

    lead: Mapped["Lead"] = relationship(back_populates="analysis_runs")
