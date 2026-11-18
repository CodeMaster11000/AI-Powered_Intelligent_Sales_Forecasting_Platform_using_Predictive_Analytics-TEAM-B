# SALESGenie AI PLATFORM
## Module 5 — Conversation Summarization Pipeline
### Technical Architecture & Implementation Report
**Conversation Intelligence • Multi-LLM Inference • JSON Extraction • PostgreSQL Persistence**

| Attribute | Specification |
|---|---|
| **Module** | Module 5 — Conversation Summarization |
| **Primary Components** | `conversation_agent.py`, `llm_client.py`, `module5_conversation.py` |
| **API Layer** | FastAPI REST endpoints |
| **Database** | PostgreSQL — `sales_interactions` |

---

## 1. Executive Summary

The SalesGenie AI Platform Conversation Summarization Pipeline converts raw sales-call transcripts and lead context into structured CRM intelligence. The pipeline is designed as a decoupled four-stage flow: preprocessing and context grounding, multi-LLM inference, validation and token accounting, and relational persistence in PostgreSQL.

The design emphasizes factual extraction rather than free-form generation. A dedicated system prompt constrains the model to information explicitly present in the transcript, requires a fixed JSON schema, and distinguishes ownership of action items between the Account Executive and the client/prospect. Multiple LLM providers are supported through cascading failover, with a deterministic local heuristic fallback for offline conditions.

The resulting record is persisted to the `sales_interactions` table and can be retrieved through FastAPI endpoints. The supplied verification figures report a 1.85-second inference SLA, 96.2% action-item recall, 98.0% owner-attribution accuracy, and 5/5 automated tests passing.

---

## 2. Objectives and Engineering Requirements

- **Transform unstructured conversation transcripts** into structured sales intelligence.
- **Ground summaries in transcript evidence** and avoid invented commitments, numbers, or deadlines.
- **Capture discussion points, action items, risks, and a single next step** in a predictable schema.
- **Support multiple LLM providers** so a single provider outage does not stop processing.
- **Persist the structured result in PostgreSQL** for CRM and account-history workflows.
- **Expose the pipeline through REST APIs** suitable for synchronous use and future asynchronous execution.
- **Track AI provider, model, prompt version, and token estimates** for operational observability.

---

## 3. End-to-End Technical Architecture

The architecture separates data preparation, inference, validation, and persistence. This separation makes individual stages replaceable and prepares the implementation for asynchronous processing without changing the business-level output contract.

```text
[Raw Transcript + Lead Context]
       │
       ▼
[Stage 1] Preprocessing & Context Grounding (conversation_agent.py)
       │
       ▼
[Stage 2] Multi-LLM Inference Engine (llm_client.py)
       │
       ▼
[Stage 3] Validation, Normalization & Token Accounting
       │
       ▼
[Stage 4] PostgreSQL Persistence (module5_conversation.py)
       │
       ▼
[Structured CRM Interaction Record (sales_interactions)]
```

### 3.1 Stage 1 — Preprocessing and Context Grounding
- Ingests transcript text containing dialogue lines, timestamps, and speaker names.
- Enriches the conversation with lead context such as company name, contact name, contact title, and technology stack.
- Serializes the combined information into a strict JSON user payload before inference.
- Keeps transcript evidence and business context together so the model can resolve entities and interpret sales-specific references.

### 3.2 Stage 2 — Multi-LLM Inference Engine
- Uses `CONVERSATION_SUMMARIZER_SYSTEM_PROMPT` as the system-level instruction.
- Uses a low temperature of `0.2` to reduce output variance and improve repeatability.
- Supports cascading provider priority: Gemini 1.5 Pro → GPT-4o-mini → Grok-2 → Ollama → deterministic local fallback.
- The inference layer is isolated in `llm_client.py`, allowing provider-specific implementations to remain separate from the conversation pipeline.

### 3.3 Stage 3 — Validation, Normalization and Token Accounting
- Parses the model response as JSON and removes accidental markdown/code-fence wrapping.
- Validates the five mandatory fields: `summary`, `discussion_points`, `action_items`, `risks`, and `next_step`.
- Normalizes the extracted structure before database persistence.
- Computes `input_tokens` and `output_tokens` using the implemented token-counting heuristics.

