import streamlit as st

from frontend.components.ui import backend_error, card_title, empty_state, html, info_grid, page_header, pill
from frontend.utils.api_client import (
    fetch_crm_records_api,
    fetch_interactions_api,
    fetch_lead_interactions_api,
    fetch_llm_providers_api,
    push_lead_crm_api,
    summarize_interaction_api,
    sync_crm_api,
    test_crm_connection_api,
)
from frontend.utils.helpers import esc


def _format_provider(provider: str) -> str:
    return "HubSpot" if provider == "hubspot" else "Salesforce"


def _provider_controls() -> None:
    left, right = st.columns(2)
    for provider, column in (("hubspot", left), ("salesforce", right)):
        with column:
            with st.container(border=True):
                card_title(_format_provider(provider), "CRM connection")
                c1, c2, c3 = st.columns(3)
                if c1.button("Test", key=f"test_{provider}", width="stretch"):
                    ok, result = test_crm_connection_api(provider)
                    if ok:
                        st.toast(f"{_format_provider(provider)} connection is available.", icon="✅")
                    else:
                        st.error(str(result))
                if c2.button("Sync", key=f"sync_{provider}", width="stretch", type="primary"):
                    with st.spinner(f"Syncing {_format_provider(provider)} contacts…"):
                        ok, result = sync_crm_api(provider)
                    if ok:
                        st.toast(f"{_format_provider(provider)} sync completed.", icon="✅")
                        st.rerun()
                    else:
                        st.error(str(result))
                c3.caption("Last records")


def _render_synced_contacts() -> None:
    top = st.columns([1, 3])
    provider = top[0].selectbox("CRM", ["All providers", "HubSpot", "Salesforce"], key="crm_filter")
    provider_key = provider.lower() if provider != "All providers" else None
    search = top[1].text_input("Search", placeholder="Company, contact, email or provider ID", key="crm_search")

    records = fetch_crm_records_api(provider_key, search)
    if records is None:
        backend_error("synced CRM records")
        return
    if not records:
        empty_state("🔗", "No synced contacts", "Test a connection and run a HubSpot or Salesforce sync.")
        return

    left, right = st.columns([1.15, 2])
    with left:
        with st.container(border=True):
            card_title("Synced contacts", f"{len(records)} records")
            if "selected_crm_record" not in st.session_state:
                st.session_state["selected_crm_record"] = records[0]["record_id"]
            ids = {row["record_id"] for row in records}
            if st.session_state["selected_crm_record"] not in ids:
                st.session_state["selected_crm_record"] = records[0]["record_id"]

            with st.container(height=520, border=False):
                for row in records:
                    rid = row["record_id"]
                    selected = rid == st.session_state["selected_crm_record"]
                    name = row.get("contact_name") or row.get("company_name") or "Unnamed contact"
                    state = row.get("sync_state") or "synced"
                    provider_name = _format_provider(row["provider"])
                    html(
                        f"<div class='sg-lead-row {'selected' if selected else ''}'><div class='sg-lead-main'>"
                        f"<div class='sg-lead-name'>{esc(name)}</div>"
                        f"<div class='sg-lead-meta'>{esc(row.get('company_name'))} · {esc(provider_name)} · {esc(state)}</div>"
                        f"</div></div>"
                    )
                    if st.button("Open" if not selected else "Viewing", key=f"crm_open_{rid}",
                                 width="stretch", type="primary" if selected else "secondary", disabled=selected):
                        st.session_state["selected_crm_record"] = rid
                        st.rerun()

    selected = next((row for row in records if row["record_id"] == st.session_state["selected_crm_record"]), records[0])
    with right:
        with st.container(border=True):
            card_title(selected.get("contact_name") or "CRM contact", "CONTACT PROFILE")
            provider_name = _format_provider(selected["provider"])
            html(
                f"<div style='display:flex;justify-content:space-between;gap:8px;flex-wrap:wrap'>"
                f"<div><b>{esc(selected.get('company_name'), 'Unknown company')}</b><br>"
                f"<span class='sg-lead-meta'>{esc(selected.get('contact_title'))}</span></div>"
                f"{pill(provider_name, 'teal')} {pill(str(selected.get('sync_state') or 'synced'), 'hot')}</div>"
            )
            info_grid([
                ("Email", selected.get("email") or "Not available"),
                ("Phone", selected.get("phone") or "Not available"),
                ("Lead status", selected.get("lead_status") or "Not available"),
                ("Provider ID", selected.get("provider_record_id") or "Not available"),
                ("Interactions", selected.get("interaction_count") or 0),
                ("Internal lead", f"#{selected['lead_id']}" if selected.get("lead_id") else "Not linked"),
            ])
            if selected.get("lead_id"):
                if st.button("Push internal lead to CRM", key=f"crm_push_{selected['record_id']}", width="stretch"):
                    with st.spinner("Pushing lead fields…"):
                        ok, result = push_lead_crm_api(selected["lead_id"], selected["provider"])
                    if ok:
                        st.toast("Lead synced back to CRM.", icon="✅")
                        st.rerun()
                    else:
                        st.error(str(result))

        lead_id = selected.get("lead_id")
        interactions = fetch_lead_interactions_api(lead_id) if lead_id else []
        with st.container(border=True):
            card_title("Call & meeting history", f"{len(interactions)} interactions")
            if not interactions:
                st.caption("No summarized calls or meetings are linked to this contact.")
            for interaction in interactions:
                _render_interaction(interaction, expanded=False, key_prefix=f"contact_{selected['record_id']}")

