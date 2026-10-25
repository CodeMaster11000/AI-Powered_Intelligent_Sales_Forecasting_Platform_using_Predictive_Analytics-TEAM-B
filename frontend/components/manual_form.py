import re
import streamlit as st

try:
    from frontend.utils.api_client import create_lead_api, fetch_users, score_lead_api
except ModuleNotFoundError:
    from utils.api_client import create_lead_api, fetch_users, score_lead_api

# Schema constraints matching backend/database/models/leads.py
LEAD_STATUSES = ["New Leads", "Qualified", "Proposal", "Negotiation", "Closed Won"]
SOURCES = ["Sales Entry", "LinkedIn", "Website Form", "CRM", "CSV"]
COMPANY_SIZES = ["1 - 10", "11 - 50", "51 - 200", "201 - 500", "501 - 1000", "1000+"]
FUNDING_STAGES = ["Bootstrapped", "Pre-Seed", "Seed", "Series A", "Series B", "Series C+", "Growth / PE", "Public"]
COMMON_TECH_STACK = [
    "AWS", "Google Cloud", "Azure", "PostgreSQL", "Snowflake", "Databricks",
    "Python", "React", "Node.js", "Docker", "Kubernetes", "Salesforce", "HubSpot"
]


def is_valid_email(email: str) -> bool:
    """Basic email validator."""
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email.strip()) is not None


