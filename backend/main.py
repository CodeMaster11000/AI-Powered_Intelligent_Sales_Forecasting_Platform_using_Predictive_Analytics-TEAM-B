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
)
from modules.module1_leads import (
    bulk_import_leads,
    create_single_lead,
    get_pipeline_stats,
    list_leads,
    seed_default_users,
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


@app.get("/api/users", response_model=list[UserResponse], tags=["Users"])
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


@app.get("/api/leads", response_model=list[LeadResponse], tags=["Leads"])
def get_all_leads(
    search: str | None = Query(None, description="Search company, contact, or email"),
    source: str | None = Query(None, description="Filter by ingestion source"),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """Retrieves recent ingested leads for the session verification feed (Wireframe 3)."""
    return list_leads(db, search=search, source=source, limit=limit)