def _render_interaction(
    interaction: dict,
    expanded: bool = True,
    key_prefix: str = "interaction",
) -> None:
    status = interaction.get("processing_status") or "unknown"
    title = f"{interaction.get('interaction_type', 'meeting').title()} · {interaction.get('subject') or 'Untitled'}"
    interaction_id = interaction.get("interaction_id", id(interaction))
    with st.expander(title, expanded=expanded, key=f"{key_prefix}_interaction_{interaction_id}"):
        info_grid([
            ("Status", status),
            ("Occurred", str(interaction.get("occurred_at") or "n/a")),
            ("AI provider", interaction.get("ai_provider") or "n/a"),
            ("AI model", interaction.get("ai_model") or "n/a"),
        ])
        if status == "failed":
            st.error(interaction.get("error_message") or "Processing failed.")
            return
        st.markdown("**Summary**")
        st.write(interaction.get("summary") or "No summary generated.")

        points = interaction.get("discussion_points") or []
        if points:
            st.markdown("**Discussion points**")
            for point in points:
                st.write(f"- {point}")

        risks = interaction.get("risks") or []
        if risks:
            st.markdown("**Risks**")
            for risk in risks:
                st.write(f"- ⚠️ {risk}")

        actions = interaction.get("action_items") or []
        if actions:
            st.markdown("**Action items**")
            for action in actions:
                if isinstance(action, dict):
                    text = action.get("task") or action.get("action") or str(action)
                    owner = action.get("owner")
                    due = action.get("due_date")
                    suffix = " · ".join(v for v in (owner and f"Owner: {owner}", due and f"Due: {due}") if v)
                    st.write(f"- {text}" + (f" ({suffix})" if suffix else ""))
                else:
                    st.write(f"- {action}")

        if interaction.get("next_step"):
            st.markdown("**Next step**")
            st.write(interaction["next_step"])

        if interaction.get("transcript_text"):
            with st.expander("View transcript", key=f"{key_prefix}_transcript_expander_{interaction_id}"):
                st.text_area(
                    "Transcript",
                    interaction["transcript_text"],
                    height=220,
                    disabled=True,
                    key=f"{key_prefix}_transcript_{interaction.get('interaction_id', id(interaction))}",
                    label_visibility="collapsed",
                )


def _render_summarize() -> None:
    with st.container(border=True):
        card_title("Summarize a call or meeting", "CONVERSATION INTELLIGENCE")
        leads = fetch_crm_records_api(search=None)
        lead_options = {}
        if leads:
            for row in leads:
                if row.get("lead_id"):
                    label = f"#{row['lead_id']} · {row.get('contact_name') or row.get('company_name')} · {row.get('company_name')}"
                    lead_options[label] = row["lead_id"]
        lead_options["No specific contact"] = None

        c1, c2 = st.columns(2)
        interaction_type = c1.selectbox("Interaction type", ["Call", "Meeting", "Email", "Note"])
        subject = c2.text_input("Subject", placeholder="Discovery call with decision maker")
        lead_label = st.selectbox("Contact / lead", list(lead_options))

        providers = fetch_llm_providers_api()
        provider_options = ["auto"]
        if isinstance(providers, dict):
            provider_options.extend(
                name for name, details in providers.items()
                if name != "preferred_provider" and isinstance(details, dict) and details.get("available")
            )
        preferred_provider = st.selectbox("AI provider", provider_options)
        transcript = st.text_area(
            "Transcript",
            height=260,
            placeholder="Paste the meeting or call transcript here…",
        )
        if st.button("Generate summary", type="primary", width="stretch", key="summarize_transcript"):
            if not transcript.strip():
                st.error("Transcript text is required.")
            else:
                with st.spinner("Conversation agent is extracting the summary and action items…"):
                    ok, result = summarize_interaction_api(
                        transcript_text=transcript.strip(),
                        lead_id=lead_options[lead_label],
                        interaction_type=interaction_type.lower(),
                        subject=subject.strip() or None,
                        preferred_provider=None if preferred_provider == "auto" else preferred_provider,
                    )
                if ok:
                    st.session_state["latest_interaction"] = result
                    st.toast("Call summary created.", icon="✅")
                    st.rerun()
                else:
                    st.error(str(result))

    latest = st.session_state.get("latest_interaction")
    if isinstance(latest, dict):
        with st.container(border=True):
            card_title("Latest summary", f"Interaction #{latest.get('interaction_id')}")
            _render_interaction(latest, key_prefix="latest")


def render_crm_conversations() -> None:
    page_header("CRM & Conversation Intelligence",
                "View synced HubSpot and Salesforce contacts, and turn call transcripts into summaries and action items.")
    _provider_controls()
    contacts_tab, activity_tab, summarize_tab = st.tabs(["🔗 Synced contacts", "📝 Interaction feed", "🎙️ Summarize transcript"])
    with contacts_tab:
        _render_synced_contacts()
    with activity_tab:
        interactions = fetch_interactions_api(limit=100)
        if interactions is None:
            backend_error("conversation interactions")
        elif not interactions:
            empty_state("📝", "No interactions yet", "Summarize a transcript to create the first call or meeting record.")
        else:
            for interaction in interactions:
                with st.container(border=True):
                    _render_interaction(
                        interaction,
                        expanded=False,
                        key_prefix=f"feed_{interaction.get('interaction_id', id(interaction))}",
                    )
    with summarize_tab:
        _render_summarize()
