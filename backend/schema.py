from datetime import datetime
from typing import Literal
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