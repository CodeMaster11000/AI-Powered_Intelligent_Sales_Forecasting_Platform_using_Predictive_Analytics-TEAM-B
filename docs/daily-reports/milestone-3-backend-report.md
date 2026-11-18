# Milestone 3 Backend Report

**Project:** SalesGenie AI Platform  
**Milestone:** 3 - CRM Integration, Provider-Neutral Persistence, and Backend Lifecycle  
**Scope:** FastAPI backend, CRM adapters, synchronization, persistence, API endpoints, testing, and operational setup  
**Status:** Implemented for the current pull-based integration scope

## 1. Executive summary

Milestone 3 extends the SalesGenie backend with a provider-neutral CRM
integration foundation and working HubSpot and Salesforce ingestion adapters.
The backend can validate provider connectivity, retrieve bounded batches of
CRM records, normalize them into the internal lead model, and persist provider
identity and synchronization results.

The milestone also establishes the persistence model required for future
activities, conversation intelligence, field mappings, and synchronization
history. Existing lead CRUD, intelligence, scoring, and outreach routes remain
available and are documented as part of the complete backend lifecycle.

The current implementation is intentionally pull-first. It does not yet
provide CRM write-back, webhook ingestion, activity synchronization, OAuth
account management, external email delivery, or AI conversation summarization
routes.

## 2. Milestone objectives and outcomes

| Objective | Outcome |
|---|---|
| Add provider-neutral CRM persistence | Implemented through five related SQLAlchemy models and an Alembic migration |
| Integrate HubSpot contacts | Implemented with bearer-token access, pagination, normalization, and local upsert |
| Integrate Salesforce records | Implemented with OAuth 2.0 client credentials, dynamic instance URLs, pagination, and Lead-to-Contact fallback |
| Preserve external CRM identity | Implemented through `crm_records` unique provider identities |
| Track synchronization operations | Implemented through run-level and record-level `crm_sync_logs` data |
| Preserve existing SalesGenie workflows | Lead CRUD, intelligence, scoring, and outreach routes remain available |
| Validate backend behavior | Mocked adapter and lead-management tests cover success, failure, pagination, validation, and normalization paths |

## 3. Backend architecture

```text
Client / Frontend
        |
        v
FastAPI routes (backend/main.py)
        |
        +--> Lead, intelligence, scoring, and outreach services
        |
        +--> CRM route handlers
                 |
                 +--> HubSpotClient
                 +--> SalesforceClient
                 |
                 v
          modules/module5_crm.py
                 |
                 +--> normalize provider records
                 +--> upsert leads by normalized email
                 +--> persist crm_records
                 +--> write crm_sync_logs
                 |
                 v
              PostgreSQL
```

The API uses synchronous FastAPI handlers and SQLAlchemy sessions. Provider
clients encapsulate HTTP authentication, requests, pagination, and provider
errors. The CRM service layer owns mapping, local upsert, sync accounting, and
transaction behavior.

## 4. Implemented endpoint catalog

### 4.1 System and users

| Method | Endpoint | Purpose | Success |
|---|---|---|---:|
| `GET` | `/health` | Check API availability | `200` |
| `GET` | `/api/users` | Return seeded sales users | `200` |

Health response:

```json
{
  "status": "healthy",
  "service": "salesgenie-api"
}
```

### 4.2 Lead management

| Method | Endpoint | Purpose | Success |
|---|---|---|---:|
| `POST` | `/api/leads` | Create one lead | `201` |
| `GET` | `/api/leads` | Search and list leads | `200` |
| `GET` | `/api/leads/stats` | Return pipeline statistics | `200` |
| `PUT` | `/api/leads/{lead_id}` | Replace editable lead fields | `200` |
| `DELETE` | `/api/leads/{lead_id}` | Delete a lead and dependent AI records | `204` |
| `POST` | `/api/leads/bulk` | Import multiple leads | `201` |

Lead creation requires `company_name` and a valid email address. Email
uniqueness is case-insensitive. Default values are `New Leads` for
`lead_status` and `CSV` for `source`.

Common lead errors:

