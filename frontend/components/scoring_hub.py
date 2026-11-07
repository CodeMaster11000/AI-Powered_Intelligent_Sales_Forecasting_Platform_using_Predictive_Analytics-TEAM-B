import streamlit as st

from frontend.components.next_best_action import render_next_best_action
from frontend.components.ui import (
    backend_error, card_title, chips, empty_state, html, info_grid, page_header,
    pill, priority_pill, progress_bar, score_ring,
)
from frontend.utils.api_client import (
    batch_score_api, fetch_lead_dossier_api, fetch_scoring_queue_api, score_lead_api,
)
from frontend.utils.helpers import PRIORITY_META, esc, fmt_pct

TIER_FILTERS = {
    "All tiers": None, "Hot (≥ 75)": "hot", "Warm (40–74)": "warm", "Cold (< 40)": "cold", "Unscored": "unscored",
}
SORTS = {
    "Score: high → low": lambda q: (q.get("score") is None, -(q.get("score") or 0)),
    "Win probability": lambda q: (q.get("conversion_probability") is None, -(q.get("conversion_probability") or 0)),
    "Company A–Z": lambda q: str(q.get("company_name", "")).lower(),
    "Newest first": lambda q: -int(q.get("lead_id", 0)),
}


def _sync_selected_lead(session_state, visible: list[dict]) -> None:
    """Keep the selection valid when search / filters change what is visible."""
    visible_ids = {lead["lead_id"] for lead in visible}
    if session_state.get("selected_lead_id") in visible_ids:
        return
    if visible:
        session_state["selected_lead_id"] = visible[0]["lead_id"]
    else:
        session_state.pop("selected_lead_id", None)


def _filter_queue(queue, query, tier, sort_key):
    rows = queue
    if query:
        q = query.strip().lower()
        rows = [r for r in rows if q in str(r.get("company_name", "")).lower()
                or q in str(r.get("contact_name", "")).lower()
                or q in str(r.get("email", "")).lower()]
    wanted = TIER_FILTERS[tier]
    if wanted:
        rows = [r for r in rows if r.get("priority") == wanted]
    return sorted(rows, key=SORTS[sort_key])


def _render_queue(queue: list[dict]) -> list[dict]:
    with st.container(border=True):
        card_title("Prospect priority queue", f"{len(queue)} leads")
        search = st.text_input("Search queue", placeholder="🔍 Search company, contact or email", label_visibility="collapsed")
        f1, f2 = st.columns(2)
        tier = f1.selectbox("Tier", list(TIER_FILTERS), label_visibility="collapsed")
        sort_key = f2.selectbox("Sort", list(SORTS), label_visibility="collapsed")

        unscored = sum(1 for q in queue if q.get("priority") == "unscored")
        if st.button(f"⚡ Batch score {unscored} unscored lead{'s' if unscored != 1 else ''}",
                     width="stretch", disabled=unscored == 0):
            with st.spinner("Scoring leads…"):
                done = batch_score_api()
            if done:
                st.toast(f"Scored {done} lead{'s' if done != 1 else ''}.", icon="✅")
            else:
                st.toast("Batch scoring did not complete. Check the backend logs.", icon="⚠️")
            st.rerun()

        visible = _filter_queue(queue, search, tier, sort_key)
        _sync_selected_lead(st.session_state, visible)
        html("<div style='height:6px'></div>")

        if not visible:
            empty_state("🔎", "No prospects match", "Try clearing the search or changing the tier filter.")
            return visible

        # Fixed-height scroll area keeps long queues from pushing the dossier off-screen.
        with st.container(height=620, border=False):
            for lead in visible:
                lid = lead["lead_id"]
                selected = lid == st.session_state.get("selected_lead_id")
                prio = lead.get("priority", "unscored")
                score = lead.get("score")
                chip = f"<div class='sg-score-chip {PRIORITY_META.get(prio, PRIORITY_META['unscored'])['css']}'>{esc(score if score is not None else '–')}</div>"
                row, btn = st.columns([4, 1.25], vertical_alignment="center")
                with row:
                    html(
                        f"<div class='sg-lead-row {'selected' if selected else ''}'>{chip}"
                        f"<div class='sg-lead-main'><div class='sg-lead-name'>{esc(lead.get('company_name'))}</div>"
                        f"<div class='sg-lead-meta'>{esc(lead.get('contact_name'))} · {esc(lead.get('funding_stage'))}</div></div></div>"
                    )
                with btn:
                    if st.button("Open" if not selected else "Viewing", key=f"sel_btn_{lid}", width="stretch",
                                 type="primary" if selected else "secondary", disabled=selected):
                        st.session_state["selected_lead_id"] = lid
                        st.rerun()
    return visible


