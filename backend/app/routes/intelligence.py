from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.models.base import get_db
from backend.app.schemas.intelligence import (
    CompanyIntelligenceResponse,
    IntelligenceAnalyzeRequest
)
from backend.app.services.intelligence_service import intelligence_service
from backend.app.ai_agents.graph import run_lead_intelligence_pipeline, get_agent_architecture_mermaid

router = APIRouter(prefix="/intelligence", tags=["Lead Intelligence & Analysis (Module 2)"])

@router.post("/analyze/{lead_id}", response_model=CompanyIntelligenceResponse)
def analyze_lead_by_id(lead_id: int, db: Session = Depends(get_db)):
    """
    Executes LangGraph Multi-Agent Company Profiling & Lead Intelligence Analysis
    for a stored prospect.
    Complies with IEEE SRS REQ-M2-01, REQ-M2-02, REQ-M2-03.
    """
    result = intelligence_service.analyze_lead(db, lead_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Lead with id {lead_id} not found")
    return result

@router.post("/analyze-raw")
def analyze_raw_prospect(request: IntelligenceAnalyzeRequest):
    """
    Directly passes a prospect payload through the LangGraph agent pipeline
    without requiring existing database persistence.
    """
    return run_lead_intelligence_pipeline(request.model_dump())

@router.get("/architecture")
def get_agent_architecture():
    """Returns the multi-agent architecture topology in Mermaid format (Day 3 deliverable)."""
    return {
        "diagram": get_agent_architecture_mermaid(),
        "agents": [
            {
                "name": "Research Agent",
                "role": "Extracts industry domain, growth signals, tech stack, and detects 4 transformation opportunities"
            },
            {
                "name": "Qualification Agent",
                "role": "Calculates Qualification Score (0-100), detects high growth indicators, tech alignment, and decision maker profiles"
            }
        ],
        "framework": "LangGraph (StateGraph)"
    }
