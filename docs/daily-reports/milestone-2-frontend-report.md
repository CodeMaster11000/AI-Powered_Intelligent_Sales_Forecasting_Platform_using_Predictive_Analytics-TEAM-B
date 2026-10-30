# Milestone 2 / Module 3 Frontend Developer Report

**Project:** SalesGenie AI Platform  
**Scope:** Module 3 - Streamlit Outreach tab  
**Tasks covered:**

1. Build the Streamlit AI Email Generator tab.
2. Support draft generation, refresh, editing, copy, save, and send actions
   through the outreach backend endpoints.

**Implementation status:** Outreach Studio UI and API integration implemented;
backend persistence and real delivery limitations also apply to the UI.

## 1. Executive summary

The Streamlit frontend includes a dedicated `Cold Outreach` workflow tab. It
loads the backend scoring queue, lets a sales representative select a target
prospect, loads the lead's AI dossier, presents provider and outreach strategy
controls, generates a personalized draft, and exposes an editable draft
editor.

The UI supports subject-line A/B variants, body editing, personalization
signals, hook score, word count, estimated reading time, CTA display, copy
view, save-draft, and send actions. It also preserves draft state per lead and
refreshes the app when a new generation is requested.

The frontend correctly reflects the current backend contract: save now creates
a durable draft record, while send is still acknowledged without external
email delivery.

## 2. Requirement traceability

| Requirement from the task | Repository evidence | Status |
|---|---|---|
| Dedicated Streamlit outreach tab | `Cold Outreach` routing in [`frontend/app.py`](../../frontend/app.py) | Implemented |
| Target prospect selection | [`render_outreach_studio`](../../frontend/components/outreach_studio.py) | Implemented |
| Load scoring queue and dossier | [`api_client.py`](../../frontend/utils/api_client.py), outreach studio | Implemented |
| Strategy controls | Provider, value-angle, tone, and custom-note controls in outreach studio | Implemented |
| Generate/refresh draft | `generate_outreach_api` and `Generate / Refresh Draft` button | Implemented |
| Edit email content | Streamlit subject selector and body text area | Implemented |
| View/copy content | `View / Copy` popover with formatted subject/body | Implemented |
| Save draft | `save_outreach_draft_api` | UI action and server persistence implemented |
| Send email | `send_outreach_email_api` | UI action implemented; real delivery pending |
| Show personalization evidence | Trigger pills, detected signals, provider badge, CTA and metrics | Implemented |

## 3. User workflow

```text
Cold Outreach tab
      |
      v
GET /api/scoring/queue
      |
      v
Select company/contact/priority
      |
      v
GET /api/leads/{lead_id}/dossier
      |
      v
Choose provider, angle, tone, and custom note
      |
      v
POST /api/outreach/generate
      |
      v
Select subject + edit body
      |
      +--> View / Copy
      +--> POST /api/outreach/save-draft
      +--> POST /api/outreach/send
```

The tab is routed from the main application in
[`frontend/app.py`](../../frontend/app.py), alongside Leads & Ingestion, AI
Lead Intelligence, and Predictive Scoring.

## 4. Implemented UI surfaces

### 4.1 Prospect selection

[`frontend/components/outreach_studio.py`](../../frontend/components/outreach_studio.py)
uses the authoritative scoring queue rather than a separate local lead list.
Each option includes company, contact, and priority. If the user navigates
from the scoring hub, `outreach_target_lead_id` preselects the forwarded lead.

### 4.2 Dossier-backed context

The selected lead's dossier supplies:

- technology stack;
- funding stage;
- contact title;
- email address; and
- the backend's persisted scoring and intelligence context.

The UI displays detected context signals before generation so the
representative can see what the draft is expected to use.

### 4.3 Strategy controls

The left strategy pane includes:

- automatic provider selection;
- Gemini, OpenAI, Grok, and Ollama choices;
- Cloud Scale & Infrastructure Efficiency;
- Pipeline Variance & Forecasting ROI;
- Tech Stack Modernization;
- Operational Cost Reduction & Security;
- consultative, direct, and problem-centric tones; and
- optional custom representative notes.

The selected values are sent in the generation request as `angle`, `tone`,
`custom_note`, and `preferred_provider`.

