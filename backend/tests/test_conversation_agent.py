import pytest
from unittest.mock import Mock
from datetime import datetime, timezone
from fastapi.testclient import TestClient

from backend.main import app
from backend.database.database import get_db
from backend.database.models.leads import Lead
from backend.database.models.sales_interactions import SalesInteraction
from backend.ai_agents.conversation_agent import (
    summarize_sales_conversation,
    _build_local_conversation_summary,
)
from modules.module5_conversation import (
    summarize_and_store_interaction,
    get_lead_interactions,
    get_interaction_by_id,
    list_interactions,
)

client = TestClient(app)

SAMPLE_TRANSCRIPT = """
[00:00] Alex Mercer: David, thanks for making time today. I noticed CloudPulse just completed your Series C funding round.
[00:15] David Vance: Thanks Alex. We've scaled our engineering team by 40%, but our pipeline visibility has degraded as a result.
[00:32] Alex Mercer: Where is the biggest operational drag right now?
[00:54] David Vance: When customer success and rev ops pull forecast reconciliations from Postgres and Snowflake, we're seeing up to 4-hour latencies.
[01:25] Alex Mercer: SalesGenie connects into your live event streams to compute conversion probabilities continuously, cutting that latency to sub-minute updates.
[01:45] David Vance: We don't have engineering cycles to spend four weeks building custom ETL connectors.
[02:00] Alex Mercer: Zero custom ETL required. We have native REST connectors that deploy in under an hour.
[02:35] Alex Mercer: Let's set up a technical deep dive with our platform architect for next Thursday at 2 PM. I'll send over our staging connector documentation this afternoon.
[02:50] David Vance: Perfect. Include Sarah Miller from our Data Platform team on that invite as well.
"""


def test_summarize_sales_conversation_extraction():
    lead_context = {
        "company_name": "CloudPulse Technologies",
        "contact_name": "David Vance",
        "contact_title": "VP Infrastructure",
        "tech_stack": ["Kafka", "Postgres", "Snowflake", "AWS"],
    }
    result = summarize_sales_conversation(
        transcript_text=SAMPLE_TRANSCRIPT,
        lead_context=lead_context,
        interaction_type="meeting",
        subject="CloudPulse Discovery Sync",
    )

    assert "summary" in result
    assert isinstance(result["summary"], str)
    assert len(result["summary"]) > 20

    assert "discussion_points" in result
    assert isinstance(result["discussion_points"], list)
    assert len(result["discussion_points"]) >= 1

    assert "action_items" in result
    assert isinstance(result["action_items"], list)
    assert len(result["action_items"]) >= 1
    for item in result["action_items"]:
        assert "task" in item
        assert "owner" in item

    assert "risks" in result
    assert isinstance(result["risks"], list)

    assert "next_step" in result
    assert isinstance(result["next_step"], str)

    assert "ai_provider" in result
    assert "prompt_version" in result
    assert result["prompt_version"] == "v1.0"
    assert result["input_tokens"] > 0
    assert result["output_tokens"] > 0


def test_local_conversation_summary_fallback():
    lead_context = {
        "company_name": "HealthBridge",
        "contact_name": "Dr. Sarah Chen",
    }
    fallback = _build_local_conversation_summary(
        transcript_text=SAMPLE_TRANSCRIPT,
        lead_context=lead_context,
        interaction_type="call",
        subject="Technical Discovery",
    )

    assert "HealthBridge" in fallback["summary"] or "Dr. Sarah Chen" in fallback["summary"]
    assert len(fallback["discussion_points"]) > 0
    assert len(fallback["action_items"]) > 0
    assert len(fallback["risks"]) > 0
    assert len(fallback["next_step"]) > 0


def test_empty_transcript_raises_value_error():
    with pytest.raises(ValueError):
        summarize_sales_conversation(transcript_text="")

    with pytest.raises(ValueError):
        summarize_sales_conversation(transcript_text="   \n\t  ")


def test_module5_service_persistence():
    db = Mock()
    lead = Mock(
        lead_id=10,
        company_name="CloudPulse Technologies",
        contact_name="David Vance",
        contact_title="VP Infrastructure",
        industry="Technology",
        tech_stack=["Kafka", "AWS"],
    )
    db.get.return_value = lead

    def mock_refresh(interaction):
        interaction.interaction_id = 99

    db.refresh.side_effect = mock_refresh

    interaction = summarize_and_store_interaction(
        db=db,
        transcript_text=SAMPLE_TRANSCRIPT,
        lead_id=10,
        interaction_type="meeting",
        subject="CloudPulse Discovery",
    )

    assert interaction.lead_id == 10
    assert interaction.interaction_type == "meeting"
    assert interaction.processing_status == "completed"
    assert interaction.summary is not None
    assert len(interaction.discussion_points) > 0
    assert len(interaction.action_items) > 0
    assert db.add.called
    assert db.commit.called


def test_api_summarize_interaction_endpoint():
    db_mock = Mock()
    lead = Mock(
        lead_id=5,
        company_name="PayFlow Systems",
        contact_name="Elena Rostova",
        contact_title="VP RevOps",
        industry="Fintech",
        tech_stack=["HubSpot", "Postgres"],
    )
    db_mock.get.return_value = lead
    db_mock.refresh.side_effect = lambda interaction: (
        setattr(interaction, "interaction_id", 99),
        setattr(interaction, "created_at", datetime.now(timezone.utc)),
    )

    app.dependency_overrides[get_db] = lambda: db_mock
    try:
        payload = {
            "lead_id": 5,
            "interaction_type": "meeting",
            "subject": "Q4 Pipeline Forecast Review",
            "transcript_text": SAMPLE_TRANSCRIPT,
        }
        res = client.post("/api/interactions/summarize", json=payload)
        assert res.status_code == 201
        data = res.json()
        assert data["lead_id"] == 5
        assert data["interaction_type"] == "meeting"
        assert data["processing_status"] == "completed"
        assert "summary" in data
        assert "discussion_points" in data
        assert "action_items" in data
    finally:
        app.dependency_overrides.clear()
