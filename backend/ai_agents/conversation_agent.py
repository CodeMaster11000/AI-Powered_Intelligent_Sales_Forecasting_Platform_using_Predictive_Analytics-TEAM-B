import json
import logging
import re
from typing import Any, Dict, List, Optional
from backend.ai_agents.llm_client import llm_client
from backend.ai_agents.prompts import CONVERSATION_SUMMARIZER_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


def summarize_sales_conversation(
    transcript_text: str,
    lead_context: Optional[Dict[str, Any]] = None,
    interaction_type: str = "meeting",
    subject: Optional[str] = None,
    preferred_provider: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Executes the Conversation Intelligence & Summarization Agent (Module 5).
    Leverages multi-LLM cascading (Gemini -> OpenAI -> Grok -> Ollama -> Local Fallback)
    to extract executive summary, discussion points, structured action items,
    risks, and next steps from verbatim sales call transcripts.
    """
    if not transcript_text or not transcript_text.strip():
        raise ValueError("Transcript text cannot be empty for summarization.")

    lead_context = lead_context or {}
    company_name = lead_context.get("company_name", "Target Account")
    contact_name = lead_context.get("contact_name", "Decision Maker")
    contact_title = lead_context.get("contact_title", "Executive")
    tech_stack = lead_context.get("tech_stack", [])
    if isinstance(tech_stack, str):
        try:
            tech_stack = json.loads(tech_stack)
        except Exception:
            tech_stack = [t.strip() for t in tech_stack.split(",") if t.strip()]

    prompt_payload = {
        "interaction_metadata": {
            "interaction_type": interaction_type,
            "subject": subject or f"Sales {interaction_type.capitalize()} with {company_name}",
        },
        "lead_context": {
            "company_name": company_name,
            "contact_name": contact_name,
            "contact_title": contact_title,
            "industry": lead_context.get("industry", "Technology"),
            "tech_stack": tech_stack,
        },
        "raw_transcript": transcript_text.strip(),
    }

    user_prompt = json.dumps(prompt_payload, indent=2)

    # Approximate token estimation
    est_input_tokens = max(1, int(len(user_prompt.split()) * 1.33))

    # 1. Attempt Multi-LLM Generation with Cascading Failover
    llm_output = llm_client.generate_json(
        system_prompt=CONVERSATION_SUMMARIZER_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        temperature=0.2,
        preferred_provider=preferred_provider,
    )

    if not isinstance(llm_output, dict):
        logger.warning("LLM provider returned no usable conversation summary; using local deterministic fallback.")
        llm_output = _build_local_conversation_summary(
            transcript_text=transcript_text,
            lead_context=lead_context,
            interaction_type=interaction_type,
            subject=subject,
        )

    # 2. Validate and Normalize Structured Output
    required_fields = ("summary", "discussion_points", "action_items", "risks", "next_step")
    for field in required_fields:
        if field not in llm_output:
            logger.warning(f"Missing field '{field}' in LLM output, falling back to local heuristic for field.")
            fallback_part = _build_local_conversation_summary(
                transcript_text=transcript_text,
                lead_context=lead_context,
                interaction_type=interaction_type,
                subject=subject,
            )
            llm_output[field] = fallback_part[field]

    # Clean and validate action items
    raw_action_items = llm_output.get("action_items") or []
    normalized_action_items = []
    if isinstance(raw_action_items, list):
        for item in raw_action_items:
            if isinstance(item, dict):
                normalized_action_items.append({
                    "task": str(item.get("task", "Follow up")).strip(),
                    "owner": str(item.get("owner", "Account Executive")).strip(),
                    "due_date": str(item.get("due_date", "TBD")).strip(),
                })
            elif isinstance(item, str) and item.strip():
                normalized_action_items.append({
                    "task": item.strip(),
                    "owner": "Account Executive",
                    "due_date": "TBD",
                })

    raw_discussion_points = llm_output.get("discussion_points") or []
    normalized_discussion_points = [
        str(dp).strip() for dp in raw_discussion_points if str(dp).strip()
    ]

    raw_risks = llm_output.get("risks") or []
    normalized_risks = [
        str(r).strip() for r in raw_risks if str(r).strip()
    ]

    summary_text = str(llm_output.get("summary", "")).strip()
    next_step_text = str(llm_output.get("next_step", "")).strip()

    provider_name = llm_client.last_provider_used or "Deterministic Local Fallback"
    est_output_tokens = max(1, int(len((summary_text + " ".join(normalized_discussion_points)).split()) * 1.33))

    return {
        "summary": summary_text,
        "discussion_points": normalized_discussion_points,
        "action_items": normalized_action_items,
        "risks": normalized_risks,
        "next_step": next_step_text,
        "ai_provider": provider_name,
        "ai_model": getattr(llm_client, "last_model_used", "multi-llm"),
        "prompt_version": "v1.0",
        "input_tokens": est_input_tokens,
        "output_tokens": est_output_tokens,
    }


def _build_local_conversation_summary(
    transcript_text: str,
    lead_context: Dict[str, Any],
    interaction_type: str,
    subject: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Deterministic rule-based fallback when external LLM APIs are unreachable.
    Guarantees 100% SLA and zero crash tolerance for Module 5.
    """
    company = lead_context.get("company_name", "the prospect")
    contact = lead_context.get("contact_name", "the client")
    
    lines = [line.strip() for line in transcript_text.split("\n") if line.strip()]

    # Extract discussion points from conversation lines
    discussion_points = []
    action_items = []
    risks = []

    for line in lines:
        cleaned = re.sub(r"^\[\d\d:\d\d\]\s*", "", line)
        lower = cleaned.lower()

        # Action items detection
        if any(w in lower for w in ["will do", "send over", "send you", "schedule", "deliver", "include", "set up"]):
            owner = "Account Executive" if any(w in lower for w in ["i'll", "we'll", "i will", "send over", "deliver"]) else contact
            action_items.append({
                "task": cleaned[:120],
                "owner": owner,
                "due_date": "Next 24-48 Hours",
            })

        # Risks detection
        elif any(w in lower for w in ["concern", "risk", "delay", "friction", "latency", "bottleneck", "hipaa", "compliance", "budget"]):
            risks.append(cleaned[:140])

        # Discussion topics
        elif any(w in lower for w in ["pipeline", "architecture", "scaling", "tech stack", "integration", "forecast", "deal"]):
            if len(discussion_points) < 5:
                discussion_points.append(cleaned[:140])

    if not discussion_points:
        discussion_points = [
            f"Evaluated current operational and technological bottlenecks at {company}.",
            f"Discussed integration feasibility and technical requirements with {contact}.",
            "Reviewed prospective ROI timeline and deployment roadmap.",
        ]

    if not action_items:
        action_items = [
            {"task": f"Deliver SalesGenie benchmark summary and technical overview to {contact}", "owner": "Account Executive", "due_date": "Next 24 Hours"},
            {"task": f"Coordinate technical discovery follow-up with {company} engineering team", "owner": "Account Executive", "due_date": "Next Week"},
        ]

    if not risks:
        risks = [
            "Technical alignment and migration timeline verification required prior to full rollout."
        ]

    summary = (
        f"Completed a {interaction_type} with {contact} at {company}. "
        f"The discussion focused on evaluating workflow efficiencies, technology integration points, and current scaling bottlenecks. "
        f"Next steps involve delivering technical documentation and scheduling follow-up evaluation."
    )

    next_step = f"Follow up with {contact} with technical specifications and confirm calendar invite for next milestone demo."

    return {
        "summary": summary,
        "discussion_points": discussion_points[:5],
        "action_items": action_items[:5],
        "risks": risks[:3],
        "next_step": next_step,
    }
