import re
import streamlit as st

# Constraints strictly matching backend/database/models/leads.py
LEAD_STATUSES = ["New Leads", "Qualified", "Proposal", "Negotiation", "Closed Won"]
SOURCES = ["Sales Entry", "LinkedIn", "Website Form", "CRM", "CSV"]
COMPANY_SIZES = ["1 - 10", "11 - 50", "51 - 200", "201 - 500", "501 - 1000", "1000+"]
FUNDING_STAGES = ["Bootstrapped", "Pre-Seed", "Seed", "Series A", "Series B", "Series C+", "Growth / PE", "Public"]
COMMON_TECH_STACK = [
    "AWS", "Google Cloud", "Azure", "PostgreSQL", "Snowflake", "Databricks",
    "Python", "React", "Node.js", "Docker", "Kubernetes", "Salesforce", "HubSpot"
]


def is_valid_email(email: str) -> bool:
    """Basic email format validator."""
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email) is not None


def render_manual_form():
    """Renders Wireframe 2: Grouped manual lead entry card grid."""
    
    # Form key versioning to enable seamless resetting
    if "manual_form_version" not in st.session_state:
        st.session_state["manual_form_version"] = 0

    v = st.session_state["manual_form_version"]

    st.caption("Enter prospect details manually. Fields marked (*) are required for pipeline qualification.")

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
                help="Select technologies identified on their job posts or website.",
                key=f"tech_stack_{v}",
            )
            
            c_sub5, c_sub6 = st.columns(2)
            with c_sub5:
                source = st.selectbox("Lead Source *", options=SOURCES, index=0, key=f"source_{v}")
            with c_sub6:
                lead_status = st.selectbox("Initial Pipeline Stage", options=LEAD_STATUSES, index=0, key=f"stage_{v}")

    # --- ACTION TOOLBAR ---
    st.markdown("<div style='margin-top: 8px;'></div>", unsafe_allow_html=True)
    b_col1, b_col2, b_col3, b_col4 = st.columns([4, 1.5, 2, 2.5])

    with b_col2:
        if st.button("Reset Form", use_container_width=True, type="secondary"):
            st.session_state["manual_form_version"] += 1
            st.rerun()

    def validate_and_create_lead():
        """Validates input fields against requirements and duplicates."""
        cleaned_company = company_name.strip()
        cleaned_email = email.strip().lower()

        if not cleaned_company:
            st.error("Company Name is required.")
            return None
        if not cleaned_email:
            st.error("Work Email is required.")
            return None
        if not is_valid_email(cleaned_email):
            st.error("Please enter a valid email address (e.g., name@company.com).")
            return None

        # Check against leads already staged in this session
        existing_emails = [lead["email"].lower() for lead in st.session_state.get("recent_ingested_leads", [])]
        if cleaned_email in existing_emails:
            st.warning(f"A lead with email '{cleaned_email}' has already been staged in this session.")
            return None

        return {
            "company_name": cleaned_company,
            "contact_name": contact_name.strip() if contact_name.strip() else "N/A",
            "contact_title": contact_title.strip() if contact_title.strip() else "N/A",
            "email": cleaned_email,
            "phone": phone.strip() if phone.strip() else "N/A",
            "industry": industry,
            "company_size": company_size,
            "annual_revenue": annual_revenue,
            "funding_stage": funding_stage,
            "funding_raised": funding_raised.strip() if funding_raised.strip() else "N/A",
            "location": location.strip() if location.strip() else "N/A",
            "tech_stack": ", ".join(tech_stack) if tech_stack else "None",
            "source": source,
            "lead_status": lead_status,
            "ai_status": "Queued",
        }

    with b_col3:
        if st.button("💾 Save & Add Another", use_container_width=True, type="secondary"):
            new_lead = validate_and_create_lead()
            if new_lead:
                st.session_state["recent_ingested_leads"].insert(0, new_lead)
                st.session_state["session_additions"] += 1
                st.session_state["manual_form_version"] += 1
                st.toast(f"Saved {new_lead['company_name']}! Ready for next lead.", icon="✅")
                st.rerun()

    with b_col4:
        if st.button("⚡ Save & Queue for Scoring", use_container_width=True, type="primary"):
            new_lead = validate_and_create_lead()
            if new_lead:
                st.session_state["recent_ingested_leads"].insert(0, new_lead)
                st.session_state["session_additions"] += 1
                st.session_state["manual_form_version"] += 1
                st.toast(f"Saved & queued {new_lead['company_name']} for AI scoring!", icon="⚡")
                st.rerun()