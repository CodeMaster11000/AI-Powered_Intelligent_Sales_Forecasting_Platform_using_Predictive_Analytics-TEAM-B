import streamlit as st

from frontend.components.ui import html, kpi_card
from frontend.utils.api_client import (
    check_backend_health,
    clear_caches,
    fetch_pipeline_stats,
    fetch_scoring_queue_api,
    fetch_users,
)
from frontend.utils.helpers import esc, fmt_int, initials


def render_header(session_additions: int = 0) -> None:
    """Brand bar, status, theme toggle and the four global pipeline KPIs."""
    mode = st.session_state.get("theme_mode", "dark")
    online = check_backend_health()
    user = (fetch_users() or [{}])[0]
    user_name = user.get("name") or "Sales Rep"
    user_role = user.get("role") or "Sales"

    bar, refresh_col, theme_col = st.columns([7, 1.2, 1.4], vertical_alignment="center")
    with bar:
        status = (
            "<span class='sg-dot on'></span>Backend online" if online
            else "<span class='sg-dot off'></span>Backend offline"
        )
        html(
            f"""<div class="sg-topbar">
              <div class="sg-brand"><span class="sg-logo">⚡</span>SalesGenie AI
                <span class="sg-pill sg-pill-slate" style="font-weight:500">{status}</span></div>
              <div class="sg-user"><span class="sg-avatar">{esc(initials(user_name))}</span>
                <b>{esc(user_name)}</b><span class="who-role" style="opacity:.65;font-size:12px">{esc(user_role)}</span></div>
            </div>"""
        )
    with refresh_col:
        if st.button("↻ Refresh", width="stretch", help="Reload data from the backend"):
            clear_caches()
            st.rerun()
    with theme_col:
        if st.button("☀️ Light" if mode == "dark" else "🌙 Dark", width="stretch", key="theme_toggle"):
            st.session_state["theme_mode"] = "light" if mode == "dark" else "dark"
            st.rerun()

    if not online:
        html(
            "<div class='sg-callout warn' style='margin-top:10px'><b>Backend is unreachable.</b> "
            "Lists will be empty and saving is disabled until the API is back. "
            "Start it with <code>uvicorn backend.main:app --reload</code>.</div>"
        )

    stats = fetch_pipeline_stats()
    total = stats.get("total_leads", 0) or 0
    pending = stats.get("pending_ai_scoring", 0) or 0
    scored = max(total - pending, 0)
    coverage = f"{scored / total * 100:.0f}%" if total else "—"

    html("<div style='height:12px'></div>")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card("Pipeline leads", fmt_int(total), "Stored in PostgreSQL")
    with c2:
        kpi_card("Added this session", f"+{session_additions}", "Current working batch")
    with c3:
        kpi_card("Scoring coverage", coverage, f"{scored} of {total} leads scored" if total else "No leads yet",
                 "good" if total and pending == 0 else "")
    with c4:
        kpi_card("Awaiting AI score", fmt_int(pending), "Run Batch Score in Predictive Scoring" if pending else "All caught up",
                 "" if pending else "good")
    html("<div style='height:6px'></div>")