def _render_factors(scoring: dict) -> None:
    factors = scoring.get("factors") or scoring.get("scoring_factors") or {}
    shown = False
    for f in factors.values():
        if not isinstance(f, dict):
            continue
        shown = True
        explanations = f.get("explanations") or []
        progress_bar(f.get("label", "Factor"), f.get("score", 0), max(1, f.get("max", 100)),
                     explanations[0] if explanations else "")
    if not shown:
        st.caption("Factor breakdown is not available for this score.")


def _render_opportunities(opps) -> None:
    if isinstance(opps, list) and opps:
        cols = st.columns(2)
        for i, o in enumerate(opps):
            with cols[i % 2]:
                if not isinstance(o, dict):
                    html(f"<div class='sg-opp'><div class='sg-opp-body'>{esc(o)}</div></div>")
                    continue
                conf = o.get("confidence")
                conf_txt = f"{conf * 100:.0f}% confidence" if isinstance(conf, (int, float)) else "Confidence n/a"
                html(
                    f"<div class='sg-opp'><div class='sg-opp-title'>{'🟢' if o.get('detected') else '⚪'} "
                    f"{esc(o.get('opportunity_name'), 'Business opportunity')}</div>"
                    f"<div class='sg-opp-meta'>{esc(o.get('impact_level'), 'Medium')} impact · {esc(conf_txt)}</div>"
                    f"<div class='sg-opp-body'>{esc(o.get('details'), '')}</div>"
                    f"<div class='sg-opp-meta'>ROI timeline: {esc(o.get('estimated_roi_timeline'), 'Not provided')}</div></div>"
                )
    elif opps:
        st.write(opps)  # legacy plain-text rows
    else:
        st.caption("No specific transformation opportunities were identified.")


