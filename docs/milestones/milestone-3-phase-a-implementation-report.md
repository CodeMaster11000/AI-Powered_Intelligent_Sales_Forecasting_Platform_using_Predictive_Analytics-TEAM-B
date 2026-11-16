# Milestone 3 Phase A Implementation Report

**Project:** SalesGenie AI Platform  
**Scope:** Provider-neutral CRM persistence and conversation-intelligence storage  
**Migration:** `6c2d7e8f9012_add_milestone3_phase_a_models`

## 1. Phase A outcome

Phase A is implemented as a persistence foundation for the later CRM adapters, sync service, and summarization endpoints. It adds five related SQLAlchemy models and one Alembic migration:

1. `crm_connections`
2. `crm_field_mappings`
3. `crm_records`
4. `crm_sync_logs`
5. `sales_interactions`

Existing `leads` remain the internal sales record. CRM records and sales interactions may reference a lead, while CRM connections own provider-specific configuration, mappings, records, and sync history.

The implementation deliberately does **not** add OAuth, provider API clients, sync routes, webhooks, or AI summarization routes. Those are Phase B/C concerns and can now build on stable tables and relationships.

## 2. Entity relationship overview

```text
crm_connections
  ├──< crm_field_mappings
  ├──< crm_records >── leads
  ├──< crm_sync_logs
  └──< sales_interactions >── leads
```

Cardinality:

- One CRM connection has many field mappings.
- One CRM connection has many external CRM records.
- One CRM connection has many sync-log entries.
- One CRM connection can be the source of many sales interactions.
- One lead can have many external CRM records.
- One lead can have many sales interactions.
- A CRM record and a sales interaction may be retained after its lead is deleted; their `lead_id` is set to `NULL` to preserve integration history.
- Deleting a CRM connection deletes its mappings, external-record identities, and sync logs. Interactions retain their content but their `connection_id` is set to `NULL`.

## 3. Table definitions

### 3.1 `crm_connections`

Represents one configured connection to a provider account.

| Column | Type | Required | Purpose |
|---|---|:---:|---|
| `connection_id` | `BIGINT` identity | Yes | Internal primary key |
| `provider` | `TEXT` | Yes | `hubspot` or `salesforce` |
| `account_identifier` | `TEXT` | Yes | Provider account/org/portal identifier |
| `display_name` | `TEXT` | No | Human-readable connection name |
| `credential_ref` | `TEXT` | No | Reference to a secret, never the raw token |
| `status` | `TEXT` | Yes | `active`, `disabled`, or `error` |
| `scopes` | `JSONB` | No | Granted OAuth/private-app scopes |
| `last_successful_sync_at` | timestamp | No | Operational freshness marker |
| `created_at`, `updated_at` | timestamp | Yes | Audit timestamps |

Security decision: the database stores a `credential_ref`, not an access token. A later secret-management implementation can resolve that reference. The Phase A schema does not claim that credentials are encrypted yet.

### 3.2 `crm_field_mappings`

Stores configurable mappings between provider properties and internal fields.

| Column | Type | Required | Purpose |
|---|---|:---:|---|
| `mapping_id` | `BIGINT` identity | Yes | Internal primary key |
| `connection_id` | `BIGINT` FK | Yes | Owning CRM connection |
| `object_type` | `TEXT` | Yes | Provider object, e.g. `contact`, `deal` |
| `provider_field` | `TEXT` | Yes | Salesforce/HubSpot property name |
| `internal_field` | `TEXT` | Yes | SalesGenie model field path |
| `direction` | `TEXT` | Yes | `inbound`, `outbound`, or `bidirectional` |
| `transform_name` | `TEXT` | No | Named transformation, e.g. name/status normalization |
| `is_active` | `BOOLEAN` | Yes | Enables disabling a mapping without deleting it |

The unique constraint on `(connection_id, object_type, provider_field, internal_field)` prevents duplicate mapping definitions for the same connection.

### 3.3 `crm_records`

Provides the external identity boundary between a provider record and an internal lead.

| Column | Type | Required | Purpose |
|---|---|:---:|---|
| `record_id` | `BIGINT` identity | Yes | Internal primary key |
| `connection_id` | `BIGINT` FK | Yes | Provider account owning the record |
| `lead_id` | `BIGINT` FK | No | Matched SalesGenie lead |
| `object_type` | `TEXT` | Yes | `lead`, `contact`, `company`, `deal`, or `activity` |
| `provider_record_id` | `TEXT` | Yes | Stable provider ID |
| `sync_state` | `TEXT` | Yes | `synced`, `pending`, or `error` |
| `provider_payload` | `JSONB` | No | Last normalized/raw provider snapshot |
| `last_synced_at` | timestamp | No | Last successful record synchronization |
| `created_at`, `updated_at` | timestamp | Yes | Audit timestamps |

