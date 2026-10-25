import json
from typing import Dict, Any, Optional
from backend.ai_agents.llm_client import llm_client
from backend.ai_agents.prompts import OUTREACH_AGENT_SYSTEM_PROMPT

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
        raise RuntimeError("Outreach agent did not return a valid response.")

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

    provider_name = llm_client.last_provider_used
    if not provider_name:
        raise RuntimeError("Outreach provider was not recorded.")
    return _format_outreach_response(llm_output, provider_name, lead_data, angle, tone)


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
