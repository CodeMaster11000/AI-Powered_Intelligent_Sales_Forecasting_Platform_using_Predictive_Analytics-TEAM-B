from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from datetime import datetime

class LeadBase(BaseModel):
    company_name: str
    industry: str
    contact_name: str
    email: str
    phone: Optional[str] = None
    company_size: Optional[str] = None
    annual_revenue: Optional[str] = None
    funding_stage: Optional[str] = None
    capital_raised: Optional[str] = None
    location: Optional[str] = None
    tech_stack: Optional[str] = None
    lead_status: Optional[str] = "New Leads"

class LeadCreate(LeadBase):
    pass

class LeadUpdate(BaseModel):
    company_name: Optional[str] = None
    industry: Optional[str] = None
    contact_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    company_size: Optional[str] = None
    annual_revenue: Optional[str] = None
    funding_stage: Optional[str] = None
    capital_raised: Optional[str] = None
    location: Optional[str] = None
    tech_stack: Optional[str] = None
    lead_status: Optional[str] = None

class LeadResponse(LeadBase):
    lead_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
