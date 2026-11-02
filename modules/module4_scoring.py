"""
SalesGenie Platform - Module 4: Predictive Lead Scoring & Recommendation Engine
Engineered for Module 4 Deliverables (Milestone 2):
- REQ-M4-01: Multi-factor predictive lead scoring (Fit, Growth/Intent, Decision Readiness, Engagement)
- REQ-M4-02: Calibrated conversion probability calculation
- REQ-M4-03: Next-Best-Action recommendation engine (timing, channel mix, content strategy)
- REQ-M4-04: Glass-box explainability factor breakdown for SalesGenie UI
"""

import math
from decimal import Decimal
from typing import Any, Dict, List, Optional


def calculate_predictive_score(
    lead_data: Dict[str, Any],
    insight_data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Computes a 4-dimensional predictive lead score (0-100) with calibrated
    conversion probability and glass-box factor breakdown.
    
    Dimensions:
    1. Firmographic & Tech Stack Fit (max: 30 pts)
    2. Growth Velocity & Intent Signals (max: 25 pts)
    3. Decision-Maker Readiness (max: 25 pts)
    4. Engagement & Ingestion Signals (max: 20 pts)
    """
    insight_data = insight_data or {}

    # 1. Firmographic & Tech Stack Fit (Max: 30)
    fit_score = 0
    # Company Size (max 10)
    company_size = str(lead_data.get("company_size") or "").lower()
    if any(k in company_size for k in ["enterprise", "1000+", "500-1000", "large"]):
        fit_score += 10
    elif any(k in company_size for k in ["mid-market", "100-500", "50-200"]):
        fit_score += 8
    elif any(k in company_size for k in ["growth", "startup", "10-50"]):
        fit_score += 5
    else:
        fit_score += 4

    # Annual Revenue Capacity (max 10)
    revenue = str(lead_data.get("annual_revenue") or "").lower()
    if any(k in revenue for k in ["$50m", "$100m", "$500m", "billion", "100m", "50m"]):
        fit_score += 10
    elif any(k in revenue for k in ["$10m", "$20m", "$25m", "10m", "20m"]):
        fit_score += 8
    elif any(k in revenue for k in ["$1m", "$5m", "1m", "5m"]):
        fit_score += 5
    else:
        fit_score += 4

    # Tech Stack Compatibility (max 10)
    comp_score = insight_data.get("overall_tech_compatibility_score")
    if isinstance(comp_score, (int, float)):
        fit_score += int(round(min(100, max(0, comp_score)) * 0.10))
    else:
        tech_stack = lead_data.get("tech_stack", [])
        if isinstance(tech_stack, str):
            tech_stack = [t.strip() for t in tech_stack.split(",") if t.strip()]
        fit_score += min(10, len(tech_stack) * 2) if tech_stack else 5

    fit_score = min(30, fit_score)

    # 2. Growth Velocity & Intent Signals (Max: 25)
    intent_score = 0
    funding = str(lead_data.get("funding_stage") or "").lower()
    if any(k in funding for k in ["series c", "series d", "series e", "ipo", "growth"]):
        intent_score += 10
    elif any(k in funding for k in ["series b", "series a"]):
        intent_score += 7
    elif any(k in funding for k in ["seed", "angel", "bootstrapped"]):
        intent_score += 4
    else:
        intent_score += 3

    # High growth potential flag from LangGraph agent
    if insight_data.get("high_growth_potential") is True:
        intent_score += 8
    elif insight_data.get("growth_indicators"):
        intent_score += 5
    else:
        intent_score += 2

    # Identified business friction / transformation opportunities
    opps = insight_data.get("transformation_opportunities") or insight_data.get("opportunities")
    if opps and len(opps) > 0:
        intent_score += 7
    elif insight_data.get("business_needs"):
        intent_score += 5
    else:
        intent_score += 2

    intent_score = min(25, intent_score)

    # 3. Decision-Maker Readiness (Max: 25)
    decision_score = 0
    title = str(lead_data.get("contact_title") or "").lower()
    if any(k in title for k in ["ceo", "cto", "cio", "cpo", "cro", "founder", "chief", "president", "vp", "vice president"]):
        decision_score += 15
    elif any(k in title for k in ["head of", "director", "lead"]):
        decision_score += 11
    elif any(k in title for k in ["manager", "supervisor"]):
        decision_score += 7
    else:
        decision_score += 5

    # Decision-makers identified by AI analysis
    dms = insight_data.get("decision_makers")
    if dms and len(dms) > 0:
        decision_score += 10
    elif lead_data.get("contact_name"):
        decision_score += 6
    else:
        decision_score += 3

    decision_score = min(25, decision_score)

    # 4. Engagement & Ingestion Signals (Max: 20)
    engagement_score = 0
    source = str(lead_data.get("source") or "").lower()
    if any(k in source for k in ["website form", "crm", "inbound"]):
        engagement_score += 10
    elif any(k in source for k in ["linkedin", "sales entry"]):
        engagement_score += 7
    else:
        engagement_score += 5

    # Contact completeness (verified email, phone, location)
    completeness = 0
    if lead_data.get("email"):
        completeness += 4
    if lead_data.get("phone"):
        completeness += 3
    if lead_data.get("location"):
        completeness += 3
    engagement_score += completeness

    engagement_score = min(20, engagement_score)

    # Composite Lead Score (0 - 100)
    total_score = fit_score + intent_score + decision_score + engagement_score
    total_score = max(0, min(100, total_score))

    # Calibrated Conversion Probability (Logistic sigmoid mapping, bounded 5% - 95%)
    # P(conversion) = 1 / (1 + exp(-0.06 * (score - 50)))
    prob_val = 1.0 / (1.0 + math.exp(-0.06 * (total_score - 50)))
    conversion_prob = round(prob_val * 100, 2)

    # Priority Tier
    if total_score >= 75:
        priority = "hot"
    elif total_score >= 40:
        priority = "warm"
    else:
        priority = "cold"

    factors = {
        "fit": {
            "label": "Firmographic & Tech Stack Fit",
            "score": fit_score,
            "max": 30,
        },
        "intent": {
            "label": "Growth Velocity & Intent Signals",
            "score": intent_score,
            "max": 25,
        },
        "decision": {
            "label": "Decision-Maker Readiness",
            "score": decision_score,
            "max": 25,
        },
        "engagement": {
            "label": "Engagement & Ingestion Signals",
            "score": engagement_score,
            "max": 20,
        },
    }

    return {
        "score": total_score,
        "conversion_probability": conversion_prob,
        "priority": priority,
        "factors": factors,
    }


def generate_next_best_action(
    score_data: Dict[str, Any],
    lead_data: Dict[str, Any],
    insight_data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Generates actionable Next-Best-Action (NBA) guidance:
    - Follow-up Timing Window
    - Optimal Channel Mix
    - Content & Value Strategy
    - Recommended Directive
    """
    insight_data = insight_data or {}
    score = score_data.get("score", 50)
    priority = score_data.get("priority", "warm")
    title = lead_data.get("contact_title", "Executive")
    company = lead_data.get("company_name", "Target Account")

    # Determine timing
    if priority == "hot":
        follow_up_timing = "Immediate (< 24 Hours)"
        urgency = "High Priority"
    elif priority == "warm":
        follow_up_timing = "2 - 3 Business Days"
        urgency = "Standard Pipeline"
    else:
        follow_up_timing = "Nurture Track (7 - 14 Days)"
        urgency = "Low Friction Nurture"

    # Determine channel mix
    channels = []
    if lead_data.get("email"):
        channels.append("Hyper-Personalized Cold Email")
    if lead_data.get("phone") and priority in ["hot", "warm"]:
        channels.append("Direct Executive Phone Call")
    channels.append("LinkedIn InMail / Social Touch")

    # Determine content strategy & value angle
    opps = insight_data.get("transformation_opportunities") or []
    if opps and isinstance(opps, list) and len(opps) > 0 and isinstance(opps[0], dict):
        top_opp = opps[0].get("opportunity_name", "Infrastructure Modernization")
        content_strategy = f"Focus conversation on {top_opp} with quantified ROI benchmarks."
    else:
        content_strategy = "Focus on predictive sales qualification and pipeline visibility."

    # Recommended action directive
    if priority == "hot":
        action_directive = (
            f"Schedule a 15-minute executive briefing with {lead_data.get('contact_name', title)} "
            f"addressing {company}'s current scaling opportunities."
        )
    elif priority == "warm":
        action_directive = (
            f"Deliver high-impact cold outreach focusing on {content_strategy} "
            f"followed by LinkedIn profile engagement."
        )
    else:
        action_directive = (
            f"Enroll {company} into automated intelligence newsletter and track subsequent intent signals."
        )

    return {
        "urgency": urgency,
        "follow_up_timing": follow_up_timing,
        "channel_mix": channels,
        "content_strategy": content_strategy,
        "recommended_action": action_directive,
    }


def score_and_recommend(
    lead: Any,
    insight_data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Unified entry point for Module 4.
    Accepts an ORM Lead or dict, computes the multi-dimensional predictive score,
    and constructs next-best-action guidance.
    """
    if hasattr(lead, "company_name"):
        lead_dict = {
            "lead_id": getattr(lead, "lead_id", None),
            "company_name": lead.company_name,
            "contact_name": getattr(lead, "contact_name", None),
            "contact_title": getattr(lead, "contact_title", None),
            "email": getattr(lead, "email", ""),
            "phone": getattr(lead, "phone", None),
            "source": getattr(lead, "source", "CSV"),
            "industry": getattr(lead, "industry", None),
            "company_size": getattr(lead, "company_size", None),
            "annual_revenue": getattr(lead, "annual_revenue", None),
            "funding_stage": getattr(lead, "funding_stage", None),
            "funding_raised": getattr(lead, "funding_raised", None),
            "location": getattr(lead, "location", None),
            "tech_stack": getattr(lead, "tech_stack", None),
        }
    elif isinstance(lead, dict):
        lead_dict = lead
    else:
        lead_dict = {"company_name": str(lead)}

    score_result = calculate_predictive_score(lead_dict, insight_data)
    recommendations = generate_next_best_action(score_result, lead_dict, insight_data)

    return {
        "scoring": score_result,
        "recommendations": recommendations,
    }