### 3.4 Stage 4 — PostgreSQL Persistence
- Writes the validated interaction to `sales_interactions`.
- Stores structured lists and objects as `JSONB` fields.
- Sets `processing_status` to `completed` after successful persistence.
- Retains provider, model, prompt version, and token information for traceability.

---

## 4. Prompt Engineering and Anti-Hallucination Guardrails

The prompt is designed as a constrained information-extraction contract. Instead of asking the LLM to produce a generic meeting summary, the system specifies exactly which fields must be returned and how evidence should be handled.

### 4.1 Core Guardrails
- **Verbatim grounding:** The model must not extrapolate or invent commitments, numbers, or deadlines that are not supported by the transcript.
- **Explicit attribution:** Action items identify whether responsibility belongs to the Account Executive or the Client/Prospect.
- **Strict JSON:** The response must follow the required machine-readable structure and is intended to be returned with `application/json` formatting.
- **Single next step:** The output identifies one recommended directive to advance the opportunity.

### 4.2 Output Contract

```json
{
  "summary": "2-4 sentence executive overview capturing friction and alignment",
  "discussion_points": [
    "Specific operational/architecture topic discussed"
  ],
  "action_items": [
    {
      "task": "Explicit deliverable",
      "owner": "Account Executive | Prospect Lead",
      "due_date": "Parsed timeframe"
    }
  ],
  "risks": [
    "Identified compliance, technical, budget or delivery constraint"
  ],
  "next_step": "Recommended single directive to advance deal"
}
```

### 4.3 Why the Schema Matters
The schema converts an otherwise unstructured narrative into predictable CRM fields. This allows downstream systems to query action items and risks independently, display them in account views, and use them for workflow automation without re-parsing the original transcript.

---

## 5. Multi-LLM Cascading and Deterministic Fallback

The inference layer is designed to tolerate provider failures. The pipeline attempts providers in sequence and only moves to the next tier when the preceding provider cannot complete the request.

| Tier | Provider / Engine | Trigger / Role | Output Strategy |
|---|---|---|---|
| **1** | Google Gemini 1.5 Pro | Primary cloud inference | Structured JSON |
| **2** | OpenAI GPT-4o-mini | Timeout / quota / provider failure | JSON object |
| **3** | xAI Grok-2 | API failure at prior tier | Structured JSON |
| **4** | Local Ollama | Offline / private-mode inference | Local JSON |
| **5** | Deterministic local engine | All model routes unavailable | Heuristic JSON |

### 5.1 Deterministic Local Fallback
The local fallback prevents the application from failing simply because network-based AI services are unavailable. The implementation scans dialogue for action verbs and risk markers and maps those signals into the same structured output contract:
- Action signals include verbs such as `"send"`, `"schedule"`, and `"deliver"`.
- Risk signals include terms such as `"latency"`, `"compliance"`, `"friction"`, and `"budget"`.
- The fallback preserves the expected schema so downstream persistence can continue.
- The supplied design describes this as a zero-downtime availability mechanism; the actual SLA should be measured separately in production.

---

## 6. Technical Showcase — Transcript to Structured JSON

The following example demonstrates the complete transformation from raw dialogue to CRM-ready intelligence. The important engineering property is that the extracted tasks and risks are tied to explicit statements in the transcript.

### 6.1 Raw Dialogue Input

```text
[00:15] David: We scaled 40%, but pipeline visibility degraded.
[00:54] David: Forecast reconciliation between Kafka and Snowflake has 4-hour latency!
[01:45] David: We don't have engineering cycles for custom ETL.
[02:00] Alex: Zero custom ETL required. Our REST connectors deploy in under 1 hour.
[02:35] Alex: Let's do a technical deep dive next Thursday at 2 PM. I'll send staging connector docs this afternoon.
[02:50] David: Perfect. Include Sarah Miller on that invite.
```

### 6.2 Extracted Intelligence

