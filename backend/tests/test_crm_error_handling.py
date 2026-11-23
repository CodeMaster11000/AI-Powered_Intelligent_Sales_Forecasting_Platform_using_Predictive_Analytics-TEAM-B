import pytest

from backend.crm.hubspot_client import HubSpotAPIError
from backend.crm.salesforce_client import SalesforceAPIError
from backend.main import crm_http_exception


@pytest.mark.parametrize(
    ("error", "expected_status"),
    [
        (HubSpotAPIError(404, "contact not found"), 404),
        (HubSpotAPIError(429, "rate limited"), 429),
        (SalesforceAPIError(401, "invalid session"), 401),
        (SalesforceAPIError(503, "service unavailable"), 503),
        (SalesforceAPIError(500, "provider failure"), 502),
    ],
)
def test_crm_errors_preserve_actionable_statuses(error, expected_status):
    response = crm_http_exception(error)

    assert response.status_code == expected_status
    assert response.detail == str(error)
