import io
import pandas as pd
import streamlit as st

from frontend.utils.api_client import fetch_leads_api


def render_staging_feed():
    """Renders Wireframe 3: Live database lead feed with search, filtering, and export."""
    st.markdown(
        """
        <div style="margin-top: 20px; margin-bottom: 12px; display: flex; justify-content: space-between; align-items: flex-end;">
            <div>
                <h3 style="margin: 0; font-size: 18px; font-weight: 700;">Recently Ingested Leads</h3>
                <p style="margin: 2px 0 0 0; font-size: 13px; opacity: 0.7;">
                    Verified prospect records stored in PostgreSQL, ready for AI qualification.
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

        # Fetch records dynamically from FastAPI
        records = fetch_leads_api(search=search_query, source=selected_source)

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

        # Prepare DataFrame for clean presentation
        df = pd.DataFrame(records)

        # Convert tech_stack list to comma-separated string for display
        if "tech_stack" in df.columns:
            df["tech_stack"] = df["tech_stack"].apply(
                lambda x: ", ".join(x) if isinstance(x, list) else (str(x) if pd.notna(x) else "-")
            )

        # Status Summary Bar
        st.markdown(
            f"""
            <div style="display: flex; gap: 10px; margin: 10px 0; font-size: 12px;">
                <span class="sg-pill sg-pill-teal">Total Results: {len(df)}</span>
                <span class="sg-pill sg-pill-slate">Stage: New Leads</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Display Data Table
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "lead_id": st.column_config.NumberColumn("ID", width="small"),
                "company_name": st.column_config.TextColumn("Company", width="medium"),
                "contact_name": st.column_config.TextColumn("Contact", width="medium"),
                "contact_title": st.column_config.TextColumn("Title", width="medium"),
                "email": st.column_config.TextColumn("Email", width="medium"),
                "industry": st.column_config.TextColumn("Industry", width="medium"),
                "funding_stage": st.column_config.TextColumn("Round", width="small"),
                "tech_stack": st.column_config.TextColumn("Tech Stack", width="medium"),
                "source": st.column_config.TextColumn("Source", width="small"),
                "lead_status": st.column_config.TextColumn("Status", width="small"),
                "created_at": st.column_config.DatetimeColumn("Ingested At", format="YYYY-MM-DD HH:mm"),
            },
        )