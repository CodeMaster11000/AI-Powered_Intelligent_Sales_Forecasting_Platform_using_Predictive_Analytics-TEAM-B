import streamlit as st

# 1. Page Configuration (Must be first Streamlit command)
st.set_page_config(
    page_title="SalesGenie AI | Sales Forecasting & Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 2. Session State Initialization
if "theme_mode" not in st.session_state:
    st.session_state["theme_mode"] = "dark"
if "session_additions" not in st.session_state:
    st.session_state["session_additions"] = 0
if "recent_ingested_leads" not in st.session_state:
    st.session_state["recent_ingested_leads"] = []
if "nav_radio" not in st.session_state:
    st.session_state["nav_radio"] = "📊 Leads & Ingestion"

# 3. Dual-Path Resilient Imports
try:
    from frontend.components.csv_uploader import render_csv_uploader
    from frontend.components.header import render_header
    from frontend.components.manual_form import render_manual_form
    from frontend.components.outreach_studio import render_outreach_studio
    from frontend.components.scoring_hub import render_scoring_hub
    from frontend.components.staging_feed import render_staging_feed
    from frontend.styles.themes import apply_theme
except ModuleNotFoundError:
    from components.csv_uploader import render_csv_uploader
    from components.header import render_header
    from components.manual_form import render_manual_form
    from components.outreach_studio import render_outreach_studio
    from components.scoring_hub import render_scoring_hub
    from components.staging_feed import render_staging_feed
    from styles.themes import apply_theme

# 4. Apply Active Theme
apply_theme()

# 5. Top Header & Live KPI Metrics Bar
render_header(session_additions=st.session_state["session_additions"])

# 6. Core Workflow Navigation Tabs (ONLY ONE st.radio HERE)
tabs = ["📊 Leads & Ingestion", "⚡ Predictive Scoring", "✉️ Cold Outreach"]

# Consume any pending programmatic navigation BEFORE the widget is created
if "pending_nav_tab" in st.session_state:
    st.session_state["nav_radio"] = st.session_state.pop("pending_nav_tab")

if st.session_state.get("nav_radio") not in tabs:
    st.session_state["nav_radio"] = tabs[0]

active_tab = st.radio(
    "Workflow Navigation",
    options=tabs,
    key="nav_radio",
    horizontal=True,
    label_visibility="collapsed",
)

st.markdown("<div style='margin-top: 8px;'></div>", unsafe_allow_html=True)

# 7. View Routing
if active_tab == "📊 Leads & Ingestion":
    tab_bulk, tab_manual = st.tabs(["📁 Bulk CSV Import", "✏️ Manual Single Entry"])
    with tab_bulk:
        render_csv_uploader()
    with tab_manual:
        render_manual_form()
    render_staging_feed()

elif active_tab == "⚡ Predictive Scoring":
    render_scoring_hub()

elif active_tab == "✉️ Cold Outreach":
    render_outreach_studio()