The unique constraint on `(connection_id, object_type, provider_record_id)` makes sync idempotent and allows the same provider ID to exist in separate accounts or object namespaces. Matching by email alone must not replace this identity table.

### 3.4 `crm_sync_logs`

Stores both run-level and record-level synchronization outcomes.

| Column | Type | Required | Purpose |
|---|---|:---:|---|
| `sync_log_id` | `BIGINT` identity | Yes | Internal primary key |
| `connection_id` | `BIGINT` FK | Yes | Connection used for the operation |
| `sync_run_id` | `TEXT` | Yes | Groups entries from one sync run |
| `operation` | `TEXT` | Yes | `pull`, `push`, or `test_connection` |
| `object_type` | `TEXT` | No | Contact/activity/deal/etc. |
| `internal_record_id` | `BIGINT` | No | Internal record affected |
| `external_record_id` | `TEXT` | No | Provider record affected |
| `status` | `TEXT` | Yes | `running`, `succeeded`, `partial`, or `failed` |
| counters | integers | Yes | Read/created/updated/failed counts |
| retry/error fields | text/integer | No | Retry count and provider/application error |
| `details` | `JSONB` | No | Cursor, response metadata, or diagnostic context |
| `started_at`, `completed_at` | timestamp | Yes/No | Operation timing |

`sync_run_id` is intentionally separate from the row primary key so one future run can record multiple object types and record outcomes while preserving one correlation identifier.

### 3.5 `sales_interactions`

Stores CRM activities and conversation-intelligence output.

| Column | Type | Required | Purpose |
|---|---|:---:|---|
| `interaction_id` | `BIGINT` identity | Yes | Internal primary key |
| `lead_id` | `BIGINT` FK | No | Related SalesGenie lead |
| `connection_id` | `BIGINT` FK | No | Source CRM connection |
| `provider_activity_id` | `TEXT` | No | Provider activity ID for deduplication |
| `interaction_type` | `TEXT` | Yes | `meeting`, `call`, `email`, or `note` |
| `occurred_at` | timestamp | Yes | When the interaction happened |
| `subject` | `TEXT` | No | Meeting/call subject |
| `transcript_text` | `TEXT` | No | Optional transcript; retention policy applies |
| `transcript_ref` | `TEXT` | No | Reference to external/object storage |
| `summary` | `TEXT` | No | Generated summary |
| `discussion_points` | `JSONB` | No | Ordered list of key points |
| `action_items` | `JSONB` | No | Structured action-item objects |
| `risks`, `next_step` | JSONB/TEXT | No | Extracted risks and recommended next step |
| `processing_status` | `TEXT` | Yes | `pending`, `completed`, or `failed` |
| AI metadata | text/integer | No | Provider, model, prompt version, token counts |
| `error_message` | `TEXT` | No | Summarization failure detail |
| `created_at`, `updated_at` | timestamp | Yes | Audit timestamps |

The unique constraint on `(connection_id, provider_activity_id)` supports idempotent import of CRM activities. Interactions created locally can leave both values null and still be stored.

## 4. Relationship and deletion behavior

| Parent | Child | Relationship | On parent delete |
|---|---|---|---|
| `crm_connections` | `crm_field_mappings` | one-to-many | Cascade delete |
| `crm_connections` | `crm_records` | one-to-many | Cascade delete |
| `crm_connections` | `crm_sync_logs` | one-to-many | Cascade delete |
| `crm_connections` | `sales_interactions` | one-to-many | Set connection to null |
| `leads` | `crm_records` | one-to-many | Set lead to null |
| `leads` | `sales_interactions` | one-to-many | Set lead to null |

The distinction is intentional: configuration and operational logs belong to a connection, while imported interaction history is valuable evidence that should survive removal of a connection or lead.

## 5. Constraints and indexes

Database checks reject unsupported providers, statuses, object types, mapping directions, and interaction types. Unique constraints protect provider identities and mapping definitions. Indexes were added for:

- `crm_records.lead_id`
- `crm_sync_logs(connection_id, started_at)`
- `crm_sync_logs.sync_run_id`
- `sales_interactions(lead_id, occurred_at)`

These support the planned sync-status and recent-activity screens without requiring broad table scans.
