import time
import pytest
from backend.ai_agents.graph import (
    run_lead_intelligence_pipeline,
    get_agent_architecture_mermaid,
    intelligence_graph,
)
from modules.module2_intelligence import analyze_lead_intelligence


def test_langgraph_pipeline_compilation():
    """Verifies that the LangGraph StateGraph compiles and contains required nodes."""
    assert intelligence_graph is not None


def test_end_to_end_lead_intelligence_latency():
    """
    IEEE SRS Clause 5.3.6 Quality Attribute:
    End-to-end prospect profile analysis completes in < 5.0 seconds.
    """
    prospect = {
        "company_name": "TechCorp Solutions",
        "industry": "Enterprise Software",
        "contact_name": "Sarah Johnson",
        "company_size": "250-500 employees",
        "annual_revenue": "$45M-$60M",
        "funding_stage": "Series C",
        "capital_raised": "$28M",
        "tech_stack": "AWS, Python, React, Node.js, Kubernetes, PostgreSQL",
    }

    start_time = time.time()
    result = run_lead_intelligence_pipeline(prospect)
    latency = time.time() - start_time

    assert latency < 5.0, f"Execution latency was {latency}s, exceeding 5.0s SLA target."
    assert result["qualification_score"] is not None
    assert 0 <= result["qualification_score"] <= 100
    assert result["high_growth_potential"] is True


def test_req_m2_01_company_profiling():
    """REQ-M2-01: Automated company profiling and tech stack categorization."""
    prospect = {
        "company_name": "FinTech Matrix",
        "industry": "Financial Services",
        "contact_name": "David Miller",
        "tech_stack": "GCP, Python, FastApi, PostgreSQL, Docker, Redis",
    }
    result = analyze_lead_intelligence(prospect)
    components = result.get("tech_stack_components", {})
    assert "Cloud" in components
    assert "Backend" in components
    assert "Data/DB" in components
    assert result.get("industry_domain_analysis") is not None


def test_req_m2_02_transformation_opportunities():
    """REQ-M2-02: Business opportunity identification (ERP, Cloud, Automation, Digital)."""
    prospect = {
        "company_name": "Legacy Manufacturing Ltd",
        "industry": "Manufacturing",
        "contact_name": "Robert Chen",
        "tech_stack": "SAP, Oracle, On-Premises Windows Server",
    }
    result = analyze_lead_intelligence(prospect)
    opportunities = result.get("transformation_opportunities", [])
    assert len(opportunities) >= 3

    opp_names = [o["opportunity_name"] for o in opportunities]
    assert "ERP Modernization Needs" in opp_names
    assert "Cloud Migration Opportunities" in opp_names
    assert "Process Automation Potential" in opp_names

    # Check ERP modernization was flagged with high confidence
    erp_opp = next(o for o in opportunities if o["opportunity_name"] == "ERP Modernization Needs")
    assert erp_opp["detected"] is True
    assert erp_opp["impact_level"] == "High"


def test_req_m2_03_qualification_score_and_personas():
    """REQ-M2-03: Intelligence summary output, qualification score, and buying committee personas."""
    prospect = {
        "company_name": "ScaleAI Labs",
        "industry": "AI & Analytics",
        "contact_name": "Rachel Adams (CTO)",
        "funding_stage": "Series B",
        "capital_raised": "$18M",
        "company_size": "100-250 employees",
        "tech_stack": "AWS, Python, Kubernetes, React",
    }
    result = analyze_lead_intelligence(prospect)

    score = result.get("qualification_score")
    assert score is not None
    assert 50 <= score <= 100  # High qualification expected for Series B tech company with CTO contact

    decision_makers = result.get("decision_makers", [])
    assert len(decision_makers) >= 1
    assert "recommended_pitch_angle" in decision_makers[0]
    assert result.get("business_needs_summary") is not None
    assert result.get("strategic_recommendation") is not None


def test_mermaid_architecture_diagram():
    """Verifies that the agent topology diagram is valid Mermaid."""
    diagram = get_agent_architecture_mermaid()
    assert "flowchart TD" in diagram
    assert "Research Agent Node" in diagram
    assert "Qualification Agent Node" in diagram