### 4.4 Draft editor and quality indicators

The right editor pane provides:

- provider-used badge;
- subject-line selector for A/B variants;
- editable email body;
- personalization trigger pills;
- hook score;
- live word count based on the edited body;
- estimated reading time;
- call-to-action display; and
- draft version keys scoped to the lead.

The versioned Streamlit keys avoid reusing one prospect's edited body for a
different prospect after a rerun.

### 4.5 Actions

The action row provides:

- **View / Copy:** renders a copy-friendly subject and body block;
- **Save as Draft:** sends the selected subject and edited body to
  `POST /api/outreach/save-draft`; and
- **Send Email:** sends the selected subject and edited body to
  `POST /api/outreach/send`.

Success/failure messages are surfaced through Streamlit toast or error
feedback. The selected body is taken from the editor, so user edits are sent
instead of the original generated body.

## 5. Frontend integration details

[`frontend/utils/api_client.py`](../../frontend/utils/api_client.py) defines
the HTTP boundary:

| Client helper | Backend route | Timeout |
|---|---|---:|
| `fetch_scoring_queue_api` | `GET /api/scoring/queue` | 3 seconds |
| `fetch_lead_dossier_api` | `GET /api/leads/{lead_id}/dossier` | 4 seconds |
| `generate_outreach_api` | `POST /api/outreach/generate` | 25 seconds |
| `fetch_llm_providers_api` | `GET /api/llm/providers` | 2 seconds |
| `save_outreach_draft_api` | `POST /api/outreach/save-draft` | 4 seconds |
| `send_outreach_email_api` | `POST /api/outreach/send` | 5 seconds |

The client uses `BACKEND_API_URL` with a default of
`http://localhost:8000`. It returns typed success/data or error tuples for
save/send and safe empty values for read/generation failures so the UI can
show an unavailable-backend state.

## 6. Frontend state and resilience

The application uses Streamlit session state for:

- active navigation tab;
- forwarded target lead;
- current draft;
- draft lead ID;
- draft version; and
- versioned body widget values.

The component stops rendering when the queue or dossier cannot be loaded,
shows an actionable error when generation fails, and avoids displaying an
uninitialized draft. Provider status has a fallback shape so the controls can
still render when the provider-status endpoint is unavailable.

## 7. Validation and evidence

The current repository contains backend tests for the outreach service and
API provider-status shape in
[`backend/tests/test_outreach_agent.py`](../../backend/tests/test_outreach_agent.py).
The frontend implementation is primarily Streamlit-rendering code and has no
dedicated component test suite, browser test, or automated interaction test
for this tab.

The backend report and
[`docs/testing/milestone-1-test-report.md`](../testing/milestone-1-test-report.md)
record the current repository test result: 24 backend tests passed after the
outreach fallback logger correction. That result validates the client-facing
API behavior indirectly, but it does not validate Streamlit rendering,
clipboard behavior, or live provider calls.

## 8. Frontend completion matrix

| Area | Assessment |
|---|---|
| Outreach tab navigation | Complete |
| Queue-based prospect selection | Complete |
| Dossier-backed context display | Complete |
| Provider, angle, tone, and notes controls | Complete |
| AI generation and refresh | Complete |
| Subject selection and body editing | Complete |
| Copy/view workflow | Complete as a copy-friendly display |
| Save-draft interaction | Complete as an API interaction; durable storage pending |
| Send interaction | Complete as an API interaction; real delivery pending |
| Streamlit automated UI tests | Not present |
| Authentication/authorization UX | Not implemented by the current API |

## 9. Known UX and integration limitations

1. Draft generation occurs automatically when a selected lead has no current
   draft, so merely opening a prospect can trigger an LLM request.
2. The UI displays a “Send Email” action, but the backend currently only
   acknowledges the request and may advance the pipeline stage.
3. Save success now means the API created a durable draft record, but the UI
   does not yet provide draft history or retrieval after a page refresh.
4. The copy surface is a formatted code block; it does not provide a dedicated
   browser clipboard API action.
5. Failure handling in the API client often returns `None` or an empty list,
   which limits the detail available to the user for some network failures.
6. There is no automated frontend test proving state isolation across multiple
   selected leads or reruns.