def _render_dossier(lead_id: int, avg_prob: float | None) -> None:
    dossier = fetch_lead_dossier_api(lead_id)
    if not dossier:
        with st.container(border=True):
            backend_error("the AI dossier for this lead")
        return

    scoring = dossier.get("scoring") or {}
    insights = dossier.get("insights") or {}
    score = scoring.get("score")
    prio = (scoring.get("priority") or "unscored").lower()
    prob = scoring.get("conversion_probability")

    with st.container(border=True):
        html(
            f"<div style='display:flex;justify-content:space-between;gap:12px;align-items:flex-start;flex-wrap:wrap'>"
            f"<div><h3 style='margin:0;font-size:19px'>{esc(dossier.get('company_name'))}</h3>"
            f"<div class='sg-lead-meta' style='white-space:normal;font-size:13px;margin-top:3px'>"
            f"{esc(dossier.get('contact_name'))} · {esc(dossier.get('contact_title'))} · {esc(dossier.get('location'))}</div></div>"
            f"{pill('Lead #' + str(dossier.get('lead_id', lead_id)), 'teal')}</div>"
        )
        html("<div style='height:8px'></div>")
        g1, g2 = st.columns(2)
        with g1:
            with st.container(border=True):
                html(
                    f"<div class='sg-gauge-wrap'>{score_ring(score)}<div><div class='sg-eyebrow'>Predictive score</div>"
                    f"<div style='margin:4px 0'>{priority_pill(prio)}</div>"
                    f"<div class='sg-kpi-sub'>out of 100</div></div></div>"
                )
        with g2:
            with st.container(border=True):
                delta = ""
                if isinstance(prob, (int, float)) and avg_prob is not None:
                    diff = prob - avg_prob
                    delta = f"{'▲' if diff >= 0 else '▼'} {abs(diff):.1f} pts vs pipeline avg ({avg_prob:.1f}%)"
                html(
                    f"<div class='sg-eyebrow'>Est. conversion probability</div>"
                    f"<div class='sg-kpi-value'>{esc(fmt_pct(prob))}</div>"
                    f"<div class='sg-kpi-sub {'good' if delta.startswith('▲') else 'bad' if delta else ''}'>{esc(delta or 'No benchmark available')}</div>"
                )

        html("<hr/>")
        card_title("Scoring factor breakdown", "Why this score")
        _render_factors(scoring)

        html("<hr/>")
        render_next_best_action(dossier.get("next_best_action"))

        html("<hr/>")
        card_title("Company intelligence & fit")
        html(
            f"<div class='sg-callout'><div class='sg-eyebrow'>Business needs & friction</div>"
            f"{esc(insights.get('business_needs'), 'No business-needs analysis yet — rescore or run Lead Intelligence.')}</div>"
        )
        html("<div style='height:10px'></div><div class='sg-eyebrow'>Value proposition fit</div><div style='height:6px'></div>")
        _render_opportunities(insights.get("transformation_opportunities") or insights.get("opportunities") or [])

        html("<hr/>")
        card_title("Multi-agent analysis")
        if insights.get("strategic_recommendation"):
            html(f"<div class='sg-callout'>💡 <b>Recommendation:</b> {esc(insights['strategic_recommendation'])}</div><div style='height:10px'></div>")
        compat = insights.get("overall_tech_compatibility_score")
        latency = insights.get("execution_latency_seconds")
        info_grid([
            ("High-growth signal", "Active" if insights.get("high_growth_potential") else "Moderate"),
            ("Tech compatibility", f"{compat}%" if compat is not None else "N/A"),
            ("Analysis latency", f"{latency:.2f}s" if isinstance(latency, (int, float)) else "N/A"),
            ("Funding stage", dossier.get("funding_stage")),
        ])
        if insights.get("industry_analysis"):
            html(f"<div style='height:10px'></div><div class='sg-eyebrow'>Company profile</div><div style='font-size:13.5px;line-height:1.55'>{esc(insights['industry_analysis'])}</div>")
        if insights.get("growth_indicators"):
            html("<div style='height:10px'></div><div class='sg-eyebrow'>Growth signals</div><div style='height:4px'></div>")
            chips([f"📈 {g}" for g in insights["growth_indicators"]], "teal")

        with st.expander("Tech alignment & buying committee"):
            for category, techs in (insights.get("tech_stack_components") or {}).items():
                st.markdown(f"- **{category}:** {', '.join(map(str, techs))}")
            for m in insights.get("tech_alignment_metrics") or insights.get("tech_alignment") or []:
                if isinstance(m, dict):
                    st.markdown(f"- **{m.get('category', 'General')}:** {m.get('compatibility_score', 0)}% — {m.get('alignment_notes', '')}")
            for p in insights.get("decision_makers") or []:
                if isinstance(p, dict):
                    st.markdown(f"- 👤 **{p.get('name', 'Unknown')}** ({p.get('role_title', 'Decision maker')}): {p.get('recommended_pitch_angle', '')}")

        html("<div style='height:6px'></div>")
        a1, a2 = st.columns([1.2, 2.2])
        with a1:
            if st.button("🔄 Rescore lead", width="stretch", key=f"rescore_{lead_id}"):
                with st.spinner("Rescoring…"):
                    ok, msg = score_lead_api(lead_id)
                if ok:
                    st.toast("Score and insights refreshed.", icon="✅")
                    st.rerun()
                st.error(f"Rescoring failed: {msg}")
        with a2:
            if st.button("✉️ Generate personalized outreach →", type="primary", width="stretch", key=f"to_outreach_{lead_id}"):
                st.session_state["outreach_target_lead_id"] = lead_id
                st.session_state["pending_nav_tab"] = "✉️ Cold Outreach"
                st.rerun()


def render_scoring_hub() -> None:
    page_header("Predictive Lead Scoring & Intelligence",
                "Evaluate prospect viability by firmographic fit, tech alignment and growth velocity.")

    queue = fetch_scoring_queue_api()
    if queue is None:
        with st.container(border=True):
            backend_error("the scoring queue")
        return
    if not queue:
        with st.container(border=True):
            empty_state("🗂️", "No leads to score yet", "Add a lead in Leads & Ingestion to start the scoring workflow.")
            if st.button("Go to Leads & Ingestion", width="stretch"):
                st.session_state["pending_nav_tab"] = "📊 Leads & Ingestion"
                st.rerun()
        return

    probs = [q["conversion_probability"] for q in queue if isinstance(q.get("conversion_probability"), (int, float))]
    avg_prob = sum(probs) / len(probs) if probs else None

    left, right = st.columns([1.5, 2.5])
    with left:
        visible = _render_queue(queue)
    with right:
        selected = st.session_state.get("selected_lead_id")
        if selected is None:
            with st.container(border=True):
                empty_state("👈", "Select a lead", "Pick a prospect from the queue to open its AI dossier.")
        else:
            _render_dossier(selected, avg_prob)
