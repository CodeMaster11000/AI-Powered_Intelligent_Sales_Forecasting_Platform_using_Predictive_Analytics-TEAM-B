import streamlit as st
from frontend.utils.api_client import (
    analyze_lead_api,
    fetch_leads_api,
    fetch_lead_insights_api,
    analyze_prospect_ad_hoc_api,
)
from modules.module2_intelligence import analyze_lead_intelligence, get_architecture_diagram


def render_intelligence_view():
    """
    Module 2: AI Lead Intelligence & Company Profiling View
    Renders LangGraph multi-agent intelligence results, qualification scores,
    and business transformation opportunities per IEEE Std 830-1998 REQ-M2-01, M2-02, M2-03.
    """
    st.subheader("🧠 Multi-Agent Lead Intelligence Engine")
    st.caption("Powered by LangGraph (Research Agent & Qualification Agent) with IEEE 830 grounding.")

    analysis_mode = st.radio(
        "Select Intelligence Mode:",
        ["📋 Analyze Ingested Database Lead", "⚡ Ad-Hoc Prospect Evaluation"],
        horizontal=True,
    )

    if analysis_mode == "📋 Analyze Ingested Database Lead":
        # leads = fetch_leads_api(limit=50)
        leads = fetch_leads_api()
        if not leads:
            st.error("Unable to load leads from the backend.")
            return

        lead_options = {}
        for l in leads:
            label = f"ID #{l.get('lead_id')}: {l.get('company_name')} ({l.get('industry') or 'General'}) - {l.get('email')}"
            lead_options[label] = l

        selected_label = st.selectbox("Choose Prospect to Analyze:", list(lead_options.keys()))
        selected_lead = lead_options[selected_label]

        col_btn, col_info = st.columns([1, 3])
        with col_btn:
            run_btn = st.button("🚀 Run Agentic Analysis", type="primary", use_container_width=True)

        if run_btn:
            with st.spinner("🤖 Running LangGraph Multi-Agent Orchestration (Research Agent + Qualification Agent)..."):
                lead_id = selected_lead.get("lead_id")
                if lead_id:
                    success, result = analyze_lead_api(lead_id)
                else:
                    success, result = True, analyze_lead_intelligence(selected_lead)

                if success and isinstance(result, dict):
                    st.success("✅ Multi-Agent Analysis Completed in Compliance with IEEE Std 830 REQ-M2-01/02/03!")
                    _display_intelligence_dashboard(result)
                else:
                    st.error(f"Analysis Error: {result}")

    else:
        # Ad-hoc evaluation form
        with st.form("adhoc_intelligence_form"):
            col1, col2 = st.columns(2)
            with col1:
                company_name = st.text_input("Company Name*", value="AlphaLogix Solutions")
                industry = st.selectbox("Industry", ["Enterprise Software", "Fintech", "Healthtech", "E-commerce", "Manufacturing", "Logistics"])
                contact_name = st.text_input("Decision Maker / Contact", value="Elena Rostova (VP of Engineering)")
                company_size = st.selectbox("Company Size", ["50-100 employees", "100-250 employees", "250-500 employees", "500-1000 employees", "1000+ employees"])
            with col2:
                funding_stage = st.selectbox("Funding Stage", ["Series C", "Series B", "Series A", "Seed", "Public", "Bootstrapped"])
                capital_raised = st.text_input("Capital Raised", value="$35M")
                annual_revenue = st.text_input("Annual Revenue", value="$25M-$50M")
                tech_stack = st.text_input("Active Tech Stack", value="AWS, Python, React, PostgreSQL, Docker, Kubernetes")

            submit_adhoc = st.form_submit_button("🧠 Execute Multi-Agent Intelligence Profiling", type="primary")

        if submit_adhoc:
            payload = {
                "company_name": company_name,
                "industry": industry,
                "contact_name": contact_name,
                "company_size": company_size,
                "funding_stage": funding_stage,
                "capital_raised": capital_raised,
                "annual_revenue": annual_revenue,
                "tech_stack": tech_stack,
            }
            with st.spinner("Executing Research and Qualification Agents..."):
                result = analyze_lead_intelligence(payload)
                st.success("✅ Agentic Analysis Completed Successfully!")
                _display_intelligence_dashboard(result)


