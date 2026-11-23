# Milestone 3 Automated Test Report

## Scope

This report validates the completed Milestone 3 features:

- HubSpot and Salesforce CRM clients, field mapping, and write-back
- Provider-neutral CRM synchronization and bounded batch limits
- CRM identity preservation, normalized lead matching, and duplicate handling
- Conversation transcript summarization and deterministic fallback
- Structured action items, discussion points, risks, and next-step normalization
- `sales_interactions` persistence and failed-processing audit records
- FastAPI conversation and CRM response behavior

## Validation summary

| Validation | Result |
|---|---:|
| Complete backend test suite | **69 passed** |
| Milestone 3 focused suite | **32 passed** |
| CRM and conversation files | **32 passed** |
| Failures remaining | **0** |

Commands used:

```bash
pytest -q backend/tests/test_conversation_agent.py \
  backend/tests/test_hubspot_client.py \
  backend/tests/test_salesforce_client.py \
  backend/tests/test_crm_error_handling.py

pytest -q backend/tests
```

Latest focused run: `32 passed in 6.69s`.

Latest complete backend run: `69 passed in 31.62s`.

## Milestone 3 requirements coverage

| Area | Coverage |
|---|---|
| HubSpot | Bearer authorization, contact pagination, provider errors, field normalization, missing-email rejection, write-back mapping, and batch validation |
| Salesforce | OAuth client credentials, dynamic instance URL, `nextRecordsUrl` pagination, Lead-to-Contact fallback, field normalization, missing-email rejection, write-back mapping, and batch validation |
| CRM persistence | Provider record identity, local lead upsert, normalized email matching, duplicate prevention, sync counters, provider error status preservation, and partial/failed sync states |
| Conversation intelligence | Transcript extraction, LLM/fallback behavior, structured output, token metadata, lead context, empty-input validation, and provider-neutral persistence |
| Interaction API | `201` creation, `404` unknown lead or interaction, `422` invalid request, list/detail filtering, and failed-interaction audit behavior |

## Failure cases found and fixed

### 1. CRM synchronization field mismatches

**Failure**

CRM payloads and SalesGenie lead fields did not always use the same normalized key format. Provider emails differing by casing or surrounding whitespace could produce duplicate local leads, and provider lifecycle values could be stored inconsistently.

**Fix**

- CRM emails are trimmed and lowercased before matching or persistence.
- Lead creation and update use the same normalized email path.
- Bulk import compares normalized existing and in-batch values.
- A PostgreSQL unique constraint protects the `leads.email` value.
- HubSpot and Salesforce status, location, name, company, and provider identity fields are mapped into explicit SalesGenie fields.
- Missing provider IDs or emails are rejected instead of creating ambiguous records.

**Regression evidence**

- `test_create_single_lead_normalizes_email_before_persisting`
- `test_bulk_import_skips_existing_and_case_insensitive_batch_duplicates`
- `test_map_hubspot_contact_normalizes_salesgenie_fields`
- `test_map_salesforce_lead_normalizes_salesgenie_fields`
- `test_map_hubspot_contact_rejects_contacts_without_email`
- `test_map_salesforce_lead_rejects_leads_without_email`

### 2. Raw or malformed summarization output

**Failure**

LLM responses could use a single string where the API contract requires a list, or contain action-item values that were strings instead of structured objects. A string list could previously be interpreted character-by-character, and malformed scalar values could leak raw Python representations into API output.

**Fix**

- Single-string discussion points and risks are split into clean text entries.
- Dict-shaped list entries are normalized to supported text fields.
- String action items are converted to `{task, owner, due_date}` objects.
- Malformed action-item fields receive safe defaults.
- Non-string summary and next-step values use deterministic fallback text.
- Missing required fields are replaced from the local deterministic fallback.
- Markdown JSON fences and malformed JSON are handled by the existing LLM JSON parser.

**Regression evidence**

- `test_summarize_normalizes_string_and_mixed_llm_output`
- `test_summarize_replaces_non_text_summary_and_next_step`
- `test_local_conversation_summary_fallback`
- `test_empty_transcript_raises_value_error`

### 3. Summarization failure records were not always operationally visible

**Failure**

A provider or database exception could prevent a conversation record from showing why processing failed.

**Fix**

- The service persists an interaction with `processing_status="failed"`.
- The original exception text is stored in `error_message`.
- The exception is re-raised so the API does not report false success.

**Regression evidence**

- `test_module5_service_persists_failed_processing_record`

### 4. CRM batch limits could accept invalid resource usage

**Failure**

Synchronization requests could request batches below 1 or above the supported 5,000-record maximum.

**Fix**

- HubSpot and Salesforce sync services reject values outside `1..5000` before provider or database work begins.

**Regression evidence**

- `test_hubspot_sync_rejects_out_of_range_batch_sizes`
- `test_salesforce_sync_rejects_out_of_range_batch_sizes`

### 5. CRM and conversation API edge cases

**Failure**

Blank transcripts could pass service handling inconsistently, and unknown lead IDs could reach summarization instead of returning an explicit API result.

**Fix**

- Pydantic rejects an empty transcript with `422`.
- The summarize endpoint rejects an unknown lead with `404`.
- The interaction service normalizes unsupported interaction types to `meeting`.

**Regression evidence**

- `test_api_rejects_empty_transcript`
- `test_api_rejects_unknown_lead`
- `test_empty_transcript_raises_value_error`

## Provider and database error behavior

The test suite verifies:

- HubSpot and Salesforce provider status codes are preserved when actionable.
- Provider `5xx` responses are translated to `502`; provider `503` remains `503`.
- Authentication, rate limit, unavailable, and network failures remain diagnosable.
- CRM synchronization marks provider and record failures in sync state/log data.
- Salesforce falls back from `Lead` to `Contact` when Lead is unavailable.
- Missing provider emails are counted as failed sync records rather than persisted.
- Failed summarization is preserved as a `failed` sales interaction.


