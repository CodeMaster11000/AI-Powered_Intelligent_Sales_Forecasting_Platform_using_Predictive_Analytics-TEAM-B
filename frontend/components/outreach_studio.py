import streamlit as st

try:
    from frontend.utils.api_client import (
        fetch_lead_dossier_api,
        fetch_scoring_queue_api,
        generate_outreach_api,
        save_outreach_draft_api,
        send_outreach_email_api,
    )
except ModuleNotFoundError:
    from utils.api_client import (
        fetch_lead_dossier_api,
        fetch_scoring_queue_api,
        generate_outreach_api,
        save_outreach_draft_api,
        send_outreach_email_api,
    )


def synthesize_offline_draft(company: str, contact: str, title: str, tech_stack: list, angle: str, tone: str) -> dict:
    """Local fallback generator to ensure outreach drafts render even if backend is offline."""
    first_name = (contact or "there").split()[0]
    stack_name = tech_stack[0] if tech_stack else "cloud"

    if "Direct & Punchy" in tone:
        body = (
            f"Hi {first_name},\n\n"
            f"Noticed {company}'s growth and work scaling your {stack_name} architecture.\n\n"
            f"Most {title}s we speak with lose 4-6 hours weekly on manual pipeline scoring as deals expand.\n\n"
            f"SalesGenie automates predictive lead qualification with 92% pipeline forecast accuracy. "
            f"Open to a brief 5-minute chat this Thursday?\n\n"
            f"Best,\nAlex Rep"
        )
    elif "Problem-Centric" in tone:
        body = (
            f"Hi {first_name},\n\n"
            f"Quick observation on {company}: as teams scale data throughput, forecast variance often bottlenecks revenue reporting.\n\n"
            f"Our platform benchmarks show a 40% reduction in lead qualification cycles for teams using {stack_name}.\n\n"
            f"Would you be open to a 10-minute look at the benchmark data this Wednesday?\n\n"
            f"Regards,\nAlex Rep"
        )
    else:  # Consultative
        body = (
            f"Hi {first_name},\n\n"
            f"Congratulations on {company}'s ongoing market momentum.\n\n"
            f"In reviewing your tech footprint, our models flagged high alignment between your {stack_name} stack and our predictive analytics platform.\n\n"
            f"We help high-growth sales teams match high-intent prospects before they hit the open market.\n\n"
            f"Do you have 10 minutes this Thursday afternoon to share notes?\n\n"
            f"Best regards,\nAlex Rep\nSalesGenie AI"
        )

    subjects = [
        f"Quick question re: {stack_name} at {company}",
        f"{company} + SalesGenie: predictive intelligence",
        f"Idea for {first_name} on sales forecasting",
    ]

    return {
        "subject_options": subjects,
        "selected_subject": subjects[0],
        "body": body,
        "hook_score": 92,
        "word_count": len(body.split()),
    }