| Condition | Response |
|---|---:|
| Duplicate email | `400` |
| Unknown lead ID | `404` |
| Invalid body or query parameter | `422` |
| Invalid status or source | `422` |

### 4.3 Intelligence, scoring, and outreach

| Method | Endpoint | Purpose | Success |
|---|---|---|---:|
| `POST` | `/api/leads/{lead_id}/analyze` | Analyze and persist lead intelligence | `200` |
| `GET` | `/api/leads/{lead_id}/insights` | Read persisted intelligence | `200` |
| `POST` | `/api/leads/batch-analyze` | Analyze selected leads | `200` |
| `POST` | `/api/intelligence/analyze-prospect` | Analyze a prospect without saving a lead | `200` |
| `GET` | `/api/intelligence/architecture` | Return LangGraph topology | `200` |
| `GET` | `/api/scoring/queue` | Return leads and score components | `200` |
| `GET` | `/api/leads/{lead_id}/dossier` | Return a complete intelligence and score dossier | `200` |
| `POST` | `/api/leads/{lead_id}/score` | Recalculate and persist a score | `200` |
| `POST` | `/api/leads/score-batch` | Score currently unscored leads | `200` |
| `POST` | `/api/outreach/generate` | Generate a personalized email draft | `200` |
| `POST` | `/api/outreach/save-draft` | Save an outreach draft | `200` |
| `POST` | `/api/outreach/send` | Record a send and advance eligible lead stage | `200` |
| `GET` | `/api/leads/{lead_id}/drafts` | List lead drafts | `200` |
| `GET` | `/api/outreach/drafts/{draft_id}` | Read one draft | `200` |
| `PATCH` | `/api/outreach/drafts/{draft_id}` | Update an active draft | `200` |
| `POST` | `/api/outreach/drafts/{draft_id}/archive` | Archive an active draft | `200` |
| `DELETE` | `/api/outreach/drafts/{draft_id}` | Permanently delete an active draft | `204` |
| `GET` | `/api/llm/providers` | Report configured provider availability | `200` |

AI endpoints are synchronous. Provider unavailability or incomplete AI output
returns `503`. The outreach send endpoint currently records application state;
it does not deliver email through an external mail provider.

### 4.4 CRM integration

| Method | Endpoint | Purpose | Success |
|---|---|---|---:|
| `POST` | `/api/crm/hubspot/test` | Validate HubSpot credentials and contact access | `200` |
| `POST` | `/api/crm/hubspot/sync` | Pull HubSpot contacts and upsert local records | `200` |
| `POST` | `/api/crm/salesforce/test` | Validate Salesforce authentication and supported object | `200` |
| `POST` | `/api/crm/salesforce/sync` | Pull Salesforce Leads or Contacts and upsert local records | `200` |

CRM synchronization accepts:

```json
{
  "max_records": 100
}
```

The default is 100 and the maximum is 5,000. A successful synchronization
returns:

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

CRM error handling:

| Condition | Response |
|---|---:|
| Provider API or authentication failure | `502` |
| Missing local configuration | `503` |
| Salesforce OAuth succeeds but neither Lead nor Contact is available | `424` |
| Invalid synchronization request | `422` |

Tokens, secrets, and provider response bodies are not returned by the
endpoints.

## 5. CRM integration details

### 5.1 HubSpot

HubSpot uses a service/private-app bearer token from
`HUBSPOT_SERVICE_KEY` (with `HUBSPOT_ACCESS_TOKEN` supported as a compatibility
fallback). Contacts are read from
`/crm/v3/objects/contacts` using the `crm.objects.contacts.read` scope.

The client follows `paging.next.after`, limits each request to the provider's
page size, and stops at the requested maximum. Contacts without an email are
rejected from local ingestion and counted as failed records.

### 5.2 Salesforce

Salesforce uses OAuth 2.0 Client Credentials Flow:

```text
POST {SALESFORCE_LOGIN_URL}/services/oauth2/token
        |
        +--> access_token (memory only)
        +--> instance_url
        |
        v
GET {instance_url}/services/data/{SALESFORCE_API_VERSION}/query
```

The client first queries `Lead`. If the configured org or Run-As user reports
that `Lead` is unavailable, it retries with `Contact`. Pagination follows
`nextRecordsUrl`. The returned `instance_url` is used for all subsequent API
requests; an instance URL does not need to be configured separately.

