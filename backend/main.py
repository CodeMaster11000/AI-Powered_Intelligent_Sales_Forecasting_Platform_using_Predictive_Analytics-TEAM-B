from decimal import Decimal
from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.database.models.company_insights import CompanyInsight
from backend.database.models.lead_scores import LeadScore
from backend.database.models.leads import Lead
from backend.database.models.users import User
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
from modules.module2_intelligence import generate_company_insights
from modules.module3_outreach import generate_personalized_email
from modules.module4_scoring import calculate_lead_score, score_lead

app = FastAPI(title="SalesGenie AI Core API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- SYSTEM & USERS ---
@app.get("/health", tags=["System"])
def health_check():
    return {"status": "healthy", "service": "salesgenie-api"}


@app.get("/api/users", response_model=list[UserResponse], tags=["Users"])
def get_users(db: Session = Depends(get_db)):
    return seed_default_users(db)


# --- LEADS CRUD & STATS ---
@app.get("/api/leads/stats", response_model=PipelineStatsResponse, tags=["Leads"])
def get_stats(db: Session = Depends(get_db)):
    return get_pipeline_stats(db)


@app.post("/api/leads", response_model=LeadResponse, status_code=status.HTTP_201_CREATED, tags=["Leads"])
def create_lead(lead_in: LeadCreate, db: Session = Depends(get_db)):
    try:
        return create_single_lead(db, lead_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/leads/bulk", response_model=BulkLeadImportResponse, status_code=status.HTTP_201_CREATED, tags=["Leads"])
def bulk_import(import_req: BulkLeadImportRequest, db: Session = Depends(get_db)):
    try:
        return bulk_import_leads(db, import_req)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/leads", response_model=list[LeadResponse], tags=["Leads"])
def get_all_leads(
    search: str | None = Query(None),
    source: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    return list_leads(db, search=search, source=source, limit=limit)


# --- SCORING & INTELLIGENCE ENDPOINTS ---
@app.get("/api/scoring/queue", tags=["Scoring"])
def get_scoring_queue(db: Session = Depends(get_db)):
    """Fetches all leads with their latest score for the Master Queue."""
    leads = db.execute(select(Lead).order_by(Lead.lead_id.asc())).scalars().all()
    queue = []

    for lead in leads:
        latest_score = db.execute(
            select(LeadScore)
            .where(LeadScore.lead_id == lead.lead_id)
            .order_by(LeadScore.generated_at.desc())
        ).scalars().first()

        if latest_score:
            score_val = latest_score.lead_score
            prob = float(latest_score.conversion_probability)
            priority = "hot" if score_val >= 75 else ("warm" if score_val >= 40 else "cold")
        else:
            score_val = None
            prob = None
            priority = "unscored"

        queue.append({
            "lead_id": lead.lead_id,
            "company_name": lead.company_name,
            "contact_name": lead.contact_name or "N/A",
            "contact_title": lead.contact_title or "Executive",
            "email": lead.email,
            "funding_stage": lead.funding_stage or "N/A",
            "industry": lead.industry or "Technology",
            "score": score_val,
            "conversion_probability": prob,
            "priority": priority,
        })

    return queue


@app.get("/api/leads/{lead_id}/dossier", tags=["Scoring"])
def get_lead_dossier(lead_id: int, db: Session = Depends(get_db)):
    """Fetches complete AI dossier with factor breakdown and company intelligence."""
    lead = db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    score_obj = db.execute(
        select(LeadScore)
        .where(LeadScore.lead_id == lead_id)
        .order_by(LeadScore.generated_at.desc())
    ).scalars().first()

    score_data = calculate_lead_score(lead)
    if score_obj:
        score_data["score"] = score_obj.lead_score
        score_data["conversion_probability"] = float(score_obj.conversion_probability)
        score_data["priority"] = "hot" if score_obj.lead_score >= 75 else ("warm" if score_obj.lead_score >= 40 else "cold")

    insight_obj = db.execute(
        select(CompanyInsight)
        .where(CompanyInsight.lead_id == lead_id)
        .order_by(CompanyInsight.generated_at.desc())
    ).scalars().first()

    if not insight_obj:
        insight_res = generate_company_insights(db, lead_id)
    else:
        insight_res = {
            "business_needs": insight_obj.business_needs,
            "opportunities": insight_obj.opportunities,
            "industry_analysis": insight_obj.industry_analysis,
            "growth_indicators": insight_obj.growth_indicators,
            "tech_alignment": insight_obj.tech_alignment,
            "decision_maker_summary": insight_obj.decision_maker_summary,
        }

    return {
        "lead_id": lead.lead_id,
        "company_name": lead.company_name,
        "contact_name": lead.contact_name or "N/A",
        "contact_title": lead.contact_title or "Executive",
        "email": lead.email,
        "location": lead.location or "N/A",
        "funding_stage": lead.funding_stage or "N/A",
        "tech_stack": lead.tech_stack or [],
        "scoring": score_data,
        "insights": insight_res,
    }


@app.post("/api/leads/{lead_id}/score", tags=["Scoring"])
def rescore_lead(lead_id: int, db: Session = Depends(get_db)):
    score_res = score_lead(db, lead_id)
    insight_res = generate_company_insights(db, lead_id)
    return {"scoring": score_res, "insights": insight_res}


@app.post("/api/leads/score-batch", tags=["Scoring"])
def score_batch(db: Session = Depends(get_db)):
    leads = db.execute(select(Lead)).scalars().all()
    count = 0
    for lead in leads:
        existing = db.execute(select(LeadScore).where(LeadScore.lead_id == lead.lead_id)).first()
        if not existing:
            score_lead(db, lead.lead_id)
            generate_company_insights(db, lead.lead_id)
            count += 1
    return {"scored_count": count}


# --- OUTREACH GENERATION ---
class OutreachRequest(BaseModel):
    lead_id: int
    angle: str = "Cloud Scale & Efficiency"
    tone: str = "Consultative / Executive"
    custom_note: str = ""


@app.post("/api/outreach/generate", tags=["Outreach"])
def generate_outreach(req: OutreachRequest, db: Session = Depends(get_db)):
    lead = db.get(Lead, req.lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    insight = db.execute(select(CompanyInsight).where(CompanyInsight.lead_id == req.lead_id)).scalars().first()
    insight_dict = {"opportunities": insight.opportunities} if insight else {}

    return generate_personalized_email(
        lead=lead,
        insight_data=insight_dict,
        angle=req.angle,
        tone=req.tone,
        custom_note=req.custom_note,
    )