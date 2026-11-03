# Persistent outreach draft workflow report

## Scope

This phase completes the draft lifecycle behind the Cold Outreach page. Drafts
are now durable database records rather than Streamlit-only session state.

## Backend changes

- Extended `outreach_emails` with lifecycle metadata:
  provider, model name, angle, tone, custom notes, subject alternatives,
  generation metadata, updated time, sent time, and archived time.
- Added forward-only migration
  `5a1b2c3d4e5f_extend_outreach_drafts`.
- Added typed draft request/response schemas in `backend/schema.py`.
- Added draft list and detail routes.
- Added draft update and archive routes.
- Existing `POST /api/outreach/save-draft` now accepts generation metadata.
- Sending an existing draft marks that record as sent. Sending without a
  draft id creates a sent outreach record.
- Sent and archived records cannot be edited.

## UI changes

- Outreach Studio loads saved drafts for the selected lead.
- The latest saved draft is restored after a page reload.
- Users can select and load older saved drafts.
- Save updates an existing draft when one is loaded.
- New saves persist provider, angle, tone, custom notes, and subject options.
- Users can archive drafts without deleting their history.
- Send actions preserve the saved draft id when available.
- Provider help text now matches fallback behavior.

## Lifecycle

```text
generated -> draft -> sent
                    \
                     -> archived
```

Archived drafts remain queryable for history but are not editable. Sent drafts
are immutable from the draft editor.

## Validation

- Full backend suite: 30 tests passed.
- Python compilation passed.
- `alembic upgrade head` applied successfully.
- `alembic check` reports no pending model/migration operations.

## Follow-up

The current application has no authenticated user context, so `user_id`
remains nullable. Actual email-provider delivery and delivery failure states
should be added when outbound email infrastructure is introduced.
