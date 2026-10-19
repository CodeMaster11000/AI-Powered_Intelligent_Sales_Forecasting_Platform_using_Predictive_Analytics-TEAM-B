import csv
import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from backend.app.models.schema_models import Lead
from backend.app.schemas.lead import LeadCreate, LeadUpdate

logger = logging.getLogger(__name__)

class LeadService:
    @staticmethod
    def create_lead(db: Session, lead_in: LeadCreate) -> Lead:
        """
        Creates a new prospect record with duplicate email check.
        REQ-M1-01 & REQ-M1-02
        """
        existing = db.query(Lead).filter(Lead.email == lead_in.email).first()
        if existing:
            return existing
            
        lead = Lead(**lead_in.model_dump())
        db.add(lead)
        db.commit()
        db.refresh(lead)
        return lead

    @staticmethod
    def get_leads(db: Session, skip: int = 0, limit: int = 100) -> List[Lead]:
        return db.query(Lead).offset(skip).limit(limit).all()

    @staticmethod
    def get_lead_by_id(db: Session, lead_id: int) -> Optional[Lead]:
        return db.query(Lead).filter(Lead.lead_id == lead_id).first()

    @staticmethod
    def update_lead_status(db: Session, lead_id: int, new_status: str) -> Optional[Lead]:
        """
        Updates the lead funnel stage across 5 predefined states:
        New Leads, Qualified, Proposal, Negotiation, Closed Won.
        REQ-M1-03
        """
        lead = db.query(Lead).filter(Lead.lead_id == lead_id).first()
        if not lead:
            return None
        lead.lead_status = new_status
        db.commit()
        db.refresh(lead)
        return lead

    @staticmethod
    def seed_from_csv(db: Session, csv_path: str) -> int:
        """
        Ingests CSV dataset with duplicate detection.
        REQ-M1-02
        """
        inserted_count = 0
        try:
            with open(csv_path, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    email = row.get("email", "").strip()
                    if not email:
                        continue
                    existing = db.query(Lead).filter(Lead.email == email).first()
                    if not existing:
                        lead = Lead(
                            company_name=row.get("company_name", ""),
                            industry=row.get("industry", ""),
                            contact_name=row.get("contact_name", ""),
                            email=email,
                            phone=row.get("phone", ""),
                            company_size=row.get("company_size", ""),
                            annual_revenue=row.get("annual_revenue", ""),
                            funding_stage=row.get("funding_stage", ""),
                            capital_raised=row.get("capital_raised", ""),
                            location=row.get("location", ""),
                            tech_stack=row.get("tech_stack", ""),
                            lead_status=row.get("lead_status", "New Leads")
                        )
                        db.add(lead)
                        inserted_count += 1
                db.commit()
        except Exception as e:
            logger.error(f"Error seeding leads from CSV {csv_path}: {e}")
            db.rollback()
        return inserted_count

lead_service = LeadService()
