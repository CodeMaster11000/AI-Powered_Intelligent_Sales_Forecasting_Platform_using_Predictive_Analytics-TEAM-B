import streamlit as st

from frontend.components.ui import backend_error, card_title, chips, empty_state, html, page_header, pill
from frontend.utils.api_client import (
    archive_outreach_draft_api, delete_outreach_draft_api, fetch_llm_providers_api,
    fetch_lead_dossier_api, fetch_outreach_drafts_api, fetch_scoring_queue_api,
    generate_outreach_api, save_outreach_draft_api, send_outreach_email_api,
    update_outreach_draft_api,
)
from frontend.utils.helpers import esc

PROVIDERS = {
    "auto": "🤖 First available provider",
    "gemini": "✨ Google Gemini",
    "openai": "⚡ OpenAI",
    "grok": "🚀 xAI Grok",
    "ollama": "🦙 Local Ollama (private)",
}
ANGLES = [
    "Cloud Scale & Infrastructure Efficiency",
    "Pipeline Variance & Forecasting ROI",
    "Tech Stack Modernization",
    "Operational Cost Reduction & Security",
]
TONES = [
    "Consultative / Executive (Recommended)",
    "Direct & Punchy (Under 100 words)",
    "Problem-Centric / Metric-Driven",
]


def _load_draft_into_state(item: dict, lead_id: int) -> None:
    st.session_state["current_draft"] = {
        "subject_options": item.get("subject_options") or [item.get("subject", "Untitled")],
        "selected_subject": item.get("subject", ""),
        "body": item.get("body", ""),
        "provider_used": item.get("provider") or "Saved draft",
    }
    if item.get("status") == "draft":
        st.session_state["draft_id"] = item.get("id")
    else:
        st.session_state.pop("draft_id", None)
    st.session_state["draft_lead_id"] = lead_id
    st.session_state["draft_version"] = st.session_state.get("draft_version", 0) + 1


def _provider_status(info: dict) -> None:
    items = []
    for key in ("gemini", "openai", "grok", "ollama"):
        p = info.get(key) or {}
        items.append(pill(f"{key.title()} ✓" if p.get("available") else f"{key.title()} ✗",
                          "teal" if p.get("available") else "slate"))
    html("<div class='sg-chips'>" + "".join(items) + "</div>")
    if not any((info.get(k) or {}).get("available") for k in PROVIDERS if k != "auto"):
        html("<div style='height:6px'></div><div class='sg-callout warn'>No AI provider is configured. "
             "Add an API key to <code>.env</code> (or run Ollama) to generate drafts.</div>")


def _strategy_panel(dossier: dict, target_id: int, saved: list[dict]) -> dict:
    """Left column. Returns the controls so the right column can regenerate with them."""
    scoring = dossier.get("scoring") or {}
    prio = (scoring.get("priority") or "unscored").lower()
    kind = {"hot": "hot", "warm": "warm", "cold": "cold"}.get(prio, "none")
    with st.container(border=True):
        card_title("Outreach strategy & engine")
        win = scoring.get("conversion_probability", 0)
        badge = pill(f"{prio.upper()} · {win}% win", kind)
        html(
            f"<div class='sg-callout'><div style='display:flex;justify-content:space-between;gap:8px;align-items:center'>"
            f"<b>Lead score {esc(scoring.get('score'), 'n/a')} / 100</b>{badge}</div></div>"
        )
        html("<div style='height:8px'></div>")

        if saved:
            labels = [
                f"{i.get('status', 'draft').title()} · {(i.get('updated_at') or i.get('created_at') or '')[:16]} · {i.get('subject', 'Untitled')}"
                for i in saved
            ]
            idx = st.selectbox("Saved drafts", range(len(saved)), format_func=lambda n: labels[n])
            if st.button("Load selected draft", width="stretch"):
                _load_draft_into_state(saved[idx], target_id)
                if saved[idx].get("status") != "draft":
                    st.toast("Archived and sent drafts are read-only. Save as a new draft to edit.", icon="ℹ️")
                st.rerun()

        provider_key = st.selectbox("AI model provider", list(PROVIDERS), format_func=PROVIDERS.get,
                                    help="If the chosen provider fails, the next available one is used.")
        angle = st.selectbox("Value angle / hook", ANGLES)
        tone = st.radio("Tone & style", TONES)

        card_title("Detected context")
        stack = dossier.get("tech_stack") or []
        chips([f"Tech: {', '.join(map(str, stack[:3]))}" if stack else "Tech: not detected",
               f"Stage: {dossier.get('funding_stage') or 'n/a'}",
               f"Contact: {dossier.get('contact_title') or 'n/a'}"])
        html("<div style='height:8px'></div>")
        note = st.text_area("Custom rep notes (optional)", height=80,
                            placeholder="e.g. Mention our recent benchmark with similar SaaS teams…")

        with st.expander("AI provider status"):
            _provider_status(fetch_llm_providers_api())

        generate = st.button("✨ Generate draft" if "current_draft" not in st.session_state
                             or st.session_state.get("draft_lead_id") != target_id else "🔄 Regenerate draft",
                             type="primary", width="stretch")
    return {"generate": generate, "provider": provider_key, "angle": angle, "tone": tone, "note": note}


