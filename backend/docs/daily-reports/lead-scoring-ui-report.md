# Lead scoring UI implementation report

## Scope

This phase verified the lead scoring API, persistence model, scoring page, and
its connection to the AI intelligence and outreach workflows.

## Findings and changes

- The scoring queue, dossier, rescore, and batch-score endpoints were wired
  correctly.
- The persisted explainability data used a different shape from the scoring
  page. The scoring result now exposes factor objects with `label`, `score`,
  `max`, and `explanations`.
- Existing database rows are supported through a compatibility normalizer in
  the dossier endpoint.
- The scoring page now distinguishes an unavailable API from an empty lead
  list instead of showing the same error for both cases.
- Rescore failures are now shown to the user rather than always reporting
  success.
- Provider timeout handling was tightened so unavailable local Ollama
  instances do not make analysis exceed the intended response budget.

## UI recommendation implemented

Predictive Scoring remains a dedicated workspace. The intelligence page is
for company research and qualification, while scoring owns the priority queue,
factor breakdown, and rescore action. The existing navigation from scoring to
Cold Outreach is preserved. A compact score summary should remain on the
intelligence page in a future visual pass, but duplicating the full queue there
would make the workflow harder to scan.

## Validation

- Python compilation passed.
- Lead intelligence and scoring tests passed after provider timeout
  stabilization.
- The full backend test suite should be rerun after the draft phase because
  the next phase changes shared outreach routes and schemas.
