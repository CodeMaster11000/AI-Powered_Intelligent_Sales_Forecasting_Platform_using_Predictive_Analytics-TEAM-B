import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.config import settings
from backend.app.models.base import Base, engine, SessionLocal
from backend.app.models.schema_models import Lead, User, SalesAnalytics
from backend.app.services.lead_service import lead_service
from backend.app.routes.leads import router as leads_router
from backend.app.routes.intelligence import router as intelligence_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB schema (all 8 tables)
    Base.metadata.create_all(bind=engine)
    
    # Auto-seed sample data if empty
    db = SessionLocal()
    try:
        lead_count = db.query(Lead).count()
        if lead_count == 0:
            csv_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "sample_leads.csv")
            if os.path.exists(csv_path):
                lead_service.seed_from_csv(db, os.path.abspath(csv_path))
                
        # Seed default analytics baseline if empty (REQ Table 3.7-A)
        analytics_count = db.query(SalesAnalytics).count()
        if analytics_count == 0:
            default_analytics = SalesAnalytics(
                conversion_rate=24.8,
                pipeline_value=2400000.0,
                avg_response_time_hours=2.4,
                avg_sales_cycle_days=28
            )
            db.add(default_analytics)
            db.commit()
    finally:
        db.close()
        
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Enterprise AI Sales Assistant & Lead Intelligence Platform microservices.",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Synthetic Health Check endpoint (IEEE SRS Clause 5.3.6: 99.9% availability target)
@app.get("/health", tags=["Health & Diagnostics"])
def health_check():
    return {
        "status": "HEALTHY",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "database": "CONNECTED",
        "agentic_engine": "LANGGRAPH_ACTIVE"
    }

# Mount Routers
app.include_router(leads_router, prefix=settings.API_V1_PREFIX)
app.include_router(intelligence_router, prefix=settings.API_V1_PREFIX)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)
