import streamlit as st

from frontend.components.ui import (
    backend_error, card_title, chips, empty_state, html, info_grid, page_header, progress_bar, score_ring,
)
from frontend.utils.api_client import (
    analyze_lead_api, analyze_prospect_ad_hoc_api, fetch_leads_api,
)
from frontend.utils.helpers import esc, priority_for

try:  # local fallback engine (used only when the API route is unavailable)
    from modules.module2_intelligence import analyze_lead_intelligence, get_architecture_diagram
except ImportError:  # pragma: no cover
    analyze_lead_intelligence = None
    get_architecture_diagram = None

MODES = ["📋 Analyze a stored lead", "⚡ Ad-hoc prospect evaluation"]
INDUSTRIES = ["Enterprise Software", "Fintech", "Healthtech", "E-commerce", "Manufacturing", "Logistics"]
SIZES = ["50-100 employees", "100-250 employees", "250-500 employees", "500-1000 employees", "1000+ employees"]
STAGES = ["Series C", "Series B", "Series A", "Seed", "Public", "Bootstrapped"]


def render_intelligence_view() -> None:
    """Lead intelligence: LangGraph research + qualification agents."""
    page_header("AI Lead Intelligence",
                "Research and qualification agents profile a company, rate fit and suggest the opening angle.")

    mode = st.radio("Mode", MODES, horizontal=True, key="intel_mode", label_visibility="collapsed")
    if mode == MODES[0]:
        _stored_lead_mode()
    else:
        _ad_hoc_mode()


def _stored_lead_mode() -> None:
    leads = fetch_leads_api()
    if leads is None:
        with st.container(border=True):
            backend_error("leads")
        return
    if not leads:
        with st.container(border=True):
            empty_state("🗂️", "No stored leads", "Add a lead first, or try the ad-hoc evaluation.")
        return

    options = {f"#{l.get('lead_id')} · {l.get('company_name')} ({l.get('industry') or 'General'}) — {l.get('email')}": l for l in leads}
    with st.container(border=True):
        label = st.selectbox("Prospect to analyze", list(options))
        lead = options[label]
        run = st.button("🚀 Run agentic analysis", type="primary", width="stretch", key="run_stored_analysis")

    result_key = "intel_result_stored"
    if run:
        with st.spinner("Research and Qualification agents are working (this can take up to a minute)…"):
            ok, result = analyze_lead_api(lead["lead_id"])
        if ok and isinstance(result, dict):
            st.session_state[result_key] = {"lead_id": lead["lead_id"], "data": result}
        else:
            st.session_state.pop(result_key, None)
            st.error(f"Analysis failed: {result}")
    cached = st.session_state.get(result_key)
    if cached and cached["lead_id"] == lead["lead_id"]:
        _display_results(cached["data"])


def _ad_hoc_mode() -> None:
    with st.form("adhoc_intelligence_form"):
        c1, c2 = st.columns(2)
        with c1:
            company = st.text_input("Company name *")
            industry = st.selectbox("Industry", INDUSTRIES)
            contact = st.text_input("Decision maker / contact", placeholder="e.g. Elena Rostova, VP Engineering")
            size = st.selectbox("Company size", SIZES)
        with c2:
            stage = st.selectbox("Funding stage", STAGES)
            raised = st.text_input("Capital raised", placeholder="e.g. $35M")
            revenue = st.text_input("Annual revenue", placeholder="e.g. $25M-$50M")
            stack = st.text_input("Active tech stack", placeholder="AWS, Python, React, PostgreSQL")
        submit = st.form_submit_button("🧠 Run intelligence profiling", width="stretch")

    if submit:
        if not company.strip():
            st.error("Company name is required.")
            return
        payload = {"company_name": company.strip(), "industry": industry, "contact_name": contact.strip(),
                   "company_size": size, "funding_stage": stage, "capital_raised": raised.strip(),
                   "annual_revenue": revenue.strip(), "tech_stack": stack.strip()}
        with st.spinner("Executing Research and Qualification agents…"):
            ok, result = analyze_prospect_ad_hoc_api(payload)
            if not ok and analyze_lead_intelligence:  # API route unavailable -> local engine
                try:
                    ok, result = True, analyze_lead_intelligence(payload)
                except Exception as exc:  # noqa: BLE001
                    ok, result = False, f"Local engine error: {exc}"
        if ok and isinstance(result, dict):
            st.session_state["intel_result_adhoc"] = result
        else:
            st.session_state.pop("intel_result_adhoc", None)
            st.error(f"Analysis failed: {result}")
    if st.session_state.get("intel_result_adhoc"):
        _display_results(st.session_state["intel_result_adhoc"])


