from frontend.components.scoring_hub import _sync_selected_lead


def test_scoring_hub_moves_selection_to_first_visible_lead_after_filtering():
    state = {"selected_lead_id": 1}
    visible_queue = [{"lead_id": 2}, {"lead_id": 3}]

    _sync_selected_lead(state, visible_queue)

    assert state["selected_lead_id"] == 2


def test_scoring_hub_clears_selection_when_filter_has_no_matches():
    state = {"selected_lead_id": 1}

    _sync_selected_lead(state, [])

    assert "selected_lead_id" not in state
