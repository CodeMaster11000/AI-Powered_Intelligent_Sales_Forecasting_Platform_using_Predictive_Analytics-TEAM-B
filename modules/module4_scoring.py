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
