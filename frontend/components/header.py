import streamlit as st

try:
    from frontend.utils.api_client import check_backend_health, fetch_pipeline_stats
except ModuleNotFoundError:
    from utils.api_client import check_backend_health, fetch_pipeline_stats


def render_header(
    session_additions: int = 0,
    total_leads: int | None = None,
    pending_scores: int | None = None,
):
    """Renders the executive branding bar, theme toggle, and live pipeline metrics."""
    current_mode = st.session_state.get("theme_mode", "dark")
    is_online = check_backend_health()

    # 1. Top Executive Navigation Bar
    nav_col, action_col = st.columns([8.2, 1.8], vertical_alignment="center")

    with nav_col:
        status_pill = (
            "<span class='sg-pill sg-pill-teal' style='font-size: 11px;'>🟢 Backend Online</span>"
            if is_online
            else "<span class='sg-pill' style='background: #FEF3C7; color: #B45309; font-size: 11px;'>🟡 Backend Offline</span>"
        )
        st.markdown(
            f"""
            <div class="sg-nav-container">
                <div class="sg-nav-brand">
                    <span style="font-size: 16px;">⚡</span> SalesGenie AI
                    <div style="margin-left: 8px;">{status_pill}</div>
                </div>
                <div style="font-size: 13px; display: flex; align-items: center; gap: 8px;">
                    <span>👤</span> <span style="font-weight: 600;">Alex Rep</span>
                    <span style="opacity: 0.6; font-size: 12px;">(Enterprise Sales)</span>
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

    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)

    # 2. Section Heading
    st.markdown(
        """
        <div style="margin-bottom: 16px;">
            <h2 class="sg-title" style="font-size: 22px;">Sales Intelligence & Lead Forecasting Platform</h2>
            <p class="sg-subtitle">
                Automated multi-vector prospect ingestion, predictive qualification scoring, and personalized outreach synthesis.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 3. Pull Live Backend Stats
    stats = fetch_pipeline_stats()
    display_total = total_leads if total_leads is not None else stats.get("total_leads", 0)
    display_pending = pending_scores if pending_scores is not None else stats.get("pending_ai_scoring", 0)
    ingestion_health = stats.get("ingestion_health", 98.4)

    # 4. Metric Overview Cards
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        with st.container(border=True):
            st.caption("TOTAL PIPELINE LEADS")
            st.markdown(f"<h3 style='margin:0; font-size: 22px; font-weight: 700;'>{display_total:,}</h3>", unsafe_allow_html=True)
            st.markdown("<span class='sg-metric-accent'>● Active in PostgreSQL</span>", unsafe_allow_html=True)

    with c2:
        with st.container(border=True):
            st.caption("SESSION ADDITIONS")
            st.markdown(f"<h3 style='margin:0; font-size: 22px; font-weight: 700;'>+{session_additions}</h3>", unsafe_allow_html=True)
            st.markdown("<span class='sg-metric-accent'>Current working batch</span>", unsafe_allow_html=True)

    with c3:
        with st.container(border=True):
            st.caption("INGESTION HEALTH")
            st.markdown(f"<h3 style='margin:0; font-size: 22px; font-weight: 700;'>{ingestion_health:.1f}%</h3>", unsafe_allow_html=True)
            st.markdown("<span class='sg-metric-accent'>SRS Target: ≥ 95%</span>", unsafe_allow_html=True)

    with c4:
        with st.container(border=True):
            st.caption("PENDING AI SCORING")
            st.markdown(f"<h3 style='margin:0; font-size: 22px; font-weight: 700;'>{display_pending}</h3>", unsafe_allow_html=True)
            st.markdown("<span class='sg-metric-accent'>Queued for Milestone 2</span>", unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 8px;'></div>", unsafe_allow_html=True)