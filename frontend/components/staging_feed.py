import io
import pandas as pd
import streamlit as st

try:
    from frontend.utils.api_client import delete_lead_api, fetch_leads_api, update_lead_api
except ModuleNotFoundError:
    from utils.api_client import delete_lead_api, fetch_leads_api, update_lead_api


LEAD_STATUSES = ["New Leads", "Qualified", "Proposal", "Negotiation", "Closed Won"]
SOURCES = ["Sales Entry", "LinkedIn", "Website Form", "CRM", "CSV"]


def render_staging_feed():
    """Renders Wireframe 3: Live database lead feed with search, filtering, and export."""
    st.markdown(
        """
        <div style="margin-top: 20px; margin-bottom: 12px; display: flex; justify-content: space-between; align-items: flex-end;">
            <div>
                <h3 class="sg-title" style="font-size: 18px;">Recently Ingested Leads</h3>
                <p class="sg-subtitle" style="font-size: 13px;">
                    Verified prospect records stored in PostgreSQL, ready for AI qualification and scoring.
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        # Search & Filter Toolbar
        f_col1, f_col2, f_col3, f_col4 = st.columns([3.5, 2, 1.5, 1], vertical_alignment="center")

        with f_col1:
            search_query = st.text_input(
                "Search leads",
                placeholder="🔍 Search company, contact, or email...",
                label_visibility="collapsed",
            )

        with f_col2:
            sources_present = ["All Sources", "CSV", "Sales Entry", "LinkedIn", "Website Form", "CRM"]
            selected_source = st.selectbox(
                "Filter Source",
                options=sources_present,
                label_visibility="collapsed",
            )

        # 1. Fetch live from FastAPI backend
        records = fetch_leads_api(search=search_query, source=selected_source)

        # 2. Fall back to local session state if backend is offline or returned empty
        if not records:
            session_leads = st.session_state.get("recent_ingested_leads", [])
            if session_leads:
                records = session_leads
                # Apply client-side filters on session records
                if search_query:
                    q = search_query.strip().lower()
                    records = [
                        r for r in records
                        if q in str(r.get("company_name", "")).lower()
                        or q in str(r.get("email", "")).lower()
                        or q in str(r.get("contact_name", "")).lower()
                    ]
                if selected_source and selected_source != "All Sources":
                    records = [r for r in records if r.get("source") == selected_source]

        with f_col3:
            if records:
                export_df = pd.DataFrame(records)
                csv_buffer = io.StringIO()
                export_df.to_csv(csv_buffer, index=False)
                st.download_button(
                    label="⬇️ Export CSV",
                    data=csv_buffer.getvalue(),
                    file_name="salesgenie_leads_export.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
            else:
                st.button("⬇️ Export CSV", disabled=True, use_container_width=True)

        with f_col4:
            if st.button("🔄", use_container_width=True, help="Refresh database feed"):
                st.rerun()

        # Empty State
        if not records:
            st.markdown(
                """
                <div style="text-align: center; padding: 28px 16px;">
                    <div style="font-size: 28px; margin-bottom: 6px;">📋</div>
                    <div style="font-size: 14px; font-weight: 600;">No matching leads in database</div>
                    <div style="font-size: 12px; opacity: 0.7; margin-top: 4px;">
                        Upload a CSV in Tab 1 or save a single lead in Tab 2 to populate the database.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            return

        # Prepare DataFrame for presentation
        df = pd.DataFrame(records)

        # Convert tech_stack list to clean string
        if "tech_stack" in df.columns:
            df["tech_stack"] = df["tech_stack"].apply(
                lambda x: ", ".join(x) if isinstance(x, list) else (str(x) if pd.notna(x) and str(x) != "nan" else "—")
            )

        # Ensure contact name display is friendly
        if "contact_name" in df.columns:
            df["contact_name"] = df["contact_name"].fillna("—")

        # Status Summary Bar
        st.markdown(
            f"""
            <div style="display: flex; gap: 10px; margin: 10px 0; font-size: 12px;">
                <span class="sg-pill sg-pill-teal">Total Results: {len(df)}</span>
                <span class="sg-pill sg-pill-slate">Active Pipeline Stage: New Leads</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Data Table with safe column mapping
        column_configs = {
            "company_name": st.column_config.TextColumn("Company", width="medium"),
            "contact_name": st.column_config.TextColumn("Contact", width="medium"),
            "contact_title": st.column_config.TextColumn("Title", width="medium"),
            "email": st.column_config.TextColumn("Email", width="medium"),
            "industry": st.column_config.TextColumn("Industry", width="medium"),
            "funding_stage": st.column_config.TextColumn("Round", width="small"),
            "tech_stack": st.column_config.TextColumn("Tech Stack", width="medium"),
            "source": st.column_config.TextColumn("Source", width="small"),
            "lead_status": st.column_config.TextColumn("Status", width="small"),
        }

        if "lead_id" in df.columns:
            column_configs["lead_id"] = st.column_config.NumberColumn("ID", width="small")
        if "created_at" in df.columns:
            column_configs["created_at"] = st.column_config.DatetimeColumn("Ingested At", format="YYYY-MM-DD HH:mm")

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config=column_configs,
        )

        # Actions stay beside the table so every persisted row has an explicit target.
        lead_options = {
            f"{record.get('company_name', 'Unnamed company')} (ID {record['lead_id']})": record
            for record in records
            if record.get("lead_id") is not None
        }
        if not lead_options:
            return

        st.markdown("#### Manage lead")
        selected_label = st.selectbox(
            "Select a lead to edit or delete",
            options=list(lead_options),
            label_visibility="collapsed",
        )
        selected = lead_options[selected_label]
        selected_id = int(selected["lead_id"])

        with st.form(f"edit_lead_form_{selected_id}"):
            edit_left, edit_middle, edit_right = st.columns(3)
            with edit_left:
                edit_company = st.text_input("Company name *", value=selected.get("company_name") or "")
                edit_contact = st.text_input("Contact name", value=selected.get("contact_name") or "")
                edit_title = st.text_input("Contact title", value=selected.get("contact_title") or "")
                edit_email = st.text_input("Email *", value=selected.get("email") or "")
                edit_phone = st.text_input("Phone", value=selected.get("phone") or "")
            with edit_middle:
                edit_industry = st.text_input("Industry", value=selected.get("industry") or "")
                edit_company_size = st.text_input("Company size", value=selected.get("company_size") or "")
                edit_revenue = st.text_input("Annual revenue", value=selected.get("annual_revenue") or "")
                edit_location = st.text_input("Location", value=selected.get("location") or "")
                edit_source = st.selectbox(
                    "Source",
                    options=SOURCES,
                    index=SOURCES.index(selected["source"]) if selected.get("source") in SOURCES else 0,
                )
            with edit_right:
                edit_status = st.selectbox(
                    "Pipeline status",
                    options=LEAD_STATUSES,
                    index=LEAD_STATUSES.index(selected["lead_status"])
                    if selected.get("lead_status") in LEAD_STATUSES else 0,
                )
                edit_funding_stage = st.text_input("Funding stage", value=selected.get("funding_stage") or "")
                edit_funding_raised = st.text_input("Funding raised", value=selected.get("funding_raised") or "")
                existing_tech = selected.get("tech_stack") or []
                if not isinstance(existing_tech, list):
                    existing_tech = [item.strip() for item in str(existing_tech).split(",") if item.strip()]
                edit_tech_stack = st.text_input(
                    "Tech stack (comma-separated)",
                    value=", ".join(existing_tech),
                )
                edit_owner = selected.get("owner_user_id")

            if st.form_submit_button("Save changes", type="primary"):
                if not edit_company.strip() or not edit_email.strip():
                    st.error("Company name and email are required.")
                else:
                    payload = {
                        "company_name": edit_company.strip(),
                        "contact_name": edit_contact.strip() or None,
                        "contact_title": edit_title.strip() or None,
                        "email": edit_email.strip().lower(),
                        "phone": edit_phone.strip() or None,
                        "industry": edit_industry.strip() or None,
                        "company_size": edit_company_size.strip() or None,
                        "annual_revenue": edit_revenue.strip() or None,
                        "location": edit_location.strip() or None,
                        "source": edit_source,
                        "lead_status": edit_status,
                        "funding_stage": edit_funding_stage.strip() or None,
                        "funding_raised": edit_funding_raised.strip() or None,
                        "tech_stack": [item.strip() for item in edit_tech_stack.split(",") if item.strip()] or None,
                        "owner_user_id": edit_owner,
                    }
                    success, result = update_lead_api(selected_id, payload)
                    if success:
                        st.toast(f"Updated {payload['company_name']}.", icon="✅")
                        st.rerun()
                    else:
                        st.error(f"Unable to update lead: {result}")

        confirm_delete = st.checkbox("I understand this permanently deletes the selected lead and its AI data.")
        if st.button("Delete selected lead", type="secondary", disabled=not confirm_delete):
            success, result = delete_lead_api(selected_id)
            if success:
                st.toast(f"Deleted {selected.get('company_name', 'lead')}.", icon="🗑️")
                st.rerun()
            else:
                st.error(f"Unable to delete lead: {result}")