"""
SalesGenie Platform - Module 2: AI Lead Intelligence & Company Analysis Engine
Engineered by Jayant Vaibhav (AI/ML Engineer)
Compliance: IEEE Std 830-1998 REQ-M2-01, REQ-M2-02, REQ-M2-03
"""

from typing import Dict, Any, Optional
from backend.app.ai_agents.graph import (
    run_lead_intelligence_pipeline,
    get_agent_architecture_mermaid
)
from backend.app.services.intelligence_service import intelligence_service

def analyze_lead_intelligence(prospect_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executes the multi-agent pipeline for a prospect profile.
    REQ-M2-01: Company Profiling
    REQ-M2-02: Transformation Opportunity Identification (ERP, Cloud, Automation, Digital)
    REQ-M2-03: Qualification Score (0-100) & High Growth Potential detection
    """
    return run_lead_intelligence_pipeline(prospect_data)

def get_architecture_diagram() -> str:
    """Returns the LangGraph Multi-Agent Architecture topology diagram."""
    return get_agent_architecture_mermaid()