```json
{
  "summary": "Completed discovery sync with David Vance (CloudPulse). Addressed 4-hour forecast reconciliation latency between Kafka and Snowflake degrading pipeline visibility. Confirmed SalesGenie zero-ETL REST connectors deploy without developer overhead.",
  "discussion_points": [
    "4-hour forecast reconciliation latency between Kafka and Snowflake",
    "Sales leadership operating on half-day stale account data",
    "Customer has zero bandwidth for custom ETL development"
  ],
  "action_items": [
    {
      "task": "Deliver staging connector documentation and security whitepaper",
      "owner": "Account Executive",
      "due_date": "This afternoon"
    },
    {
      "task": "Schedule technical deep dive with platform architect",
      "owner": "Account Executive",
      "due_date": "Next Thursday at 2:00 PM EST"
    },
    {
      "task": "Include Sarah Miller (Data Platform Lead) on calendar invite",
      "owner": "David Vance",
      "due_date": "Next Thursday at 2:00 PM EST"
    }
  ],
  "risks": [
    "Severe engineering bandwidth constraints; custom ETL requirement is an immediate deal-breaker"
  ],
  "next_step": "Send staging connector docs and invite Sarah Miller to Thursday deep dive."
}
```

This example shows the value of structured extraction: latency becomes a measurable discussion point, engineering bandwidth becomes a risk, and explicit commitments become actionable tasks with owners and timeframes.

---

## 7. PostgreSQL Persistence and API Contracts

### 7.1 `sales_interactions` Table Schema

```sql
CREATE TABLE sales_interactions (
    interaction_id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    lead_id BIGINT REFERENCES leads(lead_id) ON DELETE SET NULL,
    interaction_type TEXT NOT NULL,
    occurred_at TIMESTAMPTZ NOT NULL,
    subject TEXT,
    transcript_text TEXT,
    summary TEXT,
    discussion_points JSONB,
    action_items JSONB,
    risks JSONB,
    next_step TEXT,
    processing_status TEXT,
    ai_provider TEXT,
    ai_model TEXT,
    prompt_version TEXT,
    input_tokens INT,
    output_tokens INT
);
```

The schema combines relational identifiers with `JSONB` fields. Core metadata such as interaction identity, lead linkage, timestamp, status, provider, model, and prompt version remains directly queryable, while variable-length discussion points, action items, and risks retain their structured JSON representation.

### 7.2 FastAPI Endpoints

| Endpoint | Purpose | Expected Result |
|---|---|:---:|
| `POST /api/interactions/summarize` | Runs summarization pipeline and persists result | `201 Created` |
| `GET /api/leads/{lead_id}/interactions` | Retrieves interaction history for an account | `200 OK` (Interaction list) |
| `GET /api/interactions` | Returns paginated list of interaction summaries | `200 OK` |
| `GET /api/interactions/{interaction_id}` | Retrieves detailed record for single interaction | `200 OK` |

---

## 8. Performance Benchmarks and Test Evidence

The supplied implementation results report the following benchmark figures. These should be treated as verification results for the current test setup; production SLA claims should be revalidated under representative workloads and network conditions.

| Metric | Measured | Target / Definition | Status |
|---|---|---|:---:|
| **Inference SLA** | 1.85 seconds | Target < 5.0 s | **PASS** |
| **Action Item Recall** | 96.2% | Exact task match | **PASS** |
| **Owner Attribution Accuracy** | 98.0% | AE vs Client | **PASS** |
| **Automated Test Suite** | 5/5 tests | All tests pass (`test_conversation_agent.py`) | **PASS** |

---

## 9. Key Engineering Strengths

- **Clear separation of concerns** across preprocessing, inference, validation, and persistence.
- **Strict output schema** makes the AI result consumable by deterministic software components.
- **Grounding rules** directly address hallucination risk in sales commitments and deadlines.
- **Provider cascading** improves resilience against individual API outages or quota limitations.
- **Deterministic local fallback** maintains schema-level continuity in offline environments.
- **PostgreSQL JSONB storage** preserves structured AI output while keeping CRM metadata relational.
- **Provider/model/prompt/token metadata** supports traceability and future evaluation.

---

## 10. Conclusion

Module 5 establishes a complete technical path from raw sales conversation data to persistent CRM intelligence. Its central strength is the combination of constrained prompt engineering, multi-provider inference, deterministic validation, and durable PostgreSQL persistence. The resulting architecture is well suited for future asynchronous processing, richer CRM automation, analytics, and model evaluation.

For a production rollout, the next engineering focus should be continuous evaluation of extraction quality, provider latency and cost monitoring, stronger schema validation, and load testing of the FastAPI-to-PostgreSQL path. These improvements can be added without changing the core conversation intelligence contract.
