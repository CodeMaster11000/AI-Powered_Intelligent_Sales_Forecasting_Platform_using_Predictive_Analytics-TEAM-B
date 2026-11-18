import os
from dataclasses import dataclass
from typing import Any

import httpx


SALESFORCE_LOGIN_URL = "https://login.salesforce.com"
SALESFORCE_API_VERSION = "v60.0"
SALESFORCE_LEAD_FIELDS = (
    "Id,Company,FirstName,LastName,Title,Email,Phone,Status,LeadSource,"
    "NumberOfEmployees,AnnualRevenue,City,State,Industry"
)
SALESFORCE_CONTACT_FIELDS = (
    "Id,FirstName,LastName,Title,Email,Phone,Department,"
    "MailingCity,MailingState,Account.Name"
)


class SalesforceAPIError(RuntimeError):
    def __init__(self, status_code: int, message: str):
        super().__init__(message)
        self.status_code = status_code


@dataclass(frozen=True)
class SalesforceQueryPage:
    records: list[dict[str, Any]]
    next_records_url: str | None
    done: bool


class SalesforceClient:
    def __init__(
        self,
        consumer_key: str,
        consumer_secret: str,
        *,
        login_url: str = SALESFORCE_LOGIN_URL,
        api_version: str = SALESFORCE_API_VERSION,
        timeout: float = 15.0,
        client: httpx.Client | None = None,
    ):
        if not consumer_key.strip() or not consumer_secret.strip():
            raise ValueError("Salesforce consumer key and secret are required.")
        self._consumer_key = consumer_key
        self._consumer_secret = consumer_secret
        normalized_login_url = login_url.strip()
        if not normalized_login_url.startswith(("http://", "https://")):
            normalized_login_url = f"https://{normalized_login_url}"
        self._login_url = normalized_login_url.rstrip("/")
        self._api_version = api_version
        self.object_type = "Lead"
        self._client = client
        self._owned_client = client is None
        self._http = client or httpx.Client(timeout=timeout)
        self._access_token: str | None = None
        self._instance_url: str | None = None

    def close(self) -> None:
        if self._owned_client:
            self._http.close()

    def __enter__(self) -> "SalesforceClient":
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        self.close()

    def authenticate(self) -> None:
        try:
            response = self._http.post(
                f"{self._login_url}/services/oauth2/token",
                data={
                    "grant_type": "client_credentials",
                    "client_id": self._consumer_key,
                    "client_secret": self._consumer_secret,
                },
            )
        except httpx.RequestError as exc:
            raise SalesforceAPIError(
                503, f"Salesforce authentication request failed: {exc}"
            ) from exc

        if response.is_error:
            raise SalesforceAPIError(
                response.status_code,
                response.text[:500] or "Salesforce authentication failed.",
            )
        try:
            payload = response.json()
        except ValueError as exc:
            raise SalesforceAPIError(
                502, "Salesforce returned a non-JSON authentication response."
            ) from exc

        token = str(payload.get("access_token") or "").strip()
        instance_url = str(payload.get("instance_url") or "").strip().rstrip("/")
        if not token or not instance_url:
            raise SalesforceAPIError(
                502,
                "Salesforce authentication response did not include access_token "
                "and instance_url.",
            )
        self._access_token = token
        self._instance_url = instance_url

    def test_connection(self) -> dict[str, Any]:
        self._ensure_authenticated()
        payload = self._query_object("Lead", "Id", limit=1)
        return {
            "connected": True,
            "lead_count_sample": len(payload.get("records", [])),
            "object_type": self.object_type,
        }

    def list_leads(
        self, *, page_size: int = 200, max_records: int = 500
    ) -> list[dict[str, Any]]:
        if not 1 <= page_size <= 2000:
            raise ValueError("Salesforce page_size must be between 1 and 2000.")
        if max_records < 1:
            raise ValueError("Salesforce max_records must be positive.")

        self._ensure_authenticated()
        fields = (
            SALESFORCE_LEAD_FIELDS
            if self.object_type == "Lead"
            else SALESFORCE_CONTACT_FIELDS
        )
        payload = self._query_object(
            self.object_type, fields, limit=max_records, order_by="LastModifiedDate"
        )
        page = SalesforceQueryPage(
            records=payload.get("records", []),
            next_records_url=payload.get("nextRecordsUrl"),
            done=bool(payload.get("done", True)),
        )
        records = list(page.records)
        while not page.done and page.next_records_url and len(records) < max_records:
            payload = self._request("GET", page.next_records_url)
            page = SalesforceQueryPage(
                records=payload.get("records", []),
                next_records_url=payload.get("nextRecordsUrl"),
                done=bool(payload.get("done", True)),
            )
            records.extend(page.records)
        return records[:max_records]

    def update_record(
        self, object_type: str, record_id: str, fields: dict[str, Any]
    ) -> dict[str, Any]:
        if object_type not in {"Lead", "Contact"}:
            raise ValueError("Salesforce object type must be Lead or Contact.")
        if not record_id.strip():
            raise ValueError("Salesforce record ID cannot be empty.")
        if not fields:
            raise ValueError("Salesforce record update fields cannot be empty.")
        return self._request(
            "PATCH",
            f"/services/data/{self._api_version}/sobjects/{object_type}/{record_id}",
            json=fields,
        )

    def _query_object(
        self,
        object_type: str,
        fields: str,
        *,
        limit: int,
        order_by: str | None = None,
    ) -> dict[str, Any]:
        query = f"SELECT {fields} FROM {object_type}"
        if order_by:
            query += f" ORDER BY {order_by} DESC"
        query += f" LIMIT {limit}"
        try:
            return self._request(
                "GET",
                f"/services/data/{self._api_version}/query",
                params={"q": query},
            )
        except SalesforceAPIError as exc:
            if object_type == "Lead" and exc.status_code == 400 and "INVALID_TYPE" in str(exc):
                self.object_type = "Contact"
                try:
                    return self._request(
                        "GET",
                        f"/services/data/{self._api_version}/query",
                        params={
                            "q": f"SELECT {SALESFORCE_CONTACT_FIELDS} FROM Contact"
                            f" ORDER BY LastModifiedDate DESC LIMIT {limit}"
                        },
                    )
                except SalesforceAPIError as contact_exc:
                    if contact_exc.status_code == 400 and "INVALID_TYPE" in str(
                        contact_exc
                    ):
                        raise SalesforceAPIError(
                            424,
                            "Salesforce OAuth succeeded, but this org/user does "
                            "not expose the standard Lead or Contact sObjects. "
                            "Grant API/object access to the Run-As User or use a "
                            "Salesforce org with CRM objects enabled.",
                        ) from contact_exc
                    raise
            raise

    def _ensure_authenticated(self) -> None:
        if self._access_token is None or self._instance_url is None:
            self.authenticate()

    def _request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        if self._access_token is None or self._instance_url is None:
            raise RuntimeError("Salesforce client is not authenticated.")
        url = path if path.startswith("http") else f"{self._instance_url}{path}"
        headers = {"Authorization": f"Bearer {self._access_token}", "Accept": "application/json"}
        try:
            response = self._http.request(method, url, headers=headers, **kwargs)
        except httpx.RequestError as exc:
            raise SalesforceAPIError(503, f"Salesforce request failed: {exc}") from exc
        if response.is_error:
            raise SalesforceAPIError(
                response.status_code,
                response.text[:500] or "Salesforce returned an error.",
            )
        if response.status_code == 204:
            return {}
        try:
            return response.json()
        except ValueError as exc:
            raise SalesforceAPIError(
                502, "Salesforce returned a non-JSON response."
            ) from exc


def build_salesforce_client() -> SalesforceClient:
    consumer_key = os.getenv("SALESFORCE_CONSUMER_KEY")
    consumer_secret = os.getenv("SALESFORCE_CONSUMER_SECRET")
    if not consumer_key or not consumer_secret:
        raise RuntimeError(
            "SALESFORCE_CONSUMER_KEY and SALESFORCE_CONSUMER_SECRET are not configured."
        )
    return SalesforceClient(
        consumer_key,
        consumer_secret,
        login_url=os.getenv("SALESFORCE_LOGIN_URL", SALESFORCE_LOGIN_URL),
        api_version=os.getenv("SALESFORCE_API_VERSION", SALESFORCE_API_VERSION),
        timeout=float(os.getenv("CRM_REQUEST_TIMEOUT", "15")),
    )
