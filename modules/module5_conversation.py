"""
SalesGenie Platform - Module 5: Conversation Intelligence & Meeting/Call Summarization
Engineered for Module 5 Deliverables (Milestone 3):
- REQ-M5-01: Verbatim meeting & call transcript summarization pipeline
- REQ-M5-02: Structured action item extraction with task, owner, and due dates
- REQ-M5-03: Deal risk and technical objection detection
- REQ-M5-04: Persistence in PostgreSQL sales_interactions table with full AI metadata audit
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database.models.leads import Lead
from backend.database.models.sales_interactions import SalesInteraction
from backend.ai_agents.conversation_agent import (
    summarize_sales_conversation,
    _build_local_conversation_summary,
)

logger = logging.getLogger(__name__)


def summarize_and_store_interaction(
    db: Session,
    transcript_text: str,
    lead_id: Optional[int] = None,
    interaction_type: str = "meeting",
    subject: Optional[str] = None,
    occurred_at: Optional[datetime] = None,
    connection_id: Optional[int] = None,
    provider_activity_id: Optional[str] = None,
    preferred_provider: Optional[str] = None,
) -> SalesInteraction:
    """
    Executes the Conversation Intelligence pipeline on raw transcript text,
    extracts summary, discussion points, action items, risks, and next steps,
    and commits the record to the sales_interactions database table.
    """
    if not transcript_text or not transcript_text.strip():
        raise ValueError("Transcript text cannot be empty.")

    interaction_type = interaction_type.lower()
    if interaction_type not in ("meeting", "call", "email", "note"):
        interaction_type = "meeting"

    lead_context = {}
    if lead_id:
        lead = db.get(Lead, lead_id)
        if lead:
            lead_context = {
                "company_name": lead.company_name,
                "contact_name": lead.contact_name or "Decision Maker",
                "contact_title": lead.contact_title or "Executive",
                "industry": lead.industry or "Technology",
                "tech_stack": lead.tech_stack or [],
            }

    occurred_timestamp = occurred_at or datetime.now(timezone.utc)
    if subject is None:
        c_name = lead_context.get("company_name", "Lead")
        subject = f"{interaction_type.capitalize()} with {c_name}"

    try:
        # Run AI summarization agent
        ai_res = summarize_sales_conversation(
            transcript_text=transcript_text,
            lead_context=lead_context,
            interaction_type=interaction_type,
            subject=subject,
            preferred_provider=preferred_provider,
        )

        interaction = SalesInteraction(
            lead_id=lead_id,
            connection_id=connection_id,
            provider_activity_id=provider_activity_id,
            interaction_type=interaction_type,
            occurred_at=occurred_timestamp,
            subject=subject,
            transcript_text=transcript_text,
            summary=ai_res.get("summary"),
            discussion_points=ai_res.get("discussion_points"),
            action_items=ai_res.get("action_items"),
            risks=ai_res.get("risks"),
            next_step=ai_res.get("next_step"),
            processing_status="completed",
            ai_provider=ai_res.get("ai_provider"),
            ai_model=ai_res.get("ai_model"),
            prompt_version=ai_res.get("prompt_version", "v1.0"),
            input_tokens=ai_res.get("input_tokens"),
            output_tokens=ai_res.get("output_tokens"),
        )
        db.add(interaction)
        db.commit()
        db.refresh(interaction)
        return interaction

    except Exception as exc:
        logger.error(f"Error executing conversation summarization: {exc}")
        # Create failed interaction record for operational visibility and audit
        failed_interaction = SalesInteraction(
            lead_id=lead_id,
            connection_id=connection_id,
            provider_activity_id=provider_activity_id,
            interaction_type=interaction_type,
            occurred_at=occurred_timestamp,
            subject=subject,
            transcript_text=transcript_text,
            processing_status="failed",
            error_message=str(exc),
        )
        db.add(failed_interaction)
        db.commit()
        db.refresh(failed_interaction)
        raise exc


def get_lead_interactions(db: Session, lead_id: int) -> List[SalesInteraction]:
    """Retrieves all sales interactions for a given lead, sorted by recency."""
    return db.execute(
        select(SalesInteraction)
        .where(SalesInteraction.lead_id == lead_id)
        .order_by(SalesInteraction.occurred_at.desc(), SalesInteraction.interaction_id.desc())
    ).scalars().all()


def get_interaction_by_id(db: Session, interaction_id: int) -> Optional[SalesInteraction]:
    """Retrieves a single sales interaction by primary key."""
    return db.get(SalesInteraction, interaction_id)


def list_interactions(
    db: Session,
    limit: int = 50,
    offset: int = 0,
    interaction_type: Optional[str] = None,
) -> List[SalesInteraction]:
    """Returns a paginated list of all sales interactions with optional type filter."""
    query = select(SalesInteraction)
    if interaction_type:
        query = query.where(SalesInteraction.interaction_type == interaction_type.lower())
    query = query.order_by(SalesInteraction.occurred_at.desc(), SalesInteraction.interaction_id.desc())
    query = query.limit(limit).offset(offset)
    return db.execute(query).scalars().all()
