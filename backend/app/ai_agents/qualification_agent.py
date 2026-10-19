import logging
from typing import Dict, Any, List
from backend.app.ai_agents.state import AgentState
from backend.app.ai_agents.prompts import QUALIFICATION_AGENT_SYSTEM_PROMPT
from backend.app.ai_agents.llm_client import llm_client

logger = logging.getLogger(__name__)

def qualification_agent_node(state: AgentState) -> Dict[str, Any]:
    """
    LangGraph Node: Qualification Agent (Module 2: REQ-M2-03)
    Computes overall Qualification Score (0-100), detects High Growth Potential indicators,
    Tech Alignment metrics, and Decision Maker identification summaries.
    """
    company_name = state.get("company_name", "")
    industry = state.get("industry", "")
    contact_name = state.get("contact_name", "")
    funding = state.get("funding_stage", "") or ""
    capital = state.get("capital_raised", "") or ""
    revenue = state.get("annual_revenue", "") or ""
    size = state.get("company_size", "") or ""
    tech_stack_raw = state.get("tech_stack", "") or ""
    tech_components = state.get("tech_stack_components", {})
    opportunities = state.get("transformation_opportunities", [])
    
    trace = state.get("execution_trace", [])
    trace.append(f"QualificationAgent: Evaluating qualification score and business signals for {company_name}.")

    user_payload = f"""
    Company: {company_name}
    Contact: {contact_name}
    Industry: {industry}
    Funding: {funding} ({capital})
    Size: {size}
    Revenue: {revenue}
    Tech Components: {tech_components}
    Opportunities: {opportunities}
    """

    llm_output = llm_client.generate_json(QUALIFICATION_AGENT_SYSTEM_PROMPT, user_payload)
    if llm_output and "qualification_score" in llm_output:
        trace.append(f"QualificationAgent: Computed qualification score of {llm_output['qualification_score']} via LLM.")
        return {
            "qualification_score": llm_output.get("qualification_score", 85),
            "high_growth_potential": llm_output.get("high_growth_potential", "Series" in funding),
            "funding_analysis": llm_output.get("funding_analysis", f"{funding} funding provides verified expansion budget."),
            "tech_alignment_metrics": llm_output.get("tech_alignment_metrics", _build_tech_alignment(tech_components)),
            "overall_tech_compatibility_score": llm_output.get("overall_tech_compatibility_score", 88),
            "decision_makers": llm_output.get("decision_makers", _profile_decision_makers(contact_name, industry)),
            "business_needs_summary": llm_output.get("business_needs_summary", "Needs modern automated AI orchestration to accelerate sales pipeline throughput."),
            "strategic_recommendation": llm_output.get("strategic_recommendation", "Direct outreach highlighting 40% infra cost reduction and 65% faster cycle times."),
            "execution_trace": trace
        }

    # Deterministic IEEE SRS Compliant Scoring Engine
    score = _calculate_qualification_score(funding, revenue, size, tech_stack_raw, contact_name)
    high_growth = _check_high_growth(funding, capital)
    funding_analysis = _generate_funding_analysis(company_name, funding, capital)
    tech_metrics, overall_compat = _build_tech_alignment(tech_components)
    decision_makers = _profile_decision_makers(contact_name, industry)
    needs_summary = _build_needs_summary(company_name, funding, tech_stack_raw)
    recommendation = _build_strategic_recommendation(company_name, funding, score)

    trace.append(f"QualificationAgent: Calculated qualification score of {score}/100. High Growth = {high_growth}.")

    return {
        "qualification_score": score,
        "high_growth_potential": high_growth,
        "funding_analysis": funding_analysis,
        "tech_alignment_metrics": tech_metrics,
        "overall_tech_compatibility_score": overall_compat,
        "decision_makers": decision_makers,
        "business_needs_summary": needs_summary,
        "strategic_recommendation": recommendation,
        "execution_trace": trace
    }

