import httpx
import pytest

from backend.crm.salesforce_client import SalesforceAPIError, SalesforceClient
from modules.module5_crm import map_salesforce_lead


def test_salesforce_client_authenticates_and_paginates():
    paths: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        paths.append(request.url.path)
        if request.url.path.endswith("/oauth2/token"):
            return httpx.Response(
                200,
                json={
                    "access_token": "access-token",
                    "instance_url": "https://example.salesforce.com",
                },
                request=request,
            )
        if request.url.path.endswith("/query"):
            return httpx.Response(
                200,
                json={
                    "done": False,
                    "records": [{"Id": "lead-1", "Email": "one@example.com"}],
                    "nextRecordsUrl": "/services/data/v60.0/query/next-1",
                },
                request=request,
            )
        return httpx.Response(
            200,
            json={
                "done": True,
                "records": [{"Id": "lead-2", "Email": "two@example.com"}],
            },
            request=request,
        )

    client = SalesforceClient(
        "consumer-key",
        "consumer-secret",
        login_url="https://login.salesforce.com",
        client=httpx.Client(transport=httpx.MockTransport(handler)),
    )
    try:
        leads = client.list_leads(max_records=2)
    finally:
        client.close()

    assert [lead["Id"] for lead in leads] == ["lead-1", "lead-2"]
    assert paths == [
        "/services/oauth2/token",
        "/services/data/v60.0/query",
        "/services/data/v60.0/query/next-1",
    ]


def test_salesforce_client_reports_authentication_failure():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(400, text="invalid client", request=request)

    client = SalesforceClient(
        "consumer-key",
        "consumer-secret",
        client=httpx.Client(transport=httpx.MockTransport(handler)),
    )
    try:
        with pytest.raises(SalesforceAPIError) as error:
            client.test_connection()
    finally:
        client.close()

    assert error.value.status_code == 400
    assert "invalid client" in str(error.value)


def test_salesforce_client_falls_back_to_contacts_when_leads_are_unavailable():
    queries: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/oauth2/token"):
            return httpx.Response(
                200,
                json={
                    "access_token": "access-token",
                    "instance_url": "https://example.salesforce.com",
                },
                request=request,
            )
        query = request.url.params["q"]
        queries.append(query)
        if "FROM Lead" in query:
            return httpx.Response(
                400,
                json=[{"errorCode": "INVALID_TYPE", "message": "Lead unsupported"}],
                request=request,
            )
        return httpx.Response(
            200,
            json={"done": True, "records": [{"Id": "contact-1"}]},
            request=request,
        )

    client = SalesforceClient(
        "consumer-key",
        "consumer-secret",
        client=httpx.Client(transport=httpx.MockTransport(handler)),
    )
    try:
        result = client.test_connection()
    finally:
        client.close()

    assert result["object_type"] == "Contact"
    assert queries[0].startswith("SELECT Id FROM Lead")
    assert "FROM Contact" in queries[1]


def test_map_salesforce_lead_normalizes_salesgenie_fields():
    mapped = map_salesforce_lead(
        {
            "Id": "00Q123",
            "Company": "Example Corp",
            "FirstName": "Jane",
            "LastName": "Doe",
            "Email": "BUYER@example.com",
            "Status": "Working",
            "City": "Pune",
            "State": "MH",
        }
    )

    assert mapped["email"] == "buyer@example.com"
    assert mapped["contact_name"] == "Jane Doe"
    assert mapped["lead_status"] == "Qualified"
    assert mapped["location"] == "Pune, MH"


def test_map_salesforce_lead_rejects_leads_without_email():
    with pytest.raises(ValueError, match="has no email"):
        map_salesforce_lead({"Id": "00Q123", "Company": "Example Corp"})