def _editor_panel(target_id: int, controls: dict) -> None:
    draft = st.session_state.get("current_draft")
    has_draft = draft and st.session_state.get("draft_lead_id") == target_id

    if not has_draft:
        with st.container(border=True):
            empty_state("✉️", "No draft yet", "Choose an angle and tone, then press Generate draft. "
                        "Nothing is sent to an AI provider until you do.")
        return

    subject_options = draft.get("subject_options") or [draft.get("selected_subject", "Untitled")]
    provider_used = draft.get("provider_used", "AI")
    saved_id = st.session_state.get("draft_id")

    with st.container(border=True):
        html(
            f"<div style='display:flex;justify-content:space-between;align-items:center;gap:8px;margin-bottom:8px'>"
            f"<div class='sg-card-title' style='margin:0'>Personalized cold email</div>"
            f"{pill('✨ ' + str(provider_used), 'info')}</div>"
        )
        if saved_id:
            html(pill(f"Saved draft #{saved_id}", "teal"))
        default_idx = subject_options.index(draft["selected_subject"]) if draft.get("selected_subject") in subject_options else 0
        subject = st.selectbox("Subject line (A/B variants)", subject_options, index=default_idx)

        v_key = f"draft_body_{target_id}_{st.session_state.get('draft_version', 0)}"
        if v_key not in st.session_state:
            st.session_state[v_key] = draft.get("body", "")
        body = st.text_area("Email body", height=260, key=v_key)

        if draft.get("personalization_triggers"):
            chips([f"🎯 {t}" for t in draft["personalization_triggers"]], "teal")

        words = len(body.split())
        read_s = max(10, round(words / 3.5))
        hook = draft.get("hook_score")
        html(
            "<div class='sg-info-grid' style='margin:12px 0'>"
            f"<div class='sg-info'><span class='sg-eyebrow'>Hook score</span><b>{esc(f'{hook} / 100' if hook is not None else 'n/a')}</b></div>"
            f"<div class='sg-info'><span class='sg-eyebrow'>Words</span><b>{words}</b></div>"
            f"<div class='sg-info'><span class='sg-eyebrow'>Reading time</span><b>~{read_s}s</b></div>"
            f"<div class='sg-info'><span class='sg-eyebrow'>Call to action</span><b>{esc(draft.get('call_to_action'))}</b></div></div>"
        )
        if not body.strip():
            st.warning("The email body is empty.")

        c1, c2, c3 = st.columns([1.3, 1.3, 1.6])
        with c1:
            with st.popover("📋 View / copy", width="stretch"):
                st.caption("Use the copy icon at the top-right of the block.")
                st.code(f"Subject: {subject}\n\n{body}", language="markdown")
        with c2:
            if st.button("💾 Save draft", width="stretch", disabled=not body.strip()):
                if saved_id:
                    ok, msg = update_outreach_draft_api(saved_id, subject, body)
                else:
                    ok, msg = save_outreach_draft_api(target_id, subject, body, {
                        "provider": provider_used, "angle": controls["angle"], "tone": controls["tone"],
                        "custom_note": controls["note"], "subject_options": subject_options})
                    if ok:
                        match = next((d for d in fetch_outreach_drafts_api(target_id)
                                      if d.get("status") == "draft" and d.get("subject") == subject and d.get("body") == body), None)
                        if match:
                            st.session_state["draft_id"] = match.get("id")
                st.toast(msg, icon="💾" if ok else "⚠️")
        with c3:
            confirm_key = f"confirm_send_{target_id}"
            if st.button("🚀 Send email", type="primary", width="stretch", disabled=not body.strip()):
                st.session_state[confirm_key] = True

        if st.session_state.get(confirm_key):
            html("<div class='sg-callout warn'><b>Send this email now?</b> This logs the interaction and cannot be undone.</div>")
            y, n = st.columns(2)
            if y.button("Yes, send", type="primary", width="stretch", key=f"send_yes_{target_id}"):
                ok, msg = send_outreach_email_api(target_id, subject, body, saved_id)
                st.session_state.pop(confirm_key, None)
                st.toast(msg, icon="🚀" if ok else "⚠️")
                st.rerun()
            if n.button("Cancel", width="stretch", key=f"send_no_{target_id}"):
                st.session_state.pop(confirm_key, None)
                st.rerun()

        if saved_id:
            html("<div style='height:4px'></div>")
            a, d, _ = st.columns([1, 1, 2.2])
            if a.button("🗄️ Archive", width="stretch"):
                ok, msg = archive_outreach_draft_api(saved_id)
                st.toast(msg, icon="🗄️" if ok else "⚠️")
                if ok:
                    st.session_state.pop("draft_id", None)
                    st.session_state.pop("current_draft", None)
                    st.rerun()
            if d.button("🗑️ Delete", width="stretch"):
                ok, msg = delete_outreach_draft_api(saved_id)
                st.toast(msg, icon="🗑️" if ok else "⚠️")
                if ok:
                    st.session_state.pop("draft_id", None)
                    st.session_state.pop("current_draft", None)
                    st.rerun()


