import logging
from typing import Dict, Any, List
from backend.ai_agents.state import AgentState
from backend.ai_agents.prompts import RESEARCH_AGENT_SYSTEM_PROMPT
from backend.ai_agents.llm_client import llm_client

logger = logging.getLogger(__name__)


def research_agent_node(state: AgentState) -> Dict[str, Any]:
    """
    LangGraph Node: Research Agent (Module 2: REQ-M2-01 & REQ-M2-02)
    Performs automated company profiling, tech stack categorization,
    and business transformation opportunity detection.
    """
    company_name = state.get("company_name", "")
    industry = state.get("industry", "")
    tech_stack_raw = state.get("tech_stack", "") or ""
    size = state.get("company_size", "") or ""
    revenue = state.get("annual_revenue", "") or ""
    funding = state.get("funding_stage", "") or ""
    capital = state.get("capital_raised", "") or ""
    location = state.get("location", "") or ""

    trace = state.get("execution_trace", [])
    trace.append(f"ResearchAgent: Ingested prospect profile for {company_name} ({industry}).")

    user_payload = f"""
    Company: {company_name}
    Industry: {industry}
    Headcount / Size: {size}
    Annual Revenue: {revenue}
    Funding Stage: {funding} ({capital})
    Location: {location}
    Active Tech Stack: {tech_stack_raw}
    """

    # Attempt LLM extraction
    llm_output = llm_client.generate_json(RESEARCH_AGENT_SYSTEM_PROMPT, user_payload)

    if llm_output and "transformation_opportunities" in llm_output:
        trace.append("ResearchAgent: Extracted profile and transformation opportunities via LLM.")
        return {
            "industry_domain_analysis": llm_output.get(
                "industry_domain_analysis", f"Deep enterprise domain analysis for {company_name} in {industry}."
            ),
            "growth_indicators": llm_output.get(
                "growth_indicators", [f"{funding} stage with {capital} capital"]
            ),
            "tech_stack_components": llm_output.get(
                "tech_stack_components", _parse_tech_stack_components(tech_stack_raw)
            ),
            "transformation_opportunities": llm_output.get(
                "transformation_opportunities", _detect_opportunities(tech_stack_raw, industry, size)
            ),
            "execution_trace": trace,
        }

    # Deterministic Heuristic Engine (Grounded fallback per IEEE SRS specifications)
    trace.append("ResearchAgent: Applied IEEE 830 compliant rule-based intelligence grounding engine.")

    tech_components = _parse_tech_stack_components(tech_stack_raw)
    opportunities = _detect_opportunities(tech_stack_raw, industry, size)
    growth_indicators = _extract_growth_indicators(funding, capital, size, revenue)
    domain_analysis = _generate_domain_analysis(company_name, industry, size, location)

    return {
        "industry_domain_analysis": domain_analysis,
        "growth_indicators": growth_indicators,
        "tech_stack_components": tech_components,
        "transformation_opportunities": opportunities,
        "execution_trace": trace,
    }


def _parse_tech_stack_components(tech_stack_raw: str) -> Dict[str, List[str]]:
    tokens = [t.strip() for t in str(tech_stack_raw).split(",") if t.strip()]
    components = {
        "Cloud": [],
        "Backend": [],
        "Frontend": [],
        "Data/DB": [],
        "DevOps": [],
    }

    cloud_keywords = {"aws", "azure", "gcp", "hybrid cloud", "cloud hosting", "cloud"}
    backend_keywords = {"python", "node.js", "go", "java", "spring boot", "c#", ".net", "graphql", "fastapi"}
    frontend_keywords = {"react", "react native", "next.js", "vue", "angular"}
    data_keywords = {"postgresql", "postgres", "mongodb", "oracle", "snowflake", "spark", "kafka", "redis", "vector db"}
    devops_keywords = {"kubernetes", "docker", "terraform", "airflow", "microservices"}

    for token in tokens:
        low = token.lower()
        if any(k in low for k in cloud_keywords):
            components["Cloud"].append(token)
        elif any(k in low for k in backend_keywords):
            components["Backend"].append(token)
        elif any(k in low for k in frontend_keywords):
            components["Frontend"].append(token)
        elif any(k in low for k in data_keywords):
            components["Data/DB"].append(token)
        elif any(k in low for k in devops_keywords):
            components["DevOps"].append(token)
        else:
            components["Backend"].append(token)

    return components


