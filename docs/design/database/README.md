# Database Design

PostgreSQL 16 (runs in Docker, see the root `SETUP.md`). This folder is the source of truth for the schema: the code that creates the tables must match it, and any schema change updates these files in the same pull request.

| File | What it is |
|------|-----------|
| [er-diagram.md](er-diagram.md) | ER diagram (Mermaid, renders on GitHub) |
| `er-diagram.png` / `.svg` | Styled export for slides and reports |
| `er-diagram.mmd` / `.dot` | Editable diagram sources |
| [data-dictionary.md](data-dictionary.md) | Every table and column: type, nullable, meaning, allowed values, delete rules, indexes |

## The model in one paragraph

A sales rep (**users**) owns prospects (**leads**). Each lead gets scored over time (**lead_scores**), analyzed through immutable **lead_analysis_runs**, and profiled through **company_insights**. The rep generates cold emails and manages their lifecycle through (**outreach_emails**). Everything hangs off `leads`.

| Table | Milestone | Purpose |
|-------|-----------|---------|
| users | M1 | the people using the app |
| leads | M1 | prospects: company, contact, profile data, pipeline stage |
| lead_scores | M1 | every score a lead has had; newest row is the current score |
| company_insights | M1 | AI or rule-based profile of the company |
| lead_analysis_runs | M2 | immutable structured output from each multi-agent analysis |
| outreach_emails | M2 | generated cold emails |

Create only the tables of the milestone you are working on.

## Design decisions

- **Score history is preserved.** Each scoring run creates a `lead_scores` row with four component scores, conversion probability, scoring version, and explainability factors.
- **Analysis history is preserved.** Each multi-agent run creates a `lead_analysis_runs` row containing structured research, qualification, recommendation, and execution metadata.
- **One row per lead, not separate company and contact tables.** Proper CRMs split them, but that doubles the import and UI logic. Revisit if one company ever needs many contacts.
- **`company_insights` is one row per lead** and is overwritten on regeneration; history isn't valuable there.
- **Structured analysis fields are `jsonb`** where the application returns lists or nested objects; promote them to tables only if individual items need independent querying or lifecycle management.
- **Dashboard numbers** (conversion rate, pipeline value, averages) are computed with queries over these tables, not stored, so they never go stale.
- **Lead status and source values are database-constrained** to the values currently supported by the application.

## Conventions

- Lowercase plural snake_case table names, snake_case columns. (`user` is a reserved word in Postgres, which is another reason the table is `users`.)
- PKs: bigint identity columns named for their table (`lead_id`, `score_id`, etc.). Timestamps: `timestamptz`, stored in UTC.
- Foreign keys are real constraints. Restricted-value columns use database checks, so bad data can't enter from any code path.
- Deleting a lead deletes everything attached to it.

## Change process

1. Edit `data-dictionary.md` and the diagram source (`er-diagram.md` / `.mmd` / `.dot`); re-export the PNG/SVG if the diagram changed.
2. Put the schema change and the doc change in the **same PR**, and have the backend developer review it.
3. Once the schema is more than a day or two old, use migrations (Alembic is already in `requirements.txt`) so teammates update their local DB by running a command instead of wiping data.
