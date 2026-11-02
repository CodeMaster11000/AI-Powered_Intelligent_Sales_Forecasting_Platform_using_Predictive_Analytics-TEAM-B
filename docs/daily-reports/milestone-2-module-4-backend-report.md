# Milestone 2 - Module 4 Backend Daily Report

**Date:** 2026-10-30  
**Area:** Lead scoring and conversion probability  
**Role:** Backend engineering

## Work completed

Implemented an explainable lead-scoring service in
[`modules/module4_scoring.py`](../../../modules/module4_scoring.py).

The score is calculated from four dimensions:

| Component | Weight |
|---|---:|
| Engagement | 20% |
| Fit | 30% |
| Intent | 30% |
| Decision readiness | 20% |

Each component is bounded from `0` to `100`. The weighted result becomes the
lead score, and conversion probability is calculated as:

```text
conversion_probability = lead_score * 0.85
```

The probability is capped between `0` and `100`.

## Signals used

The backend scoring service uses the data currently available in the system:

- lead lifecycle status;
- acquisition source;
- contact name, title, and email;
- company industry, size, and revenue;
- funding stage;
- technology stack;
- AI-detected business needs;
- transformation opportunities;
- high-growth potential;
- decision-maker analysis; and
- lead ownership.

Behavioral signals such as email opens, link clicks, website visits, and
meeting activity are not included yet because those event models are not
implemented in the current schema.

## Database changes

Added the following fields to `lead_scores`:

```text
engagement_score
fit_score
intent_score
decision_readiness_score
scoring_version
scoring_factors
```

The `scoring_factors` JSON field stores human-readable explanations for each
component score. `scoring_version` currently stores `module4-v1`.

Added and applied migration:

[`4f8e2c7a1b90_add_module4_score_components.py`](../../../migrations/versions/4f8e2c7a1b90_add_module4_score_components.py)

The migration also adds database checks ensuring every component remains within
the `0..100` range.

## API changes

The existing scoring endpoints now expose component-level results.

### `GET /api/scoring/queue`

Scored queue items now include:

```json
{
  "score": 82,
  "conversion_probability": 69.7,
  "engagement_score": 80,
  "fit_score": 90,
  "intent_score": 85,
  "decision_readiness_score": 70,
  "priority": "hot"
}
```

Unscored leads return `null` for the score components.

### `GET /api/leads/{lead_id}/dossier`

The dossier now includes the component scores, scoring version, and scoring
factor explanations in the `scoring` object.

### `POST /api/leads/{lead_id}/score`

Re-running a score recalculates and persists all four components, the weighted
score, conversion probability, and factor explanations.

## Integration behavior

The scoring service is invoked during stored lead intelligence analysis. The
existing AI research and qualification pipeline remains in place, while the
new Module 4 service provides a deterministic and explainable scoring layer
for persistence and API consumption.

The existing lifecycle behavior is preserved: a `New Leads` record is promoted
to `Qualified` when its resulting score is at least `70`.

## Validation

- Full backend test suite: **26 passed**
- Module 4 scoring test added for all four dimensions and factor groups
- Alembic migration applied successfully
- Current migration head: `4f8e2c7a1b90`
- Python compilation completed successfully
- Database range constraints verified through the migration

## Current limitations

- No behavioral engagement-event table exists yet.
- Conversion probability is a deterministic business heuristic, not a
  statistically trained calibration model.
- Scores are recalculated synchronously during analysis.
- Score history is not yet exposed as a dedicated API endpoint.
- Authentication and authorization are not currently implemented on scoring
  endpoints.

## Related implementation files

- [`module4_scoring.py`](../../../modules/module4_scoring.py)
- [`module2_intelligence.py`](../../../modules/module2_intelligence.py)
- [`lead_scores.py`](../../../backend/database/models/lead_scores.py)
- [`backend/main.py`](../../../backend/main.py)
- [`test_lead_intelligence.py`](../../../backend/tests/test_lead_intelligence.py)
- [`api-contract.md`](../api-contract.md)
