"""Module 4: explainable lead scoring and conversion probability."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class LeadScoringResult:
    engagement_score: int
    fit_score: int
    intent_score: int
    decision_readiness_score: int
    lead_score: int
    conversion_probability: float
    factors: dict[str, list[str]]


def calculate_lead_score(lead: Any, intelligence: dict[str, Any] | None = None) -> LeadScoringResult:
    """Calculate a bounded, explainable score from lead and intelligence signals."""
    intelligence = intelligence or {}
    engagement, engagement_factors = _engagement_score(lead)
    fit, fit_factors = _fit_score(lead, intelligence)
    intent, intent_factors = _intent_score(lead, intelligence)
    readiness, readiness_factors = _decision_readiness_score(lead, intelligence)

    total = round(
        engagement * 0.20
        + fit * 0.30
        + intent * 0.30
        + readiness * 0.20
    )
    probability = round(min(100.0, max(0.0, total * 0.85)), 2)

    return LeadScoringResult(
        engagement_score=engagement,
        fit_score=fit,
        intent_score=intent,
        decision_readiness_score=readiness,
        lead_score=total,
        conversion_probability=probability,
        factors={
            "engagement": engagement_factors,
            "fit": fit_factors,
            "intent": intent_factors,
            "decision_readiness": readiness_factors,
        },
    )


def _engagement_score(lead: Any) -> tuple[int, list[str]]:
    score = 20
    factors = ["Baseline engagement score"]
    status = str(getattr(lead, "lead_status", "") or "")
    source = str(getattr(lead, "source", "") or "")

    if status in {"Qualified", "Proposal", "Negotiation", "Closed Won"}:
        score += 35
        factors.append(f"Lifecycle stage indicates active engagement: {status}")
    elif status == "New Leads":
        score += 10
        factors.append("New lead has baseline engagement only")

    if source in {"Website Form", "Sales Entry"}:
        score += 25
        factors.append(f"High-intent acquisition source: {source}")
    elif source in {"LinkedIn", "CRM"}:
        score += 15
        factors.append(f"Tracked acquisition source: {source}")

    if getattr(lead, "contact_name", None):
        score += 10
        factors.append("Named contact is available")
    if getattr(lead, "email", None):
        score += 10
        factors.append("Reachable email is available")
    return min(score, 100), factors


def _fit_score(lead: Any, intelligence: dict[str, Any]) -> tuple[int, list[str]]:
    score = 20
    factors = ["Baseline firmographic fit score"]
    tech_stack = _as_text(getattr(lead, "tech_stack", None)).lower()
    industry = _as_text(getattr(lead, "industry", None)).lower()
    size = _as_text(getattr(lead, "company_size", None)).lower()
    revenue = _as_text(getattr(lead, "annual_revenue", None)).lower()

    modern_stack = ("aws", "gcp", "azure", "kubernetes", "docker", "python", "react")
    matched_stack = [item for item in modern_stack if item in tech_stack]
    score += min(30, len(matched_stack) * 6)
    if matched_stack:
        factors.append(f"Modern technology fit: {', '.join(matched_stack)}")

    if any(token in size for token in ("100-", "250-", "500-", "1000+", "enterprise")):
        score += 15
        factors.append("Target company size supports enterprise adoption")
    if "$" in revenue or any(token in revenue for token in ("million", "m")):
        score += 10
        factors.append("Revenue signal supports purchasing capacity")
    if industry:
        score += 10
        factors.append(f"Industry context supplied: {industry}")
    if intelligence.get("overall_tech_compatibility_score", 0) >= 70:
        score += 15
        factors.append("AI intelligence reports strong technology compatibility")
    return min(score, 100), factors


def _intent_score(lead: Any, intelligence: dict[str, Any]) -> tuple[int, list[str]]:
    score = 15
    factors = ["Baseline buying-intent score"]
    funding = _as_text(getattr(lead, "funding_stage", None)).lower()
    opportunities = intelligence.get("transformation_opportunities") or []
    needs = _as_text(intelligence.get("business_needs_summary")).lower()

    if any(stage in funding for stage in ("series b", "series c", "series d", "public")):
        score += 30
        factors.append(f"Growth funding indicates active investment capacity: {funding}")
    elif funding:
        score += 15
        factors.append(f"Funding stage supplied: {funding}")
    if opportunities:
        score += min(30, len(opportunities) * 10)
        factors.append(f"{len(opportunities)} transformation opportunity signals detected")
    if needs:
        score += 15
        factors.append("Documented business need provides an intent signal")
    if intelligence.get("high_growth_potential") is True:
        score += 10
        factors.append("AI intelligence flags high growth potential")
    return min(score, 100), factors


def _decision_readiness_score(
    lead: Any, intelligence: dict[str, Any]
) -> tuple[int, list[str]]:
    score = 15
    factors = ["Baseline decision-readiness score"]
    contact = _as_text(getattr(lead, "contact_name", None)).lower()
    title = _as_text(getattr(lead, "contact_title", None)).lower()
    decision_makers = intelligence.get("decision_makers") or []

    senior_titles = ("ceo", "cto", "cfo", "coo", "cpo", "chief", "vp", "vice president", "director", "head")
    if any(item in title or item in contact for item in senior_titles):
        score += 35
        factors.append("Primary contact appears to be a senior decision maker")
    elif contact:
        score += 15
        factors.append("Named contact is available")
    if getattr(lead, "email", None):
        score += 15
        factors.append("Contact channel is available")
    if decision_makers:
        score += 20
        factors.append("AI analysis identified a buying committee persona")
    if getattr(lead, "owner_user_id", None):
        score += 15
        factors.append("Lead is assigned to an owner")
    return min(score, 100), factors


def _as_text(value: Any) -> str:
    if isinstance(value, list):
        return ", ".join(str(item) for item in value)
    return str(value or "")


def calculate_predictive_score(
    lead_data: dict[str, Any],
    insight_data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return the legacy dictionary contract used by the scoring UI."""
    insight_data = insight_data or {}
    tech_stack = _as_text(lead_data.get("tech_stack")).lower()
    size = _as_text(lead_data.get("company_size")).lower()
    revenue = _as_text(lead_data.get("annual_revenue")).lower()
    funding = _as_text(lead_data.get("funding_stage")).lower()

    fit = 10 if any(value in size for value in ("enterprise", "1000+", "500-1000", "large")) else 5
    fit += 10 if any(value in revenue for value in ("50m", "100m", "500m", "billion")) else 5
    fit += round(min(100, max(0, float(insight_data.get("overall_tech_compatibility_score", 50)))) / 10)
    fit = min(30, fit)

    intent = 10 if any(value in funding for value in ("series c", "series d", "ipo", "growth")) else 7 if "series" in funding else 4
    intent += 8 if insight_data.get("high_growth_potential") else 5 if insight_data.get("growth_indicators") else 2
    opportunities = insight_data.get("transformation_opportunities") or insight_data.get("opportunities")
    intent += 7 if opportunities else 5 if insight_data.get("business_needs") else 2
    intent = min(25, intent)

    title = _as_text(lead_data.get("contact_title")).lower()
    decision = 15 if any(value in title for value in ("ceo", "cto", "cio", "chief", "president", "vp", "founder")) else 11 if any(value in title for value in ("director", "head", "lead")) else 5
    decision += 10 if insight_data.get("decision_makers") else 6 if lead_data.get("contact_name") else 3
    decision = min(25, decision)

    source = _as_text(lead_data.get("source")).lower()
    engagement = 10 if any(value in source for value in ("website form", "crm", "inbound")) else 7 if any(value in source for value in ("linkedin", "sales entry")) else 5
    engagement += sum(1 for key in ("email", "phone", "location") if lead_data.get(key)) * 3
    engagement = min(20, engagement)

    score = min(100, fit + intent + decision + engagement)
    probability = round(100 / (1 + __import__("math").exp(-0.06 * (score - 50))), 2)
    priority = "hot" if score >= 75 else "warm" if score >= 40 else "cold"
    return {
        "score": score,
        "conversion_probability": probability,
        "priority": priority,
        "factors": {
            "fit": {"score": fit, "max": 30},
            "intent": {"score": intent, "max": 25},
            "decision": {"score": decision, "max": 25},
            "engagement": {"score": engagement, "max": 20},
        },
    }