def _display_results(data: dict) -> None:
    score = data.get("qualification_score", 0) or 0
    prob = data.get("conversion_probability")
    prob = prob if prob is not None else round(score * 0.85, 1)
    latency = data.get("execution_latency_seconds")

    html("<div style='height:8px'></div>")
    c1, c2 = st.columns([1, 3])
    with c1:
        with st.container(border=True):
            html(f"<div style='display:flex;justify-content:center'>{score_ring(score, 120)}</div>"
                 f"<div class='sg-eyebrow' style='text-align:center'>Qualification score</div>")
    with c2:
        with st.container(border=True):
            info_grid([
                ("Fit", "High fit" if score >= 75 else "Medium fit" if priority_for(score) == "warm" else "Low fit"),
                ("Conversion probability", f"{prob}%"),
                ("Processing time", f"{latency}s" if latency is not None else "n/a"),
                ("Growth signal", "Active (funded)" if data.get("high_growth_potential") else "Moderate"),
            ])
            html("<div style='height:10px'></div>")
            html(f"<div class='sg-callout'>💡 <b>Recommendation:</b> "
                 f"{esc(data.get('strategic_recommendation'), 'Direct executive engagement recommended.')}</div>")

    left, right = st.columns(2)
    with left:
        with st.container(border=True):
            card_title("Company profile", "REQ-M2-01")
            html(f"<div style='font-size:13.5px;line-height:1.6'>{esc(data.get('industry_analysis') or data.get('industry_domain_analysis'), 'Enterprise domain analyzed.')}</div>")
            if data.get("growth_indicators"):
                html("<div style='height:10px'></div><div class='sg-eyebrow'>Key growth signals</div><div style='height:4px'></div>")
                chips([f"📈 {g}" for g in data["growth_indicators"]], "teal")
    with right:
        with st.container(border=True):
            card_title("Business needs", "REQ-M2-03")
            html(f"<div style='font-size:13.5px;line-height:1.6'>{esc(data.get('business_needs') or data.get('business_needs_summary'), 'Operational efficiency scaling.')}</div>")

    with st.container(border=True):
        card_title("Business transformation opportunities", "REQ-M2-02")
        opps = data.get("transformation_opportunities") or []
        if not opps:
            st.caption("No opportunities identified.")
        cols = st.columns(min(len(opps), 3) or 1)
        for i, o in enumerate(opps):
            conf = o.get("confidence")
            conf_txt = f"{conf * 100:.0f}%" if isinstance(conf, (int, float)) else "n/a"
            with cols[i % len(cols)]:
                html(
                    f"<div class='sg-opp'><div class='sg-opp-title'>{'🟢' if o.get('detected') else '⚪'} {esc(o.get('opportunity_name'))}</div>"
                    f"<div class='sg-opp-meta'>{esc(o.get('impact_level'), 'Medium')} impact · {esc(conf_txt)} confidence</div>"
                    f"<div class='sg-opp-body'>{esc(o.get('details'), '')}</div>"
                    f"<div class='sg-opp-meta'>ROI: {esc(o.get('estimated_roi_timeline'), '3–6 months')}</div></div>"
                )

    with st.expander("Tech alignment & buying committee"):
        t, p = st.columns(2)
        with t:
            st.markdown("**Tech alignment**")
            for m in data.get("tech_alignment_metrics") or []:
                progress_bar(m.get("category", "General"), m.get("compatibility_score", 0), 100, m.get("alignment_notes", ""))
        with p:
            st.markdown("**Buying committee**")
            for dm in data.get("decision_makers") or []:
                st.markdown(f"👤 **{dm.get('name')}** — *{dm.get('role_title')}*")
                st.caption(f"Pitch angle: {dm.get('recommended_pitch_angle')}")

    if get_architecture_diagram:
        with st.expander("LangGraph agent architecture"):
            st.markdown(get_architecture_diagram())
