import io
import pandas as pd
import streamlit as st


def render_staging_feed():
    """Renders Wireframe 3: Ingestion feed & staging queue."""
    st.markdown(
        """
        <div style="margin-top: 20px; margin-bottom: 12px; display: flex; justify-content: space-between; align-items: flex-end;">
            <div>
                <h3 style="margin: 0; font-size: 18px; font-weight: 700;">Recently Ingested Leads (This Session)</h3>
                <p style="margin: 2px 0 0 0; font-size: 13px; opacity: 0.7;">
                    Verified prospect records staged in memory, ready for PostgreSQL commit and AI scoring.
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    records = st.session_state.get("recent_ingested_leads", [])

    # Empty State
    if not records:
        with st.container(border=True):
            st.markdown(
                """
                <div style="text-align: center; padding: 32px 16px;">
                    <div style="font-size: 32px; margin-bottom: 8px;">📋</div>
                    <div style="font-size: 15px; font-weight: 600;">No leads staged yet this session</div>
                    <div style="font-size: 13px; opacity: 0.7; margin-top: 4px;">
                        Upload a CSV in Tab 1 or fill in the manual lead form in Tab 2 to populate your staging queue.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        return

    # Populated State: Search, Filter, and Controls
    df = pd.DataFrame(records)

    with st.container(border=True):
        # Quick Search & Filter Toolbar
        f_col1, f_col2, f_col3, f_col4 = st.columns([3, 2, 1.5, 1.5], vertical_alignment="center")

        with f_col1:
            search_query = st.text_input(
                "Search staged leads",
                placeholder="🔍 Search by company, email, or contact...",
                label_visibility="collapsed",
            )

        with f_col2:
            sources_present = ["All Sources"] + sorted(list(df["source"].unique()))
            selected_source = st.selectbox(
                "Filter Source",
                options=sources_present,
                label_visibility="collapsed",
            )

        with f_col3:
            # Export staged data button
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            st.download_button(
                label="⬇️ Export Staged",
                data=csv_buffer.getvalue(),
                file_name="staged_leads_session.csv",
                mime="text/csv",
                use_container_width=True,
            )

        with f_col4:
            if st.button("🗑️ Clear Queue", use_container_width=True, type="secondary"):
                st.session_state["recent_ingested_leads"] = []
                st.session_state["session_additions"] = 0
                st.toast("Staging queue cleared.", icon="ℹ️")
                st.rerun()

        # Apply Filtering
        filtered_df = df.copy()
        if search_query:
            query = search_query.lower()
            filtered_df = filtered_df[
                filtered_df["company_name"].astype(str).str.lower().str.contains(query)
                | filtered_df["email"].astype(str).str.lower().str.contains(query)
                | filtered_df["contact_name"].astype(str).str.lower().str.contains(query)
            ]

        if selected_source != "All Sources":
            filtered_df = filtered_df[filtered_df["source"] == selected_source]

        # Status Summary Bar
        st.markdown(
            f"""
            <div style="display: flex; gap: 12px; margin: 12px 0 10px 0; font-size: 12px;">
                <span class="sg-pill sg-pill-teal">Staged Leads: {len(filtered_df)}</span>
                <span class="sg-pill sg-pill-slate">Ready for AI Scoring: {len(filtered_df[filtered_df['ai_status'] == 'Queued'])}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Main Data Table
        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "company_name": st.column_config.TextColumn("Company", help="Company Name"),
                "contact_name": st.column_config.TextColumn("Contact", help="Primary Contact Name"),
                "contact_title": st.column_config.TextColumn("Job Title"),
                "email": st.column_config.TextColumn("Email Address"),
                "industry": st.column_config.TextColumn("Industry"),
                "funding_stage": st.column_config.TextColumn("Round"),
                "tech_stack": st.column_config.TextColumn("Tech Stack"),
                "source": st.column_config.TextColumn("Source"),
                "lead_status": st.column_config.TextColumn("Stage"),
                "ai_status": st.column_config.TextColumn("AI Status"),
            },
        )