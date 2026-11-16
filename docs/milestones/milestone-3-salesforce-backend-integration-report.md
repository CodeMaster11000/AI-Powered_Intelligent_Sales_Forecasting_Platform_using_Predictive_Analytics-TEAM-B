# Milestone 3 Salesforce Backend Integration Report

**Scope:** Backend-only Salesforce client-credentials integration  
**Status:** Implemented  

## 1. What is implemented

The backend now supports:

- Salesforce OAuth 2.0 Client Credentials authentication.
- Dynamic use of the `instance_url` returned by Salesforce.
- SOQL retrieval of Salesforce Lead records.
- `nextRecordsUrl` pagination.
- Salesforce Lead to SalesGenie field normalization.
- Local lead upsert by normalized email.
- Provider identity persistence in `crm_records`.
- Sync-run accounting in `crm_sync_logs`.

The implementation assumes the Salesforce External Client App/Connected App has Client Credentials Flow enabled, the `api` scope granted, and a Run-As User configured. Consumer key and secret alone are not used directly against CRM records; they are exchanged for a short-lived access token first. The adapter first tries `Lead`; if Salesforce reports that `Lead` is unsupported for the configured org/user, it falls back to `Contact`.

## 2. Required environment

The backend container receives these values from [docker-compose.yml](../../docker-compose.yml):

```dotenv
SALESFORCE_CONSUMER_KEY=...
SALESFORCE_CONSUMER_SECRET=...
SALESFORCE_LOGIN_URL=https://login.salesforce.com
SALESFORCE_API_VERSION=v60.0
CRM_REQUEST_TIMEOUT=15
```

For a Salesforce sandbox, use the sandbox login URL instead:

```dotenv
SALESFORCE_LOGIN_URL=https://test.salesforce.com
```

The consumer secret is never returned by an endpoint, written to the database, or included in sync logs. The database connection stores only the reference string:

```text
SALESFORCE_CONSUMER_KEY/SALESFORCE_CONSUMER_SECRET
```

## 3. Authentication flow

```text
SALESFORCE_LOGIN_URL
    |
    | POST /services/oauth2/token
    | grant_type=client_credentials
    | client_id + client_secret
    v
Salesforce token response
    |
    +--> access_token (in-memory only)
    +--> instance_url
    v
GET {instance_url}/services/data/{api_version}/query
```

The client does not require `SALESFORCE_INSTANCE_URL` because Salesforce returns it during authentication. It also does not use username/password/security-token authentication.

## 4. Backend endpoints

### Test Salesforce connection

```http
POST /api/crm/salesforce/test
```

This authenticates and runs:

```sql
SELECT Id FROM Lead LIMIT 1
```

If `Lead` is unavailable, the endpoint retries with `Contact` and returns `"object_type": "Contact"`.

Successful response:

```json
{
  "provider": "salesforce",
  "connected": true,
  "lead_count_sample": 1
}
```

Authentication/API failures return `502`; missing local configuration returns `503`. No token or Salesforce response payload is returned.

### Synchronize Salesforce Leads or Contacts

```http
POST /api/crm/salesforce/sync
Content-Type: application/json

{
  "max_records": 100
}
```

`max_records` defaults to 100 and is capped at 5,000. The response uses the same sync result contract as HubSpot:

```json
{
  "sync_run_id": "uuid",
  "status": "succeeded",
  "records_read": 10,
  "records_created": 8,
  "records_updated": 2,
  "records_failed": 0
}
```

## 5. Salesforce-to-SalesGenie mapping

| Salesforce Lead field | SalesGenie field | Behavior |
|---|---|---|
| `Id` | `crm_records.provider_record_id` | Stable Salesforce identity |
| `Email` | `leads.email` | Case-normalized upsert key |
| `FirstName` + `LastName` | `leads.contact_name` | Joined into one display name |
| `Company` or `Account.Name` | `leads.company_name` | Contacts use the related Account name; otherwise falls back to the provider record ID |
| `Title` | `leads.contact_title` | Direct mapping |
| `Phone` | `leads.phone` | Direct mapping |
| `Industry` | `leads.industry` | Direct mapping |
| `NumberOfEmployees` | `leads.company_size` | Converted to text |
| `AnnualRevenue` | `leads.annual_revenue` | Converted to text |
| `City` + `State` or `MailingCity` + `MailingState` | `leads.location` | Joined as `City, State` |
| `Status` | `leads.lead_status` | Lead statuses normalized; Salesforce Contacts default to `New Leads` |
| — | `leads.source` | Always `CRM` for this ingestion path |
| Full Salesforce record | `crm_records.provider_payload` | Last provider snapshot |

Leads without email are rejected from local ingestion because the existing SalesGenie Lead contract requires an email. They are counted as failed records.

## 6. Try the integration

1. Confirm the External Client App has:
   - OAuth enabled.
   - Client Credentials Flow enabled.
   - `api` scope.
   - A Run-As User with API access.
2. Ensure the values exist in the host `.env`.
3. Recreate the backend so Docker receives updated values:

   ```bash
   docker compose up -d --force-recreate backend
   ```

4. Verify presence without exposing values:

   ```bash
   docker compose exec backend sh -c \
     'test -n "$SALESFORCE_CONSUMER_KEY" && test -n "$SALESFORCE_CONSUMER_SECRET" && echo configured'
   ```

5. Test authentication and API access:

   ```bash
   curl -X POST http://localhost:8000/api/crm/salesforce/test
   ```

6. Pull a bounded batch:

   ```bash
   curl -X POST http://localhost:8000/api/crm/salesforce/sync \
     -H 'Content-Type: application/json' \
     -d '{"max_records":25}'
   ```

## 7. Expected setup errors

| Response/error | Likely cause |
|---|---|
| `SALESFORCE_CONSUMER_KEY ... not configured` | Docker container was not recreated after editing `.env`, or variable names differ |
| `invalid_client_id` / `invalid client` | Wrong consumer key or app not enabled |
| `unsupported_grant_type` | Client Credentials Flow is not enabled or configured for the app |
| `invalid_grant` / Run-As error | No valid Run-As User or the user lacks API permission |
| `INVALID_SESSION_ID` | Token exchange succeeded but the session is not authorized for the requested API |
| `INVALID_TYPE` for `Lead` | The Run-As user/org does not expose Leads; this implementation automatically retries with Contacts |
| `424` standard Lead/Contact unavailable | OAuth succeeded, but the Run-As user/org exposes neither standard CRM object; grant object/API access or use a CRM-enabled Salesforce org |
| `INVALID_FIELD` | Salesforce org lacks one of the selected standard fields or API version is incompatible |
| `REQUEST_LIMIT_EXCEEDED` | Salesforce daily API allocation was exceeded |

## 8. Validation

The adapter has mocked tests covering:

- Token exchange and dynamic instance URL usage.
- Salesforce query pagination.
- Authentication failure propagation.
- Lead field normalization.
- Missing-email rejection.

Run:

```bash
pytest -q backend/tests/test_salesforce_client.py backend/tests/test_hubspot_client.py
```

The real Salesforce probe should be run manually with the configured org because it authenticates against your account and reads live Lead data.
