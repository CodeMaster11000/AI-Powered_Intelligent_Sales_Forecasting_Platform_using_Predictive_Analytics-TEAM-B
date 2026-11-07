import streamlit as st

from frontend.components.ui import html
from frontend.utils.helpers import esc


def render_next_best_action(action: dict | None) -> None:
    """Recommended follow-up for the selected lead."""
    if not action:
        st.caption("No next best action is available for this lead yet.")
        return

    channels = action.get("channel_mix") or []
    html(
        f"""<div class="nba-heading"><div><div class="nba-kicker">Recommended follow-up</div><h5>Next Best Action</h5></div>
        <span class="nba-badge">AI guidance</span></div>
        <div class="nba-action">{esc(action.get("recommended_action"), "Review the lead and choose a follow-up.")}</div>
        <div class="nba-details">
          <div class="nba-detail"><span class="nba-label">Urgency</span><strong>{esc(action.get("urgency"), "Standard pipeline")}</strong></div>
          <div class="nba-detail"><span class="nba-label">Follow-up window</span><strong>{esc(action.get("follow_up_timing"), "Nurture track")}</strong></div>
          <div class="nba-detail"><span class="nba-label">Channels</span><strong>{len(channels)} recommended</strong></div>
        </div>"""
    )
    if channels:
        html("<div class='nba-section-label'>Recommended channel mix</div>" + "".join(
            f"<div class='nba-channel'><span>→</span>{esc(c)}</div>" for c in channels))
    if action.get("content_strategy"):
        html(f"<div class='nba-section-label'>Content strategy</div><div class='nba-content'>{esc(action['content_strategy'])}</div>")
