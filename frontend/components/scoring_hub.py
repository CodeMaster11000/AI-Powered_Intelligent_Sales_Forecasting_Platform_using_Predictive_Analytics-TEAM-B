import streamlit as st

try:
    from frontend.utils.api_client import (
        batch_score_api,
        fetch_lead_dossier_api,
        fetch_scoring_queue_api,
        score_lead_api,
    )
except ModuleNotFoundError:
    from utils.api_client import (
        batch_score_api,
        fetch_lead_dossier_api,
        fetch_scoring_queue_api,
        score_lead_api,
    )


def render_scoring_hub():
    """Renders the Master-Detail Lead Scoring & Intelligence Hub (Wireframe A)."""
    
    st.markdown(
        """
        <div style="margin-bottom: 16px;">
            <h3 class="sg-title" style="font-size: 20px;">Predictive Lead Scoring & Intelligence</h3>
            <p class="sg-subtitle">Evaluate prospect viability via firmographic fit, tech alignment, and growth velocity.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 1. Fetch the authoritative queue from the backend
    queue = fetch_scoring_queue_api()

    if not queue:
        with st.container(border=True):
            st.error("Unable to load the scoring queue from the backend.")
        return

    # 2. Master-Detail Split: Left Queue (1.6) | Right Dossier (2.4)
    left_col, right_col = st.columns([1.6, 2.4])

    # --- LEFT PANE: LEAD QUEUE ---
    with left_col:
        with st.container(border=True):
            st.markdown("<h4 style='margin:0 0 8px 0; font-size: 15px; font-weight: 600;'>Prospect Priority Queue</h4>", unsafe_allow_html=True)
            
            search_query = st.text_input("Search Queue", placeholder="🔍 Search prospect...", label_visibility="collapsed")
            
            f_col1, f_col2 = st.columns([1.2, 1.3])
            with f_col1:
                tier_filter = st.selectbox(
                    "Priority Tier",
                    ["All Tiers", "Hot (≥ 75)", "Warm (40-74)", "Cold (< 40)", "Unscored"],
                    label_visibility="collapsed",
                )
            with f_col2:
                unscored_count = sum(1 for q in queue if q.get("priority") == "unscored")
                if st.button(f"⚡ Batch Score ({unscored_count})", use_container_width=True, disabled=(unscored_count == 0)):
                    done = batch_score_api()
                    st.toast(f"Scored {done} leads successfully!", icon="✅")
                    st.rerun()

            # Filter logic
            filtered_queue = queue
            if search_query:
                q_low = search_query.strip().lower()
                filtered_queue = [
                    q for q in filtered_queue
                    if q_low in str(q.get("company_name", "")).lower()
                    or q_low in str(q.get("contact_name", "")).lower()
                ]

            if tier_filter == "Hot (≥ 75)":
                filtered_queue = [q for q in filtered_queue if q.get("priority") == "hot"]
            elif tier_filter == "Warm (40-74)":
                filtered_queue = [q for q in filtered_queue if q.get("priority") == "warm"]
            elif tier_filter == "Cold (< 40)":
                filtered_queue = [q for q in filtered_queue if q.get("priority") == "cold"]
            elif tier_filter == "Unscored":
                filtered_queue = [q for q in filtered_queue if q.get("priority") == "unscored"]

            st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)

            # Keep selection valid
            if "selected_lead_id" not in st.session_state and filtered_queue:
                st.session_state["selected_lead_id"] = filtered_queue[0]["lead_id"]

            if not filtered_queue:
                st.caption("No prospects match current filter.")
            else:
                for lead in filtered_queue:
                    lid = lead["lead_id"]
                    is_selected = (lid == st.session_state.get("selected_lead_id"))
                    score_val = lead.get("score")
                    priority = lead.get("priority", "unscored")

                    # Priority Pill formatting
                    if priority == "hot":
                        pill_html = f"<span class='sg-pill sg-pill-teal'>🔥 {score_val} HOT</span>"
                    elif priority == "warm":
                        pill_html = f"<span class='sg-pill' style='background:#FEF3C7; color:#B45309;'>🌤️ {score_val} WARM</span>"
                    elif priority == "cold":
                        pill_html = f"<span class='sg-pill sg-pill-slate'>❄️ {score_val} COLD</span>"
                    else:
                        pill_html = "<span class='sg-pill sg-pill-slate'>⚪ UNSCORED</span>"

                    # Compact Single-Row Layout
                    r_card, r_btn = st.columns([3.6, 1.2], vertical_alignment="center")
                    with r_card:
                        selected_style = "border-left: 3px solid #0F766E; padding-left: 8px;" if is_selected else "padding-left: 8px;"
                        st.markdown(
                            f"""
                            <div style="{selected_style}">
                                <div style="font-weight: 600; font-size: 13px; line-height: 1.2;">{lead['company_name']} {pill_html}</div>
                                <div style="font-size: 11px; opacity: 0.7; margin-top: 2px;">{lead['contact_name']} • {lead.get('funding_stage', 'Growth')}</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                    with r_btn:
                        btn_label = "Active" if is_selected else "Inspect"
                        if st.button(btn_label, key=f"sel_btn_{lid}", use_container_width=True, type="primary" if is_selected else "secondary"):
                            st.session_state["selected_lead_id"] = lid
                            st.rerun()

                    st.markdown("<hr style='margin: 6px 0; border: none; border-top: 1px solid rgba(125,125,125,0.15);'/>", unsafe_allow_html=True)

    # --- RIGHT PANE: THE AI LEAD DOSSIER ---
    with right_col:
        sel_id = st.session_state.get("selected_lead_id")
        dossier = fetch_lead_dossier_api(sel_id) if sel_id else None

        if not dossier and sel_id:
            st.error("Unable to load the AI dossier for the selected lead.")
            return

        if not dossier:
            with st.container(border=True):
                st.caption("Select a lead from the queue on the left to inspect its AI Dossier.")
            return

        scoring = dossier.get("scoring", {})
        insights = dossier.get("insights", {})

        with st.container(border=True):
            # Header info
            st.markdown(
                f"""
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
                    <div>
                        <h3 style="margin: 0; font-size: 18px; font-weight: 700;">{dossier['company_name']}</h3>
                        <p style="margin: 2px 0 0 0; font-size: 13px; opacity: 0.8;">{dossier['contact_name']} • {dossier['contact_title']} • {dossier['location']}</p>
                    </div>
                    <span class="sg-pill sg-pill-teal">Lead ID #{dossier['lead_id']}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Score & Win Probability Gauges
            kpi1, kpi2 = st.columns(2)
            with kpi1:
                with st.container(border=True):
                    st.caption("LEAD PREDICTIVE SCORE")
                    st.markdown(f"<h2 style='margin:0; font-weight: 700; color: #0F766E;'>{scoring.get('score', 0)} / 100</h2>", unsafe_allow_html=True)
                    st.markdown(f"<span class='sg-pill sg-pill-teal'>Priority: {scoring.get('priority', 'warm').upper()}</span>", unsafe_allow_html=True)

            with kpi2:
                with st.container(border=True):
                    st.caption("EST. CONVERSION PROBABILITY")
                    st.markdown(f"<h2 style='margin:0; font-weight: 700;'>{scoring.get('conversion_probability', 0)}%</h2>", unsafe_allow_html=True)
                    st.caption("Benchmark Avg: 22.4%")

            st.markdown("<hr style='margin: 14px 0;'/>", unsafe_allow_html=True)

            # Factor Breakdown (Glass Box AI)
            st.markdown("<h5 style='margin: 0 0 8px 0; font-size: 14px; font-weight: 600;'>Scoring Factor Breakdown</h5>", unsafe_allow_html=True)
            factors = scoring.get("factors", {})
            for _, f_data in factors.items():
                max_pts = max(1, f_data.get("max", 100))
                earned = f_data.get("score", 0)
                ratio = min(1.0, max(0.0, earned / max_pts))

                c_lbl, c_bar = st.columns([2, 3])
                c_lbl.markdown(f"<div style='font-size: 12px;'>{f_data.get('label', 'Factor')}</div>", unsafe_allow_html=True)
                with c_bar:
                    st.progress(ratio, text=f"{earned} / {max_pts} pts")

            st.markdown("<hr style='margin: 14px 0;'/>", unsafe_allow_html=True)

            # AI Company Intelligence
            st.markdown("<h5 style='margin: 0 0 8px 0; font-size: 14px; font-weight: 600;'>AI Company Intelligence & Fit</h5>", unsafe_allow_html=True)
            
            needs = insights.get("business_needs", "Assessing infrastructure scaling needs.")
            opps = insights.get("opportunities", "Predictive qualification match identified.")

            st.markdown(
                f"""
                <div style="background: rgba(125,125,125,0.06); padding: 10px 14px; border-radius: 6px; margin-bottom: 8px;">
                    <div style="font-size: 11px; font-weight: 600; color: #0F766E; text-transform: uppercase;">Business Needs & Friction</div>
                    <div style="font-size: 13px; margin-top: 2px;">{needs}</div>
                </div>
                <div style="background: rgba(125,125,125,0.06); padding: 10px 14px; border-radius: 6px; margin-bottom: 14px;">
                    <div style="font-size: 11px; font-weight: 600; color: #0F766E; text-transform: uppercase;">Value Proposition Fit</div>
                    <div style="font-size: 13px; margin-top: 2px;">{opps}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Bottom Action Bar with Tab-Switch Synchronization
            act1, act2 = st.columns([1.5, 2.5])
            with act1:
                if st.button("🔄 Rescore Lead", use_container_width=True):
                    score_lead_api(sel_id)
                    st.toast("Recalculated score and insights!", icon="✅")
                    st.rerun()

            # Fixed:
            with act2:
                if st.button("✉️ Generate Personalized Outreach ➡️", type="primary", use_container_width=True):
                    st.session_state["outreach_target_lead_id"] = sel_id
                    st.session_state["pending_nav_tab"] = "✉️ Cold Outreach"
                    st.rerun()