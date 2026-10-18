from datetime import datetime
from decimal import Decimal
from sqlalchemy import (BigInteger, CheckConstraint, DateTime, ForeignKey, Identity, Integer,Numeric, func)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.database.database import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from backend.database.models.leads import Lead


class LeadScore(Base):
    __tablename__ = "lead_scores"
    __table_args__ = (
        CheckConstraint(
            "lead_score BETWEEN 0 AND 100", name="ck_lead_scores_score"
        ),
        CheckConstraint(
            "conversion_probability BETWEEN 0 AND 100",
            name="ck_lead_scores_probability",
        ),
    )

    score_id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    lead_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("leads.lead_id", ondelete="CASCADE"))
    lead_score: Mapped[int] = mapped_column(Integer)
    conversion_probability: Mapped[Decimal] = mapped_column(Numeric(5, 2))
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    lead: Mapped["Lead"] = relationship(back_populates="scores")