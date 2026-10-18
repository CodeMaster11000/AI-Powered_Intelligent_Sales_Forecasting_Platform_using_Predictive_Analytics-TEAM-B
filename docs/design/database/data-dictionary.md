# Data Dictionary

Conventions: table and column names are lowercase snake_case; primary keys are `bigint` identity columns named `id`; all timestamps are `timestamptz` (UTC). "Null: no" means the column is required.
Milestone tags: **M1** built first, **M2**/**M3** later.

## users (M1)
| Column | Type | Null | Notes |
|--------|------|------|-------|
| id | bigint | no | PK |
| name | text | no | |
| email | text | no | unique |
| role | text | no | `rep`, `manager`, `admin` |
| created_at | timestamptz | no | default now |

## leads (M1)
One row per prospect (a company plus its main contact).

| Column | Type | Null | Notes |
|--------|------|------|-------|
| id | bigint | no | PK |
| owner_id | bigint | yes | FK users.id, the rep who owns the lead; on user delete set null |
| company_name | text | no | |
| industry | text | yes | |
| contact_name | text | yes | |
| contact_title | text | yes | used to judge decision-maker level when scoring |
| email | text | no | unique; the duplicate check on import |
| phone | text | yes | |
| company_size | text | yes | e.g. `250-500` |
| location | text | yes | |
| funding_stage | text | yes | e.g. `Series C` |
| tech_stack | jsonb | yes | list of strings, e.g. `["AWS","Python"]` |
| stage | text | no | pipeline stage, default `new` |
| source | text | no | how it entered the system, default `csv` |
| created_at | timestamptz | no | default now |
| updated_at | timestamptz | no | refreshed on every change |

## lead_scores (M1)
Every score a lead has ever had. The current score is the newest row.

| Column | Type | Null | Notes |
|--------|------|------|-------|
| id | bigint | no | PK |
| lead_id | bigint | no | FK leads.id, on lead delete cascade |
| score | int | no | 0 to 100 |
| priority | text | no | `hot`, `warm`, `cold` |
| factors | jsonb | yes | breakdown of why, e.g. `{"company_growth": 25, "industry_match": 22}` |
| reason | text | no | what triggered it: `csv_import`, `manual_rescore`, `call_logged`... |
| created_at | timestamptz | no | default now |

## company_insights (M1)
One profile per lead; regenerating overwrites it.

| Column | Type | Null | Notes |
|--------|------|------|-------|
| id | bigint | no | PK |
| lead_id | bigint | no | FK leads.id, **unique** (one per lead), on lead delete cascade |
| summary | text | yes | short company overview |
| opportunities | text | yes | where the product could fit |
| pain_points | text | yes | likely problems the company has |
| created_at | timestamptz | no | refreshed when regenerated |

## outreach_emails (M2)
| Column | Type | Null | Notes |
|--------|------|------|-------|
| id | bigint | no | PK |
| lead_id | bigint | no | FK leads.id, on lead delete cascade |
| user_id | bigint | yes | FK users.id, who generated it; on user delete set null |
| subject | text | no | |
| body | text | no | |
| status | text | no | `draft`, `sent`; default `draft` |
| created_at | timestamptz | no | default now |

## interactions (M3)
Calls, meetings and notes with a lead.

| Column | Type | Null | Notes |
|--------|------|------|-------|
| id | bigint | no | PK |
| lead_id | bigint | no | FK leads.id, on lead delete cascade |
| user_id | bigint | yes | FK users.id, who logged it; on user delete set null |
| type | text | no | `call`, `meeting`, `email_reply`, `note` |
| occurred_at | timestamptz | no | when it happened |
| raw_notes | text | yes | pasted transcript or notes |
| summary | text | yes | generated summary |
| action_items | jsonb | yes | list of `{task, owner, due_date}` |
| created_at | timestamptz | no | default now |

---

## Allowed values (enforce with database checks)
- **leads.stage**: `new`, `qualified`, `proposal`, `negotiation`, `won`, `lost`
- **leads.source**: `csv`, `manual`
- **lead_scores.priority**: `hot`, `warm`, `cold`
- **lead_scores.score**: 0 to 100 inclusive
- **users.role**: `rep`, `manager`, `admin`
- **outreach_emails.status**: `draft`, `sent`
- **interactions.type**: `call`, `meeting`, `email_reply`, `note`

## Relationships
| Parent | Child | Cardinality | On parent delete |
|--------|-------|-------------|------------------|
| users | leads (owner_id) | 1 : N | set null |
| users | outreach_emails (user_id) | 1 : N | set null |
| users | interactions (user_id) | 1 : N | set null |
| leads | lead_scores | 1 : N | cascade |
| leads | company_insights | 1 : 1 | cascade |
| leads | outreach_emails | 1 : N | cascade |
| leads | interactions | 1 : N | cascade |

## Indexes
Index every foreign key column (`owner_id`, `lead_id`, `user_id`), plus `leads.stage` and `lead_scores (lead_id, created_at)` so "latest score per lead" is fast. `leads.email` and `users.email` are already indexed by their unique constraints.
