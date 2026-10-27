"""
SalesGenie Platform - Module 2: AI Lead Intelligence & Company Analysis Engine
Engineered for Module 2 Deliverables:
- REQ-M2-01: Automated company profiling
- REQ-M2-02: Business opportunity identification (ERP, Cloud, Process Automation, Digital Transformation)
- REQ-M2-03: Intelligence summary output, Qualification Scoring (0-100), and Decision Maker mapping
"""

import json
from decimal import Decimal
from typing import Dict, Any, List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database.models.leads import Lead
from backend.database.models.company_insights import CompanyInsight
from backend.database.models.lead_scores import LeadScore
from backend.database.models.lead_analysis_runs import LeadAnalysisRun
from backend.ai_agents.graph import (
    run_lead_intelligence_pipeline,
    get_agent_architecture_mermaid,
)


def analyze_lead_intelligence(prospect_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executes the LangGraph multi-agent intelligence pipeline on raw prospect data.
    Does not require database session; suitable for ad-hoc or preview evaluation.
    """
    return run_lead_intelligence_pipeline(prospect_data)


def analyze_and_store_lead_intelligence(db: Session, lead_id: int) -> Dict[str, Any]:
    """
    Fetches lead from database, executes the LangGraph multi-agent pipeline,
    and persists generated insights to company_insights and lead_scores tables.
    Also updates lead_status to 'Qualified' if qualification_score >= 70.
    """
    lead = db.execute(select(Lead).where(Lead.lead_id == lead_id)).scalar_one_or_none()
    if not lead:
        raise ValueError(f"Lead with id {lead_id} not found in database.")

    # Prepare payload for AI agent
    tech_stack_str = ""
    if isinstance(lead.tech_stack, list):
        tech_stack_str = ", ".join(lead.tech_stack)
    elif lead.tech_stack:
        tech_stack_str = str(lead.tech_stack)

    prospect_payload = {
        "lead_id": lead.lead_id,
        "company_name": lead.company_name,
        "industry": lead.industry or "Technology",
        "contact_name": lead.contact_name or "Decision Maker",
        "email": lead.email,
        "phone": lead.phone,
        "company_size": lead.company_size,
        "annual_revenue": lead.annual_revenue,
        "funding_stage": lead.funding_stage,
        "capital_raised": lead.funding_raised,
        "location": lead.location,
        "tech_stack": tech_stack_str,
    }

    # Run LangGraph pipeline
    result_state = run_lead_intelligence_pipeline(prospect_payload)

    raw_score = result_state.get("qualification_score")
    if not isinstance(raw_score, int) or not 0 <= raw_score <= 100:
        raise RuntimeError("Qualification agent did not return a valid score.")
    score = raw_score
    conversion_prob = Decimal(str(round(score * 0.85, 2)))

    # Keep every structured agent field in a dedicated immutable run record.
    analysis_run = LeadAnalysisRun(
        lead_id=lead_id,
        qualification_score=score,
        high_growth_potential=result_state.get("high_growth_potential"),
        funding_analysis=result_state.get("funding_analysis"),
        overall_tech_compatibility_score=result_state.get("overall_tech_compatibility_score"),
        industry_domain_analysis=result_state.get("industry_domain_analysis"),
        business_needs_summary=result_state.get("business_needs_summary"),
        strategic_recommendation=result_state.get("strategic_recommendation"),
        growth_indicators=result_state.get("growth_indicators"),
        tech_stack_components=result_state.get("tech_stack_components"),
        transformation_opportunities=result_state.get("transformation_opportunities"),
        tech_alignment_metrics=result_state.get("tech_alignment_metrics"),
        decision_makers=result_state.get("decision_makers"),
        execution_trace=result_state.get("execution_trace"),
        errors=result_state.get("errors"),
        execution_latency_seconds=result_state.get("execution_latency_seconds"),
    )
    db.add(analysis_run)

    # 1. Update or create CompanyInsight
    existing_insight = db.execute(
        select(CompanyInsight)
        .where(CompanyInsight.lead_id == lead_id)
        .order_by(CompanyInsight.generated_at.desc())
    ).scalars().first()

    opportunities_str = json.dumps(result_state.get("transformation_opportunities", []))
    growth_str = json.dumps(result_state.get("growth_indicators", []))
    tech_alignment_str = json.dumps(result_state.get("tech_alignment_metrics", []))
    decision_makers_str = json.dumps(result_state.get("decision_makers", []))

    if existing_insight:
        existing_insight.business_needs = result_state.get("business_needs_summary")
        existing_insight.opportunities = opportunities_str
        existing_insight.industry_analysis = result_state.get("industry_domain_analysis")
        existing_insight.qualification_score = score
        existing_insight.growth_indicators = growth_str
        existing_insight.tech_alignment = tech_alignment_str
        existing_insight.decision_maker_summary = decision_makers_str
    else:
        new_insight = CompanyInsight(
            lead_id=lead_id,
            business_needs=result_state.get("business_needs_summary"),
            opportunities=opportunities_str,
            industry_analysis=result_state.get("industry_domain_analysis"),
            qualification_score=score,
            growth_indicators=growth_str,
            tech_alignment=tech_alignment_str,
            decision_maker_summary=decision_makers_str,
        )
        db.add(new_insight)

    # 2. Update or create LeadScore
    existing_score = db.execute(
        select(LeadScore)
        .where(LeadScore.lead_id == lead_id)
        .order_by(LeadScore.generated_at.desc())
    ).scalars().first()

    if existing_score:
        existing_score.lead_score = score
        existing_score.conversion_probability = conversion_prob
    else:
        new_score = LeadScore(
            lead_id=lead_id,
            lead_score=score,
            conversion_probability=conversion_prob,
        )
        db.add(new_score)

    # 3. Lifecycle stage tracking: promote to Qualified if score >= 70
    if score >= 70 and lead.lead_status == "New Leads":
        lead.lead_status = "Qualified"

    db.commit()

    return {
        "lead_id": lead_id,
        "company_name": lead.company_name,
        "qualification_score": score,
        "conversion_probability": float(conversion_prob),
        "lead_status": lead.lead_status,
        "high_growth_potential": result_state.get("high_growth_potential"),
        "business_needs": result_state.get("business_needs_summary"),
        "strategic_recommendation": result_state.get("strategic_recommendation"),
        "industry_analysis": result_state.get("industry_domain_analysis"),
        "transformation_opportunities": result_state.get("transformation_opportunities"),
        "tech_alignment_metrics": result_state.get("tech_alignment_metrics"),
        "decision_makers": result_state.get("decision_makers"),
        "growth_indicators": result_state.get("growth_indicators"),
        "tech_stack_components": result_state.get("tech_stack_components"),
        "overall_tech_compatibility_score": result_state.get("overall_tech_compatibility_score"),
        "funding_analysis": result_state.get("funding_analysis"),
        "execution_trace": result_state.get("execution_trace"),
        "execution_latency_seconds": result_state.get("execution_latency_seconds"),
    }


def get_lead_insights(db: Session, lead_id: int) -> Optional[Dict[str, Any]]:
    """Retrieves the latest complete structured intelligence run for a lead."""
    analysis_run = db.execute(
        select(LeadAnalysisRun)
        .where(LeadAnalysisRun.lead_id == lead_id)
        .order_by(LeadAnalysisRun.generated_at.desc(), LeadAnalysisRun.analysis_id.desc())
    ).scalars().first()

    if analysis_run:
        score = db.execute(
            select(LeadScore)
            .where(LeadScore.lead_id == lead_id)
            .order_by(LeadScore.generated_at.desc())
        ).scalars().first()
        return {
            "analysis_id": analysis_run.analysis_id,
            "lead_id": analysis_run.lead_id,
            "qualification_score": analysis_run.qualification_score,
            "conversion_probability": float(score.conversion_probability) if score else None,
            "high_growth_potential": analysis_run.high_growth_potential,
            "funding_analysis": analysis_run.funding_analysis,
            "overall_tech_compatibility_score": analysis_run.overall_tech_compatibility_score,
            "business_needs": analysis_run.business_needs_summary,
            "business_needs_summary": analysis_run.business_needs_summary,
            "strategic_recommendation": analysis_run.strategic_recommendation,
            "industry_analysis": analysis_run.industry_domain_analysis,
            "industry_domain_analysis": analysis_run.industry_domain_analysis,
            "opportunities": analysis_run.transformation_opportunities,
            "transformation_opportunities": analysis_run.transformation_opportunities,
            "growth_indicators": analysis_run.growth_indicators,
            "tech_stack_components": analysis_run.tech_stack_components,
            "tech_alignment": analysis_run.tech_alignment_metrics,
            "tech_alignment_metrics": analysis_run.tech_alignment_metrics,
            "decision_maker_summary": analysis_run.decision_makers,
            "decision_makers": analysis_run.decision_makers,
            "execution_trace": analysis_run.execution_trace,
            "errors": analysis_run.errors,
            "execution_latency_seconds": analysis_run.execution_latency_seconds,
            "generated_at": str(analysis_run.generated_at),
        }

    # Backward-compatible read path for databases that have not been rescored
    # since the structured analysis table was introduced.
    insight = db.execute(
        select(CompanyInsight)
        .where(CompanyInsight.lead_id == lead_id)
        .order_by(CompanyInsight.generated_at.desc())
    ).scalars().first()
    if not insight:
        return None

    score = db.execute(
        select(LeadScore)
        .where(LeadScore.lead_id == lead_id)
        .order_by(LeadScore.generated_at.desc())
    ).scalars().first()

    return {
        "insight_id": insight.insight_id,
        "lead_id": insight.lead_id,
        "qualification_score": insight.qualification_score,
        "conversion_probability": float(score.conversion_probability) if score else None,
        "business_needs": insight.business_needs,
        "opportunities": _safe_json_loads(insight.opportunities),
        "industry_analysis": insight.industry_analysis,
        "growth_indicators": _safe_json_loads(insight.growth_indicators),
        "tech_alignment": _safe_json_loads(insight.tech_alignment),
        "decision_maker_summary": _safe_json_loads(insight.decision_maker_summary),
        "strategic_recommendation": None,
        "high_growth_potential": None,
        "tech_stack_components": None,
        "tech_alignment_metrics": _safe_json_loads(insight.tech_alignment),
        "decision_makers": _safe_json_loads(insight.decision_maker_summary),
        "execution_trace": None,
        "errors": None,
        "execution_latency_seconds": None,
        "generated_at": str(insight.generated_at),
    }


def batch_analyze_leads(db: Session, lead_ids: List[int]) -> List[Dict[str, Any]]:
    """Executes multi-agent intelligence analysis for a list of leads."""
    results = []
    for lid in lead_ids:
        try:
            res = analyze_and_store_lead_intelligence(db, lid)
            results.append(res)
        except Exception as e:
            results.append({"lead_id": lid, "error": str(e)})
    return results


def get_architecture_diagram() -> str:
    """Returns the LangGraph Multi-Agent Architecture topology diagram."""
    return get_agent_architecture_mermaid()


def _safe_json_loads(val: Optional[str]):
    if not val:
        return None
    try:
        return json.loads(val)
    except Exception:
        return val
