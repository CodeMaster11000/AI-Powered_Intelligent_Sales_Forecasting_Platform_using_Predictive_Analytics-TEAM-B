from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


# Matching database CHECK constraints
LeadStatusType = Literal["New Leads", "Qualified", "Proposal", "Negotiation", "Closed Won"]
SourceType = Literal["CRM", "Website Form", "LinkedIn", "Sales Entry", "CSV"]


class LeadBase(BaseModel):
    company_name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    contact_name: str | None = None
    contact_title: str | None = None
    industry: str | None = None
    phone: str | None = None
    lead_status: LeadStatusType = "New Leads"
    source: SourceType = "CSV"
    company_size: str | None = None
    annual_revenue: str | None = None
    funding_stage: str | None = None
    funding_raised: str | None = None
    location: str | None = None
    tech_stack: list[str] | None = None
    owner_user_id: int | None = None


class LeadCreate(LeadBase):
    pass


class LeadUpdate(LeadBase):
    pass


class LeadResponse(LeadBase):
    model_config = ConfigDict(from_attributes=True)

    lead_id: int
    created_at: datetime
    updated_at: datetime


class BulkLeadImportRequest(BaseModel):
    leads: list[LeadCreate]
    skip_duplicates: bool = True


class BulkLeadImportResponse(BaseModel):
    total_received: int
    imported_count: int
    skipped_duplicates: int
    errors: list[str] = []


class PipelineStatsResponse(BaseModel):
    total_leads: int
    session_additions: int = 0
    ingestion_health: float
    pending_ai_scoring: int


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    name: str
    email: str
    role: str


# Module 2: AI Lead Intelligence Schemas (REQ-M2-01, M2-02, M2-03)
# =====================================================================

class ProspectAnalysisRequest(BaseModel):
    """Ad-hoc analysis payload for any prospect without requiring prior database insertion."""
    company_name: str
    industry: Optional[str] = "Technology"
    contact_name: Optional[str] = "Decision Maker"
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    company_size: Optional[str] = None
    annual_revenue: Optional[str] = None
    funding_stage: Optional[str] = None
    capital_raised: Optional[str] = None
    location: Optional[str] = None
    tech_stack: Optional[str] = None


class CompanyInsightResponse(BaseModel):
    insight_id: Optional[int] = None
    analysis_id: Optional[int] = None
    lead_id: int
    qualification_score: Optional[int] = None
    conversion_probability: Optional[float] = None
    high_growth_potential: Optional[bool] = None
    funding_analysis: Optional[str] = None
    overall_tech_compatibility_score: Optional[int] = None
    business_needs: Optional[str] = None
    business_needs_summary: Optional[str] = None
    strategic_recommendation: Optional[str] = None
    opportunities: Optional[Any] = None
    transformation_opportunities: Optional[Any] = None
    industry_analysis: Optional[str] = None
    industry_domain_analysis: Optional[str] = None
    growth_indicators: Optional[Any] = None
    tech_stack_components: Optional[Any] = None
    tech_alignment: Optional[Any] = None
    tech_alignment_metrics: Optional[Any] = None
    decision_maker_summary: Optional[Any] = None
    decision_makers: Optional[Any] = None
    execution_trace: Optional[Any] = None
    errors: Optional[Any] = None
    execution_latency_seconds: Optional[float] = None
    generated_at: Optional[str] = None


class LeadAnalysisResponse(BaseModel):
    lead_id: int
    company_name: str
    qualification_score: int
    conversion_probability: float
    lead_status: str
    high_growth_potential: Optional[bool] = None
    funding_analysis: Optional[str] = None
    overall_tech_compatibility_score: Optional[int] = None
    business_needs: Optional[str] = None
    strategic_recommendation: Optional[str] = None
    industry_analysis: Optional[str] = None
    growth_indicators: Optional[List[str]] = None
    tech_stack_components: Optional[Dict[str, List[str]]] = None
    transformation_opportunities: Optional[List[Dict[str, Any]]] = None
    tech_alignment_metrics: Optional[List[Dict[str, Any]]] = None
    decision_makers: Optional[List[Dict[str, Any]]] = None
    execution_trace: Optional[List[str]] = None
    errors: Optional[List[str]] = None
    execution_latency_seconds: Optional[float] = None


class BatchAnalysisRequest(BaseModel):
    lead_ids: List[int]