def render_outreach_studio() -> None:
    page_header("AI Outreach Studio", "Turn prospect intelligence into a personalized cold email you can edit, save and send.")

    queue = fetch_scoring_queue_api()
    if queue is None:
        with st.container(border=True):
            backend_error("leads")
        return
    if not queue:
        with st.container(border=True):
            empty_state("✉️", "No leads available", "Add and score a lead before drafting outreach.")
        return

    labels = {f"{q['company_name']} — {q.get('contact_name', 'Contact')} ({str(q.get('priority', 'unscored')).upper()})": q["lead_id"]
              for q in queue}
    ids = list(labels.values())
    preselect = st.session_state.pop("outreach_target_lead_id", None)
    if preselect in ids:
        st.session_state["outreach_target_select"] = list(labels)[ids.index(preselect)]
    if st.session_state.get("outreach_target_select") not in labels:
        st.session_state["outreach_target_select"] = next(iter(labels))
    label = st.selectbox("Target prospect", list(labels), key="outreach_target_select")
    target_id = labels[label]

    dossier = fetch_lead_dossier_api(target_id)
    if not dossier:
        with st.container(border=True):
            backend_error("the AI dossier for this lead")
        return

    saved = fetch_outreach_drafts_api(target_id)
    active = st.session_state.get("draft_id")
    if active and not any(i.get("id") == active and i.get("status") == "draft" for i in saved):
        st.session_state.pop("draft_id", None)

    # Opening a lead that already has drafts shows the latest one. Nothing is generated automatically.
    if st.session_state.get("draft_lead_id") != target_id:
        st.session_state.pop("current_draft", None)
        st.session_state.pop("draft_id", None)
        if saved:
            _load_draft_into_state(saved[0], target_id)

    left, right = st.columns([1.4, 2.6])
    with left:
        controls = _strategy_panel(dossier, target_id, saved)

    if controls["generate"]:
        with right:
            with st.spinner("AI agent is writing your outreach…"):
                ok, result = generate_outreach_api(target_id, controls["angle"], controls["tone"],
                                                   controls["note"], controls["provider"])
        if ok and isinstance(result, dict):
            st.session_state["current_draft"] = result
            st.session_state.pop("draft_id", None)
            st.session_state["draft_lead_id"] = target_id
            st.session_state["draft_version"] = st.session_state.get("draft_version", 0) + 1
            st.rerun()
        with right:
            st.error(f"The outreach model did not produce a draft: {result}")
        return

    with right:
        _editor_panel(target_id, controls)
