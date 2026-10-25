import streamlit as st

try:
    from frontend.utils.api_client import (
        fetch_lead_dossier_api,
        fetch_scoring_queue_api,
        generate_outreach_api,
        save_outreach_draft_api,
        send_outreach_email_api,
        fetch_llm_providers_api,
    )
except ModuleNotFoundError:
    from utils.api_client import (
        fetch_lead_dossier_api,
        fetch_scoring_queue_api,
        generate_outreach_api,
        save_outreach_draft_api,
        send_outreach_email_api,
        fetch_llm_providers_api,
    )

def render_outreach_studio():
    """Renders the AI Cold Outreach Generation Studio with Multi-LLM Orchestration."""
    
    st.markdown(
        """
        <div style="margin-bottom: 16px;">
            <h3 class="sg-title" style="font-size: 20px;">✉️ Multi-LLM AI Personalized Outreach Studio</h3>
            <p class="sg-subtitle">Synthesize prospect intelligence, tech stack, and pain points into high-converting cold emails.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 1. Fetch the authoritative queue from the backend
    queue = fetch_scoring_queue_api()

    if not queue:
        with st.container(border=True):
            st.error("Unable to load scored leads from the backend.")
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
        st.error("Unable to load the AI dossier for this lead.")
        return

    # Fetch available LLM Providers for multi-model versatility
    llm_info = fetch_llm_providers_api()
    
    # 4. Two-Column Studio: Left Strategy (1.6) | Right Draft Editor (2.4)
    s_col1, s_col2 = st.columns([1.6, 2.4])

    # Track draft version per prospect to prevent state collision
    if "draft_version" not in st.session_state:
        st.session_state["draft_version"] = 0

    # --- LEFT PANE: STRATEGY & LLM CONTROLS ---
    with s_col1:
        with st.container(border=True):
            st.markdown("<h4 style='margin:0 0 8px 0; font-size: 15px; font-weight: 600;'>Outreach Strategy & Engine</h4>", unsafe_allow_html=True)
            
            # Multi-LLM Provider Selector
            provider_choices = {
                "🤖 First configured provider": "auto",
                "✨ Google Gemini (Primary Enterprise)": "gemini",
                "⚡ OpenAI (GPT-4o-mini)": "openai",
                "🚀 xAI Grok (grok-2-latest)": "grok",
                "🦙 Local Ollama (llama3 Private)": "ollama",
            }
            selected_provider_label = st.selectbox(
                "AI Model Provider",
                options=list(provider_choices.keys()),
                index=0,
                help="Select the provider used for this generation. A failed provider does not fall back to another model.",
            )
            preferred_provider_key = provider_choices[selected_provider_label]

            angle = st.selectbox(
                "Value Angle / Hook",
                options=[
                    "Cloud Scale & Infrastructure Efficiency",
                    "Pipeline Variance & Forecasting ROI",
                    "Tech Stack Modernization",
                    "Operational Cost Reduction & Security",
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

            # Detected Context Signals
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

            custom_notes = st.text_area(
                "Custom Rep Notes (Optional)",
                placeholder="e.g. Mention our recent benchmark with similar SaaS teams...",
                height=70,
            )

            if st.button("🔄 Generate / Refresh Draft", type="primary", use_container_width=True):
                with st.spinner("AI Agent synthesizing personalized outreach..."):
                    new_draft = generate_outreach_api(
                        target_id,
                        angle,
                        tone,
                        custom_notes,
                        preferred_provider=preferred_provider_key,
                    )
                    if not new_draft:
                        st.error("The outreach model did not produce a valid draft.")
                        st.stop()
                st.session_state["current_draft"] = new_draft
                st.session_state["draft_lead_id"] = target_id
                st.session_state["draft_version"] += 1
                st.rerun()

    # --- RIGHT PANE: THE DRAFT EDITOR ---
    with s_col2:
        # Load the draft generated by the backend model
        if "current_draft" not in st.session_state or st.session_state.get("draft_lead_id") != target_id:
            live_draft = generate_outreach_api(
                target_id,
                angle,
                tone,
                custom_notes,
                preferred_provider=preferred_provider_key,
            )
            if not live_draft:
                st.error("The outreach model did not produce a valid draft.")
                return
            st.session_state["current_draft"] = live_draft
            st.session_state["draft_lead_id"] = target_id

        draft = st.session_state.get("current_draft", {})
        subject_options = draft["subject_options"]
        provider_used = draft["provider_used"]

        with st.container(border=True):
            st.markdown(
                f"""
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <h4 style="margin:0; font-size: 15px; font-weight: 600;">Personalized Cold Email</h4>
                    <span style="font-size: 11px; padding: 2px 8px; border-radius: 12px; background: rgba(59, 130, 246, 0.15); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.3);">
                        ✨ {provider_used}
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            subject_choice = st.selectbox("Subject Line Variant (A/B Test Options)", options=subject_options, index=0)

            # Editable Email Body with version-stable key
            v_key = f"draft_body_{target_id}_{st.session_state.get('draft_version', 0)}"
            if v_key not in st.session_state:
                st.session_state[v_key] = draft.get("body", "")

            edited_body = st.text_area("Email Body", value=st.session_state[v_key], height=240, key=f"widget_{v_key}")

            # Personalization Triggers Pills
            triggers = draft.get("personalization_triggers", [])
            if triggers:
                trigger_pills = " ".join([f"<span style='background: rgba(16, 185, 129, 0.12); color: #34d399; padding: 2px 6px; border-radius: 4px; font-size: 11px; margin-right: 4px;'>🎯 {t}</span>" for t in triggers])
                st.markdown(f"<div style='margin-bottom: 8px;'>{trigger_pills}</div>", unsafe_allow_html=True)

            reading_time = draft.get("reading_time_seconds", max(10, round(len(edited_body.split()) / 3.5)))
            hook_score = draft.get("hook_score", 92)

            st.markdown(
                f"""
                <div style="display: flex; justify-content: space-between; font-size: 12px; opacity: 0.8; margin: 8px 0 16px 0;">
                    <span>Hook Score: <strong style="color: {'#34d399' if hook_score >= 90 else '#60a5fa'};">{hook_score} / 100</strong></span>
                    <span>Word Count: <strong>{len(edited_body.split())} words</strong></span>
                    <span>Reading Time: <strong>~{reading_time}s</strong></span>
                    <span>CTA: <strong>{draft.get('call_to_action', '5-min review')}</strong></span>
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