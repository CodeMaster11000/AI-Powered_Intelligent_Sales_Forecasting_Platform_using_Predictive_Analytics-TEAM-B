from typing import Any, Dict, Optional
from backend.ai_agents.outreach_agent import generate_personalized_outreach


def generate_personalized_email(
    lead: Any,
    insight_data: Optional[Dict[str, Any]] = None,
    angle: str = "Cloud Scale & Infrastructure Efficiency",
    tone: str = "Consultative / Executive",
    custom_note: str = "",
    preferred_provider: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Module 3: AI Personalized Outreach Generation Engine.
    Orchestrates the multi-LLM Outreach Agent (Gemini, OpenAI, xAI Grok, Ollama)
    grounded in prospect dossier signals, tech stack, and transformation opportunities.
    """
    insight_data = insight_data or {}

    # Extract lead data whether lead is an ORM model or a dictionary
    if hasattr(lead, "company_name"):
        lead_dict = {
            "lead_id": getattr(lead, "lead_id", None),
            "company_name": lead.company_name,
            "contact_name": getattr(lead, "contact_name", None),
            "contact_title": getattr(lead, "contact_title", None),
            "email": getattr(lead, "email", ""),
            "phone": getattr(lead, "phone", None),
            "industry": getattr(lead, "industry", None),
            "company_size": getattr(lead, "company_size", None),
            "annual_revenue": getattr(lead, "annual_revenue", None),
            "funding_stage": getattr(lead, "funding_stage", None),
            "funding_raised": getattr(lead, "funding_raised", None),
            "location": getattr(lead, "location", None),
            "tech_stack": getattr(lead, "tech_stack", None),
        }
    elif isinstance(lead, dict):
        lead_dict = lead
    else:
        lead_dict = {"company_name": str(lead)}

    return generate_personalized_outreach(
        lead_data=lead_dict,
        insight_data=insight_data,
        angle=angle,
        tone=tone,
        custom_note=custom_note,
        preferred_provider=preferred_provider,
    )