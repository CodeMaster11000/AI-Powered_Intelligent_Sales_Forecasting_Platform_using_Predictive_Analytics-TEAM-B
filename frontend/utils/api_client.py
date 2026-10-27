import os
import requests

API_BASE_URL = os.environ.get("BACKEND_API_URL", "http://localhost:8000")


def check_backend_health() -> bool:
    """Verifies whether the FastAPI server is reachable."""
    try:
        res = requests.get(f"{API_BASE_URL}/health", timeout=1.5)
        return res.status_code == 200
    except requests.RequestException:
        return False


def fetch_pipeline_stats() -> dict:
    """Fetches high-level metrics for the header KPI cards."""
    try:
        res = requests.get(f"{API_BASE_URL}/api/leads/stats", timeout=2.0)
        if res.status_code == 200:
            return res.json()
    except requests.RequestException:
        pass
    return {"total_leads": 0, "session_additions": 0, "ingestion_health": 98.4, "pending_ai_scoring": 0}


def fetch_users() -> list[dict]:
    """Retrieves available sales reps for lead owner assignment."""
    try:
        res = requests.get(f"{API_BASE_URL}/api/users", timeout=2.0)
        if res.status_code == 200:
            return res.json()
    except requests.RequestException:
        pass
    return [{"user_id": 1, "name": "Alex Rep", "role": "Sales Representative"}]


def create_lead_api(payload: dict) -> tuple[bool, dict | str]:
    """Creates a single prospect lead in PostgreSQL.
    
    Returns (True, lead_data_dict) on success, or (False, error_message) on failure.
    """
    try:
        res = requests.post(f"{API_BASE_URL}/api/leads", json=payload, timeout=4.0)
        if res.status_code in (200, 201):
            return True, res.json()
        error_detail = res.json().get("detail", res.text)
        return False, error_detail
    except requests.exceptions.ConnectionError:
        return False, "Backend is offline. Start FastAPI backend with 'uvicorn backend.main:app --reload'."
    except requests.RequestException as e:
        return False, f"Request failed: {e}"


def bulk_import_api(leads: list[dict], skip_duplicates: bool = True) -> tuple[bool, dict | str]:
    """Imports and validates a batch of prospect records."""
    try:
        payload = {"leads": leads, "skip_duplicates": skip_duplicates}
        res = requests.post(f"{API_BASE_URL}/api/leads/bulk", json=payload, timeout=12.0)
        if res.status_code in (200, 201):
            return True, res.json()
        error_detail = res.json().get("detail", res.text)
        return False, error_detail
    except requests.exceptions.ConnectionError:
        return False, "Backend is offline. Start FastAPI backend with 'uvicorn backend.main:app --reload'."
    except requests.RequestException as e:
        return False, f"Import network error: {e}"


def fetch_leads_api(search: str | None = None, source: str | None = None) -> list[dict]:
    """Queries stored leads with search and source filters."""
    try:
        params = {}
        if search:
            params["search"] = search.strip()
        if source and source != "All Sources":
            params["source"] = source
        res = requests.get(f"{API_BASE_URL}/api/leads", params=params, timeout=3.0)
        if res.status_code == 200:
            return res.json()
    except requests.RequestException:
        pass
    return []


def fetch_scoring_queue_api() -> list[dict]:
    """Retrieves all leads formatted for the Scoring Master Queue."""
    try:
        res = requests.get(f"{API_BASE_URL}/api/scoring/queue", timeout=3.0)
        if res.status_code == 200:
            return res.json()
    except requests.RequestException:
        pass
    return []


def fetch_lead_dossier_api(lead_id: int) -> dict | None:
    """Retrieves the full AI dossier, score breakdown, and company insights for a lead."""
    try:
        res = requests.get(f"{API_BASE_URL}/api/leads/{lead_id}/dossier", timeout=4.0)
        if res.status_code == 200:
            return res.json()
    except requests.RequestException:
        pass
    return None


def score_lead_api(lead_id: int) -> tuple[bool, dict | str]:
    """Triggers predictive scoring and company intelligence generation for a lead."""
    try:
        res = requests.post(f"{API_BASE_URL}/api/leads/{lead_id}/score", timeout=6.0)
        if res.status_code in (200, 201):
            return True, res.json()
        error_detail = res.json().get("detail", res.text)
        return False, error_detail
    except requests.RequestException as e:
        return False, f"Scoring service error: {e}"


