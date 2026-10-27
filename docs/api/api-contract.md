# SalesGenie API contract

This document describes the **implemented** HTTP contract exposed by
`backend.main:app`. It is intended for frontend, integration, and AI-agent
consumers. The FastAPI-generated contract remains the source of truth for
machine-readable details:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

Update this document in the same change as an endpoint or request/response
schema change.

## 1. Connection and conventions

| Item | Contract |
|---|---|
| Base URL | `http://localhost:8000` by default |
| Frontend override | Set `BACKEND_API_URL` |
| Content type | `application/json` for requests with a body |
| Authentication | None currently implemented |
| IDs | Integer `lead_id`, `user_id`, and `insight_id` values |
| Timestamps | ISO-8601 strings returned by the database |
| Unknown fields | Request models use Pydantic's default handling; clients should send only documented fields and must not rely on unknown fields being preserved |
| CORS | Currently allows all origins, methods, headers, and credentials; restrict this before production |

Successful requests return JSON. Validation failures use FastAPI's standard
`422 Unprocessable Entity` response. Application errors use:

```json
{
  "detail": "Human-readable error message"
}
```

Common status codes:

| Status | Meaning |
|---:|---|
| `200` | Successful read or operation |
| `201` | Lead or bulk import operation accepted and created |
| `400` | Duplicate lead or other domain validation error |
| `404` | Lead or insight does not exist |
| `422` | Request body or query parameter failed schema validation |
| `503` | AI/LLM service is unavailable or returned incomplete output |

## 2. Domain values

`lead_status` must be one of:

```text
New Leads | Qualified | Proposal | Negotiation | Closed Won
```

`source` must be one of:

```text
CRM | Website Form | LinkedIn | Sales Entry | CSV
```

Scores are integers from `0` to `100`. Conversion probability is represented
as a number from `0` to `100` (the current intelligence implementation derives
it as `qualification_score * 0.85`).

## 3. Endpoint index

| Method | Path | Tag | Purpose | Success |
|---|---|---|---|---:|
| `GET` | `/health` | System | Check API availability | `200` |
| `GET` | `/api/users` | Users | List seeded sales users | `200` |
| `GET` | `/api/leads/stats` | Leads | Return pipeline KPIs | `200` |
| `POST` | `/api/leads` | Leads | Create one lead | `201` |
| `PUT` | `/api/leads/{lead_id}` | Leads | Replace an existing lead | `200` |
| `DELETE` | `/api/leads/{lead_id}` | Leads | Delete a lead and dependent AI records | `204` |
| `POST` | `/api/leads/bulk` | Leads | Import multiple leads | `201` |
| `GET` | `/api/leads` | Leads | Search and list leads | `200` |
| `POST` | `/api/leads/{lead_id}/analyze` | Lead Intelligence | Analyze and persist AI intelligence | `200` |
| `GET` | `/api/leads/{lead_id}/insights` | Lead Intelligence | Read persisted intelligence | `200` |
| `POST` | `/api/leads/batch-analyze` | Lead Intelligence | Analyze selected leads | `200` |
| `POST` | `/api/intelligence/analyze-prospect` | Lead Intelligence | Analyze a prospect without saving a lead | `200` |
| `GET` | `/api/intelligence/architecture` | Lead Intelligence | Return LangGraph topology | `200` |
| `GET` | `/api/scoring/queue` | Scoring | Return leads and latest score | `200` |
| `GET` | `/api/leads/{lead_id}/dossier` | Scoring | Return complete score and intelligence dossier | `200` |
| `POST` | `/api/leads/{lead_id}/score` | Scoring | Re-run and persist scoring | `200` |
| `POST` | `/api/leads/score-batch` | Scoring | Score every currently unscored lead | `200` |
| `POST` | `/api/outreach/generate` | Outreach | Generate an AI email draft | `200` |
| `POST` | `/api/outreach/save-draft` | Outreach | Acknowledge a draft save | `200` |
| `POST` | `/api/outreach/send` | Outreach | Acknowledge send and advance lead stage | `200` |
| `GET` | `/api/llm/providers` | AI Engine | Report configured provider availability | `200` |

## 4. System and users

### `GET /health`

No request parameters.

```json
{
  "status": "healthy",
  "service": "salesgenie-api"
}
```

### `GET /api/users`

No request parameters. If the user table is empty, the service creates and
returns the default sales users before responding.

```json
[
  {
    "user_id": 1,
    "name": "Alex Rep",
    "email": "alex@salesgenie.ai",
    "role": "Sales Representative"
  }
]
```

## 5. Leads

### Lead object

The lead response contains these fields:

