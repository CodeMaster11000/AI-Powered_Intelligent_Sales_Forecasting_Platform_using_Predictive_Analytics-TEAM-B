from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database.models.lead_scores import LeadScore
from backend.database.models.leads import Lead


def calculate_lead_score(lead: Lead) -> dict:
    """Calculates lead score, probability, and factor points from lead attributes."""
    
    # 1. Authority / Decision Maker (Max 20 pts)
    authority_pts = 8
    title = (lead.contact_title or "").lower()
    if any(k in title for k in ["vp", "vice president", "chief", "cto", "cio", "cpo", "founder", "head"]):
        authority_pts = 20
    elif any(k in title for k in ["director", "lead", "architect"]):
        authority_pts = 15
    elif any(k in title for k in ["manager", "principal"]):
        authority_pts = 12

    # 2. Firmographic & Size Fit (Max 30 pts)
    size_pts = 12
    size = (lead.company_size or "").lower()
    if any(k in size for k in ["51", "100", "200", "250", "500"]):
        size_pts = 30  # Prime sweet spot for B2B SaaS
    elif any(k in size for k in ["501", "1000", "1000+"]):
        size_pts = 24
    elif any(k in size for k in ["11", "50"]):
        size_pts = 18

    # 3. Growth & Investment Signals (Max 25 pts)
    growth_pts = 5
    funding = (lead.funding_stage or "").lower()
    if any(k in funding for k in ["series b", "series c", "growth"]):
        growth_pts = 25
    elif any(k in funding for k in ["series a"]):
        growth_pts = 20
    elif any(k in funding for k in ["seed"]):
        growth_pts = 14

    # 4. Tech Stack Fit (Max 25 pts)
    tech_pts = 6
    stack = lead.tech_stack or []
    if isinstance(stack, list):
        high_value_tech = {"aws", "kubernetes", "snowflake", "postgresql", "salesforce", "docker", "python"}
        matched = sum(1 for t in stack if str(t).strip().lower() in high_value_tech)
        tech_pts = min(25, 8 + (matched * 6))

    total_score = min(100, max(0, authority_pts + size_pts + growth_pts + tech_pts))
    conversion_prob = round(total_score * 0.72 + 2.5, 2)

    priority = "hot" if total_score >= 75 else ("warm" if total_score >= 40 else "cold")

    return {
        "score": total_score,
        "conversion_probability": conversion_prob,
        "priority": priority,
        "factors": {
            "firmographic_fit": {"score": size_pts, "max": 30, "label": "Company Size & Profile"},
            "tech_alignment": {"score": tech_pts, "max": 25, "label": "Tech Stack Fit"},
            "growth_velocity": {"score": growth_pts, "max": 25, "label": "Funding & Growth Stage"},
            "decision_maker": {"score": authority_pts, "max": 20, "label": "Decision-Maker Level"},
        },
    }


def score_lead(db: Session, lead_id: int) -> dict:
    """Scores a lead and saves the score to PostgreSQL."""
    lead = db.get(Lead, lead_id)
    if not lead:
        raise ValueError(f"Lead ID {lead_id} not found.")

    score_result = calculate_lead_score(lead)

    db_score = LeadScore(
        lead_id=lead.lead_id,
        lead_score=score_result["score"],
        conversion_probability=Decimal(str(score_result["conversion_probability"])),
    )
    db.add(db_score)
    db.commit()

    return score_result