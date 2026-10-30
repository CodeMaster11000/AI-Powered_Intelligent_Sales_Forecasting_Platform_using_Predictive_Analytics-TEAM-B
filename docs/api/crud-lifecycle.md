# Lead API CRUD Lifecycle

This page describes the lead lifecycle implemented by
`backend.main:app` at the end of Milestone 1. The generated OpenAPI schema
at `/openapi.json` remains the machine-readable source of truth.

## Lifecycle at a glance

```text
create one or many leads
        |
        v
list/search leads and inspect pipeline statistics
        |
        +--> update a lead or delete it (including dependent AI records)
        |
        +--> analyze a lead -> persist complete structured run, insight, and score -> optionally promote to Qualified
        |
        +--> read the latest insight or complete scoring dossier
```

## Create

### Single lead

`POST /api/leads` accepts a `LeadCreate` payload and returns `201 Created`.
`company_name` and a valid `email` are required. The request model supplies
`New Leads` and `CSV` defaults for `lead_status` and `source`.

The service checks email uniqueness before inserting the SQLAlchemy `Lead`
record. A duplicate returns `400`; invalid request data returns FastAPI's
standard `422`.

### Bulk import

`POST /api/leads/bulk` accepts an array of the same lead payloads. With
`skip_duplicates=true` (the default), existing emails and duplicates in the
same request are counted in `skipped_duplicates`. Email matching is
case-insensitive. With `skip_duplicates=false`, the first duplicate aborts the
request with `400` and no batch insert is committed.

The response reports `total_received`, `imported_count`,
`skipped_duplicates`, and `errors`.

## Read

| Endpoint | Purpose |
|---|---|
| `GET /api/leads` | List newest leads, optionally filtered by `search`, `source`, and `limit` |
| `GET /api/leads/stats` | Return total leads, ingestion health, and pending AI scoring count |
| `GET /api/leads/{lead_id}/insights` | Read the latest persisted company insight |
| `GET /api/leads/{lead_id}/dossier` | Read the lead profile with score and intelligence, generating missing analysis |
| `GET /api/scoring/queue` | Read every lead with its latest score or `unscored` status |

Unknown lead or insight records return `404` on the resource-specific routes.

## Intelligence and lifecycle transition

`POST /api/leads/{lead_id}/analyze` runs the synchronous LangGraph workflow:

1. Research agent profiles the industry, technology, growth indicators, and
   transformation opportunities.
2. Qualification agent produces a 0-100 qualification score, technology
   alignment, personas, business needs, and a recommendation.
3. The service stores the complete structured output in `lead_analysis_runs`,
   and upserts the compatibility `company_insights` and `lead_scores` records.
4. A lead in `New Leads` is promoted to `Qualified` when its score is at least
   70.

The response includes the generated analysis and execution latency. AI
provider or incomplete-output failures return `503`.

`POST /api/intelligence/analyze-prospect` performs the same analysis without
creating or modifying a database lead.

## Update and delete

`PUT /api/leads/{lead_id}` accepts a complete `LeadUpdate` payload and returns
the updated lead. It preserves email uniqueness while Pydantic and database
constraints validate email, status, and source values. Unknown leads return
`404`, and a duplicate email returns `400`.

`DELETE /api/leads/{lead_id}` returns `204 No Content`. Deleting a lead also
cascades its company insight and score records. Unknown leads return `404`.

The Recently Ingested Leads table exposes both operations through its
**Manage lead** controls.

## Persistence relationships

- `leads` stores the prospect and pipeline state.
- `company_insights` stores the latest generated intelligence for a lead.
- `lead_scores` stores the current persisted score in the present
  implementation; re-analysis updates the latest row rather than exposing a
  score-history API.
- `lead_analysis_runs` stores each complete multi-agent output as structured
  fields and JSONB values, including opportunities, growth indicators, tech
  components, alignment metrics, personas, recommendation, trace, and
  execution metadata. Predictive scoring reads the latest run.
- Deleting a lead at the database level cascades its insight and score rows.
