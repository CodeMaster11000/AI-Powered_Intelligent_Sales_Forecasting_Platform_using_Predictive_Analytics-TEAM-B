from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.ai_agents.outreach_agent import generate_personalized_outreach
from modules.module3_outreach import generate_personalized_email
from backend.main import SaveDraftRequest, save_outreach_draft

client = TestClient(app)


def test_outreach_agent_direct_tone():
    lead = {
        "company_name": "Databricks",
        "contact_name": "Ali Ghodsi",
        "contact_title": "CEO & Co-Founder",
        "tech_stack": ["Spark", "AWS", "Python"],
        "industry": "Data Intelligence",
        "funding_stage": "Growth",
    }
    result = generate_personalized_outreach(
        lead_data=lead,
        insight_data={},
        angle="Cloud Scale & Infrastructure Efficiency",
        tone="Direct & Punchy (Under 100 words)",
        custom_note="Saw your recent lakehouse launch.",
    )

    assert "subject_options" in result
    assert len(result["subject_options"]) >= 3
    assert result["selected_subject"] in result["subject_options"]
    assert "Ali" in result["body"]
    assert "Databricks" in result["body"]
    assert "Spark" in result["body"]
    assert result["hook_score"] >= 80
    assert result["word_count"] > 0
    assert result["reading_time_seconds"] > 0
    assert len(result["personalization_triggers"]) > 0


def test_outreach_agent_problem_centric_tone():
    lead = {
        "company_name": "FintechHub",
        "contact_name": "Marcus Vance",
        "contact_title": "VP of Revenue Operations",
        "tech_stack": ["PostgreSQL", "Kafka", "Docker"],
        "industry": "Fintech",
        "funding_stage": "Series B",
    }
    result = generate_personalized_outreach(
        lead_data=lead,
        insight_data={"business_needs": "Reducing forecast latency"},
        angle="Pipeline Variance & Forecasting ROI",
        tone="Problem-Centric / Metric-Driven",
    )

    assert "FintechHub" in result["body"]
    assert "PostgreSQL" in result["body"]
    assert "pipeline variance" in result["body"].lower() or "forecast" in result["body"].lower()
    assert result["hook_score"] >= 85


def test_outreach_agent_consultative_tone():
    lead = {
        "company_name": "HealthBridge",
        "contact_name": "Dr. Sarah Chen",
        "contact_title": "Chief Information Officer",
        "tech_stack": ["Azure", "Kubernetes", "FHIR"],
        "industry": "Healthtech",
        "funding_stage": "Series C",
    }
    result = generate_personalized_outreach(
        lead_data=lead,
        insight_data={
            "opportunities": "FHIR API integration and compliance automation",
            "growth_indicators": "Recent $40M Series C",
        },
        angle="Tech Stack Modernization",
        tone="Consultative / Executive",
    )

    assert "Dr." in result["body"] or "Sarah" in result["body"]
    assert "HealthBridge" in result["body"]
    assert result["hook_score"] >= 85


def test_module3_wrapper():
    lead_dict = {
        "company_name": "ScaleAI",
        "contact_name": "Alexandr Wang",
        "contact_title": "CEO",
        "tech_stack": ["PyTorch", "GCP"],
    }
    res = generate_personalized_email(
        lead=lead_dict,
        insight_data={},
        angle="Cloud Scale",
        tone="Consultative / Executive",
    )
    assert "body" in res
    assert "ScaleAI" in res["body"]


def test_api_llm_providers_endpoint():
    response = client.get("/api/llm/providers")
    assert response.status_code == 200
    data = response.json()
    assert "gemini" in data
    assert "openai" in data
    assert "grok" in data
    assert "ollama" in data


def test_save_outreach_draft_persists_record():
    db = Mock()
    lead = Mock(lead_id=7, company_name="Example Corp")
    db.get.return_value = lead

    def refresh_draft(draft):
        draft.id = 42

    db.refresh.side_effect = refresh_draft
    result = save_outreach_draft(
        SaveDraftRequest(
            lead_id=7,
            subject="A useful subject",
            body="A personalized message.",
        ),
        db,
    )

    saved_draft = db.add.call_args.args[0]
    assert saved_draft.lead_id == 7
    assert saved_draft.subject == "A useful subject"
    assert saved_draft.body == "A personalized message."
    assert saved_draft.status == "draft"
    assert result["draft_id"] == 42
    db.commit.assert_called_once_with()
    db.refresh.assert_called_once_with(saved_draft)
