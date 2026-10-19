from typing import TypedDict, List, Dict, Any, Optional

class AgentState(TypedDict):
    """
    State shared across LangGraph multi-agent execution pipeline.
    Adheres to LangGraph state persistence standards.
    """
    # Input Prospect Data (REQ-M1-01, REQ-M1-02)
    lead_id: Optional[int]
    company_name: str
    industry: str
    contact_name: str
    email: Optional[str]
    phone: Optional[str]
    company_size: Optional[str]
    annual_revenue: Optional[str]
    funding_stage: Optional[str]
    capital_raised: Optional[str]
    location: Optional[str]
    tech_stack: Optional[str]
    
    # Research Agent Intermediate Outputs (REQ-M2-01, REQ-M2-02)
    industry_domain_analysis: Optional[str]
    growth_indicators: Optional[List[str]]
    tech_stack_components: Optional[Dict[str, List[str]]]
    transformation_opportunities: Optional[List[Dict[str, Any]]]
    
    # Qualification Agent Final Outputs (REQ-M2-03)
    qualification_score: Optional[int]
    high_growth_potential: Optional[bool]
    funding_analysis: Optional[str]
    tech_alignment_metrics: Optional[List[Dict[str, Any]]]
    overall_tech_compatibility_score: Optional[int]
    decision_makers: Optional[List[Dict[str, Any]]]
    business_needs_summary: Optional[str]
    strategic_recommendation: Optional[str]
    
    # Execution Metadata & Trace
    execution_trace: List[str]
    errors: List[str]
