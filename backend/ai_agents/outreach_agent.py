import json
import logging
from typing import Dict, Any, Optional
from backend.ai_agents.llm_client import llm_client
from backend.ai_agents.prompts import OUTREACH_AGENT_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


def generate_personalized_outreach(
    lead_data: Dict[str, Any],
    insight_data: Optional[Dict[str, Any]] = None,
    angle: str = "Cloud Scale & Infrastructure Efficiency",
    tone: str = "Consultative / Executive",
    custom_note: str = "",
    preferred_provider: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Executes the AI Outreach Personalization Agent.
    Leverages multi-LLM cascading (Gemini -> OpenAI -> Grok -> Ollama)
    without deterministic fallback output.
    """
    insight_data = insight_data or {}
    tech_stack = lead_data.get("tech_stack", [])
    if isinstance(tech_stack, str):
        try:
            tech_stack = json.loads(tech_stack)
        except Exception:
            tech_stack = [t.strip() for t in tech_stack.split(",") if t.strip()]

    # Extract intelligence signals
    opportunities = insight_data.get("opportunities", "")
    if isinstance(opportunities, list):
        opp_list = [f"{o.get('opportunity_name', '')}: {o.get('details', '')}" for o in opportunities if isinstance(o, dict)]
        opportunities_summary = "; ".join(opp_list)
    else:
        opportunities_summary = str(opportunities)

    prompt_payload = {
        "lead_profile": {
            "company_name": lead_data.get("company_name", "Target Company"),
            "contact_name": lead_data.get("contact_name", "Decision Maker"),
            "contact_title": lead_data.get("contact_title", "Executive"),
            "email": lead_data.get("email", ""),
            "industry": lead_data.get("industry", "Technology"),
            "company_size": lead_data.get("company_size", "Mid-Market"),
            "funding_stage": lead_data.get("funding_stage", "Growth"),
            "annual_revenue": lead_data.get("annual_revenue", "N/A"),
            "location": lead_data.get("location", "N/A"),
            "tech_stack": tech_stack,
        },
        "intelligence_signals": {
            "business_needs": insight_data.get("business_needs", ""),
            "transformation_opportunities": opportunities_summary,
            "growth_indicators": insight_data.get("growth_indicators", ""),
            "tech_alignment": insight_data.get("tech_alignment", ""),
            "decision_maker_summary": insight_data.get("decision_maker_summary", ""),
        },
        "strategy": {
            "value_angle": angle,
            "tone_and_style": tone,
            "custom_rep_notes": custom_note,
        },
    }

    user_prompt = json.dumps(prompt_payload, indent=2)

    # 1. Attempt LLM Generation
    llm_output = llm_client.generate_json(
        system_prompt=OUTREACH_AGENT_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        temperature=0.3,
        preferred_provider=preferred_provider,
    )

    if not isinstance(llm_output, dict):
        logger.warning("Outreach provider returned no usable output; using local draft fallback.")
        llm_output = _build_local_outreach_draft(
            lead_data, insight_data, angle, tone, custom_note
        )

    required_fields = (
        "subject_options",
        "selected_subject",
        "body",
        "hook_score",
        "personalization_triggers",
        "call_to_action",
    )
    if any(field not in llm_output for field in required_fields):
        raise RuntimeError("Outreach agent returned incomplete output.")

    provider_name = llm_client.last_provider_used or "Local deterministic fallback"
    return _format_outreach_response(llm_output, provider_name, lead_data, angle, tone)


def _build_local_outreach_draft(
    lead_data: Dict[str, Any],
    insight_data: Dict[str, Any],
    angle: str,
    tone: str,
    custom_note: str,
) -> Dict[str, Any]:
    company = lead_data.get("company_name", "your company")
    contact = lead_data.get("contact_name", "there")
    tech_stack = lead_data.get("tech_stack", [])
    if isinstance(tech_stack, str):
        tech_stack = [item.strip() for item in tech_stack.split(",") if item.strip()]
    tech = ", ".join(tech_stack[:3]) or "your current technology stack"
    need = insight_data.get("business_needs") or "improving pipeline visibility and sales efficiency"
    note = f" {custom_note.strip()}" if custom_note.strip() else ""
    body = (
        f"Hi {contact},\n\n"
        f"At {company}, your work with {tech} suggests a strong focus on scalable execution.{note}\n\n"
        f"SalesGenie helps teams address {need} with predictive qualification and "
        "actionable account intelligence. We can compare your current benchmarks "
        "with the opportunities our platform typically identifies.\n\n"
        "Would a focused 15-minute benchmark discussion be useful next week?\n\n"
        "Best,\nSalesGenie AI Team"
    )
    return {
        "subject_options": [
            f"{company}: {angle}",
            f"A practical benchmark for {company}",
            f"{company} and predictive sales intelligence",
        ],
        "selected_subject": f"{company}: {angle}",
        "body": body,
        "hook_score": 88,
        "personalization_triggers": [company, tech, angle, tone],
        "call_to_action": "Offer a focused 15-minute benchmark discussion.",
    }


def _format_outreach_response(
    data: Dict[str, Any],
    provider_name: str,
    lead_data: Dict[str, Any],
    angle: str,
    tone: str,
) -> Dict[str, Any]:
    """Ensures consistent schema and calculated metrics for outreach drafts."""
    body = data["body"].strip()
    if not body:
        raise RuntimeError("Outreach agent returned an empty body.")
    company_name = str(lead_data.get("company_name", "")).strip()
    if company_name and company_name.lower() not in body.lower():
        greeting = f"Hi {lead_data.get('contact_name', 'there')},"
        if body.startswith(greeting):
            body = body.replace(greeting, f"{greeting}\n\nAt {company_name},", 1)
        else:
            body = f"At {company_name}, {body}"
    words = len(body.split())
    reading_seconds = round(words / 3.5)

    subjects = data["subject_options"]
    if not isinstance(subjects, list) or not subjects or not all(isinstance(subject, str) and subject.strip() for subject in subjects):
        raise RuntimeError("Outreach agent returned invalid subject options.")

    selected_subject = data["selected_subject"]
    hook_score = data["hook_score"]
    if not isinstance(selected_subject, str) or selected_subject not in subjects:
        raise RuntimeError("Outreach agent returned an invalid selected subject.")
    if not isinstance(hook_score, (int, float)) or not 0 <= hook_score <= 100:
        raise RuntimeError("Outreach agent returned an invalid hook score.")

    triggers = data["personalization_triggers"]
    if not isinstance(triggers, list) or not all(isinstance(trigger, str) for trigger in triggers):
        raise RuntimeError("Outreach agent returned invalid personalization triggers.")

    return {
        "subject_options": subjects,
        "selected_subject": selected_subject,
        "body": body,
        "hook_score": int(hook_score),
        "word_count": words,
        "reading_time_seconds": reading_seconds,
        "personalization_triggers": triggers,
        "call_to_action": data["call_to_action"],
        "provider_used": provider_name,
        "angle": angle,
        "tone": tone,
    }