```json
{
  "lead_id": 101,
  "company_name": "Acme Cloud",
  "email": "buyer@acme.example",
  "contact_name": "Jane Doe",
  "contact_title": "VP Engineering",
  "industry": "SaaS",
  "phone": "+1-555-0100",
  "lead_status": "New Leads",
  "source": "Website Form",
  "company_size": "100-250",
  "annual_revenue": "$10M-$50M",
  "funding_stage": "Series B",
  "funding_raised": "$30M",
  "location": "New York, US",
  "tech_stack": ["AWS", "Python", "PostgreSQL"],
  "owner_user_id": 1,
  "created_at": "2026-10-26T14:30:00+00:00",
  "updated_at": "2026-10-26T14:30:00+00:00"
}
```

`company_name` and a valid `email` are required. `lead_status` defaults to
`New Leads`; `source` defaults to `CSV`. All other lead fields are optional.

### `POST /api/leads`

Creates one lead. Email uniqueness is enforced by the service.

```json
{
  "company_name": "Acme Cloud",
  "email": "buyer@acme.example",
  "contact_name": "Jane Doe",
  "contact_title": "VP Engineering",
  "industry": "SaaS",
  "source": "Website Form",
  "tech_stack": ["AWS", "Python", "PostgreSQL"],
  "owner_user_id": 1
}
```

