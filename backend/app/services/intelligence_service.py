import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from backend.app.models.schema_models import Lead, CompanyInsight
from backend.app.schemas.intelligence import (
    CompanyIntelligenceResponse,
    TransformationOpportunity,
    TechAlignmentMetric,
    DecisionMakerProfile
)
from backend.app.ai_agents.graph import run_lead_intelligence_pipeline

logger = logging.getLogger(__name__)

class IntelligenceService:
    @staticmethod
    def analyze_lead(db: Session, lead_id: int) -> Optional[CompanyIntelligenceResponse]:
        """
        Executes Module 2 Lead Intelligence workflow for a specific Lead.
        Adheres to REQ-M2-01, REQ-M2-02, REQ-M2-03.
        """
        lead = db.query(Lead).filter(Lead.lead_id == lead_id).first()
        if not lead:
            return None

        prospect_payload = {
            "lead_id": lead.lead_id,
            "company_name": lead.company_name,
            "industry": lead.industry,
            "contact_name": lead.contact_name,
            "email": lead.email,
            "phone": lead.phone,
            "company_size": lead.company_size,
            "annual_revenue": lead.annual_revenue,
            "funding_stage": lead.funding_stage,
            "capital_raised": lead.capital_raised,
            "location": lead.location,
            "tech_stack": lead.tech_stack
        }

        # Run LangGraph pipeline
        result = run_lead_intelligence_pipeline(prospect_payload)

        # Upsert into Company_Insights
        existing_insight = db.query(CompanyInsight).filter(CompanyInsight.lead_id == lead.lead_id).first()
        if not existing_insight:
            existing_insight = CompanyInsight(lead_id=lead.lead_id)
            db.add(existing_insight)

        existing_insight.qualification_score = result.get("qualification_score", 0)
        existing_insight.business_needs = result.get("business_needs_summary", "")
        existing_insight.opportunities = json.dumps(result.get("transformation_opportunities", []))
        existing_insight.industry_analysis = result.get("industry_domain_analysis", "")
        existing_insight.tech_alignment = json.dumps(result.get("tech_alignment_metrics", []))
        existing_insight.decision_maker_summary = json.dumps(result.get("decision_makers", []))
        existing_insight.high_growth_indicators = json.dumps(result.get("growth_indicators", []))
        existing_insight.raw_agent_output = json.dumps({
            "trace": result.get("execution_trace", []),
            "latency": result.get("execution_latency_seconds", 0.0)
        })
        existing_insight.generated_at = datetime.utcnow()

        db.commit()
        db.refresh(existing_insight)

        # Build response schema
        opps = [TransformationOpportunity(**o) for o in result.get("transformation_opportunities", [])]
        tech_metrics = [TechAlignmentMetric(**t) for t in result.get("tech_alignment_metrics", [])]
        dms = [DecisionMakerProfile(**d) for d in result.get("decision_makers", [])]

        return CompanyIntelligenceResponse(
            lead_id=lead.lead_id,
            company_name=lead.company_name,
            qualification_score=result.get("qualification_score", 0),
            high_growth_potential=result.get("high_growth_potential", False),
            growth_indicators=result.get("growth_indicators", []),
            funding_analysis=result.get("funding_analysis", ""),
            transformation_opportunities=opps,
            industry_domain_analysis=result.get("industry_domain_analysis", ""),
            tech_alignment_metrics=tech_metrics,
            overall_tech_compatibility_score=result.get("overall_tech_compatibility_score", 85),
            decision_makers=dms,
            business_needs_summary=result.get("business_needs_summary", ""),
            strategic_recommendation=result.get("strategic_recommendation", ""),
            generated_at=existing_insight.generated_at
        )

intelligence_service = IntelligenceService()
