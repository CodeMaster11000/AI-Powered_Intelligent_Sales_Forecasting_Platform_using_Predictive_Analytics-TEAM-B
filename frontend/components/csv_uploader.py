import io
import pandas as pd
import streamlit as st

from frontend.utils.api_client import bulk_import_api, fetch_users
from frontend.utils.csv_parser import (
    TARGET_SCHEMA_FIELDS,
    auto_match_column,
    generate_sample_csv,
)


def render_csv_uploader():
    """Renders the Bulk CSV Ingestion interface with database commit support."""
    
    if "demo_active" not in st.session_state:
        st.session_state["demo_active"] = False

    with st.container(border=True):
        # Action toolbar
        t_col1, t_col2, t_col3 = st.columns([2.5, 1.2, 1.3])

        with t_col1:
            st.markdown("<h4 style='margin:0; font-size: 16px; font-weight: 600;'>Bulk Prospect Import</h4>", unsafe_allow_html=True)
            st.caption("Upload a `.csv` file with prospect company and contact details.")

        with t_col2:
            st.download_button(
                label="⬇️ Download Template",
                data=generate_sample_csv(),
                file_name="salesgenie_prospect_template.csv",
                mime="text/csv",
                use_container_width=True,
            )

        with t_col3:
            if st.button("⚡ Load Demo Batch (3 Leads)", use_container_width=True):
                st.session_state["demo_active"] = True

        st.markdown("<div style='margin-top: 8px;'></div>", unsafe_allow_html=True)

        # File Dropzone
        uploaded_file = st.file_uploader(
            "Upload Prospects CSV",
            type=["csv"],
            help="Upload a standard CSV file with company and contact details.",
            label_visibility="collapsed",
        )

        df = None
        file_display_name = ""

        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                file_display_name = uploaded_file.name
            except Exception as e:
                st.error(f"Failed to read CSV: {e}")
                return
        elif st.session_state["demo_active"]:
            df = pd.read_csv(io.StringIO(generate_sample_csv()))
            file_display_name = "Q4_outbound_prospects_sample.csv"

        if df is None:
            return

        # Active Data Mapping State
        row_count = len(df)
        st.markdown(
            f"""
            <div class="sg-file-banner">
                <div style="font-size: 13px; font-weight: 600;">
                    📄 File Loaded: <code>{file_display_name}</code> ({row_count} prospect rows detected)
                </div>
                <span class="sg-pill sg-pill-teal">Ready for Mapping</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<h5 style='font-size: 14px; font-weight: 600; margin: 12px 0 2px 0;'>Smart Column Mapping</h5>", unsafe_allow_html=True)
        st.caption("Confirm detected CSV columns against database fields. Required fields marked (*).")

        target_options = ["-- Ignore Field --"] + [
            f"{v['label']} {'*' if v['required'] else ''} ({k})"
            for k, v in TARGET_SCHEMA_FIELDS.items()
        ]
        key_to_option = {
            k: f"{v['label']} {'*' if v['required'] else ''} ({k})"
            for k, v in TARGET_SCHEMA_FIELDS.items()
        }

        # Header Row
        h_col1, h_col2, h_col3, h_col4 = st.columns([2.2, 3, 3, 1.2])
        h_col1.caption("CSV COLUMN HEADER")
        h_col2.caption("TARGET LEAD FIELD")
        h_col3.caption("SAMPLE DATA (ROW 1)")
        h_col4.caption("STATUS")

        column_mapping = {}

        for idx, col_name in enumerate(df.columns):
            c1, c2, c3, c4 = st.columns([2.2, 3, 3, 1.2])

            sample_val = str(df[col_name].iloc[0]) if not df.empty else "N/A"
            sample_display = (sample_val[:28] + "...") if len(sample_val) > 28 else sample_val

            guessed_key = auto_match_column(col_name)
            default_index = 0
            if guessed_key in key_to_option:
                target_str = key_to_option[guessed_key]
                default_index = target_options.index(target_str)

            c1.markdown(f"<div style='padding-top: 8px; font-size: 13px; font-weight: 500;'>{col_name}</div>", unsafe_allow_html=True)

            selected_option = c2.selectbox(
                f"Map {col_name}",
                options=target_options,
                index=default_index,
                key=f"col_map_{idx}",
                label_visibility="collapsed",
            )

            c3.markdown(
                f"<div style='padding-top: 8px; opacity: 0.8; font-family: monospace; font-size: 12px;'>{sample_display}</div>",
                unsafe_allow_html=True,
            )

            if selected_option != "-- Ignore Field --":
                target_field_key = selected_option.split("(")[-1].replace(")", "").strip()
                column_mapping[col_name] = target_field_key
                if guessed_key == target_field_key:
                    c4.markdown("<div style='padding-top: 6px;'><span class='sg-pill sg-pill-teal'>Auto ✓</span></div>", unsafe_allow_html=True)
                else:
                    c4.markdown("<div style='padding-top: 6px;'><span class='sg-pill sg-pill-slate'>Mapped</span></div>", unsafe_allow_html=True)
            else:
                c4.markdown("<div style='padding-top: 6px;'><span class='sg-pill sg-pill-slate'>Ignored</span></div>", unsafe_allow_html=True)

        st.divider()

        # Pre-import verification checks
        st.markdown("<h5 style='font-size: 14px; font-weight: 600; margin-bottom: 6px;'>Pre-Import Validation</h5>", unsafe_allow_html=True)

        mapped_targets = list(column_mapping.values())
        has_company = "company_name" in mapped_targets
        has_email = "email" in mapped_targets

        val_col1, val_col2 = st.columns([2.5, 1.5])

        with val_col1:
            if has_company and has_email:
                st.success(f"✓ Mandatory fields (`company_name` & `email`) verified across all {row_count} rows.")
            else:
                missing = []
                if not has_company:
                    missing.append("Company Name")
                if not has_email:
                    missing.append("Work Email")
                st.error(f"Missing mandatory mapping: {', '.join(missing)}.")

            # Assignment fixed: skip_dupes defined here
            skip_dupes = st.checkbox(
                "Skip existing duplicates based on email check (Recommended)",
                value=True,
            )

        with val_col2:
            users_list = fetch_users()
            user_options = {u["name"]: u["user_id"] for u in users_list}
            owner_name = st.selectbox(
                "Assign Ingested Leads To",
                options=list(user_options.keys()) if user_options else ["Alex Rep"],
                index=0,
            )
            selected_owner_id = user_options.get(owner_name)

        # Action Buttons
        btn_col1, btn_col2, btn_col3 = st.columns([4, 1.5, 2.5])

        with btn_col2:
            if st.button("Reset File", use_container_width=True):
                st.session_state["demo_active"] = False
                st.rerun()

        with btn_col3:
            ready = has_company and has_email
            if st.button(
                f"⚡ Import & Commit {row_count} Leads",
                type="primary",
                use_container_width=True,
                disabled=not ready,
            ):
                leads_to_post = []
                for _, r in df.iterrows():
                    lead_dict = {
                        "company_name": str(r.get([c for c, m in column_mapping.items() if m == "company_name"][0], "Unknown")).strip(),
                        "email": str(r.get([c for c, m in column_mapping.items() if m == "email"][0], "")).strip().lower(),
                        "source": "CSV",
                        "lead_status": "New Leads",
                        "owner_user_id": selected_owner_id,
                    }
                    if "contact_name" in mapped_targets:
                        val = str(r.get([c for c, m in column_mapping.items() if m == "contact_name"][0], "")).strip()
                        lead_dict["contact_name"] = val if val and val != "nan" else None
                    if "contact_title" in mapped_targets:
                        val = str(r.get([c for c, m in column_mapping.items() if m == "contact_title"][0], "")).strip()
                        lead_dict["contact_title"] = val if val and val != "nan" else None
                    if "industry" in mapped_targets:
                        val = str(r.get([c for c, m in column_mapping.items() if m == "industry"][0], "")).strip()
                        lead_dict["industry"] = val if val and val != "nan" else None
                    if "company_size" in mapped_targets:
                        val = str(r.get([c for c, m in column_mapping.items() if m == "company_size"][0], "")).strip()
                        lead_dict["company_size"] = val if val and val != "nan" else None
                    if "funding_stage" in mapped_targets:
                        val = str(r.get([c for c, m in column_mapping.items() if m == "funding_stage"][0], "")).strip()
                        lead_dict["funding_stage"] = val if val and val != "nan" else None
                    if "location" in mapped_targets:
                        val = str(r.get([c for c, m in column_mapping.items() if m == "location"][0], "")).strip()
                        lead_dict["location"] = val if val and val != "nan" else None
                    if "tech_stack" in mapped_targets:
                        raw_stack = str(r.get([c for c, m in column_mapping.items() if m == "tech_stack"][0], "")).strip()
                        if raw_stack and raw_stack != "nan":
                            lead_dict["tech_stack"] = [t.strip() for t in raw_stack.split(",") if t.strip()]
                        else:
                            lead_dict["tech_stack"] = None

                    leads_to_post.append(lead_dict)

                success, result = bulk_import_api(leads_to_post, skip_duplicates=skip_dupes)

                if success:
                    imported = result.get("imported_count", 0)
                    skipped = result.get("skipped_duplicates", 0)
                    st.session_state["session_additions"] += imported
                    st.session_state["demo_active"] = False
                    st.toast(f"Committed {imported} leads to PostgreSQL! ({skipped} duplicates skipped)", icon="✅")
                    st.rerun()
                else:
                    st.error(f"Import failed: {result}")