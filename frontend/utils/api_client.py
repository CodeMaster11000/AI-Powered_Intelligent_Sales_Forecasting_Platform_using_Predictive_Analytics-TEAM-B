"""Backend API client for the Streamlit frontend.

Design notes
------------
* Every public function keeps the name used by the original frontend.
* Read endpoints are cached for a few seconds with ``st.cache_data``. Streamlit
  re-runs the whole script on every click; without caching each rerun fired
  6-10 HTTP requests. Failures raise inside the cached helper, so errors are
  never cached.
* Any write clears the read caches so the UI never shows stale data.
* ``None`` means "request failed"; ``[]`` means "worked, nothing there". The
  original client returned ``[]`` for both, so error states could not be shown.
* ``generate_outreach_api`` now returns ``(ok, draft_or_error)`` so the UI can
  show *why* generation failed.
"""
from __future__ import annotations

import os
from typing import Any

import requests
import streamlit as st

API_BASE_URL = os.environ.get("BACKEND_API_URL", "http://localhost:8000").rstrip("/")
OFFLINE_MESSAGE = "Backend is offline. Start the API with 'uvicorn backend.main:app --reload'."


class ApiError(Exception):
    """Raised inside cached readers so failures are not cached."""


def _detail(res: requests.Response) -> str:
    try:
        body = res.json()
    except ValueError:
        return res.text or f"HTTP {res.status_code}"
    detail = body.get("detail", body) if isinstance(body, dict) else body
    if isinstance(detail, list):  # FastAPI validation errors
        return "; ".join(
            f"{'.'.join(str(p) for p in d.get('loc', [])[1:])}: {d.get('msg')}"
            if isinstance(d, dict) else str(d)
            for d in detail
        )
    return str(detail)


def _write(method: str, path: str, *, json: Any = None, timeout: float = 6.0,
           ok_codes: tuple[int, ...] = (200, 201)) -> tuple[bool, Any]:
    """Mutating request -> ``(ok, payload_or_error_message)``."""
    try:
        res = requests.request(method, f"{API_BASE_URL}{path}", json=json, timeout=timeout)
    except requests.exceptions.ConnectionError:
        return False, OFFLINE_MESSAGE
    except requests.RequestException as exc:
        return False, f"Request failed: {exc}"
    if res.status_code in ok_codes:
        clear_caches()
        if res.status_code == 204 or not res.content:
            return True, ""
        try:
            return True, res.json()
        except ValueError:
            return True, ""
    return False, _detail(res)


def clear_caches() -> None:
    """Drop every cached read. Called automatically after each mutation."""
    st.cache_data.clear()


@st.cache_data(ttl=5, show_spinner=False)
def _cached_health() -> bool:
    try:
        return requests.get(f"{API_BASE_URL}/health", timeout=1.5).status_code == 200
    except requests.RequestException as exc:
        raise ApiError(OFFLINE_MESSAGE) from exc


@st.cache_data(ttl=10, show_spinner=False)
def _cached_get(path: str, params_key: tuple = (), timeout: float = 4.0) -> Any:
    try:
        res = requests.get(f"{API_BASE_URL}{path}", params=dict(params_key) or None, timeout=timeout)
    except requests.RequestException as exc:
        raise ApiError(OFFLINE_MESSAGE) from exc
    if res.status_code != 200:
        raise ApiError(_detail(res))
    return res.json()


def _safe_get(path: str, params: dict | None = None, timeout: float = 4.0) -> Any | None:
    try:
        return _cached_get(path, tuple(sorted((params or {}).items())), timeout)
    except ApiError:
        return None


# ------------------------------- System ----------------------------------- #
def check_backend_health() -> bool:
    try:
        return _cached_health()
    except ApiError:
        return False


def fetch_pipeline_stats() -> dict:
    data = _safe_get("/api/leads/stats", timeout=2.0)
    if isinstance(data, dict):
        return data
    return {"total_leads": 0, "session_additions": 0, "ingestion_health": None, "pending_ai_scoring": 0}


def fetch_users() -> list[dict]:
    data = _safe_get("/api/users", timeout=2.0)
    if isinstance(data, list):
        return data
    return [{"user_id": 1, "name": "Alex Rep", "role": "Sales Representative"}]


def fetch_llm_providers_api() -> dict:
    data = _safe_get("/api/llm/providers", timeout=2.0)
    if isinstance(data, dict):
        return data
    return {
        "gemini": {"available": False, "model": "gemini-1.5-pro"},
        "openai": {"available": False, "model": "gpt-4o-mini"},
        "grok": {"available": False, "model": "grok-2-latest"},
        "ollama": {"available": False, "model": "llama3"},
        "preferred_provider": "auto",
        "last_used_provider": None,
    }


