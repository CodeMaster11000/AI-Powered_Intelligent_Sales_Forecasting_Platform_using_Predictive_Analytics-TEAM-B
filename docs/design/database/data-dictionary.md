# Data Dictionary

This dictionary reflects the current SQLAlchemy models and Alembic migrations.
Primary keys are bigint identity columns and timestamps are UTC `timestamptz`.

## users

`user_id` PK, `name` required, `email` required and unique, `role` required
(`Sales Representative`, `BDR`, `Sales Manager`, or `RevOps`), optional
`department`, and `created_at`.

## leads

`lead_id` PK, optional `owner_user_id` FK to `users` (`SET NULL`), required
`company_name`, `email`, and `source`, plus optional `industry`, `contact_name`,
`contact_title`, `phone`, `company_size`, `annual_revenue`, `funding_stage`,
`funding_raised`, `location`, and JSONB `tech_stack`. `lead_status` defaults to
`New Leads` and is constrained to the supported pipeline statuses. The table
also stores `created_at` and `updated_at`.

## lead_scores

Each scoring run is retained. Columns are `score_id` PK, `lead_id` FK,
`lead_score`, `conversion_probability`, four component scores
(`engagement_score`, `fit_score`, `intent_score`,
`decision_readiness_score`), `scoring_version`, JSONB `scoring_factors`, and
`generated_at`. Score and component values are constrained to `0..100`.

## company_insights

Columns are `insight_id` PK, `lead_id` FK, `business_needs`, `opportunities`,
`industry_analysis`, `qualification_score`, `growth_indicators`,
`tech_alignment`, `decision_maker_summary`, and `generated_at`.

## lead_analysis_runs

Immutable structured output from each analysis run: `analysis_id` PK, `lead_id`
FK, `qualification_score`, `high_growth_potential`, `funding_analysis`,
`overall_tech_compatibility_score`, `industry_domain_analysis`,
`business_needs_summary`, `strategic_recommendation`, JSONB structured output
fields (`growth_indicators`, `tech_stack_components`,
`transformation_opportunities`, `tech_alignment_metrics`, `decision_makers`,
`execution_trace`, `errors`), `execution_latency_seconds`, and `generated_at`.

## outreach_emails

Columns are `id` PK, `lead_id` FK, optional `user_id` FK, required `subject`,
`body`, and `status` (`draft`, `sent`, or `archived`). Generation metadata is
stored in optional `provider`, `model_name`, `angle`, `tone`, `custom_note`,
JSONB `subject_options`, and JSONB `generation_metadata`. Lifecycle timestamps
are `created_at`, `updated_at`, optional `sent_at`, and optional
`archived_at`.

## Relationships and delete rules

| Parent | Child | Cardinality | On parent delete |
|---|---|---:|---|
| users | leads (`owner_user_id`) | 1:N | set null |
| users | outreach_emails (`user_id`) | 1:N | set null |
| leads | lead_scores | 1:N | cascade |
| leads | company_insights | 1:N | cascade |
| leads | lead_analysis_runs | 1:N | cascade |
| leads | outreach_emails | 1:N | cascade |

## Current database constraints

- `leads.lead_status`: `New Leads`, `Qualified`, `Proposal`, `Negotiation`, `Closed Won`
- `leads.source`: `CRM`, `Website Form`, `LinkedIn`, `Sales Entry`, `CSV`
- `outreach_emails.status`: `draft`, `sent`, `archived`
- Score, probability, and component fields: `0..100`
- `users.email` is unique.
