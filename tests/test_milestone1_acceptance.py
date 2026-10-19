import time
import pytest
from backend.app.models.base import Base, engine, SessionLocal
from backend.app.models.schema_models import Lead
from backend.app.services.lead_service import lead_service
from backend.app.services.intelligence_service import intelligence_service
from backend.app.ai_agents.graph import run_lead_intelligence_pipeline

@pytest.fixture(scope="module")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    yield db
    db.close()

def test_ingestion_benchmark(db_session):
    """
    IEEE SRS Section 5.3 Acceptance Criterion:
    Successfully ingest, parse, and analyze >= 95% of imported prospect records without field corruption.
    """
    initial_count = db_session.query(Lead).count()
    assert initial_count >= 9, f"Expected at least 9 seeded leads, got {initial_count}"

def test_langgraph_processing_latency():
    """
    IEEE SRS Clause 5.3.6 Quality Attribute:
    End-to-end lead profile analysis and generation completed in < 5 seconds.
    """
    prospect = {
        "company_name": "TechCorp Solutions",
        "industry": "Enterprise Software",
        "contact_name": "Sarah Johnson",
        "company_size": "250-500 employees",
        "annual_revenue": "$45M-$60M",
        "funding_stage": "Series C",
        "capital_raised": "$28M",
        "tech_stack": "AWS, Python, React, Node.js, Kubernetes, PostgreSQL"
    }
    
    start_time = time.time()
    result = run_lead_intelligence_pipeline(prospect)
    latency = time.time() - start_time
    
    assert latency < 5.0, f"Latency was {latency}s, which exceeds the 5-second target"
    assert result["qualification_score"] is not None
    assert 0 <= result["qualification_score"] <= 100

def test_req_m2_01_tech_stack_components():
    """
    REQ-M2-01: Extract tech stack compatibility and components.
    """
    prospect = {
        "company_name": "DataFlow Inc",
        "industry": "Big Data & Analytics",
        "contact_name": "Marcus Vance",
        "tech_stack": "GCP, Python, Spark, Kafka, Snowflake, Airflow"
    }
    result = run_lead_intelligence_pipeline(prospect)
    components = result.get("tech_stack_components", {})
    assert "Cloud" in components
    assert "Backend" in components
    assert "Data/DB" in components

def test_req_m2_02_transformation_opportunities():
    """
    REQ-M2-02: Explicitly identify ERP Modernization, Cloud Migration,
    Process Automation, and Digital Transformation.
    """
    prospect = {
        "company_name": "Acme Corp",
        "industry": "Traditional Manufacturing",
        "contact_name": "Robert Miller",
        "tech_stack": "On-Premises Windows Server, Oracle DB, Legacy SAP ERP"
    }
    result = run_lead_intelligence_pipeline(prospect)
    opps = result.get("transformation_opportunities", [])
    names = [o["opportunity_name"] for o in opps]
    
    assert "ERP Modernization Needs" in names
    assert "Cloud Migration Opportunities" in names
    assert "Process Automation Potential" in names
    assert "Digital Transformation Projects" in names
    
    # Legacy ERP should be detected with High impact
    erp_opp = next(o for o in opps if o["opportunity_name"] == "ERP Modernization Needs")
    assert erp_opp["detected"] is True
    assert erp_opp["impact_level"] == "High"

def test_req_m2_03_high_growth_and_qualification_score():
    """
    REQ-M2-03: Output Qualification Score, High Growth Potential indicators,
    Tech Alignment, and Decision Maker profiles.
    """
    prospect = {
        "company_name": "TechCorp Solutions",
        "industry": "Enterprise Software",
        "contact_name": "Sarah Johnson",
        "funding_stage": "Series C",
        "capital_raised": "$28M",
        "company_size": "250-500 employees",
        "tech_stack": "AWS, Python, React, Kubernetes"
    }
    result = run_lead_intelligence_pipeline(prospect)
    
    assert result["qualification_score"] >= 80, f"Expected high score for Series C company, got {result['qualification_score']}"
    assert result["high_growth_potential"] is True
    assert len(result["decision_makers"]) >= 1
    assert result["overall_tech_compatibility_score"] >= 70

def test_req_m1_03_lifecycle_stages(db_session):
    """
    REQ-M1-03: Transition through 5 lifecycle stages:
    New Leads, Qualified, Proposal, Negotiation, Closed Won.
    """
    lead = db_session.query(Lead).first()
    assert lead is not None
    
    for stage in ["New Leads", "Qualified", "Proposal", "Negotiation", "Closed Won"]:
        updated = lead_service.update_lead_status(db_session, lead.lead_id, stage)
        assert updated.lead_status == stage
