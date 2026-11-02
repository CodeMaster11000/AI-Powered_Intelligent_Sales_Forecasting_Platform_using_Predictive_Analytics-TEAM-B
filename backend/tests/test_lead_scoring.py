import pytest
from modules.module4_scoring import (
    calculate_predictive_score,
    generate_next_best_action,
    score_and_recommend,
)


def test_calculate_predictive_score_enterprise_hot():
    lead = {
        "company_name": "Databricks",
        "contact_name": "Ali Ghodsi",
        "contact_title": "CEO & Co-Founder",
        "company_size": "Enterprise (1000+)",
        "annual_revenue": "$500M+",
        "funding_stage": "Growth / IPO Track",
        "email": "ali@databricks.com",
        "phone": "+1-415-555-0100",
        "location": "San Francisco, CA",
        "source": "Inbound Website Form",
        "tech_stack": ["Spark", "AWS", "Python", "Kubernetes"],
    }
    insights = {
        "high_growth_potential": True,
        "overall_tech_compatibility_score": 92,
        "growth_indicators": ["Recent $500M funding round"],
        "transformation_opportunities": [
            {"opportunity_name": "Lakehouse Optimization", "details": "Scale compute efficiency"}
        ],
        "decision_makers": [
            {"name": "Ali Ghodsi", "role_title": "CEO"}
        ],
    }

    result = calculate_predictive_score(lead, insights)

    assert result["score"] >= 75
    assert result["priority"] == "hot"
    assert 50.0 <= result["conversion_probability"] <= 100.0
    assert "factors" in result
    assert "fit" in result["factors"]
    assert "intent" in result["factors"]
    assert "decision" in result["factors"]
    assert "engagement" in result["factors"]
    assert result["factors"]["fit"]["score"] <= 30
    assert result["factors"]["intent"]["score"] <= 25
    assert result["factors"]["decision"]["score"] <= 25
    assert result["factors"]["engagement"]["score"] <= 20


def test_calculate_predictive_score_seed_startup():
    lead = {
        "company_name": "Stealth AI",
        "contact_name": "John Doe",
        "contact_title": "Software Engineer",
        "company_size": "Startup (1-10)",
        "annual_revenue": "Pre-revenue",
        "funding_stage": "Seed",
        "email": "john@stealth.io",
        "source": "CSV",
    }
    insights = {
        "high_growth_potential": False,
        "overall_tech_compatibility_score": 40,
    }

    result = calculate_predictive_score(lead, insights)

    assert result["score"] < 50
    assert result["priority"] in ["warm", "cold"]
    assert result["conversion_probability"] < 50.0


def test_generate_next_best_action_hot():
    score_data = {"score": 85, "priority": "hot"}
    lead = {
        "company_name": "Snowflake",
        "contact_name": "Frank Slootman",
        "contact_title": "Chairman",
        "email": "frank@snowflake.com",
        "phone": "+1-800-555-0199",
    }
    insights = {
        "transformation_opportunities": [
            {"opportunity_name": "Cloud Data Modernization"}
        ]
    }

    nba = generate_next_best_action(score_data, lead, insights)

    assert nba["urgency"] == "High Priority"
    assert "< 24 Hours" in nba["follow_up_timing"]
    assert "Hyper-Personalized Cold Email" in nba["channel_mix"]
    assert "Direct Executive Phone Call" in nba["channel_mix"]
    assert "Cloud Data Modernization" in nba["content_strategy"]


def test_score_and_recommend_unified():
    lead = {
        "company_name": "HealthBridge",
        "contact_name": "Dr. Sarah Chen",
        "contact_title": "Chief Information Officer",
        "company_size": "Enterprise",
        "annual_revenue": "$45M",
        "funding_stage": "Series C",
        "email": "sarah.chen@healthbridge.org",
        "tech_stack": ["Azure", "Kubernetes", "FHIR"],
    }
    insights = {
        "high_growth_potential": True,
        "overall_tech_compatibility_score": 88,
        "transformation_opportunities": [
            {"opportunity_name": "FHIR API Interoperability"}
        ],
        "decision_makers": [{"name": "Dr. Sarah Chen", "role_title": "CIO"}],
    }

    res = score_and_recommend(lead, insights)

    assert "scoring" in res
    assert "recommendations" in res
    assert res["scoring"]["priority"] == "hot"
    assert res["recommendations"]["urgency"] == "High Priority"

