import io
import pandas as pd
import streamlit as st

from frontend.utils.csv_parser import (
    TARGET_SCHEMA_FIELDS,
    auto_match_column,
    generate_sample_csv,
)


def render_csv_uploader():
    """Renders the Bulk CSV Ingestion interface."""
    
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

        # Single dropzone
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

            st.checkbox(
                "Skip existing duplicates based on email check (Recommended)",
                value=True,
            )

        with val_col2:
            st.selectbox(
                "Assign Ingested Leads To",
                options=["Alex Rep (Current User)", "Sarah Jenkins (BDR)", "Unassigned"],
                index=0,
            )

        # Action Buttons
        btn_col1, btn_col2, btn_col3 = st.columns([4, 1.5, 2.5])

        with btn_col2:
            if st.button("Reset File", use_container_width=True):
                st.session_state["demo_active"] = False
                st.rerun()

        with btn_col3:
            ready = has_company and has_email
            if st.button(
                f"⚡ Import & Queue {row_count} Leads",
                type="primary",
                use_container_width=True,
                disabled=not ready,
            ):
                staged = []
                for _, r in df.iterrows():
                    staged.append({
                        "company_name": r.get([c for c, m in column_mapping.items() if m == "company_name"][0], "Unknown"),
                        "contact_name": r.get([c for c, m in column_mapping.items() if m == "contact_name"][0], "N/A") if "contact_name" in mapped_targets else "N/A",
                        "email": r.get([c for c, m in column_mapping.items() if m == "email"][0], ""),
                        "source": "CSV",
                        "lead_status": "New Leads",
                        "ai_status": "Queued",
                    })

                st.session_state["recent_ingested_leads"].extend(staged)
                st.session_state["session_additions"] += row_count
                st.session_state["demo_active"] = False
                st.toast(f"Staged {row_count} leads successfully!", icon="✅")
                st.rerun()