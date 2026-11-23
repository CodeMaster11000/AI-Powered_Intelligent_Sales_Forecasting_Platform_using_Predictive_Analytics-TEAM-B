# CRM Duplicate and Predictable Error Handling Test Report

## Scope

This report covers:

1. Preventing duplicate leads by normalizing and uniquely enforcing email addresses.
2. Preserving actionable CRM provider errors during HubSpot and Salesforce operations.
3. Recording failed CRM syncs and failed CRM write-backs with their provider status and message.

## Changes implemented

### Lead email uniqueness

- Manual lead creation and update now normalize email addresses with trim-and-lowercase before querying or persisting.
- CSV/bulk import now compares normalized emails against normalized database values and stores normalized values.
- Duplicate lead conflicts raise HTTP `409 Conflict`, including database constraint races.
- The `leads` table model now declares `uq_leads_email`.
- Migration `8e4f1a2b3c5d_add_unique_lead_email` normalizes existing values before creating the constraint.
- The migration refuses to continue if normalized duplicates already exist, listing the first five conflicting addresses so they can be merged safely first.

### CRM error handling

- CRM provider statuses `400`, `401`, `403`, `404`, `409`, `422`, `429`, and `503` are returned to API clients unchanged.
- Provider `5xx` responses other than `503` are translated to `502 Bad Gateway`.
- Network and timeout failures remain `503 Service Unavailable`.
- Invalid CRM request parameters return `400`.
- Salesforce's existing `424 Failed Dependency` behavior remains supported for unavailable CRM objects.
- Failed CRM push operations mark the linked `CRMRecord` as `error` and store the provider status/message in `CRMSyncLog`.
- Failed pull operations store a failed sync log with status, error code, and error message.

## Test coverage

### Automated tests

The following focused tests passed:

```text
pytest -q backend/tests/test_lead_management.py \
  backend/tests/test_hubspot_client.py \
  backend/tests/test_salesforce_client.py \
  backend/tests/test_crm_error_handling.py

24 passed
```

The tests cover:

- Case-insensitive duplicate detection during bulk import.
- Email normalization before persistence.
- HubSpot and Salesforce provider error extraction.
- HTTP status preservation for not-found, authentication, rate-limit, unavailable, and provider-server errors.
- Existing CRM pagination, mapping, and write-back behavior.

Python syntax validation also passed:

```text
python -m compileall -q backend modules migrations/versions/8e4f1a2b3c5d_add_unique_lead_email.py
```

## Migration prerequisite

Run the migration only after checking existing data. If two existing leads differ only by email casing or whitespace, the migration intentionally stops instead of silently merging them. Those records must be reviewed and merged first.

After resolving conflicts, run:

```text
alembic upgrade head
```

## Expected API behavior

| Situation | Expected result |
|---|---|
| Create a lead with an existing email | `409 Conflict` |
| Import the same email with different casing | Skipped when duplicate skipping is enabled |
| Update a lead to another lead's email | `409 Conflict` |
| CRM record does not exist during write-back | Provider `404`, local record marked `error` |
| CRM credentials rejected | Provider `401` or `403` |
| CRM rate limit | Provider `429` |
| CRM network/timeout failure | `503 Service Unavailable` |
| CRM provider server failure | `502 Bad Gateway` |
| Invalid CRM sync request | `400 Bad Request` |

## Remaining operational recommendation

The migration must be applied in each deployed environment. After deployment, verify the constraint exists in PostgreSQL and exercise one duplicate-create, one duplicate-update, one CRM `404`, and one CRM `429` scenario against the running API.

---

# Predictable Error Handling Inventory

## Evidence reviewed

The complete backend test set was reviewed:

- `test_lead_management.py`
- `test_hubspot_client.py`
- `test_salesforce_client.py`
- `test_crm_error_handling.py`
- `test_llm_client.py`
- `test_lead_intelligence.py`
- `test_lead_scoring.py`
- `test_outreach_agent.py`
- `test_conversation_agent.py`
- `test_milestone2_surfaces.py`

The corresponding API handlers, lead services, CRM clients, LLM client, outreach agent, conversation agent, and schemas were also checked.

## Error category matrix