def batch_score_api() -> int:
    """Triggers batch scoring for all currently unscored leads."""
    try:
        res = requests.post(f"{API_BASE_URL}/api/leads/score-batch", timeout=15.0)
        if res.status_code == 200:
            return res.json().get("scored_count", 0)
    except requests.RequestException:
        pass
    return 0


def generate_outreach_api(
    lead_id: int,
    angle: str,
    tone: str,
    custom_note: str = "",
    preferred_provider: str | None = None,
) -> dict | None:
    """Generates targeted email subject variants and body drafts via AI Outreach Agent."""
    try:
        payload = {
            "lead_id": lead_id,
            "angle": angle,
            "tone": tone,
            "custom_note": custom_note,
            "preferred_provider": preferred_provider,
        }
        res = requests.post(f"{API_BASE_URL}/api/outreach/generate", json=payload, timeout=25.0)
        if res.status_code == 200:
            return res.json()
    except requests.RequestException:
        pass
    return None


def fetch_llm_providers_api() -> dict:
    """Fetches real-time status of configured LLM providers (Gemini, OpenAI, Grok, Ollama)."""
    try:
        res = requests.get(f"{API_BASE_URL}/api/llm/providers", timeout=2.0)
        if res.status_code == 200:
            return res.json()
    except requests.RequestException:
        pass
    return {
        "gemini": {"available": False, "model": "gemini-1.5-pro"},
        "openai": {"available": False, "model": "gpt-4o-mini"},
        "grok": {"available": False, "model": "grok-2-latest"},
        "ollama": {"available": False, "model": "llama3"},
        "preferred_provider": "auto",
        "last_used_provider": None,
    }


def save_outreach_draft_api(lead_id: int, subject: str, body: str) -> tuple[bool, str]:
    """Persists a customized outreach email draft."""
    try:
        payload = {"lead_id": lead_id, "subject": subject, "body": body, "status": "draft"}
        res = requests.post(f"{API_BASE_URL}/api/outreach/save-draft", json=payload, timeout=4.0)
        if res.status_code in (200, 201):
            return True, "Draft saved successfully!"
        return False, res.json().get("detail", "Draft could not be saved.")
    except requests.RequestException:
        return False, "Draft could not be saved because the backend is unavailable."


def send_outreach_email_api(lead_id: int, subject: str, body: str) -> tuple[bool, str]:
    """Dispatches cold outreach email and logs interaction status."""
    try:
        payload = {"lead_id": lead_id, "subject": subject, "body": body}
        res = requests.post(f"{API_BASE_URL}/api/outreach/send", json=payload, timeout=5.0)
        if res.status_code in (200, 201):
            return True, "Outreach email dispatched and interaction logged!"
        return False, "Outreach was not sent."
    except requests.RequestException:
        return False, "Outreach was not sent because the backend is unavailable."


def analyze_lead_api(lead_id: int) -> tuple[bool, dict | str]:
    """Runs the LangGraph intelligence pipeline for a stored lead."""
    try:
        res = requests.post(f"{API_BASE_URL}/api/leads/{lead_id}/analyze", timeout=300.0)
        if res.status_code == 200:
            return True, res.json()
        return False, res.json().get("detail", res.text)
    except requests.RequestException as e:
        return False, f"Analysis service error: {e}"


def fetch_lead_insights_api(lead_id: int) -> dict | None:
    """Retrieves persisted intelligence for a lead."""
    try:
        res = requests.get(f"{API_BASE_URL}/api/leads/{lead_id}/insights", timeout=4.0)
        if res.status_code == 200:
            return res.json()
    except requests.RequestException:
        pass
    return None


def analyze_prospect_ad_hoc_api(payload: dict) -> tuple[bool, dict | str]:
    """Runs intelligence analysis without creating a database lead."""
    try:
        res = requests.post(
            f"{API_BASE_URL}/api/intelligence/analyze-prospect",
            json=payload,
            timeout=300.0,
        )
        if res.status_code == 200:
            return True, res.json()
        return False, res.json().get("detail", res.text)
    except requests.RequestException as e:
        return False, f"Analysis service error: {e}"