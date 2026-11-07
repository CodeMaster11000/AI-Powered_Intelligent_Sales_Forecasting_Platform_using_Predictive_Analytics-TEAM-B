"""Pipeline & Forecast dashboard (new). Built only from existing endpoints."""
from __future__ import annotations

import altair as alt
import pandas as pd
import streamlit as st

from frontend.components.ui import backend_error, card_title, empty_state, html, kpi_card, page_header, priority_pill
from frontend.styles.themes import get_tokens
from frontend.utils.api_client import fetch_leads_api, fetch_scoring_queue_api
from frontend.utils.helpers import esc, fmt_pct

STAGES = ["New Leads", "Qualified", "Proposal", "Negotiation", "Closed Won"]
TIER_COLORS = {"Hot": "#10B981", "Warm": "#F59E0B", "Cold": "#94A3B8", "Unscored": "#475569"}
FIELDS_FOR_COMPLETENESS = ["contact_name", "contact_title", "phone", "industry", "company_size",
                           "annual_revenue", "funding_stage", "location", "tech_stack"]


def _chart_style(chart: alt.Chart) -> alt.Chart:
    t = get_tokens()  # follow the active light/dark theme
    return (chart.configure_view(strokeWidth=0).configure(background="transparent")
            .configure_axis(labelColor=t["text_muted"], titleColor=t["text_muted"], gridColor=t["border"], domain=False)
            .configure_legend(labelColor=t["text_muted"], titleColor=t["text_muted"]))


def render_dashboard() -> None:
    page_header("Pipeline & Forecast",
                "Where the pipeline stands today and how many deals the AI scores expect to convert.")

    queue = fetch_scoring_queue_api()
    if queue is None:
        with st.container(border=True):
            backend_error("pipeline data")
        return
    if not queue:
        with st.container(border=True):
            empty_state("📈", "Nothing to forecast yet", "Import or add leads, then score them to see the forecast.")
        return

    leads = fetch_leads_api() or []
    qdf = pd.DataFrame(queue)
    scored = qdf[qdf["priority"] != "unscored"].copy()
    total, n_scored = len(qdf), len(scored)

    avg_score = scored["score"].mean() if n_scored else None
    expected_wins = (scored["conversion_probability"].fillna(0).sum() / 100) if n_scored else 0.0
    hot = int((qdf["priority"] == "hot").sum())
    avg_prob = scored["conversion_probability"].mean() if n_scored else None

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card("Expected conversions", f"{expected_wins:.1f}", f"of {n_scored} scored leads (sum of win probabilities)")
    with c2:
        kpi_card("Avg win probability", fmt_pct(avg_prob), "Across scored leads")
    with c3:
        kpi_card("Avg lead score", f"{avg_score:.0f} / 100" if avg_score is not None else "—", f"{hot} hot lead{'s' if hot != 1 else ''}")
    with c4:
        kpi_card("Scoring coverage", f"{n_scored / total * 100:.0f}%", f"{total - n_scored} still unscored",
                 "good" if n_scored == total else "")

    html("<div style='height:10px'></div>")
    left, right = st.columns(2)

    with left:
        with st.container(border=True):
            card_title("Lead score distribution", "Scored leads")
            if n_scored:
                bins = pd.cut(scored["score"], bins=[-1, 19, 39, 59, 74, 100],
                              labels=["0–19", "20–39", "40–59", "60–74", "75–100"])
                dist = bins.value_counts().sort_index().reset_index()
                dist.columns = ["Score band", "Leads"]
                chart = alt.Chart(dist).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4, color="#2DD4BF").encode(
                    x=alt.X("Score band:N", sort=None, axis=alt.Axis(labelAngle=0)),
                    y=alt.Y("Leads:Q", axis=alt.Axis(tickMinStep=1)),
                    tooltip=["Score band", "Leads"]).properties(height=240)
                st.altair_chart(_chart_style(chart), width="stretch")
            else:
                empty_state("⚪", "No scored leads yet", "Run Batch Score to populate this chart.")

    with right:
        with st.container(border=True):
            card_title("Priority mix & expected wins", "By tier")
            tier_label = {"hot": "Hot", "warm": "Warm", "cold": "Cold", "unscored": "Unscored"}
            mix = qdf.assign(Tier=qdf["priority"].map(tier_label)).groupby("Tier").agg(
                Leads=("lead_id", "count"),
                Wins=("conversion_probability", lambda s: s.fillna(0).sum() / 100)).reset_index()
            mix["Wins"] = mix["Wins"].round(2)
            chart = alt.Chart(mix).mark_bar(cornerRadiusTopRight=4, cornerRadiusBottomRight=4).encode(
                y=alt.Y("Tier:N", sort=["Hot", "Warm", "Cold", "Unscored"], title=None),
                x=alt.X("Leads:Q", axis=alt.Axis(tickMinStep=1)),
                color=alt.Color("Tier:N", legend=None, scale=alt.Scale(
                    domain=list(TIER_COLORS), range=list(TIER_COLORS.values()))),
                tooltip=["Tier", "Leads", alt.Tooltip("Wins:Q", title="Expected wins")]).properties(height=240)
            st.altair_chart(_chart_style(chart), width="stretch")

    left, right = st.columns([1, 1])
    with left:
        with st.container(border=True):
            card_title("Pipeline by stage", "Lead status")
            if leads:
                ldf = pd.DataFrame(leads)
                counts = ldf["lead_status"].fillna("New Leads").value_counts().reindex(STAGES, fill_value=0).reset_index()
                counts.columns = ["Stage", "Leads"]
                chart = alt.Chart(counts).mark_bar(cornerRadiusTopRight=4, cornerRadiusBottomRight=4, color="#60A5FA").encode(
                    y=alt.Y("Stage:N", sort=STAGES, title=None), x=alt.X("Leads:Q", axis=alt.Axis(tickMinStep=1)),
                    tooltip=["Stage", "Leads"]).properties(height=220)
                st.altair_chart(_chart_style(chart), width="stretch")
                filled = ldf.reindex(columns=FIELDS_FOR_COMPLETENESS).apply(
                    lambda col: col.map(lambda v: bool(v) if not isinstance(v, float) else not pd.isna(v))).values.mean()
                st.caption(f"Lead profile completeness: **{filled * 100:.0f}%** across {len(FIELDS_FOR_COMPLETENESS)} enrichment fields.")
            else:
                empty_state("📋", "No lead records", "Stage data comes from the leads table.")

    with right:
        with st.container(border=True):
            card_title("Top opportunities", "Highest win probability")
            top = scored.sort_values(["conversion_probability", "score"], ascending=False).head(6)
            if top.empty:
                empty_state("🎯", "No scored leads yet")
            for _, row in top.iterrows():
                html(
                    f"<div class='sg-lead-row'><div class='sg-lead-main'><div class='sg-lead-name'>{esc(row['company_name'])}</div>"
                    f"<div class='sg-lead-meta'>{esc(row['contact_name'])} · {esc(row.get('industry'))}</div></div>"
                    f"<div style='text-align:right'><div style='font-weight:700'>{esc(fmt_pct(row['conversion_probability']))}</div>"
                    f"{priority_pill(row['priority'], row['score'])}</div></div>"
                )
            if st.button("Open Predictive Scoring →", width="stretch", key="dash_to_scoring"):
                st.session_state["pending_nav_tab"] = "⚡ Predictive Scoring"
                st.rerun()