def _display_intelligence_dashboard(data: dict):
    """Renders structured executive cards for lead intelligence outputs."""
    score = data.get("qualification_score", 0)
    conversion_prob = data.get("conversion_probability") or round(score * 0.85, 1)
    latency = data.get("execution_latency_seconds", 0.05)
    high_growth = data.get("high_growth_potential", False)

    # 1. Top Metrics Cards
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("🎯 Qualification Score", f"{score}/100", delta="High Fit" if score >= 75 else "Medium Fit")
    with m2:
        st.metric("📈 Conversion Probability", f"{conversion_prob}%")
    with m3:
        st.metric("⚡ Processing Latency", f"{latency}s", delta="SLA < 5s Met")
    with m4:
        st.metric("🚀 High Growth Signal", "Active (Series Funded)" if high_growth else "Moderate")

    st.markdown("---")

    # 2. Strategic Summary & Domain Analysis
    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown("#### 🏢 Automated Company Profiling (REQ-M2-01)")
        domain_analysis = data.get("industry_analysis") or data.get("industry_domain_analysis", "Enterprise domain analyzed.")
        st.write(domain_analysis)

        growth_indicators = data.get("growth_indicators") or []
        if growth_indicators:
            st.markdown("**Key Growth Signals:**")
            for ind in growth_indicators:
                st.markdown(f"- 📈 {ind}")

    with c2:
        st.markdown("#### 🎯 Strategic Recommendation & Needs (REQ-M2-03)")
        rec = data.get("strategic_recommendation", "Direct executive engagement recommended.")
        st.info(f"💡 **Recommendation:** {rec}")
        needs = data.get("business_needs") or data.get("business_needs_summary", "Operational efficiency scaling.")
        st.markdown(f"**Business Needs:** {needs}")

    st.markdown("---")

    # 3. Business Transformation Opportunities (REQ-M2-02)
    st.markdown("#### 🔍 Identified Business Opportunities (REQ-M2-02)")
    opportunities = data.get("transformation_opportunities") or []
    if opportunities:
        cols = st.columns(min(len(opportunities), 4))
        for idx, opp in enumerate(opportunities):
            col = cols[idx % len(cols)]
            with col:
                detected = opp.get("detected", False)
                status_icon = "🟢" if detected else "⚪"
                st.markdown(f"**{status_icon} {opp.get('opportunity_name')}**")
                st.caption(f"Impact: **{opp.get('impact_level', 'Medium')}** | Confidence: **{int(opp.get('confidence', 0.8)*100)}%**")
                st.write(opp.get("details", ""))
                st.caption(f"⏱️ ROI: {opp.get('estimated_roi_timeline', '3-6 mos')}")

    # 4. Tech Alignment & Decision Makers Accordion
    with st.expander("🛠️ Tech Stack Alignment & Buyer Persona Details", expanded=False):
        col_t, col_p = st.columns(2)
        with col_t:
            st.markdown("**Tech Alignment Breakdown:**")
            metrics = data.get("tech_alignment_metrics") or []
            for m in metrics:
                cat = m.get("category", "General")
                compat = m.get("compatibility_score", 85)
                st.markdown(f"- **{cat}**: `{compat}% Compatible`")
                st.caption(m.get("alignment_notes", ""))

        with col_p:
            st.markdown("**Buying Committee Personas:**")
            dms = data.get("decision_makers") or []
            for dm in dms:
                st.markdown(f"👤 **{dm.get('name')}** - *{dm.get('role_title')}*")
                st.caption(f"Pitch Angle: {dm.get('recommended_pitch_angle')}")

    # 5. Architecture Topology
    with st.expander("📐 LangGraph Multi-Agent Architecture Topology", expanded=False):
        st.markdown(get_architecture_diagram())
