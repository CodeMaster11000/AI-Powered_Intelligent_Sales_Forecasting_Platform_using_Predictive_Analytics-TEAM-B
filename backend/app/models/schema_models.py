from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.models.base import Base

class User(Base):
    """
    Users table - Stores enterprise credentials, user role assignments, and organizational metadata.
    SRS Section 2.4 - Table 2.4-A
    """
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    role = Column(String(50), nullable=False)  # Sales Rep, BDR, Sales Manager, RevOps
    department = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    analytics = relationship("SalesAnalytics", back_populates="user")

class Lead(Base):
    """
    Leads table - Central FK target for all lead activity.
    SRS Section 2.4 & REQ-M1-01, REQ-M1-02, REQ-M1-03
    """
    __tablename__ = "leads"
    
    lead_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    company_name = Column(String(150), nullable=False, index=True)
    industry = Column(String(100), nullable=False)
    contact_name = Column(String(100), nullable=False)
    email = Column(String(150), nullable=False, index=True)
    phone = Column(String(50), nullable=True)
    
    # Demographic & firmographic fields (REQ-M1-02)
    company_size = Column(String(50), nullable=True)       # e.g., 250-500 employees
    annual_revenue = Column(String(50), nullable=True)     # e.g., $45M-$60M
    funding_stage = Column(String(50), nullable=True)      # e.g., Series C
    capital_raised = Column(String(50), nullable=True)     # e.g., $28M
    location = Column(String(100), nullable=True)          # e.g., San Francisco, CA
    tech_stack = Column(Text, nullable=True)               # e.g., AWS, Python, React, Kubernetes
    
    # Lifecycle Stage: New Leads, Qualified, Proposal, Negotiation, Closed Won (REQ-M1-03)
    lead_status = Column(String(50), default="New Leads")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    insights = relationship("CompanyInsight", back_populates="lead", cascade="all, delete-orphan")
    scores = relationship("LeadScore", back_populates="lead", cascade="all, delete-orphan")
    interactions = relationship("SalesInteraction", back_populates="lead", cascade="all, delete-orphan")
    campaigns = relationship("OutreachCampaign", back_populates="lead", cascade="all, delete-orphan")
    sync_logs = relationship("CRMSyncLog", back_populates="lead", cascade="all, delete-orphan")

class LeadScore(Base):
    """
    Lead_Scores table - Historical AI predictive lead scores (0-100) and conversion probabilities.
    SRS Section 2.4 & REQ-M4-01, REQ-M4-02, REQ-M4-03
    """
    __tablename__ = "lead_scores"
    
    score_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    lead_id = Column(Integer, ForeignKey("leads.lead_id"), nullable=False)
    lead_score = Column(Float, nullable=False)                 # 0 - 100
    conversion_probability = Column(Float, nullable=False)     # 0.0 - 1.0 (e.g. 78%)
    segment = Column(String(20), nullable=True)                # Hot, Warm, Cold
    scoring_breakdown = Column(Text, nullable=True)            # JSON details of weighted factors
    generated_at = Column(DateTime, default=datetime.utcnow)
    
    lead = relationship("Lead", back_populates="scores")

class CompanyInsight(Base):
    """
    Company_Insights table - AI-generated intelligence, tech stack compatibility, and business signals.
    SRS Section 2.4 & REQ-M2-01, REQ-M2-02, REQ-M2-03
    """
    __tablename__ = "company_insights"
    
    insight_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    lead_id = Column(Integer, ForeignKey("leads.lead_id"), nullable=False)
    qualification_score = Column(Integer, default=0)           # 0 - 100 (REQ-M2-03)
    business_needs = Column(Text, nullable=True)               # Qualitative needs summary
    opportunities = Column(Text, nullable=True)                # ERP, Cloud, Automation, Digital
    industry_analysis = Column(Text, nullable=True)            # Domain data, market position
    tech_alignment = Column(Text, nullable=True)               # Stack compatibility details
    decision_maker_summary = Column(Text, nullable=True)       # Identified key personas
    high_growth_indicators = Column(Text, nullable=True)       # Series C funding, rapid expansion
    raw_agent_output = Column(Text, nullable=True)             # Full LangGraph agent output JSON
    generated_at = Column(DateTime, default=datetime.utcnow)
    
    lead = relationship("Lead", back_populates="insights")

class SalesInteraction(Base):
    """
    Sales_Interactions table - Stores meeting transcripts, summaries, and action items.
    SRS Section 2.4 & REQ-M5-01, REQ-M5-02
    """
    __tablename__ = "sales_interactions"
    
    interaction_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    lead_id = Column(Integer, ForeignKey("leads.lead_id"), nullable=False)
    interaction_type = Column(String(50), default="Discovery Call")
    summary = Column(Text, nullable=True)
    action_items = Column(Text, nullable=True)
    interaction_date = Column(DateTime, default=datetime.utcnow)
    
    lead = relationship("Lead", back_populates="interactions")

class OutreachCampaign(Base):
    """
    Outreach_Campaigns table - AI-generated outreach templates, cold emails, and multi-channel states.
    SRS Section 2.4 & REQ-M3-01, REQ-M3-02, REQ-M3-03
    """
    __tablename__ = "outreach_campaigns"
    
    campaign_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    lead_id = Column(Integer, ForeignKey("leads.lead_id"), nullable=False)
    email_subject = Column(String(255), nullable=True)
    email_content = Column(Text, nullable=True)
    campaign_status = Column(String(50), default="Draft")
    timing_recommendation = Column(Text, nullable=True)
    channel_mix = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    lead = relationship("Lead", back_populates="campaigns")

class CRMSyncLog(Base):
    """
    CRM_Sync_Logs table - Real-time integration events, OAuth state, sync status, and audit parameters.
    SRS Section 2.4 & REQ-M5-03, Table 3.6-A
    """
    __tablename__ = "crm_sync_logs"
    
    sync_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    lead_id = Column(Integer, ForeignKey("leads.lead_id"), nullable=False)
    crm_platform = Column(String(50), default="Salesforce")  # Salesforce, HubSpot
    sync_status = Column(String(50), default="Success")      # Success, Failed, Retrying
    event_type = Column(String(50), default="Contact Synced") # Contact Synced, Activity Logged, Deal Stage Updated
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    lead = relationship("Lead", back_populates="sync_logs")

class SalesAnalytics(Base):
    """
    Sales_Analytics table - Aggregate sales pipeline performance metrics, conversion tracking.
    SRS Section 2.4 & REQ-M6-01, Table 3.7-A
    """
    __tablename__ = "sales_analytics"
    
    analytics_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    conversion_rate = Column(Float, default=24.8)             # Baseline 24.8%
    pipeline_value = Column(Float, default=2400000.0)         # Baseline $2.4M
    avg_response_time_hours = Column(Float, default=2.4)     # Baseline 2.4 hours
    avg_sales_cycle_days = Column(Integer, default=28)        # Baseline 28 days
    generated_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="analytics")
