import os
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.models.base import get_db
from backend.app.schemas.lead import LeadCreate, LeadResponse
from backend.app.services.lead_service import lead_service

router = APIRouter(prefix="/leads", tags=["Lead Management (Module 1)"])

@router.get("", response_model=List[LeadResponse])
def list_leads(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retrieve list of all ingested prospect profiles (REQ-M1-01)."""
    return lead_service.get_leads(db, skip=skip, limit=limit)

@router.post("", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
def create_lead(lead_in: LeadCreate, db: Session = Depends(get_db)):
    """Create or manually enter a new prospect record (REQ-M1-01, REQ-M1-02)."""
    return lead_service.create_lead(db, lead_in)

@router.get("/{lead_id}", response_model=LeadResponse)
def get_lead(lead_id: int, db: Session = Depends(get_db)):
    lead = lead_service.get_lead_by_id(db, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead

@router.patch("/{lead_id}/status", response_model=LeadResponse)
def update_lead_status(lead_id: int, new_status: str, db: Session = Depends(get_db)):
    """Update lead sales lifecycle stage (REQ-M1-03)."""
    valid_stages = ["New Leads", "Qualified", "Proposal", "Negotiation", "Closed Won"]
    if new_status not in valid_stages:
        raise HTTPException(status_code=400, detail=f"Invalid stage. Must be one of {valid_stages}")
    updated = lead_service.update_lead_status(db, lead_id, new_status)
    if not updated:
        raise HTTPException(status_code=404, detail="Lead not found")
    return updated

@router.post("/seed")
def seed_sample_leads(db: Session = Depends(get_db)):
    """Seeds sample leads from data/sample_leads.csv into PostgreSQL/SQLite."""
    csv_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "sample_leads.csv")
    csv_path = os.path.abspath(csv_path)
    count = lead_service.seed_from_csv(db, csv_path)
    return {"message": f"Successfully ingested {count} leads from sample dataset.", "count": count}
