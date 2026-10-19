from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime

class TransformationOpportunity(BaseModel):
    opportunity_name: str  # ERP Modernization, Cloud Migration, Process Automation, Digital Transformation
    detected: bool
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    details: str
    impact_level: str  # High, Medium, Low
    estimated_roi_timeline: Optional[str] = None

class TechAlignmentMetric(BaseModel):
    category: str  # Cloud, Backend, Frontend, Data/DB, DevOps
    prospect_stack: List[str]
    compatibility_score: int = Field(ge=0, le=100)
    alignment_notes: str

class DecisionMakerProfile(BaseModel):
    name: str
    role_title: str
    authority_level: str  # High (C-Level/VP), Medium (Director), Low (Individual Contributor)
    likely_pain_points: List[str]
    recommended_pitch_angle: str

class CompanyIntelligenceResponse(BaseModel):
    lead_id: int
    company_name: str
    qualification_score: int = Field(ge=0, le=100)  # e.g. 92
    
    # Growth & Funding Signals (REQ-M2-03)
    high_growth_potential: bool
    growth_indicators: List[str]
    funding_analysis: str
    
    # Business Transformation Opportunities (REQ-M2-02)
    transformation_opportunities: List[TransformationOpportunity]
    
    # Tech Stack & Alignment (REQ-M2-01 & REQ-M2-03)
    industry_domain_analysis: str
    tech_alignment_metrics: List[TechAlignmentMetric]
    overall_tech_compatibility_score: int
    
    # Decision Maker Profiling (REQ-M2-03)
    decision_makers: List[DecisionMakerProfile]
    
    # Executive Summary
    business_needs_summary: str
    strategic_recommendation: str
    
    generated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class IntelligenceAnalyzeRequest(BaseModel):
    lead_id: Optional[int] = None
    company_name: str
    industry: str
    contact_name: str
    company_size: Optional[str] = None
    annual_revenue: Optional[str] = None
    funding_stage: Optional[str] = None
    capital_raised: Optional[str] = None
    location: Optional[str] = None
    tech_stack: Optional[str] = None
