# Milestone 2 / Module 3 Backend Developer Report

**Project:** SalesGenie AI Platform  
**Scope:** Module 3 - Outreach generation API  
**Tasks covered:**

1. Build the AI email/outreach generation service using prompt templates, lead
   context, and pain points.
2. Provide outreach generation, refresh, edit, copy, save, and send support
   for the Streamlit outreach tab through backend APIs.

**Implementation status:** Core generation workflow and durable draft
persistence implemented; external email delivery remains pending.

## 1. Executive summary

The backend implementation provides a synchronous FastAPI outreach workflow
that loads a lead and its latest intelligence dossier, constructs a grounded
outreach prompt, invokes a configured LLM provider, validates the structured
result, and returns a consistent draft response to the frontend.

The implementation also exposes provider discovery, draft-save, and send
routes. The latter two routes currently provide workflow acknowledgements:
`save-draft` validates the lead and returns metadata without writing an
`outreach_emails` row, while `send` validates the lead and advances a
`New Leads` or `Qualified` lead to `Proposal` without sending through an
external mail provider or logging an interaction.

## 2. Requirement traceability

| Requirement from the task | Repository evidence | Status |
|---|---|---|
| Prompt-based AI outreach generation | [`OUTREACH_AGENT_SYSTEM_PROMPT`](../../backend/ai_agents/prompts.py), [`outreach_agent.py`](../../backend/ai_agents/outreach_agent.py) | Implemented |
| Ground generation in prospect data | [`generate_outreach`](../../backend/main.py), [`generate_personalized_outreach`](../../backend/ai_agents/outreach_agent.py) | Implemented |
| Use business needs, opportunities, growth, technology, and persona signals | [`outreach_agent.py`](../../backend/ai_agents/outreach_agent.py) | Implemented |
| Support value angle, tone, and custom rep notes | [`OutreachRequest`](../../backend/main.py), [`module3_outreach.py`](../../modules/module3_outreach.py) | Implemented |
| Generate subject variants and an editable email body | [`OUTREACH_AGENT_SYSTEM_PROMPT`](../../backend/ai_agents/prompts.py), response formatter in [`outreach_agent.py`](../../backend/ai_agents/outreach_agent.py) | Implemented |
| Save outreach campaigns/drafts | [`save_outreach_draft`](../../backend/main.py), [`outreach_emails.py`](../../backend/database/models/outreach_emails.py), Alembic migration | Implemented for draft records |
| Send generated outreach | [`send_outreach_email`](../../backend/main.py) | State transition acknowledgement; delivery integration pending |
| Support multiple LLM providers | [`llm_client.py`](../../backend/ai_agents/llm_client.py) | Implemented |
| Expose provider availability to the UI | `/api/llm/providers` in [`main.py`](../../backend/main.py) | Implemented |

## 3. Backend architecture and data flow

```text
POST /api/outreach/generate
        |
        v
Load Lead + latest CompanyInsight
        |
        v
modules.module3_outreach.generate_personalized_email
        |
        v
backend.ai_agents.outreach_agent
  - normalize tech stack
  - summarize opportunities
  - build grounded JSON prompt
  - call LLMClient
  - validate and normalize response
        |
        v
Structured outreach response -> Streamlit API client
```

The generation route is intentionally dossier-aware. It uses the latest
`company_insights` record when available and passes these signals to the
outreach agent:

- business needs;
- transformation opportunities;
- industry analysis;
- growth indicators;
- technology alignment; and
- decision-maker summary.

Lead profile data additionally includes company, contact, title, email,
industry, size, revenue, funding, location, and technology stack.

## 4. Implemented backend components

### 4.1 FastAPI routes

The routes are defined in [`backend/main.py`](../../backend/main.py):

| Method and route | Responsibility | Current behavior |
|---|---|---|
| `POST /api/outreach/generate` | Generate a personalized outreach draft | Loads lead and latest insight, invokes the AI service, returns structured output |
| `POST /api/outreach/save-draft` | Save a selected subject/body | Validates lead and acknowledges the request; does not yet persist content |
| `POST /api/outreach/send` | Send selected subject/body | Validates lead, advances eligible lead stage to `Proposal`, and acknowledges; does not deliver email |
| `GET /api/llm/providers` | Report provider configuration | Returns availability, model names, preferred provider, and last-used provider |

The route returns `404` when the target lead does not exist and maps
unavailable or incomplete AI output to `503`.

### 4.2 Module 3 service wrapper

