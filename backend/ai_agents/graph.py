import time
import logging
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from backend.ai_agents.state import AgentState
from backend.ai_agents.research_agent import research_agent_node
from backend.ai_agents.qualification_agent import qualification_agent_node

logger = logging.getLogger(__name__)


def build_lead_intelligence_graph():
    """
    Constructs the LangGraph multi-agent orchestration workflow
    for Module 2: Lead Intelligence & Company Analysis.
    """
    workflow = StateGraph(AgentState)

    # Register Agent Nodes
    workflow.add_node("research_agent", research_agent_node)
    workflow.add_node("qualification_agent", qualification_agent_node)

    # Define Agent Execution Flow
    workflow.set_entry_point("research_agent")
    workflow.add_edge("research_agent", "qualification_agent")
    workflow.add_edge("qualification_agent", END)

    return workflow.compile()


# Singleton compiled agent graph
intelligence_graph = build_lead_intelligence_graph()


def run_lead_intelligence_pipeline(prospect_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executes the multi-agent pipeline for an ingested prospect profile.
    Measures processing latency to verify sub-5-second SLA target (REQ IEEE 830 Clause 5.3.6).
    """
    initial_state: AgentState = {
        "lead_id": prospect_data.get("lead_id"),
        "company_name": prospect_data.get("company_name", "Unknown Company"),
        "industry": prospect_data.get("industry", "Technology"),
        "contact_name": prospect_data.get("contact_name", "Decision Maker"),
        "email": prospect_data.get("email"),
        "phone": prospect_data.get("phone"),
        "company_size": prospect_data.get("company_size"),
        "annual_revenue": prospect_data.get("annual_revenue"),
        "funding_stage": prospect_data.get("funding_stage"),
        "capital_raised": prospect_data.get("capital_raised") or prospect_data.get("funding_raised"),
        "location": prospect_data.get("location"),
        "tech_stack": prospect_data.get("tech_stack"),

        "industry_domain_analysis": None,
        "growth_indicators": None,
        "tech_stack_components": None,
        "transformation_opportunities": None,

        "qualification_score": None,
        "high_growth_potential": None,
        "funding_analysis": None,
        "tech_alignment_metrics": None,
        "overall_tech_compatibility_score": None,
        "decision_makers": None,
        "business_needs_summary": None,
        "strategic_recommendation": None,

        "execution_trace": [],
        "errors": [],
    }

    start_time = time.time()
    result_state = intelligence_graph.invoke(initial_state)
    elapsed_seconds = round(time.time() - start_time, 3)

    result_state["execution_latency_seconds"] = elapsed_seconds
    return result_state


def get_agent_architecture_mermaid() -> str:
    """
    Returns Mermaid diagram string of the LangGraph agent architecture
    for documentation and Day 3 deliverables.
    """
    return """```mermaid
flowchart TD
    Start([Prospect Ingested]) --> R[Research Agent Node]
    subgraph Lead Intelligence Multi-Agent System
        R --> |Extract Tech Stack & Domain| R_Out[Industry Analysis & Transformation Ops]
        R_Out --> Q[Qualification Agent Node]
        Q --> |Evaluate Growth Signals| Q_Score[Qualification Score 0-100]
        Q --> |Tech Alignment| Q_Tech[Compatibility Metrics]
        Q --> |Persona Mapping| Q_DM[Decision Maker Profiles]
    end
    Q_Score --> Persist[(PostgreSQL Company_Insights)]
    Q_Tech --> Persist
    Q_DM --> Persist
    Persist --> EndNode([Presentation Layer / Streamlit Leads Tab])
```"""
