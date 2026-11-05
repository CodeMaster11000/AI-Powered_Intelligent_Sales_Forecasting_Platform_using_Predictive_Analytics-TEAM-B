import streamlit as st


def render_next_best_action(action: dict | None) -> None:
    """Render the recommended follow-up for the selected lead."""
    if not action:
        st.caption("No next best action is available for this lead yet.")
        return

    channels = action.get("channel_mix") or []
    recommended_action = action.get(
        "recommended_action", "Review the lead and choose a follow-up."
    )
    urgency = action.get("urgency", "Standard Pipeline")
    follow_up = action.get("follow_up_timing", "Nurture Track")

    st.markdown(
        """
        <div class="nba-heading">
            <div>
                <div class="nba-kicker">Recommended follow-up</div>
                <h5>Next Best Action</h5>
            </div>
            <span class="nba-badge">AI guidance</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div class='nba-action'>{recommended_action}</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="nba-details">
            <div class="nba-detail">
                <span class="nba-label">Urgency</span>
                <strong>{urgency}</strong>
            </div>
            <div class="nba-detail">
                <span class="nba-label">Follow-up window</span>
                <strong>{follow_up}</strong>
            </div>
            <div class="nba-detail">
                <span class="nba-label">Channels</span>
                <strong>{len(channels)} recommended</strong>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if channels:
        st.markdown("<div class='nba-section-label'>Recommended channel mix</div>", unsafe_allow_html=True)
        for channel in channels:
            st.markdown(f"<div class='nba-channel'><span>→</span>{channel}</div>", unsafe_allow_html=True)

    content_strategy = action.get("content_strategy")
    if content_strategy:
        st.markdown("<div class='nba-section-label'>Content strategy</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='nba-content'>{content_strategy}</div>", unsafe_allow_html=True)