# -------------------------------- Leads ----------------------------------- #
def fetch_leads_api(search: str | None = None, source: str | None = None) -> list[dict] | None:
    """Stored leads. ``None`` = backend unreachable, ``[]`` = no matches."""
    params: dict[str, str] = {}
    if search and search.strip():
        params["search"] = search.strip()
    if source and source != "All Sources":
        params["source"] = source
    return _safe_get("/api/leads", params)


def create_lead_api(payload: dict) -> tuple[bool, dict | str]:
    return _write("POST", "/api/leads", json=payload, timeout=5.0)


def update_lead_api(lead_id: int, payload: dict) -> tuple[bool, dict | str]:
    return _write("PUT", f"/api/leads/{lead_id}", json=payload, timeout=5.0)


def delete_lead_api(lead_id: int) -> tuple[bool, str]:
    ok, result = _write("DELETE", f"/api/leads/{lead_id}", ok_codes=(204,), timeout=5.0)
    return ok, "" if ok else str(result)


def bulk_import_api(leads: list[dict], skip_duplicates: bool = True) -> tuple[bool, dict | str]:
    return _write("POST", "/api/leads/bulk",
                  json={"leads": leads, "skip_duplicates": skip_duplicates}, timeout=30.0)


# ------------------------------- Scoring ---------------------------------- #
def fetch_scoring_queue_api() -> list[dict] | None:
    """Scoring queue. ``None`` = backend unreachable, ``[]`` = no leads yet."""
    return _safe_get("/api/scoring/queue")


def fetch_lead_dossier_api(lead_id: int) -> dict | None:
    return _safe_get(f"/api/leads/{lead_id}/dossier")


def score_lead_api(lead_id: int) -> tuple[bool, dict | str]:
    return _write("POST", f"/api/leads/{lead_id}/score", timeout=20.0)


def batch_score_api() -> int:
    ok, result = _write("POST", "/api/leads/score-batch", timeout=60.0)
    return int(result.get("scored_count", 0)) if ok and isinstance(result, dict) else 0


# ------------------------------- Outreach --------------------------------- #
def generate_outreach_api(lead_id: int, angle: str, tone: str, custom_note: str = "",
                          preferred_provider: str | None = None) -> tuple[bool, dict | str]:
    return _write(
        "POST", "/api/outreach/generate",
        json={"lead_id": lead_id, "angle": angle, "tone": tone,
              "custom_note": custom_note, "preferred_provider": preferred_provider},
        timeout=60.0,
    )


def save_outreach_draft_api(lead_id: int, subject: str, body: str,
                            metadata: dict | None = None) -> tuple[bool, str]:
    ok, result = _write(
        "POST", "/api/outreach/save-draft",
        json={"lead_id": lead_id, "subject": subject, "body": body, "status": "draft", **(metadata or {})},
    )
    return (True, "Draft saved.") if ok else (False, str(result) or "Draft could not be saved.")


def fetch_outreach_drafts_api(lead_id: int) -> list[dict]:
    data = _safe_get(f"/api/leads/{lead_id}/drafts")
    return data if isinstance(data, list) else []


def update_outreach_draft_api(draft_id: int, subject: str, body: str) -> tuple[bool, str]:
    ok, result = _write("PATCH", f"/api/outreach/drafts/{draft_id}", json={"subject": subject, "body": body})
    return (True, "Draft updated.") if ok else (False, str(result) or "Draft could not be updated.")


def archive_outreach_draft_api(draft_id: int) -> tuple[bool, str]:
    ok, result = _write("POST", f"/api/outreach/drafts/{draft_id}/archive")
    return (True, "Draft archived.") if ok else (False, str(result) or "Draft could not be archived.")


def delete_outreach_draft_api(draft_id: int) -> tuple[bool, str]:
    ok, result = _write("DELETE", f"/api/outreach/drafts/{draft_id}", ok_codes=(204,))
    return (True, "Draft deleted.") if ok else (False, str(result) or "Draft could not be deleted.")


def send_outreach_email_api(lead_id: int, subject: str, body: str,
                            draft_id: int | None = None) -> tuple[bool, str]:
    ok, result = _write(
        "POST", "/api/outreach/send",
        json={"lead_id": lead_id, "subject": subject, "body": body, "draft_id": draft_id},
    )
    return (True, "Outreach email dispatched and interaction logged.") if ok else (
        False, str(result) or "Outreach was not sent.")


# ----------------------------- Intelligence ------------------------------- #
def analyze_lead_api(lead_id: int) -> tuple[bool, dict | str]:
    return _write("POST", f"/api/leads/{lead_id}/analyze", timeout=300.0)


def fetch_lead_insights_api(lead_id: int) -> dict | None:
    return _safe_get(f"/api/leads/{lead_id}/insights")


def analyze_prospect_ad_hoc_api(payload: dict) -> tuple[bool, dict | str]:
    return _write("POST", "/api/intelligence/analyze-prospect", json=payload, timeout=300.0)
