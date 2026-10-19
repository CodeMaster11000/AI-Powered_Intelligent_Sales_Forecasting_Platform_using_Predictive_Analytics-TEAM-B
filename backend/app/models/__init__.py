from backend.app.models.base import Base, engine, SessionLocal, get_db
from backend.app.models.schema_models import (
    User, Lead, LeadScore, CompanyInsight, 
    SalesInteraction, OutreachCampaign, CRMSyncLog, SalesAnalytics
)
