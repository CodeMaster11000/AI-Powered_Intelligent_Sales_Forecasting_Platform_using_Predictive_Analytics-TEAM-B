# Database Design

PostgreSQL 16 (runs in Docker, see root `SETUP.md`). This folder is the source of truth for the schema design; the code that creates the tables must match it, and any schema change updates these files in the same pull request.

| File | What it is |
|------|-----------|
| [er-diagram.md](er-diagram.md) | ER diagram (Mermaid, renders on GitHub) |
| `er-diagram.png` / `.svg` | Styled export of the same diagram, for slides and reports |
| `er-diagram.mmd` / `.dot` | Editable diagram sources |
| [data-dictionary.md](data-dictionary.md) | Every table and column: type, nullable, meaning, allowed values |

## Overview

Eight tables from SRS section 2.4. **Leads** is the center: five tables point at it, and **Users** owns Leads and analytics.

| Table | Milestone | Role |
|-------|-----------|------|
| users | 1 | accounts and roles (RBAC) |
| leads | 1 | prospects, profile data, lifecycle stage |
| company_insights | 1 | AI/rule-generated company intelligence and qualification score |
| lead_scores | 2 | predictive score history |
| outreach_campaigns | 2 | generated outreach emails |
| sales_interactions | 3 | call/meeting summaries, action items |
| crm_sync_logs | 3 | CRM sync audit trail |
| sales_analytics | 4 | dashboard aggregates |

## Conventions

- Tables: lowercase plural snake_case (`leads`). Columns: snake_case. (The SRS capitalizes names; lowercase avoids quoting headaches in Postgres. `user` is a reserved word, which is why the table is `users`.)
- PKs: bigint identity. Timestamps: timestamptz in UTC.
- Foreign keys are real constraints, and every FK column gets an index.
- Restricted-value columns (role, lead_status, source) use a database-level check so bad data can't enter from any code path.

## Change process

1. Edit `data-dictionary.md` and the diagram source (`er-diagram.md` / `.mmd` / `.dot`).
2. Re-export the PNG/SVG if the diagram changed.
3. Put the schema change and the doc change in the **same PR**, and ask the backend person to review.
4. Use migrations (Alembic is already in requirements) once the schema is more than a day old, so teammates update their local DBs by running a command, not by wiping data.
