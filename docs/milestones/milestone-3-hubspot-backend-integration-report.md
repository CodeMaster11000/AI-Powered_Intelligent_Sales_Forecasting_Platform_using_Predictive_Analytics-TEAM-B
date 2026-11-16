# Milestone 3 HubSpot Backend Integration Report

**Scope:** Backend-only HubSpot contact integration  
**Status:** Implemented  

## 1. What is implemented

The backend now supports:

- HubSpot bearer-token connection testing.
- Paginated HubSpot contact retrieval.
- HubSpot contact to SalesGenie lead field normalization.
- Idempotent local lead upsert by email.
- Provider identity persistence in `crm_records`.
- Sync-run accounting in `crm_sync_logs`.
- A reusable `HubSpotClient` that can be replaced with a mocked HTTP client in tests.

The integration is intentionally pull-first and bounded. It does not yet create/update HubSpot records, process activities, receive webhooks, or implement Salesforce authentication.

## 2. Required environment

Add these values to the local `.env` file. Never commit `.env` or print the token:

```dotenv
HUBSPOT_SERVICE_KEY=your_hubspot_service_or_private_app_token
HUBSPOT_API_BASE_URL=https://api.hubapi.com/
CRM_REQUEST_TIMEOUT=15
```

`HUBSPOT_SERVICE_KEY` is sent only as:

```text
Authorization: Bearer <token>
```

It is not stored in `crm_connections.credential_ref`. The database stores the reference name `HUBSPOT_SERVICE_KEY`, not the secret.

The HubSpot app/token needs contact read access, represented by the expected scope:

```text
crm.objects.contacts.read
```

If HubSpot rejects the token with `401` or `403`, verify that the value is the actual service/private-app access token and that the required CRM scope is enabled.

## 3. Backend endpoints

### Test HubSpot connection

```http
POST /api/crm/hubspot/test
```

The backend makes a minimal authenticated contacts request. A successful response is:

```json
{
  "provider": "hubspot",
  "connected": true,
  "contact_count_sample": 1
}
```

Provider failures are returned as `502`; missing configuration is returned as `503`. The response never includes the token.

### Synchronize contacts

```http
POST /api/crm/hubspot/sync
Content-Type: application/json

{
  "max_records": 100
}
```

`max_records` defaults to 100 and is capped at 5,000. The response reports:

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

## 4. HubSpot-to-SalesGenie mapping

| HubSpot property | SalesGenie field | Behavior |
|---|---|---|
| `id` | `crm_records.provider_record_id` | Stable provider identity |
| `email` | `leads.email` | Case-normalized upsert key |
| `firstname` + `lastname` | `leads.contact_name` | Joined into one display name |
| `company` | `leads.company_name` | Falls back to `HubSpot Contact <id>` if absent |
| `jobtitle` | `leads.contact_title` | Direct mapping |
| `phone` | `leads.phone` | Direct mapping |
| `industry` | `leads.industry` | Direct mapping |
| `numberofemployees` | `leads.company_size` | Stored as the provider value |
| `annualrevenue` | `leads.annual_revenue` | Stored as the provider value |
| `city` + `state` | `leads.location` | Joined as `City, State` |
| `hs_lead_status` / `lifecyclestage` | `leads.lead_status` | Normalized to existing database statuses |
| — | `leads.source` | Always `CRM` for this ingestion path |
| Full response | `crm_records.provider_payload` | Last provider snapshot |

Contacts without an email are not inserted because the existing SalesGenie lead contract requires an email. They increment `records_failed` and the reason is retained in the sync log.

## 5. Persistence flow

```text
HubSpot API
    |
    | GET /crm/v3/objects/contacts
    | pagination through paging.next.after
    v
HubSpotClient
    |
    | normalize properties
    v
sync_hubspot_contacts()
    |
    +--> leads
    |      match by normalized email
    |      create or update
    |
    +--> crm_records
    |      unique(connection, object_type, provider_record_id)
    |      preserve HubSpot identity and payload
    |
    +--> crm_sync_logs
           counts, run ID, status, failures, timestamps
```

The generated connection uses:

```text
provider: hubspot
account_identifier: environment
credential_ref: HUBSPOT_SERVICE_KEY
```

This is suitable for the current single-account pilot. A later OAuth/secret-management phase should replace the environment connection lookup with an explicit account identifier and secret reference.

## 7. How to try it

1. Put the real token in the local `.env` only.
2. Ensure PostgreSQL is running and the Phase A migration is applied:

   ```bash
   alembic upgrade head
   ```

3. Start the backend:

   ```bash
   uvicorn backend.main:app --reload
   ```

4. Test credentials:

   ```bash
   curl -X POST http://localhost:8000/api/crm/hubspot/test
   ```

5. Pull a bounded batch:

   ```bash
   curl -X POST http://localhost:8000/api/crm/hubspot/sync \
     -H 'Content-Type: application/json' \
     -d '{"max_records": 25}'
   ```

Do not paste the token into the command line, commit it, or include it in screenshots/logs.
## 9. Validation

Focused validation completed:

```text
11 HubSpot and lead-management tests passed
CRM routes registered in FastAPI
Python compilation passed
```

The external HubSpot test is intentionally not run automatically because it would consume the configured account and expose environment-dependent behavior. Run the two curl commands only after confirming the token scopes and test-account data.

