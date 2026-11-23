import httpx
import pytest
from unittest.mock import Mock

from backend.crm.hubspot_client import HubSpotAPIError, HubSpotClient
from modules.module5_crm import map_hubspot_contact, sync_hubspot_contacts


def test_hubspot_client_paginates_contacts():
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.url.params.get("after") is None:
            return httpx.Response(
                200,
                json={
                    "results": [{"id": "1", "properties": {"email": "one@example.com"}}],
                    "paging": {"next": {"after": "2"}},
                },
                request=request,
            )
        return httpx.Response(
            200,
            json={"results": [{"id": "2", "properties": {"email": "two@example.com"}}]},
            request=request,
        )

    client = HubSpotClient(
        "test-token",
        client=httpx.Client(
            transport=httpx.MockTransport(handler),
            base_url="https://api.hubapi.com/",
        ),
    )
    try:
        contacts = client.list_contacts(max_records=2)
    finally:
        client.close()

    assert [contact["id"] for contact in contacts] == ["1", "2"]
    assert requests[1].url.params["after"] == "2"
    assert requests[0].headers["Authorization"] == "Bearer test-token"


def test_hubspot_client_reports_provider_errors():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, text="invalid token", request=request)

    client = HubSpotClient(
        "test-token",
        client=httpx.Client(
            transport=httpx.MockTransport(handler),
            base_url="https://api.hubapi.com/",
        ),
    )
    try:
        with pytest.raises(HubSpotAPIError) as error:
            client.test_connection()
    finally:
        client.close()

    assert error.value.status_code == 401
    assert "invalid token" in str(error.value)


def test_hubspot_client_updates_contact():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "PATCH"
        assert request.url.path.endswith("/crm/v3/objects/contacts/42")
        assert request.read() == b'{"properties":{"company":"Example Corp"}}'
        return httpx.Response(200, json={"id": "42"}, request=request)

    client = HubSpotClient(
        "test-token",
        client=httpx.Client(
            transport=httpx.MockTransport(handler),
            base_url="https://api.hubapi.com/",
        ),
    )
    try:
        result = client.update_contact("42", {"company": "Example Corp"})
    finally:
        client.close()

    assert result == {"id": "42"}


def test_map_hubspot_contact_normalizes_salesgenie_fields():
    mapped = map_hubspot_contact(
        {
            "id": "42",
            "properties": {
                "email": "BUYER@example.com",
                "firstname": "Jane",
                "lastname": "Doe",
                "company": "Example Corp",
                "hs_lead_status": "Qualified",
                "city": "Pune",
                "state": "MH",
            },
        }
    )

    assert mapped["email"] == "buyer@example.com"
    assert mapped["contact_name"] == "Jane Doe"
    assert mapped["lead_status"] == "Qualified"
    assert mapped["location"] == "Pune, MH"


def test_map_hubspot_contact_rejects_contacts_without_email():
    with pytest.raises(ValueError, match="has no email"):
        map_hubspot_contact({"id": "42", "properties": {}})


@pytest.mark.parametrize("max_records", [0, 5001, -1])
def test_hubspot_sync_rejects_out_of_range_batch_sizes(max_records):
    with pytest.raises(ValueError, match="between 1 and 5000"):
        sync_hubspot_contacts(Mock(), Mock(), max_records=max_records)
