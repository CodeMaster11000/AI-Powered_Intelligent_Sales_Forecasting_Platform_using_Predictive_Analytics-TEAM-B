# Milestone 1 Test Report

## Report status

This report records the test cases and the validation method for Milestone 1.
The focused run below was executed after installing both
`requirements-dev.txt` and the optional AI dependencies in
`requirements-ai.txt`.

**Observed run after fixes:** 22 passed, 1 warning in 14.22 seconds.

The warning is a deprecation warning from the installed Google GenAI
dependency and does not cause a test failure.

The two failures observed in the initial run were fixed:

1. Intelligence calls could exceed the 5-second SLA because two unbounded
   remote provider calls ran sequentially. Gemini calls now have a bounded
   timeout, and the research and qualification agents use explicit
   deterministic rule-based results when a provider times out or returns
   incomplete data.
2. Outreach responses could omit the company name or fail completely when a
   provider timed out. The formatter now enforces company context, and the
   agent has an explicit local draft fallback containing the lead's company,
   contact, technology, and requested angle.

## Test cases

| ID | Area | Expected result |
|---|---|---|
| M1-T01 | Single lead creation | Valid lead is mapped to a `Lead` record and committed |
| M1-T02 | Single lead duplicate | Existing email raises a domain validation error and is not committed |
| M1-T03 | Bulk import | Existing and in-batch duplicate emails are skipped by default |
| M1-T04 | Bulk import strict mode | A duplicate aborts strict import without committing a partial batch |
| M1-T05 | Request validation | Invalid email and unsupported lifecycle status are rejected |
| M1-T06 | Agent compilation | LangGraph graph is available with research and qualification nodes |
| M1-T07 | Agent profiling | Industry analysis and categorized technology components are returned |
| M1-T08 | Opportunity detection | ERP, cloud, and automation opportunities are detected for the fixture |
| M1-T09 | Qualification output | Score, business needs, recommendation, and decision-maker data are returned |
| M1-T10 | Latency | End-to-end fixture completes below 5 seconds |

## Coverage and limitations

The repository already contains agent tests for Module 2 and outreach tests.
The new lead-management tests cover the pure service behavior without
requiring a live database. A PostgreSQL-backed integration run is still
required to validate Alembic constraints, foreign keys, timestamps, and
transaction behavior against the real schema.

Milestone 1 acceptance is not marked fully signed off by this report alone:
the pasted milestone plan also calls for a sample dataset, UI integration,
ingestion coverage across all planned vectors, and a demo/sign-off review.
Those items need evidence from the team before being marked complete.