| Category | Current handling | Tested? | Expected API behavior |
|---|---|---:|---|
| Missing required manual lead fields | Pydantic validation rejects the request | Yes, schema-level | `422 Unprocessable Entity` |
| Invalid manual email | `EmailStr` validation rejects it | Yes | `422 Unprocessable Entity` |
| Invalid lead status/source | Pydantic literal validation rejects it | Yes | `422 Unprocessable Entity` |
| Duplicate manual email | Case-insensitive pre-check plus database constraint | Yes | `409 Conflict` |
| Duplicate update email | Case-insensitive pre-check plus database constraint | Partially | `409 Conflict` |
| Duplicate CSV/bulk email | Normalized existing and in-batch detection | Yes | Skip by default; `409` when duplicate skipping is disabled |
| CSV malformed row/file format | No multipart file-upload parser exists; bulk ingestion currently accepts JSON | No | JSON validation `422`; file-specific errors are not currently applicable |
| Missing local lead | Explicit `LookupError`/endpoint handling | Covered in service/API paths | `404 Not Found` |
| Missing CRM connection | Explicit service validation | Service path | `400 Bad Request` |
| Missing CRM record on write-back | Explicit local validation; provider deletion preserves provider `404` | Provider status helper tested | `404` and local CRM record marked `error` |
| Missing HubSpot token | Configuration validation | Not directly | `503 Service Unavailable` |
| Missing Salesforce credentials | Configuration validation | Not directly | `503 Service Unavailable` |
| Invalid CRM token/session | Provider error preserved | HubSpot client tested; status mapping tested | `401 Unauthorized` |
| Insufficient CRM permissions | Provider error preserved | Status mapping tested | `403 Forbidden` |
| CRM rate limit | Provider status preserved | Status mapping tested | `429 Too Many Requests`; retry policy is not implemented |
| CRM network/timeout failure | Converted to provider error `503` | Not directly | `503 Service Unavailable` |
| CRM non-JSON response | Converted to `502` | Not directly | `502 Bad Gateway` |
| CRM malformed record without email/ID | Record skipped and sync becomes partial | Mapping tests cover missing email | Successful response with `partial` status and failed-record count |
| Salesforce Lead object unavailable | Falls back to Contact; both unavailable becomes `424` | Yes | `424 Failed Dependency` |
| LLM API key absent | Provider is marked unavailable; other providers/local fallback are attempted | Yes, all providers disabled | Feature-specific fallback or `503` where no fallback exists |
| LLM provider authentication/network failure | Broad provider exception is logged and the next provider is attempted | Not provider-mocked | Fallback; if no usable result, feature-specific fallback or `503` |
| Invalid LLM JSON | Parser returns `None`; provider cascade continues | Yes, parser formats tested | Fallback; no raw malformed output is persisted |
| Incomplete outreach output | Raises `RuntimeError` after fallback output validation | Not directly | Outreach endpoint returns `503` |
| Invalid outreach subject/hook/triggers | Raises `RuntimeError` | Not directly | Outreach endpoint returns `503` |
| Empty conversation transcript | Raises `ValueError` before processing | Yes | `400 Bad Request` |
| Conversation AI failure | Failed interaction record is persisted, then exception is re-raised | Fallback behavior tested; failure persistence not directly | Endpoint currently returns `500` for unexpected summarization errors |
| Missing interaction lead | Current service permits a missing optional lead and uses generic context | Not directly | This is currently allowed for transcript-only interactions |
| Invalid interaction type | Service normalizes it to `meeting` | Not directly | Current behavior is defaulting, not rejecting |
| Missing intelligence result | Endpoint returns an explicit unavailable response | Not directly | `503 Service Unavailable` |
| Missing draft/interaction | Explicit endpoint checks | Some draft cases tested | `404 Not Found` |
| Invalid draft state transition | Explicit conflict checks | Archived draft deletion tested | `409 Conflict` |
| Draft belongs to another lead | Explicit ownership check | Not directly | `400 Bad Request` |
| Database failure | Some service paths rollback and convert to runtime errors; coverage is incomplete | No | Usually `503`, but a global database exception policy is not defined |

## Manual and CSV ingestion clarification

There is no current `UploadFile` or multipart CSV endpoint in the backend. The implemented bulk-import contract is `/api/leads/bulk`, which accepts a JSON array of `LeadCreate` objects. Therefore:

- Missing fields, invalid email formats, invalid enum values, and malformed JSON are handled by FastAPI/Pydantic with `422`.
- Duplicate emails are handled by the lead service and return `409` when not skipped.
- File size, file encoding, CSV delimiter, missing CSV headers, and malformed CSV rows are not currently handled because file parsing is not implemented in this backend path.

## Token and credential handling

HubSpot and Salesforce configuration failures are detected before API use and returned as `503`. Provider authentication failures are represented by typed provider exceptions and now retain actionable statuses. LLM providers are initialized independently; missing or invalid provider setup disables that provider and allows cascading to the next configured provider.

The current LLM client logs provider exception text and returns `None` after all providers fail. This avoids crashing the generation layer, but it does not yet expose a structured error code, retry-after value, or per-provider failure report to the API consumer.

## Remaining gaps identified by testing review

The following are not currently implemented or directly covered by tests:

1. Bounded retries with exponential backoff for CRM `429` and transient `5xx` responses.
2. Automatic token refresh for expired OAuth sessions.
3. Multipart CSV upload and row-level CSV error reporting.
4. Endpoint tests for all lead, CRM, draft, interaction, and AI `404/409/503` branches.
5. Database integration tests against PostgreSQL for the new unique constraint and concurrent duplicate inserts.
6. Structured provider error codes and retry metadata for LLM failures.
7. Consistent global handling for unexpected database exceptions.

These are test and operational coverage gaps, not silent success paths: the existing implementation generally returns an error or uses an explicit deterministic fallback. They should be added before production hardening.