Required configuration:

```dotenv
SALESFORCE_CONSUMER_KEY=...
SALESFORCE_CONSUMER_SECRET=...
SALESFORCE_LOGIN_URL=https://login.salesforce.com
SALESFORCE_API_VERSION=v60.0
CRM_REQUEST_TIMEOUT=15
```

Use `https://test.salesforce.com` for a Salesforce sandbox.

## 6. Provider-to-SalesGenie mapping

| Provider value | Internal value | Notes |
|---|---|---|
| Provider record ID | `crm_records.provider_record_id` | Stable external identity |
| Email | `leads.email` | Trimmed and lowercased for matching |
| First and last name | `leads.contact_name` | Joined into a display name |
| Company or Account name | `leads.company_name` | Provider-specific fallback when absent |
| Job title | `leads.contact_title` | Direct mapping |
| Phone | `leads.phone` | Direct mapping |
| Industry | `leads.industry` | Direct mapping where available |
| Employee count | `leads.company_size` | Stored as text |
| Annual revenue | `leads.annual_revenue` | Stored as text |
| City and state | `leads.location` | Joined as `City, State` |
| Provider lifecycle/status | `leads.lead_status` | Normalized to SalesGenie statuses |
| — | `leads.source` | Set to `CRM` |
| Full provider record | `crm_records.provider_payload` | Latest provider snapshot |

The local lead is upserted by normalized email, while the
`(connection_id, object_type, provider_record_id)` key preserves provider
identity and makes repeated syncs idempotent.

## 7. Persistence model

```text
crm_connections
  ├──< crm_field_mappings
  ├──< crm_records >── leads
  ├──< crm_sync_logs
  └──< sales_interactions >── leads
```

### 7.1 Tables

| Table | Responsibility |
|---|---|
| `crm_connections` | Provider account, status, scope metadata, and secret reference |
| `crm_field_mappings` | Configurable provider-to-internal field mappings |
| `crm_records` | External identity, normalized payload, lead association, and sync state |
| `crm_sync_logs` | Run correlation, counters, timing, errors, and diagnostic details |
| `sales_interactions` | Future CRM activities, transcripts, summaries, risks, and action items |

The database stores `credential_ref` values such as
`HUBSPOT_SERVICE_KEY`; it does not store raw access tokens or consumer
secrets. Unique constraints and indexes support idempotent ingestion and
recent synchronization queries.

Deletion behavior is deliberate:

- Deleting a CRM connection cascades mappings, CRM records, and sync logs.
- Deleting a connection sets `sales_interactions.connection_id` to `NULL`.
- Deleting a lead sets related CRM record and interaction `lead_id` values to
  `NULL`, preserving integration history.
- Deleting a lead cascades current company insight and score records.

## 8. End-to-end backend lifecycle

### 8.1 Lead lifecycle

```text
Create/import
    |
    v
List/search and inspect statistics
    |
    +--> Update or delete
    |
    +--> Analyze intelligence
             |
             +--> persist analysis run and insight
             +--> calculate and persist score
             +--> promote New Leads to Qualified when score >= 70
    |
    +--> score, generate outreach, save draft, send/advance stage
```

### 8.2 CRM synchronization lifecycle

```text
Validate configuration
    |
    v
Test provider authentication/API access
    |
    v
Start bounded sync with sync_run_id
    |
    v
Fetch provider pages
    |
    v
Normalize records
    |
    +--> reject records without email
    +--> upsert leads by normalized email
    +--> upsert crm_records by provider identity
    +--> record created/updated/failed counters
    |
    v
Complete crm_sync_logs with status and timestamps
```

Repeated pulls do not create duplicate local leads for the same normalized
email. Provider snapshots and sync results remain available for operational
diagnosis.

## 9. Testing and validation

### 9.1 Focused automated coverage

The documented focused tests cover:

