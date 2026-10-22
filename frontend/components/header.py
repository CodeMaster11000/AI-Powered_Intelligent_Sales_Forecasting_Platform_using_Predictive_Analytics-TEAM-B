import streamlit as st
from frontend.utils.api_client import check_backend_health, fetch_pipeline_stats


def render_header(session_additions: int = 0):
    current_mode = st.session_state.get("theme_mode", "dark")
    is_online = check_backend_health()

    # Top Navigation Row
    nav_col, action_col = st.columns([8.2, 1.8], vertical_alignment="center")

    with nav_col:
        status_dot = "🟢" if is_online else "🟡 Offline"
        st.markdown(
            f"""
            <div class="sg-nav-container">
                <div class="sg-nav-brand">
                    <span style="font-size: 16px;">⚡</span> SalesGenie AI
                    <span style="font-size: 11px; font-weight: 500; opacity: 0.8; margin-left: 6px;">{status_dot}</span>
                </div>
                <div class="sg-nav-links">
                    <span class="sg-nav-link sg-nav-active">📊 Leads & Ingestion</span>
                    <span class="sg-nav-link">⚡ Predictive Scoring</span>
                    <span class="sg-nav-link">✉️ Cold Outreach</span>
                    <span class="sg-nav-link">📈 Pipeline Insights</span>
                </div>
                <div style="font-size: 13px;">
                    👤 <span style="font-weight: 600;">Alex Rep</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with action_col:
        toggle_label = "☀️ Light Mode" if current_mode == "dark" else "🌙 Dark Mode"
        if st.button(toggle_label, use_container_width=True, type="secondary"):
            st.session_state["theme_mode"] = "light" if current_mode == "dark" else "dark"
            st.rerun()

    st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)

    # Title & Subtitle
    st.markdown(
        """
        <div style="margin-bottom: 18px;">
            <h2 class="sg-title">Lead Ingestion & Pipeline Staging</h2>
            <p class="sg-subtitle">
                Ingest prospect records across data vectors. Validated records are queued for automated predictive scoring and qualification.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Pull live stats from backend
    stats = fetch_pipeline_stats()
    total_leads = stats.get("total_leads", 0)
    pending_scores = stats.get("pending_ai_scoring", 0)

    # 4 Metric Cards
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        with st.container(border=True):
            st.caption("TOTAL PIPELINE LEADS")
            st.markdown(f"<h3 style='margin:0; font-size: 24px; font-weight: 700;'>{total_leads:,}</h3>", unsafe_allow_html=True)
            st.markdown("<span class='sg-metric-accent'>● Stored in PostgreSQL</span>", unsafe_allow_html=True)

    with c2:
        with st.container(border=True):
            st.caption("SESSION ADDITIONS")
            st.markdown(f"<h3 style='margin:0; font-size: 24px; font-weight: 700;'>+{session_additions}</h3>", unsafe_allow_html=True)
            st.markdown("<span class='sg-metric-accent'>Current intake batch</span>", unsafe_allow_html=True)

    with c3:
        with st.container(border=True):
            st.caption("INGESTION HEALTH")
            st.markdown("<h3 style='margin:0; font-size: 24px; font-weight: 700;'>98.4%</h3>", unsafe_allow_html=True)
            st.markdown("<span class='sg-metric-accent'>SRS Target: ≥ 95%</span>", unsafe_allow_html=True)

    with c4:
        with st.container(border=True):
            st.caption("PENDING AI SCORING")
            st.markdown(f"<h3 style='margin:0; font-size: 24px; font-weight: 700;'>{pending_scores}</h3>", unsafe_allow_html=True)
            st.markdown("<span class='sg-metric-accent'>Step 2 Queue</span>", unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)