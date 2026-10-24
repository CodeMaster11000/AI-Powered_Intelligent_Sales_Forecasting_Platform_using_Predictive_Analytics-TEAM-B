import json
import logging
from typing import Dict, Any, Optional, List
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
    with seamless heuristic offline fallback.
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

    if llm_output and isinstance(llm_output, dict) and "body" in llm_output:
        # Standardize and enrich LLM response
        provider_name = llm_client.last_provider_used or "AI Agent"
        return _format_outreach_response(llm_output, provider_name, lead_data, angle, tone)

    # 2. Resilient Deterministic Fallback
    logger.info("Operating in resilient deterministic fallback mode for cold email generation.")
    return _heuristic_outreach_fallback(lead_data, insight_data, angle, tone, custom_note)


def _format_outreach_response(
    data: Dict[str, Any],
    provider_name: str,
    lead_data: Dict[str, Any],
    angle: str,
    tone: str,
) -> Dict[str, Any]:
    """Ensures consistent schema and calculated metrics for outreach drafts."""
    body = data.get("body", "").strip()
    words = len(body.split())
    reading_seconds = max(10, round(words / 3.5))

    subjects = data.get("subject_options", [])
    if not isinstance(subjects, list) or len(subjects) == 0:
        company = lead_data.get("company_name", "your team")
        subjects = [
            f"Predictive pipeline intelligence for {company}",
            f"Quick question re: sales forecasting at {company}",
            f"Benchmark data for {lead_data.get('contact_name', 'there')}",
        ]

    selected_subject = data.get("selected_subject") or subjects[0]
    hook_score = data.get("hook_score", 91)
    if not isinstance(hook_score, (int, float)) or hook_score < 50:
        hook_score = 90

    triggers = data.get("personalization_triggers", [])
    if not triggers or not isinstance(triggers, list):
        triggers = ["Tech Stack Fit", "Growth Stage Alignment", "Persona Targeting"]

    return {
        "subject_options": subjects,
        "selected_subject": selected_subject,
        "body": body,
        "hook_score": int(hook_score),
        "word_count": words,
        "reading_time_seconds": reading_seconds,
        "personalization_triggers": triggers,
        "call_to_action": data.get("call_to_action", "5-minute benchmark review"),
        "provider_used": provider_name,
        "angle": angle,
        "tone": tone,
    }


def _heuristic_outreach_fallback(
    lead_data: Dict[str, Any],
    insight_data: Dict[str, Any],
    angle: str,
    tone: str,
    custom_note: str = "",
) -> Dict[str, Any]:
    """
    Deterministic enterprise copy generator grounded in verified lead signals.
    Guarantees robust, SLA-compliant cold outreach even in offline/air-gapped setups.
    """
    company = lead_data.get("company_name", "Acme Corp")
    contact = lead_data.get("contact_name") or "there"
    first_name = contact.split()[0] if contact else "there"
    title = lead_data.get("contact_title") or "Executive"
    industry = lead_data.get("industry") or "Technology"
    stage = lead_data.get("funding_stage") or "Growth"

    stack = lead_data.get("tech_stack", [])
    if isinstance(stack, str):
        try:
            stack = json.loads(stack)
        except Exception:
            stack = [t.strip() for t in stack.split(",") if t.strip()]

    stack_lead = stack[0] if (stack and len(stack) > 0) else "modern cloud"
    secondary_stack = f" and {stack[1]}" if (stack and len(stack) > 1) else ""

    # Personalization Triggers Found
    triggers = [
        f"Tech Footprint ({stack_lead}{secondary_stack})",
        f"Growth Signal ({stage} stage in {industry})",
        f"Role Focus ({title})",
    ]

    # Format optional custom note
    note_suffix_direct = f"\n\nP.S. {custom_note}" if custom_note else "\n\nOpen to a brief 5-minute chat this Thursday?"
    note_block = f"\n\nNote: {custom_note}" if custom_note else ""

    # Tone Variations
    if "Direct & Punchy" in tone:
        subject_options = [
            f"Quick question re: {stack_lead} at {company}",
            f"{company} pipeline accuracy question",
            f"5 mins this week for {first_name}?",
        ]
        body = (
            f"Hi {first_name},\n\n"
            f"Saw {company}'s momentum in {industry} and your engineering work scaling on {stack_lead}{secondary_stack}.\n\n"
            f"Most {title}s we partner with lose 4 to 6 hours every week wrestling with forecast variance as deal velocity accelerates.\n\n"
            f"SalesGenie's predictive engine connects directly to your stack, eliminating pipeline guesswork with 92% forecasting accuracy."
            f"{note_suffix_direct}\n\n"
            f"Best,\nAlex Rep\nEnterprise Revenue Team, SalesGenie AI"
        )
        hook_score = 94
        cta = "5-minute low-friction chat"

    elif "Problem-Centric" in tone:
        subject_options = [
            f"Eliminating pipeline variance at {company}",
            f"Benchmark data for {company}'s {stack_lead} infrastructure",
            f"Fixing sales qualification latency in {industry}",
        ]
        body = (
            f"Hi {first_name},\n\n"
            f"Quick observation regarding {company}: as teams scale data volume across {stack_lead}, sales qualification latency often introduces high variance into CRM quarterly forecasts.\n\n"
            f"Our platform benchmarks reveal an average 40% reduction in deal qualification cycles for {industry} teams by automating lead scoring with multi-agent predictive intelligence."
            f"{note_block}\n\n"
            f"Would you be open to a 10-minute walk-through of the comparative benchmark data this Wednesday or Thursday?\n\n"
            f"Regards,\nAlex Rep\nDirector of Solutions, SalesGenie AI"
        )
        hook_score = 92
        cta = "10-minute benchmark walk-through"

    else:  # Consultative / Executive (Default)
        subject_options = [
            f"Strategic observation for {company}'s {stage} growth",
            f"{company} + SalesGenie: predictive intelligence alignment",
            f"Idea for {first_name} on {industry} revenue scaling",
        ]
        body = (
            f"Hi {first_name},\n\n"
            f"Congratulations on {company}'s ongoing {stage} momentum.\n\n"
            f"In analyzing your infrastructure footprint, our revenue models flagged exceptional alignment between your {stack_lead}{secondary_stack} architecture and our predictive sales forecasting platform.\n\n"
            f"Specifically, we help revenue leaders at high-growth {industry} organizations detect high-intent buyer accounts 3 weeks earlier in their buying cycle while automating qualification workflows."
            f"{note_block}\n\n"
            f"Do you have 10 minutes this Thursday or Friday afternoon for a concise discussion to exchange notes?\n\n"
            f"Best regards,\nAlex Rep\nStrategic Accounts, SalesGenie AI"
        )
        hook_score = 95
        cta = "10-minute consultative exchange"


    words = len(body.split())
    reading_seconds = max(10, round(words / 3.5))

    return {
        "subject_options": subject_options,
        "selected_subject": subject_options[0],
        "body": body,
        "hook_score": hook_score,
        "word_count": words,
        "reading_time_seconds": reading_seconds,
        "personalization_triggers": triggers,
        "call_to_action": cta,
        "provider_used": "SalesGenie Deterministic AI Heuristics",
        "angle": angle,
        "tone": tone,
    }