- HubSpot pagination through `paging.next.after`.
- HubSpot provider error propagation.
- HubSpot field normalization and missing-email rejection.
- Salesforce client-credentials authentication.
- Salesforce dynamic instance URL usage.
- Salesforce `nextRecordsUrl` pagination.
- Salesforce Lead-to-Contact fallback.
- Salesforce field normalization and missing-email rejection.
- Lead creation, duplicate prevention, update, delete, bulk import, and
  schema validation.

The current focused files contain four HubSpot tests, five Salesforce tests,
and seven lead-management tests. The Milestone 2 test report also records a
full repository result of 36 passed and 0 failed for that validation run,
including the existing AI outreach and scoring coverage.

Representative commands:

```bash
pytest -q backend/tests/test_hubspot_client.py \
  backend/tests/test_salesforce_client.py \
  backend/tests/test_lead_management.py

python -m compileall backend modules
```

External CRM probes are intentionally manual because they authenticate against
real accounts and read environment-dependent data.

## 10. Deployment and operational procedure

1. Configure provider secrets in the local environment or deployment secret
   store. Never commit `.env` or print tokens.
2. Apply database migrations:

   ```bash
   alembic upgrade head
   ```

3. Recreate the backend container after changing environment variables:

   ```bash
   docker compose up -d --force-recreate backend
   ```

4. Verify the service:

   ```bash
   curl http://localhost:8000/health
   ```

5. Test the configured provider:

   ```bash
   curl -X POST http://localhost:8000/api/crm/hubspot/test
   curl -X POST http://localhost:8000/api/crm/salesforce/test
   ```

6. Run a bounded synchronization:

   ```bash
   curl -X POST http://localhost:8000/api/crm/hubspot/sync \
     -H 'Content-Type: application/json' \
     -d '{"max_records":25}'
   ```

Use the Salesforce equivalent endpoint when Salesforce is configured. Keep
batch sizes bounded to reduce provider rate-limit risk and simplify recovery.

## 11. Security and reliability controls

- Provider credentials are read from environment configuration.
- Access tokens are held in memory for the client lifetime.
- Authorization headers are masked in the HTTP clients.
- Credential references, not raw secrets, are stored in the database.
- Provider payloads are retained for traceability, but credentials are not
  included in the documented sync response.
- CRM requests have a configurable timeout.
- Sync requests cap `max_records` at 5,000.
- Provider failures are translated into explicit HTTP errors.
- Unique provider identity constraints and normalized email matching make
  synchronization repeatable.
- CORS is currently permissive (`*`) and must be restricted before production.
- Authentication and authorization are not currently implemented and must be
  added before exposing the API outside a trusted deployment boundary.

## 12. Known limitations and next steps

### Current limitations

1. CRM write-back currently covers synchronized lead/contact fields; custom
   provider fields and additional CRM objects are not yet mapped.
2. Webhook/event ingestion is not implemented.
3. Activity synchronization and transcript processing are represented in the
   schema but not exposed as completed routes.
4. CRM connection management is environment-driven rather than a multi-account
   OAuth administration flow.
5. The send endpoint records outreach state but does not deliver email.
6. API authentication and role-based authorization are not implemented.
7. CORS allows all origins and should be restricted for production.
8. Sync retries, scheduling, and background job execution are future
   operational work.

### Recommended next steps

1. Add API authentication, authorization, rate limiting, and production CORS
   restrictions.
2. Add connection-management endpoints backed by a secret manager.
3. Add scheduled and resumable background synchronization with retry policy.
4. Add CRM activity/webhook ingestion and deduplication.
5. Extend outbound field mapping and CRM write-back to additional objects and
   provider-specific custom fields.
6. Add sync-status and interaction-history read endpoints.
7. Add integration tests against disposable CRM fixtures or provider sandboxes.
8. Add external email delivery and delivery-status tracking.

## 13. Source documents

- [Salesforce backend integration report](../milestones/milestone-3-salesforce-backend-integration-report.md)
- [HubSpot backend integration report](../milestones/milestone-3-hubspot-backend-integration-report.md)
- [Milestone 3 Phase A implementation report](../milestones/milestone-3-phase-a-implementation-report.md)
- [API contract](../api/api-contract.md)
- [Lead CRUD lifecycle](../api/crud-lifecycle.md)
- [Milestone 2 test report](../testing/milestone-2-test-report.md)
