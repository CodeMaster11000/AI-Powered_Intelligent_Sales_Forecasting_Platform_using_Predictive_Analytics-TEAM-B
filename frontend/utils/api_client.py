import os
import requests

API_BASE_URL = os.environ.get("BACKEND_API_URL", "http://localhost:8000")


def check_backend_health() -> bool:
    try:
        res = requests.get(f"{API_BASE_URL}/health", timeout=1.5)
        return res.status_code == 200
    except requests.RequestException:
        return False


def fetch_pipeline_stats() -> dict:
    try:
        res = requests.get(f"{API_BASE_URL}/api/leads/stats", timeout=2.0)
        if res.status_code == 200:
            return res.json()
    except requests.RequestException:
        pass
    return {"total_leads": 0, "session_additions": 0, "ingestion_health": 98.4, "pending_ai_scoring": 0}


def fetch_users() -> list[dict]:
    try:
        res = requests.get(f"{API_BASE_URL}/api/users", timeout=2.0)
        if res.status_code == 200:
            return res.json()
    except requests.RequestException:
        pass
    return [{"user_id": 1, "name": "Alex Rep (Dev Mode)", "role": "Sales Representative"}]


def create_lead_api(payload: dict) -> tuple[bool, str]:
    try:
        res = requests.post(f"{API_BASE_URL}/api/leads", json=payload, timeout=3.0)
        if res.status_code == 201:
            return True, "Lead saved to database successfully!"
        error_detail = res.json().get("detail", res.text)
        return False, error_detail
    except requests.RequestException as e:
        return False, f"Could not connect to backend: {e}"


def bulk_import_api(leads: list[dict], skip_duplicates: bool = True) -> tuple[bool, dict | str]:
    try:
        payload = {"leads": leads, "skip_duplicates": skip_duplicates}
        res = requests.post(f"{API_BASE_URL}/api/leads/bulk", json=payload, timeout=10.0)
        if res.status_code == 201:
            return True, res.json()
        error_detail = res.json().get("detail", res.text)
        return False, error_detail
    except requests.RequestException as e:
        return False, f"Could not connect to backend: {e}"


def fetch_leads_api(search: str | None = None, source: str | None = None) -> list[dict]:
    try:
        params = {}
        if search:
            params["search"] = search
        if source and source != "All Sources":
            params["source"] = source
        res = requests.get(f"{API_BASE_URL}/api/leads", params=params, timeout=3.0)
        if res.status_code == 200:
            return res.json()
    except requests.RequestException:
        pass
    return []