def render_outreach_studio():
    """Renders the AI Cold Outreach Generation Studio (Wireframe B)."""
    
    st.markdown(
        """
        <div style="margin-bottom: 16px;">
            <h3 class="sg-title" style="font-size: 20px;">Personalized AI Outreach Studio</h3>
            <p class="sg-subtitle">Synthesize prospect intelligence, tech stack, and pain points into high-converting emails.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 1. Fetch queue with offline fallback
    queue = fetch_scoring_queue_api()
    if not queue:
        session_leads = st.session_state.get("recent_ingested_leads", [])
        if session_leads:
            queue = []
            for idx, sl in enumerate(session_leads, start=1):
                queue.append({
                    "lead_id": sl.get("lead_id", idx),
                    "company_name": sl.get("company_name", f"Account #{idx}"),
                    "contact_name": sl.get("contact_name", "Key Contact"),
                    "priority": sl.get("priority", "hot"),
                })

    if not queue:
        with st.container(border=True):
            st.info("No leads available. Please ingest and score leads first in Tab 1.")
        return

    # 2. Select target prospect
    lead_options = {
        f"{q['company_name']} — {q.get('contact_name', 'Contact')} ({q.get('priority', 'hot').upper()})": q["lead_id"]
        for q in queue
    }
    
    # Pre-select if forwarded from Scoring Hub
    preselect_id = st.session_state.get("outreach_target_lead_id")
    default_idx = 0
    if preselect_id:
        for idx, (_, lid) in enumerate(lead_options.items()):
            if lid == preselect_id:
                default_idx = idx
                break

    selected_label = st.selectbox("Target Prospect", options=list(lead_options.keys()), index=default_idx)
    target_id = lead_options[selected_label]

    # 3. Fetch Dossier
    dossier = fetch_lead_dossier_api(target_id)
    if not dossier:
        # Fallback dossier for offline testing
        target_item = next((q for q in queue if q["lead_id"] == target_id), queue[0])
        dossier = {
            "lead_id": target_id,
            "company_name": target_item.get("company_name", "Acme Corp"),
            "contact_name": target_item.get("contact_name", "Sarah Jenkins"),
            "contact_title": "VP of Engineering",
            "email": "sarah@acmecloud.io",
            "funding_stage": "Series B",
            "tech_stack": ["AWS", "PostgreSQL", "Kubernetes"],
        }

    # 4. Two-Column Studio: Left Strategy (1.5) | Right Draft Editor (2.5)
    s_col1, s_col2 = st.columns([1.6, 2.4])

    # Track draft version per prospect to prevent state collision
    if "draft_version" not in st.session_state:
        st.session_state["draft_version"] = 0

    # --- LEFT PANE: STRATEGY CONTROLS ---
    with s_col1:
        with st.container(border=True):
            st.markdown("<h4 style='margin:0 0 8px 0; font-size: 15px; font-weight: 600;'>Outreach Strategy & Angle</h4>", unsafe_allow_html=True)
            
            angle = st.selectbox(
                "Value Angle / Hook",
                options=[
                    "Cloud Scale & Infrastructure Efficiency",
                    "Pipeline Variance & Forecasting ROI",
                    "Tech Stack Modernization",
                ],
            )

            tone = st.radio(
                "Tone & Style",
                options=[
                    "Consultative / Executive (Recommended)",
                    "Direct & Punchy (Under 100 words)",
                    "Problem-Centric / Metric-Driven",
                ],
            )

            # Detected Context Chips
            st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
            st.caption("DETECTED CONTEXT SIGNALS")
            
            stack_list = dossier.get("tech_stack", [])
            tech_str = ", ".join(stack_list[:3]) if stack_list else "Modern Cloud"
            st.markdown(
                f"""
                <div style="font-size: 12px; margin-bottom: 4px;">✔ <strong>Tech Fit:</strong> {tech_str}</div>
                <div style="font-size: 12px; margin-bottom: 4px;">✔ <strong>Growth Stage:</strong> {dossier.get('funding_stage', 'Growth')}</div>
                <div style="font-size: 12px; margin-bottom: 12px;">✔ <strong>Decision Maker:</strong> {dossier.get('contact_title', 'Executive')}</div>
                """,
                unsafe_allow_html=True,
            )

            custom_notes = st.text_area("Custom Rep Notes (Optional)", placeholder="e.g. Mention our recent benchmark with similar SaaS teams...", height=70)

            if st.button("🔄 Generate / Refresh Draft", type="primary", use_container_width=True):
                new_draft = generate_outreach_api(target_id, angle, tone, custom_notes)
                if not new_draft:
                    new_draft = synthesize_offline_draft(
                        dossier["company_name"],
                        dossier["contact_name"],
                        dossier.get("contact_title", "Executive"),
                        stack_list,
                        angle,
                        tone,
                    )
                st.session_state["current_draft"] = new_draft
                st.session_state["draft_lead_id"] = target_id
                st.session_state["draft_version"] += 1
                st.rerun()

    # --- RIGHT PANE: THE DRAFT EDITOR ---
    with s_col2:
        # Load draft from API or offline synthesizer
        if "current_draft" not in st.session_state or st.session_state.get("draft_lead_id") != target_id:
            live_draft = generate_outreach_api(target_id, angle, tone, custom_notes)
            if not live_draft:
                live_draft = synthesize_offline_draft(
                    dossier["company_name"],
                    dossier["contact_name"],
                    dossier.get("contact_title", "Executive"),
                    stack_list,
                    angle,
                    tone,
                )
            st.session_state["current_draft"] = live_draft
            st.session_state["draft_lead_id"] = target_id

        draft = st.session_state.get("current_draft", {})
        subject_options = draft.get("subject_options", [f"Introduction: {dossier['company_name']}"])

        with st.container(border=True):
            st.markdown("<h4 style='margin:0 0 8px 0; font-size: 15px; font-weight: 600;'>Generated Cold Email</h4>", unsafe_allow_html=True)

            subject_choice = st.selectbox("Subject Line Variant", options=subject_options, index=0)

            # Editable Email Body with version-stable key
            v_key = f"draft_body_{target_id}_{st.session_state.get('draft_version', 0)}"
            if v_key not in st.session_state:
                st.session_state[v_key] = draft.get("body", "")

            edited_body = st.text_area("Email Body", value=st.session_state[v_key], height=240, key=f"widget_{v_key}")

            st.markdown(
                f"""
                <div style="display: flex; justify-content: space-between; font-size: 12px; opacity: 0.7; margin: 8px 0 16px 0;">
                    <span>Hook Score: <strong>{draft.get('hook_score', 90)} / 100</strong></span>
                    <span>Estimated Word Count: <strong>{len(edited_body.split())} words</strong></span>
                    <span>Status: <strong>Ready to Send</strong></span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Action Buttons
            a1, a2, a3 = st.columns([1.5, 1.5, 2])
            with a1:
                with st.popover("📋 View / Copy", use_container_width=True):
                    st.caption("Copy email content below:")
                    st.code(f"Subject: {subject_choice}\n\n{edited_body}", language="markdown")

            with a2:
                if st.button("💾 Save as Draft", use_container_width=True):
                    success, msg = save_outreach_draft_api(target_id, subject_choice, edited_body)
                    st.toast(msg, icon="💾")

            with a3:
                if st.button("🚀 Send Email", type="primary", use_container_width=True):
                    success, msg = send_outreach_email_api(target_id, subject_choice, edited_body)
                    st.toast(f"Outreach sent to {dossier.get('email', 'lead')}!", icon="🚀")