[`modules/module3_outreach.py`](../../modules/module3_outreach.py) provides
the module boundary expected by the API and accepts either an ORM lead model
or a dictionary. It normalizes the lead into the provider-independent shape
used by the outreach agent.

### 4.3 Outreach personalization agent

[`backend/ai_agents/outreach_agent.py`](../../backend/ai_agents/outreach_agent.py)
implements the generation and response contract:

- converts JSON or comma-separated technology-stack data into a list;
- converts structured opportunity objects into a concise prompt summary;
- builds a JSON prompt containing lead profile, intelligence, and strategy;
- requests structured JSON from `LLMClient`;
- supplies a local deterministic draft when no provider returns usable output;
- verifies required fields;
- ensures the company is represented in the body;
- validates subjects, selected subject, hook score, and personalization
  triggers; and
- calculates word count and estimated reading time.

The response contains:

```text
subject_options
selected_subject
body
hook_score
word_count
reading_time_seconds
personalization_triggers
call_to_action
provider_used
angle
tone
```

### 4.4 Multi-LLM provider layer

[`backend/ai_agents/llm_client.py`](../../backend/ai_agents/llm_client.py)
supports:

- Google Gemini;
- OpenAI;
- xAI Grok through an OpenAI-compatible endpoint; and
- local Ollama.

Provider selection can be automatic or explicitly requested. API keys and
model names are read from environment variables, and provider availability is
reported without exposing credentials. JSON parsing supports clean JSON,
Markdown-fenced JSON, and JSON surrounded by explanatory text.

### 4.5 Prompt and response contract

[`backend/ai_agents/prompts.py`](../../backend/ai_agents/prompts.py) requires:

- three distinct subject variants;
- a company- and technology-specific opening;
- direct connection to SalesGenie predictive intelligence;
- requested value-angle and tone adherence;
- custom representative notes where supplied; and
- a low-friction call to action.

The public HTTP contract is documented in
[`docs/api/api-contract.md`](../api/api-contract.md), including request fields,
response fields, status codes, and known limitations.

## 5. Persistence and delivery assessment

The `outreach_emails` model and Alembic migration now provide durable draft
storage. The remaining delivery limitations are:

- `send` does not call SMTP, an email API, or a queue;
- no delivery ID, delivery status, retry state, or provider error is stored;
- no `interactions` record is created for the send operation.

The current send behavior is still useful for the implemented demo workflow:
it validates the lead and transitions `New Leads`/`Qualified` to `Proposal`.
It must not be described as production email delivery.

## 6. Validation and tests

The outreach-specific tests are in
[`backend/tests/test_outreach_agent.py`](../../backend/tests/test_outreach_agent.py):

- direct and punchy tone generation;
- problem-centric and metric-driven generation;
- consultative generation;
- company, contact, and technology personalization;
- subject options and selected-subject consistency;
- hook score and reading metrics;
- personalization triggers;
- the Module 3 wrapper; and
- provider-status API shape.

The LLM client tests in
[`backend/tests/test_llm_client.py`](../../backend/tests/test_llm_client.py)
cover provider ordering, JSON parsing, initialization shape, and offline
provider behavior. The repository's current test report records a complete
24-test backend pass after fixing the undefined fallback logger in
[`outreach_agent.py`](../../backend/ai_agents/outreach_agent.py).

The tests exercise the deterministic/offline path and contract behavior. They
do not prove successful calls against live Gemini, OpenAI, Grok, or Ollama
accounts, nor do they prove actual email delivery.

## 7. Operational requirements

Core dependencies are in [`requirements.txt`](../../requirements.txt);
provider and agent dependencies are in
[`requirements-ai.txt`](../../requirements-ai.txt). A normal local run
requires:

1. PostgreSQL through [`docker-compose.yml`](../../docker-compose.yml);
2. the Alembic schema applied;
3. FastAPI started with `uvicorn backend.main:app --reload`;
4. Streamlit started with `streamlit run frontend/app.py`; and
5. optional provider environment variables such as `GEMINI_API_KEY`,
   `OPENAI_API_KEY`, `XAI_API_KEY`/`GROK_API_KEY`, and Ollama settings.

## 8. Backend completion matrix

| Area | Assessment |
|---|---|
| AI prompt and personalization service | Complete for the current Module 3 scope |
| Structured response validation | Complete |
| Provider selection/status | Complete |
| API integration with lead intelligence | Complete |
| Draft acknowledgement endpoint | Complete as a demo acknowledgement |
| Durable campaign/draft storage | Complete for saved draft records |
| External email delivery | Not complete |
| Delivery logging, retries, and audit history | Not complete |
| Authentication and authorization | Not implemented in the current API |