def _calculate_qualification_score(funding: str, revenue: str, size: str, tech_stack: str, contact: str) -> int:
    score = 40  # baseline base points
    
    # Growth & Funding Factor (+25 points max)
    if "Series C" in funding or "Series D" in funding:
        score += 25
    elif "Series B" in funding:
        score += 20
    elif "Series A" in funding:
        score += 15
    elif "Public" in funding:
        score += 22
    elif "Seed" in funding:
        score += 10
    else:
        score += 8
        
    # Tech Alignment & Modern Stack (+20 points max)
    low_stack = tech_stack.lower()
    tech_points = 0
    if any(k in low_stack for k in ["aws", "gcp", "azure"]):
        tech_points += 7
    if any(k in low_stack for k in ["kubernetes", "docker", "microservices"]):
        tech_points += 6
    if any(k in low_stack for k in ["python", "node.js", "react", "fastapi"]):
        tech_points += 7
    score += min(20, tech_points)
    
    # Headcount & Revenue Budget Capacity (+15 points max)
    if any(k in size for k in ["250-500", "500-1000", "1000+"]):
        score += 10
    elif any(k in size for k in ["100-250", "80-150"]):
        score += 8
    else:
        score += 5
        
    # Decision Maker Title Alignment (+10 points max)
    contact_lower = contact.lower()
    if any(title in contact_lower for title in ["cto", "ceo", "cpo", "coo", "vp", "chief", "head", "director"]):
        score += 10
    else:
        score += 7
        
    return min(98, max(45, score))

def _check_high_growth(funding: str, capital: str) -> bool:
    return any(stage in funding for stage in ["Series B", "Series C", "Series D"])

def _generate_funding_analysis(company: str, funding: str, capital: str) -> str:
    if "Series C" in funding:
        return (
            f"Series C funding ({capital or '$28M+'}) signals aggressive commercial expansion, "
            f"allocated departmental tool budgets, and urgent need for scalable revenue infrastructure."
        )
    elif "Series B" in funding:
        return (
            f"Series B capital ({capital or '$15M+'}) focuses on operational scaling and sales acceleration."
        )
    elif "Seed" in funding or "Series A" in funding:
        return "Early-stage growth with focus on product-market fit and capital efficiency."
    return "Established balance sheet with recurring enterprise procurement capacity."

def _build_tech_alignment(tech_components: Dict[str, List[str]]):
    metrics = []
    
    cloud_items = tech_components.get("Cloud", [])
    metrics.append({
        "category": "Cloud Infrastructure",
        "prospect_stack": cloud_items if cloud_items else ["Standard Cloud"],
        "compatibility_score": 95 if cloud_items else 70,
        "alignment_notes": "Cloud-native infrastructure facilitates zero-friction API webhook integration."
    })
    
    data_items = tech_components.get("Data/DB", [])
    metrics.append({
        "category": "Data & Persistence",
        "prospect_stack": data_items if data_items else ["Relational DB"],
        "compatibility_score": 90 if data_items else 75,
        "alignment_notes": "Compatible data schemas allow bidirectional CRM and analytics ingestion."
    })
    
    devops_items = tech_components.get("DevOps", [])
    metrics.append({
        "category": "Containerization & DevOps",
        "prospect_stack": devops_items if devops_items else ["Container Baseline"],
        "compatibility_score": 92 if devops_items else 65,
        "alignment_notes": "Containerized workloads ensure predictable microservice integration latency."
    })
    
    overall = int(sum(m["compatibility_score"] for m in metrics) / len(metrics))
    return metrics, overall

def _profile_decision_makers(contact_name: str, industry: str) -> List[Dict[str, Any]]:
    return [
        {
            "name": contact_name,
            "role_title": "Primary Technical / Operational Decision Maker",
            "authority_level": "High (Budget & Technical Sign-off)",
            "likely_pain_points": [
                "Sales team spend too much time on manual prospect research",
                "Lack of standardized personalized outreach messaging",
                "Need for real-time visibility into pipeline conversion probabilities"
            ],
            "recommended_pitch_angle": "Emphasize agentic automation saving 15+ hours/week per rep with 65% faster qualification."
        },
        {
            "name": "VP of Sales / Head of RevOps",
            "role_title": "Commercial Buying Sponsor",
            "authority_level": "High (Commercial Authorization)",
            "likely_pain_points": [
                "Low email open & conversion rates from cold lists",
                "Suboptimal lead routing and delayed follow-up actions"
            ],
            "recommended_pitch_angle": "Demonstrate predictive conversion scoring and automatic next-best-action alerts."
        }
    ]

def _build_needs_summary(company: str, funding: str, tech_stack: str) -> str:
    return (
        f"{company} urgently requires an enterprise-grade AI Sales Assistant to eliminate manual research "
        f"friction, accelerate lead qualification, and synchronize high-converting outreach with their existing CRM stack."
    )

def _build_strategic_recommendation(company: str, funding: str, score: int) -> str:
    if score >= 85:
        return f"HIGH PRIORITY ENGAGEMENT: Target immediately with tailored multi-channel outreach referencing their {funding} expansion milestones and ROI benchmarks."
    elif score >= 70:
        return "MEDIUM PRIORITY: Send relevant industry case study and schedule technical exploration call within 5 business days."
    return "NURTURE STREAM: Enroll in bi-weekly educational content track focusing on digital transformation."
