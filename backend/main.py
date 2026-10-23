from typing import Optional, List
from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.schema import (
    BulkLeadImportRequest,
    BulkLeadImportResponse,
    LeadCreate,
    LeadResponse,
    PipelineStatsResponse,
    UserResponse,
    ProspectAnalysisRequest,
    CompanyInsightResponse,
    LeadAnalysisResponse,
    BatchAnalysisRequest,
)
from modules.module1_leads import (
    bulk_import_leads,
    create_single_lead,
    get_pipeline_stats,
    list_leads,
    seed_default_users,
)
from modules.module2_intelligence import (
    analyze_lead_intelligence,
    analyze_and_store_lead_intelligence,
    get_lead_insights,
    batch_analyze_leads,
    get_architecture_diagram,
)

app = FastAPI(
    title="SalesGenie AI Core API",
    version="1.0.0",
    description="Backend API for predictive lead intelligence, scoring, and automated outreach.",
)

# Enable CORS for local Streamlit consumption
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["System"])
def health_check():
    return {"status": "healthy", "service": "salesgenie-api"}


# =====================================================================
# Module 1: Lead Ingestion & CRUD Endpoints (REQ-M1-01, M1-02, M1-03)
# =====================================================================

@app.get("/api/users", response_model=List[UserResponse], tags=["Users"])
def get_users(db: Session = Depends(get_db)):
    """Returns available sales representatives for lead assignment."""
    return seed_default_users(db)


@app.get("/api/leads/stats", response_model=PipelineStatsResponse, tags=["Leads"])
def get_stats(db: Session = Depends(get_db)):
    """Returns live KPI metrics for top header cards."""
    return get_pipeline_stats(db)


@app.post("/api/leads", response_model=LeadResponse, status_code=status.HTTP_201_CREATED, tags=["Leads"])
def create_lead(lead_in: LeadCreate, db: Session = Depends(get_db)):
    """Creates a single prospect lead (Wireframe 2)."""
    try:
        return create_single_lead(db, lead_in)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.post("/api/leads/bulk", response_model=BulkLeadImportResponse, status_code=status.HTTP_201_CREATED, tags=["Leads"])
def bulk_import(import_req: BulkLeadImportRequest, db: Session = Depends(get_db)):
    """Ingests, deduplicates, and stages a batch of CSV prospects (Wireframe 1)."""
    try:
        return bulk_import_leads(db, import_req)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.get("/api/leads", response_model=List[LeadResponse], tags=["Leads"])
def get_all_leads(
    search: Optional[str] = Query(None, description="Search company, contact, or email"),
    source: Optional[str] = Query(None, description="Filter by ingestion source"),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """Retrieves recent ingested leads for the session verification feed (Wireframe 3)."""
    return list_leads(db, search=search, source=source, limit=limit)


# =====================================================================
# Module 2: AI Lead Intelligence & Analysis Endpoints (REQ-M2-01, M2-02, M2-03)
# =====================================================================

@app.post("/api/leads/{lead_id}/analyze", response_model=LeadAnalysisResponse, tags=["Lead Intelligence"])
def analyze_lead(lead_id: int, db: Session = Depends(get_db)):
    """
    Triggers LangGraph multi-agent intelligence pipeline (Research + Qualification)
    for an ingested prospect, persists insights to PostgreSQL, and updates lead score.
    """
    try:
        return analyze_and_store_lead_intelligence(db, lead_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Analysis failed: {str(e)}")


@app.get("/api/leads/{lead_id}/insights", response_model=CompanyInsightResponse, tags=["Lead Intelligence"])
def get_lead_insight_record(lead_id: int, db: Session = Depends(get_db)):
    """Retrieves generated company intelligence profile and qualification score for a prospect."""
    insight = get_lead_insights(db, lead_id)
    if not insight:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No intelligence insight found for lead {lead_id}")
    return insight


@app.post("/api/leads/batch-analyze", response_model=List[dict], tags=["Lead Intelligence"])
def batch_analyze(req: BatchAnalysisRequest, db: Session = Depends(get_db)):
    """Runs LangGraph multi-agent intelligence analysis for a batch of lead IDs."""
    return batch_analyze_leads(db, req.lead_ids)


@app.post("/api/intelligence/analyze-prospect", tags=["Lead Intelligence"])
def analyze_raw_prospect(prospect: ProspectAnalysisRequest):
    """
    Executes ad-hoc multi-agent intelligence profiling on prospect payload
    without requiring persistent database storage.
    """
    try:
        return analyze_lead_intelligence(prospect.model_dump())
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.get("/api/intelligence/architecture", tags=["Lead Intelligence"])
def get_agent_architecture():
    """Returns the LangGraph Multi-Agent Architecture topology diagram and specifications."""
    return {
        "framework": "LangGraph",
        "nodes": ["research_agent", "qualification_agent"],
        "architecture_diagram_mermaid": get_architecture_diagram(),
    }