def render_manual_form():
    """Renders Wireframe 2: Grouped manual lead entry connected to PostgreSQL."""
    
    if "manual_form_version" not in st.session_state:
        st.session_state["manual_form_version"] = 0

    v = st.session_state["manual_form_version"]

    st.caption("Enter prospect details manually. Fields marked (*) are committed directly to PostgreSQL.")

    # Fetch live users for owner assignment
    users_list = fetch_users()
    user_options = {u["name"]: u["user_id"] for u in users_list}
    if not user_options:
        st.error("Unable to load lead owners from the backend.")
        return

    # 2x2 Grid of Semantic Cards
    row1_left, row1_right = st.columns(2)
    row2_left, row2_right = st.columns(2)

    # --- CARD 1: CONTACT DETAILS ---
    with row1_left:
        with st.container(border=True):
            st.markdown(
                """
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
                    <span style="font-size: 14px; font-weight: 600;">👤 Primary Contact</span>
                    <span class="sg-pill sg-pill-slate">Decision Maker</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            contact_name = st.text_input("Contact Full Name", placeholder="e.g. Sarah Jenkins", key=f"contact_name_{v}")
            contact_title = st.text_input(
                "Job Title",
                placeholder="e.g. VP of Engineering",
                help="Used by AI scoring to assess decision-maker level.",
                key=f"contact_title_{v}",
            )
            email = st.text_input("Work Email *", placeholder="e.g. sarah@acmecloud.io", key=f"email_{v}")
            phone = st.text_input("Direct Phone Number", placeholder="e.g. +1 (415) 555-0192", key=f"phone_{v}")

    # --- CARD 2: COMPANY FIRMOGRAPHICS ---
    with row1_right:
        with st.container(border=True):
            st.markdown(
                """
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
                    <span style="font-size: 14px; font-weight: 600;">🏢 Company Firmographics</span>
                    <span class="sg-pill sg-pill-slate">Account Profile</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            company_name = st.text_input("Company Name *", placeholder="e.g. Acme Cloud Corp", key=f"company_name_{v}")
            
            c_sub1, c_sub2 = st.columns(2)
            with c_sub1:
                industry = st.selectbox(
                    "Industry",
                    options=["Cloud Infrastructure", "Enterprise SaaS", "Fintech", "Healthtech", "E-commerce", "AI / ML", "Cybersecurity", "Other"],
                    key=f"industry_{v}",
                )
            with c_sub2:
                company_size = st.selectbox("Company Size (Headcount)", options=COMPANY_SIZES, index=2, key=f"size_{v}")

            c_sub3, c_sub4 = st.columns(2)
            with c_sub3:
                location = st.text_input("Headquarters (City, Country)", placeholder="e.g. Austin, TX, USA", key=f"location_{v}")
            with c_sub4:
                annual_revenue = st.selectbox(
                    "Estimated Revenue",
                    options=["< $1M", "$1M - $5M", "$5M - $10M", "$10M - $25M", "$25M - $50M", "$50M+"],
                    index=2,
                    key=f"revenue_{v}",
                )

    # --- CARD 3: GROWTH & INVESTMENT SIGNALS ---
    with row2_left:
        with st.container(border=True):
            st.markdown(
                """
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
                    <span style="font-size: 14px; font-weight: 600;">🚀 Growth & Financial Signals</span>
                    <span class="sg-pill sg-pill-teal">Scoring Input</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            funding_stage = st.selectbox("Funding Stage", options=FUNDING_STAGES, index=3, key=f"funding_stage_{v}")
            funding_raised = st.text_input("Total Capital Raised", placeholder="e.g. $14.5M", key=f"funding_raised_{v}")

    # --- CARD 4: TECH STACK & ATTRIBUTION ---
    with row2_right:
        with st.container(border=True):
            st.markdown(
                """
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
                    <span style="font-size: 14px; font-weight: 600;">⚙️ Tech Stack & Attribution</span>
                    <span class="sg-pill sg-pill-slate">System Keys</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            tech_stack = st.multiselect(
                "Known Tech Stack",
                options=COMMON_TECH_STACK,
                default=["AWS", "PostgreSQL"],
                help="Select technologies identified on company assets.",
                key=f"tech_stack_{v}",
            )
            
            c_sub5, c_sub6 = st.columns(2)
            with c_sub5:
                source = st.selectbox("Lead Source *", options=SOURCES, index=0, key=f"source_{v}")
            with c_sub6:
                lead_status = st.selectbox("Initial Pipeline Stage", options=LEAD_STATUSES, index=0, key=f"stage_{v}")

            owner_name = st.selectbox("Lead Owner", options=list(user_options.keys()), index=0, key=f"owner_{v}")
            owner_id = user_options.get(owner_name)

    # --- ACTION BUTTONS ---
    st.markdown("<div style='margin-top: 8px;'></div>", unsafe_allow_html=True)
    b_col1, b_col2, b_col3, b_col4 = st.columns([4, 1.5, 2, 2.5])

    with b_col2:
        if st.button("Reset Form", use_container_width=True, type="secondary"):
            st.session_state["manual_form_version"] += 1
            st.rerun()

    def build_lead_payload():
        """Validates input fields and returns API-ready dictionary."""
        cleaned_company = company_name.strip()
        cleaned_email = email.strip().lower()

        if not cleaned_company:
            st.error("Company Name is required.")
            return None
        if not cleaned_email:
            st.error("Work Email is required.")
            return None
        if not is_valid_email(cleaned_email):
            st.error("Please enter a valid email address.")
            return None

        return {
            "company_name": cleaned_company,
            "contact_name": contact_name.strip() if contact_name.strip() else None,
            "contact_title": contact_title.strip() if contact_title.strip() else None,
            "email": cleaned_email,
            "phone": phone.strip() if phone.strip() else None,
            "industry": industry,
            "company_size": company_size,
            "annual_revenue": annual_revenue,
            "funding_stage": funding_stage,
            "funding_raised": funding_raised.strip() if funding_raised.strip() else None,
            "location": location.strip() if location.strip() else None,
            "tech_stack": tech_stack if tech_stack else None,
            "source": source,
            "lead_status": lead_status,
            "owner_user_id": owner_id,
        }

    with b_col3:
        if st.button("💾 Save & Add Another", use_container_width=True, type="secondary"):
            payload = build_lead_payload()
            if payload:
                success, result = create_lead_api(payload)
                if success:
                    st.session_state["session_additions"] += 1
                    st.session_state["manual_form_version"] += 1
                    st.toast(f"Saved {payload['company_name']} to PostgreSQL!", icon="✅")
                    st.rerun()
                else:
                    if "Backend is offline" in str(result):
                        st.session_state.setdefault("recent_ingested_leads", []).insert(0, payload)
                        st.session_state["session_additions"] += 1
                        st.session_state["manual_form_version"] += 1
                        st.warning(f"Backend offline: Saved {payload['company_name']} in local session.")
                        st.rerun()
                    else:
                        st.error(f"Error: {result}")

    with b_col4:
        if st.button("⚡ Save & Queue for Scoring", use_container_width=True, type="primary"):
            payload = build_lead_payload()
            if payload:
                success, result = create_lead_api(payload)
                if success:
                    lead_id = result.get("lead_id") if isinstance(result, dict) else None
                    if lead_id:
                        score_lead_api(lead_id)
                        st.session_state["selected_lead_id"] = lead_id

                    st.session_state["session_additions"] += 1
                    st.session_state["manual_form_version"] += 1
                    st.toast(f"Committed & scored {payload['company_name']}!", icon="⚡")
                    st.rerun()
                else:
                    if "Backend is offline" in str(result):
                        payload["score"] = 72
                        payload["priority"] = "warm"
                        st.session_state.setdefault("recent_ingested_leads", []).insert(0, payload)
                        st.session_state["session_additions"] += 1
                        st.session_state["manual_form_version"] += 1
                        st.warning(f"Backend offline: Staged {payload['company_name']} in local session.")
                        st.rerun()
                    else:
                        st.error(f"Error: {result}")