import os
from dataclasses import dataclass
from typing import Any

import httpx


HUBSPOT_API_BASE_URL = "https://api.hubapi.com/"
HUBSPOT_CONTACT_PROPERTIES = (
    "email,firstname,lastname,company,jobtitle,phone,industry,"
    "lifecyclestage,hs_lead_status,numberofemployees,annualrevenue,city,state"
)


class HubSpotAPIError(RuntimeError):
    def __init__(self, status_code: int, message: str):
        super().__init__(message)
        self.status_code = status_code


@dataclass(frozen=True)
class HubSpotPage:
    results: list[dict[str, Any]]
    next_after: str | None


class HubSpotClient:
    def __init__(
        self,
        access_token: str,
        *,
        base_url: str = HUBSPOT_API_BASE_URL,
        timeout: float = 15.0,
        client: httpx.Client | None = None,
    ):
        if not access_token.strip():
            raise ValueError("HubSpot access token cannot be empty.")
        self._client = client
        self._owned_client = client is None
        self._http = client or httpx.Client(
            base_url=base_url.rstrip("/") + "/",
            timeout=timeout,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json",
            },
        )
        if client is not None:
            self._http.headers.update(
                {
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/json",
                }
            )

    def close(self) -> None:
        if self._owned_client:
            self._http.close()

    def __enter__(self) -> "HubSpotClient":
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        self.close()

    def test_connection(self) -> dict[str, Any]:
        response = self._request(
            "GET",
            "crm/v3/objects/contacts",
            params={"limit": 1, "properties": "email"},
        )
        return {
            "connected": True,
            "contact_count_sample": len(response.get("results", [])),
        }

    def list_contacts(self, *, limit: int = 100, max_records: int = 500) -> list[dict[str, Any]]:
        if not 1 <= limit <= 100:
            raise ValueError("HubSpot page limit must be between 1 and 100.")
        if max_records < 1:
            raise ValueError("HubSpot max_records must be positive.")

        contacts: list[dict[str, Any]] = []
        after: str | None = None
        while len(contacts) < max_records:
            params: dict[str, Any] = {
                "limit": min(limit, max_records - len(contacts)),
                "properties": HUBSPOT_CONTACT_PROPERTIES,
            }
            if after is not None:
                params["after"] = after
            payload = self._request(
                "GET", "crm/v3/objects/contacts", params=params
            )
            page = HubSpotPage(
                results=payload.get("results", []),
                next_after=(payload.get("paging") or {})
                .get("next", {})
                .get("after"),
            )
            contacts.extend(page.results)
            if not page.next_after or not page.results:
                break
            after = page.next_after
        return contacts[:max_records]

    def _request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        try:
            response = self._http.request(method, path, **kwargs)
        except httpx.RequestError as exc:
            raise HubSpotAPIError(503, f"HubSpot request failed: {exc}") from exc

        if response.is_error:
            detail = response.text[:500] or "HubSpot returned an error."
            raise HubSpotAPIError(response.status_code, detail)
        try:
            return response.json()
        except ValueError as exc:
            raise HubSpotAPIError(
                502, "HubSpot returned a non-JSON response."
            ) from exc


def build_hubspot_client() -> HubSpotClient:
    access_token = os.getenv("HUBSPOT_SERVICE_KEY") or os.getenv(
        "HUBSPOT_ACCESS_TOKEN"
    )
    if not access_token:
        raise RuntimeError(
            "HUBSPOT_SERVICE_KEY is not configured. Configure a HubSpot "
            "service/private-app bearer token with CRM contact read scope."
        )
    return HubSpotClient(
        access_token,
        base_url=os.getenv("HUBSPOT_API_BASE_URL", HUBSPOT_API_BASE_URL),
        timeout=float(os.getenv("CRM_REQUEST_TIMEOUT", "15")),
    )
