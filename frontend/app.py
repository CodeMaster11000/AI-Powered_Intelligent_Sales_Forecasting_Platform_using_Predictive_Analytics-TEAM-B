"""SalesGenie AI - Streamlit entry point.

Run from the repository root:   streamlit run frontend/app.py
"""
import os
import sys

# Make the repository root importable (``frontend.*`` and ``modules.*``) however the app is launched.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st  # noqa: E402

st.set_page_config(
    page_title="SalesGenie AI | Sales Forecasting & Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from frontend.components.csv_uploader import render_csv_uploader  # noqa: E402
from frontend.components.dashboard import render_dashboard  # noqa: E402
from frontend.components.header import render_header  # noqa: E402
from frontend.components.intelligence_view import render_intelligence_view  # noqa: E402
from frontend.components.manual_form import render_manual_form  # noqa: E402
from frontend.components.outreach_studio import render_outreach_studio  # noqa: E402
from frontend.components.scoring_hub import render_scoring_hub  # noqa: E402
from frontend.components.staging_feed import render_staging_feed  # noqa: E402
from frontend.styles.themes import apply_theme  # noqa: E402

NAV_DASHBOARD = "📈 Dashboard"
NAV_LEADS = "📊 Leads & Ingestion"
NAV_INTEL = "🧠 AI Lead Intelligence"
NAV_SCORING = "⚡ Predictive Scoring"
NAV_OUTREACH = "✉️ Cold Outreach"
TABS = [NAV_DASHBOARD, NAV_LEADS, NAV_INTEL, NAV_SCORING, NAV_OUTREACH]

# ---- session defaults ------------------------------------------------------
st.session_state.setdefault("theme_mode", "dark")
st.session_state.setdefault("session_additions", 0)
st.session_state.setdefault("recent_ingested_leads", [])
st.session_state.setdefault("nav_radio", NAV_DASHBOARD)

# Programmatic navigation (e.g. "Open Predictive Scoring") must be applied BEFORE the radio is created.
if "pending_nav_tab" in st.session_state:
    st.session_state["nav_radio"] = st.session_state.pop("pending_nav_tab")
if st.session_state["nav_radio"] not in TABS:
    st.session_state["nav_radio"] = NAV_DASHBOARD

apply_theme()
render_header(session_additions=st.session_state["session_additions"])

active = st.radio("Workflow navigation", TABS, key="nav_radio", horizontal=True, label_visibility="collapsed")
st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

if active == NAV_DASHBOARD:
    render_dashboard()
elif active == NAV_LEADS:
    tab_bulk, tab_manual = st.tabs(["📁 Bulk CSV import", "✏️ Manual entry"])
    with tab_bulk:
        render_csv_uploader()
    with tab_manual:
        render_manual_form()
    render_staging_feed()
elif active == NAV_INTEL:
    render_intelligence_view()
elif active == NAV_SCORING:
    render_scoring_hub()
elif active == NAV_OUTREACH:
    render_outreach_studio()