def _detect_opportunities(tech_stack_raw: str, industry: str, size: str) -> List[Dict[str, Any]]:
    low_stack = str(tech_stack_raw).lower()
    low_ind = str(industry).lower()

    opportunities = []

    # 1. ERP Modernization Needs (REQ-M2-02)
    has_legacy_erp = any(k in low_stack for k in ["sap", "oracle", "legacy", "windows server", "on-premises"])
    opportunities.append({
        "opportunity_name": "ERP Modernization Needs",
        "detected": has_legacy_erp or ("manufacturing" in low_ind or "enterprise" in low_ind),
        "confidence": 0.92 if has_legacy_erp else 0.65,
        "details": "Legacy on-premise ERP & enterprise databases present high maintenance overhead and lack API scalability.",
        "impact_level": "High" if has_legacy_erp else "Medium",
        "estimated_roi_timeline": "6-9 months post implementation",
    })

    # 2. Cloud Migration Opportunities (REQ-M2-02)
    has_onprem_or_hybrid = any(k in low_stack for k in ["on-premises", "hybrid", "windows server", "oracle"])
    opportunities.append({
        "opportunity_name": "Cloud Migration Opportunities",
        "detected": has_onprem_or_hybrid or ("cloud" not in low_stack and "aws" not in low_stack and "azure" not in low_stack),
        "confidence": 0.95 if has_onprem_or_hybrid else 0.40,
        "details": "Opportunities to transition core workloads to containerized AWS/Azure cloud infrastructure, reducing infra cost by 35-40%.",
        "impact_level": "High" if has_onprem_or_hybrid else "Low",
        "estimated_roi_timeline": "3-6 months",
    })

    # 3. Process Automation Potential (REQ-M2-02)
    opportunities.append({
        "opportunity_name": "Process Automation Potential",
        "detected": True,
        "confidence": 0.88,
        "details": "High qualification friction and manual research in current sales workflows suitable for agentic orchestration.",
        "impact_level": "High",
        "estimated_roi_timeline": "Immediate (1-3 months)",
    })

    # 4. Digital Transformation Projects (REQ-M2-02)
    is_growth_or_modern = any(k in low_stack for k in ["kubernetes", "microservices", "react", "python", "ai"])
    opportunities.append({
        "opportunity_name": "Digital Transformation Projects",
        "detected": True,
        "confidence": 0.89 if is_growth_or_modern else 0.72,
        "details": "Active scaling of product engineering capabilities, integrating real-time intelligence and automated sales pipelines.",
        "impact_level": "High" if is_growth_or_modern else "Medium",
        "estimated_roi_timeline": "4-8 months",
    })

    return opportunities


def _extract_growth_indicators(funding: str, capital: str, size: str, revenue: str) -> List[str]:
    indicators = []
    if funding and funding != "Bootstrapped" and funding != "N/A":
        indicators.append(f"{funding} Funding Stage ({capital}) signaling active budget allocation for expansion tools")
    if size:
        indicators.append(f"Operating at {size} headcount scale with expanding technical departments")
    if revenue and revenue != "N/A":
        indicators.append(f"Strong top-line stability with estimated {revenue} annual revenue throughput")
    if not indicators:
        indicators.append("Stable operating posture with continuous technology refresh cycles")
    return indicators


def _generate_domain_analysis(company: str, industry: str, size: str, location: str) -> str:
    return (
        f"{company} operates as a prominent player in the {industry} sector based in {location or 'the US'}. "
        f"With an organizational scale of {size or 'growing team'}, their operations demand high availability, "
        f"low-latency system integration, and rapid automated data pipelines to maintain market competitiveness."
    )
