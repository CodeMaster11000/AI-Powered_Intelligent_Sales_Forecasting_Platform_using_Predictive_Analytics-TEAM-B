# Milestone 1 Test Plan

## Scope

The Milestone 1 test scope covers lead ingestion and validation, the
LangGraph intelligence workflow, score/insight output, and the API-facing
contract surfaces that are implemented in this repository.

## Test layers

| Layer | Current coverage |
|---|---|
| Lead service unit tests | Single-create success and duplicate rejection; bulk duplicate handling; case-insensitive email matching |
| Schema validation | Email format, required company name/email, status and source enum values |
| Agent tests | Graph compilation, latency target, company profiling, transformation opportunities, qualification score/personas, Mermaid topology |
| Outreach regression tests | Existing tone-specific agent and wrapper tests |
| API smoke tests | Existing LLM provider endpoint test; health and route-level database tests should be added when a disposable test database fixture is available |

## Commands

Install development dependencies, then run:

```bash
pytest -q
```

For only the Milestone 1 lead and agent tests:

```bash
pytest -q backend/tests/test_lead_management.py backend/tests/test_lead_intelligence.py
```

## Acceptance evidence

- All imported leads must be validated through the Pydantic request models.
- Duplicate emails must not create duplicate records.
- Bulk import must report imported and skipped counts.
- Agent output must include a score in the inclusive range 0-100.
- Agent execution must remain below the documented 5-second target in the
  existing test environment.
- Persistence and schema-integrity validation require PostgreSQL and Alembic;
  they are not replaced by mock-only tests.