def generate_next_best_action(
    score_data: dict[str, Any],
    lead_data: dict[str, Any],
    insight_data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Generate an actionable follow-up recommendation for a scored lead."""
    insight_data = insight_data or {}
    priority = score_data.get("priority", "warm")
    timing = {"hot": "Immediate (< 24 Hours)", "warm": "2 - 3 Business Days"}.get(
        priority, "Nurture Track (7 - 14 Days)"
    )
    urgency = {"hot": "High Priority", "warm": "Standard Pipeline"}.get(
        priority, "Low Friction Nurture"
    )
    channels = ["LinkedIn InMail / Social Touch"]
    if lead_data.get("email"):
        channels.insert(0, "Hyper-Personalized Cold Email")
    if lead_data.get("phone") and priority in {"hot", "warm"}:
        channels.insert(1, "Direct Executive Phone Call")
    opportunities = insight_data.get("transformation_opportunities") or []
    opportunity = opportunities[0].get("opportunity_name") if opportunities and isinstance(opportunities[0], dict) else "predictive sales qualification"
    return {
        "urgency": urgency,
        "follow_up_timing": timing,
        "channel_mix": channels,
        "content_strategy": f"Focus conversation on {opportunity} with quantified ROI benchmarks.",
        "recommended_action": f"Schedule a discovery session with {lead_data.get('contact_name', 'the primary contact')}.",
    }


def score_and_recommend(
    lead_data: dict[str, Any],
    insight_data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    scoring = calculate_predictive_score(lead_data, insight_data)
    return {
        "scoring": scoring,
        "recommendations": generate_next_best_action(scoring, lead_data, insight_data),
    }
