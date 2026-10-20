import streamlit as st

# 1. Page Configuration must be first
st.set_page_config(
    page_title="Leads Ingestion | SalesGenie AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 2. Initialize Session State
if "theme_mode" not in st.session_state:
    st.session_state["theme_mode"] = "dark"
if "recent_ingested_leads" not in st.session_state:
    st.session_state["recent_ingested_leads"] = []
if "session_additions" not in st.session_state:
    st.session_state["session_additions"] = 0

from frontend.components.csv_uploader import render_csv_uploader
from frontend.components.header import render_header
from frontend.components.manual_form import render_manual_form
from frontend.components.staging_feed import render_staging_feed
from frontend.styles.themes import apply_theme

# 3. Apply Active Theme
apply_theme()

# 4. Render Header (with theme switcher)
render_header(
    total_leads=1284,
    session_additions=st.session_state["session_additions"],
    pending_scores=18,
)

# 5. Work Area Tabs
tab_bulk, tab_manual = st.tabs(["📁 Bulk CSV Import", "✏️ Manual Single Entry"])

with tab_bulk:
    render_csv_uploader()

with tab_manual:
    render_manual_form()

# 6. Session Feed
render_staging_feed()