Returns a complete [Lead object](#lead-object) with `201`. An existing email
returns `400`.

### `PUT /api/leads/{lead_id}`

Replaces all editable fields for an existing lead. The payload uses the same
fields and validation rules as the create endpoint:

```json
{
  "company_name": "Acme Cloud",
  "email": "new-buyer@acme.example",
  "lead_status": "Qualified",
  "source": "Website Form",
  "tech_stack": ["AWS", "Python"]
}
```

Returns the updated [Lead object](#lead-object) with `200`. Unknown lead IDs
return `404`; an email already used by another lead returns `400`.

### `DELETE /api/leads/{lead_id}`

Deletes the lead and its dependent company insight and score records. Returns
`204 No Content`. Unknown lead IDs return `404`.

### `POST /api/leads/bulk`

Imports an array of the same lead payloads accepted by the single-create
endpoint.

```json
{
  "leads": [
    {
      "company_name": "Acme Cloud",
      "email": "buyer@acme.example",
      "source": "CSV"
    }
  ],
  "skip_duplicates": true
}
```

`skip_duplicates` defaults to `true` and skips emails already in the database
or duplicated within the request. When `false`, the first duplicate causes a
`400` response and the batch is not imported.

```json
{
  "total_received": 1,
  "imported_count": 1,
  "skipped_duplicates": 0,
  "errors": []
}
```

### `GET /api/leads`

Query parameters:

| Parameter | Type | Default | Description |
|---|---|---:|---|
| `search` | string | none | Case-insensitive match against company, email, or contact name |
| `source` | string | none | Filter by a valid source; `"All Sources"` disables the filter |
| `limit` | integer | `50` | Number of results, inclusive range `1..200` |

Results are ordered newest first:

```json
[
  { "...": "Lead object" }
]
```

### `GET /api/leads/stats`

```json
{
  "total_leads": 42,
  "session_additions": 0,
  "ingestion_health": 98.4,
  "pending_ai_scoring": 7
}
```

`pending_ai_scoring` counts leads with no persisted score. `ingestion_health`
is currently a service metric of `100.0` when there are no leads and `98.4`
when at least one lead exists.

## 6. AI lead intelligence

### AI processing model

The intelligence pipeline is synchronous:

```text
request -> research_agent -> qualification_agent -> response
                         \-> persistence for stored-lead endpoints
```

The research agent produces domain analysis, growth indicators, categorized
technology components, and transformation opportunities. The qualification
agent produces a 0-100 score, growth potential, funding analysis, technology
alignment, decision-maker profiles, business needs, and a strategic
recommendation. Both agents use the configured LLM provider cascade.

### `POST /api/leads/{lead_id}/analyze`

Takes no body. Runs the graph for an existing lead, stores a complete immutable
`lead_analysis_runs` record, updates the compatibility `company_insights` and
`lead_scores` records, and returns:

```json
{
  "lead_id": 101,
  "company_name": "Acme Cloud",
  "qualification_score": 82,
  "conversion_probability": 69.7,
  "lead_status": "Qualified",
  "high_growth_potential": true,
  "funding_analysis": "Series B funding supports expansion.",
  "overall_tech_compatibility_score": 88,
  "business_needs": "Reduce deployment friction and forecast variance.",
  "strategic_recommendation": "Prioritize an executive discovery session.",
  "industry_analysis": "Acme Cloud operates in the SaaS sector...",
  "growth_indicators": ["Series B funding signaling expansion"],
  "tech_stack_components": { "Cloud": ["AWS"], "Backend": ["Python"] },
  "transformation_opportunities": [
    {
      "opportunity_name": "Cloud Migration Opportunities",
      "detected": true,
      "confidence": 0.95,
      "details": "Opportunity details",
      "impact_level": "High",
      "estimated_roi_timeline": "3-6 months"
    }
  ],
  "tech_alignment_metrics": [
    { "metric": "Cloud readiness", "score": 88 }
  ],
  "decision_makers": [
    { "name": "Jane Doe", "role": "VP Engineering" }
  ],
  "execution_trace": ["ResearchAgent: ...", "QualificationAgent: ..."],
  "errors": [],
  "execution_latency_seconds": 2.341
}
```

If the score is at least `70`, a lead in `New Leads` is promoted to
`Qualified`. AI failures return `503`; an unknown lead returns `404`.

### `GET /api/leads/{lead_id}/insights`

Returns the latest persisted insight, or `404` if analysis has not yet been
generated:

```json
{
  "analysis_id": 72,
  "lead_id": 101,
  "qualification_score": 82,
  "conversion_probability": 69.7,
  "business_needs": "Reduce deployment friction.",
  "strategic_recommendation": "Prioritize an executive discovery session.",
  "opportunities": [],
  "transformation_opportunities": [],
  "industry_analysis": "Acme Cloud operates in the SaaS sector...",
  "growth_indicators": ["Series B funding signaling expansion"],
  "tech_alignment": [],
  "decision_maker_summary": [],
  "decision_makers": [],
  "execution_trace": [],
  "generated_at": "2026-10-26 14:31:02+00:00"
}
```

The latest complete structured run is returned, with JSONB fields decoded into
arrays/objects. Older leads without a `lead_analysis_runs` row are automatically
rescored when their predictive dossier is opened.

### `POST /api/leads/batch-analyze`

```json
{
  "lead_ids": [101, 102, 103]
}
```

Returns one result per requested ID. A failed item is represented in the
result list rather than failing the entire batch:

```json
[
  { "lead_id": 101, "qualification_score": 82, "...": "analysis fields" },
  { "lead_id": 999, "error": "Lead with id 999 not found in database." }
]
```

### `POST /api/intelligence/analyze-prospect`

Runs the same two-agent pipeline without requiring a database lead and does
not persist results. `company_name` is required; the remaining fields are
optional and have the defaults shown:

```json
{
  "company_name": "Acme Cloud",
  "industry": "Technology",
  "contact_name": "Decision Maker",
  "email": "buyer@acme.example",
  "phone": "+1-555-0100",
  "company_size": "100-250",
  "annual_revenue": "$10M-$50M",
  "funding_stage": "Series B",
  "capital_raised": "$30M",
  "location": "New York, US",
  "tech_stack": "AWS, Python, PostgreSQL"
}
```

The response is the raw `AgentState`, including intermediate fields such as
`industry_domain_analysis`, `growth_indicators`, `tech_stack_components`,
`funding_analysis`, `overall_tech_compatibility_score`, `execution_trace`, and
`errors`, in addition to the qualification outputs. This endpoint returns
`503` when an LLM provider cannot produce complete agent output.

### `GET /api/intelligence/architecture`

Returns the current orchestration metadata:

```json
{
  "framework": "LangGraph",
  "nodes": ["research_agent", "qualification_agent"],
  "architecture_diagram_mermaid": "```mermaid\\nflowchart TD\\n..."
}
```

## 7. Scoring

### `GET /api/scoring/queue`

Returns every lead with its latest score. Unscored leads are included:

```json
[
  {
    "lead_id": 101,
    "company_name": "Acme Cloud",
    "contact_name": "Jane Doe",
    "contact_title": "VP Engineering",
    "email": "buyer@acme.example",
    "funding_stage": "Series B",
    "industry": "SaaS",
    "score": 82,
    "conversion_probability": 69.7,
    "priority": "hot"
  },
  {
    "lead_id": 102,
    "company_name": "Beta Inc",
    "contact_name": "N/A",
    "contact_title": "Executive",
    "email": "contact@beta.example",
    "funding_stage": "N/A",
    "industry": "Technology",
    "score": null,
    "conversion_probability": null,
    "priority": "unscored"
  }
]
```

Priority is `hot` for score `>=75`, `warm` for `40..74`, and `cold` below
`40`.

### `GET /api/leads/{lead_id}/dossier`

Returns the lead profile plus `scoring` and `insights`. If either is missing,
the endpoint automatically runs and persists analysis before responding.

```json
{
  "lead_id": 101,
  "company_name": "Acme Cloud",
  "contact_name": "Jane Doe",
  "contact_title": "VP Engineering",
  "email": "buyer@acme.example",
  "location": "New York, US",
  "funding_stage": "Series B",
  "tech_stack": ["AWS", "Python"],
  "scoring": {
    "score": 82,
    "conversion_probability": 69.7,
    "priority": "hot"
  },
  "insights": { "...": "CompanyInsightResponse" }
}
```

### `POST /api/leads/{lead_id}/score`

Takes no body. Re-runs the AI pipeline and returns:

```json
{
  "scoring": {
    "score": 82,
    "conversion_probability": 69.7,
    "priority": "hot"
  },
  "insights": { "...": "LeadAnalysisResponse" }
}
```

### `POST /api/leads/score-batch`

Takes no body. Scores every lead that has no existing score and skips leads
that already have one:

```json
{
  "scored_count": 12
}
```

## 8. AI outreach

### `POST /api/outreach/generate`

Generates subject options and a personalized email using the lead profile,
latest persisted intelligence (when available), and the selected strategy.

```json
{
  "lead_id": 101,
  "angle": "Cloud Scale & Efficiency",
  "tone": "Consultative / Executive",
  "custom_note": "Mention the recent platform launch.",
  "preferred_provider": "auto"
}
```

`angle`, `tone`, and `custom_note` default to the values above and
`preferred_provider` is optional. The provider may be `auto`, `gemini`,
`openai`, `grok`, or `ollama`, subject to configured availability.

```json
{
  "subject_options": ["Scaling Acme Cloud without added platform overhead"],
  "selected_subject": "Scaling Acme Cloud without added platform overhead",
  "body": "Hi Jane, ...",
  "hook_score": 91,
  "word_count": 87,
  "reading_time_seconds": 25,
  "personalization_triggers": ["Series B expansion", "AWS platform"],
  "call_to_action": "Would a 20-minute conversation next week be useful?",
  "provider_used": "gemini",
  "angle": "Cloud Scale & Efficiency",
  "tone": "Consultative / Executive"
}
```

The lead must exist (`404`). Incomplete or unavailable AI output returns
`503`.

### `POST /api/outreach/save-draft`

Acknowledges a draft save. It currently does not persist the subject/body in a
dedicated outreach table.

```json
{
  "lead_id": 101,
  "subject": "Scaling Acme Cloud",
  "body": "Hi Jane, ...",
  "status": "draft"
}
```

Response:

```json
{
  "status": "saved",
  "lead_id": 101,
  "company_name": "Acme Cloud",
  "subject": "Scaling Acme Cloud"
}
```

### `POST /api/outreach/send`

Accepts:

```json
{
  "lead_id": 101,
  "subject": "Scaling Acme Cloud",
  "body": "Hi Jane, ..."
}
```

Response:

```json
{
  "status": "sent",
  "lead_id": 101,
  "recipient": "buyer@acme.example",
  "company_name": "Acme Cloud",
  "subject": "Scaling Acme Cloud",
  "lead_status": "Proposal"
}
```

When the current status is `New Leads` or `Qualified`, this operation changes
it to `Proposal`. The current implementation acknowledges the operation; it
does not call an external email delivery provider.

## 9. LLM provider status

### `GET /api/llm/providers`

Reports configuration and the most recently used provider:

```json
{
  "gemini": { "available": true, "model": "gemini-1.5-pro" },
  "openai": { "available": false, "model": "gpt-4o-mini" },
  "grok": { "available": false, "model": "grok-2-latest" },
  "ollama": {
    "available": true,
    "model": "llama3",
    "base_url": "http://localhost:11434"
  },
  "preferred_provider": "auto",
  "last_used_provider": "gemini"
}
```

Availability is determined by the backend's configured credentials/connectivity.
Do not expose provider secrets or use this endpoint as an authorization check.

## 10. Client integration examples

```bash
# Create a lead
curl -X POST http://localhost:8000/api/leads \
  -H 'Content-Type: application/json' \
  -d '{"company_name":"Acme Cloud","email":"buyer@acme.example","source":"CSV"}'

# Search leads
curl 'http://localhost:8000/api/leads?search=acme&limit=20'

# Generate and persist intelligence
curl -X POST http://localhost:8000/api/leads/101/analyze

# Generate outreach from the latest intelligence
curl -X POST http://localhost:8000/api/outreach/generate \
  -H 'Content-Type: application/json' \
  -d '{"lead_id":101,"angle":"Cloud Scale & Efficiency","tone":"Consultative / Executive"}'
```

AI endpoints are synchronous and can take substantially longer than simple
CRUD endpoints. Clients should use request timeouts appropriate to the
operation (the bundled frontend allows up to 300 seconds for AI generation
when using a local model).
