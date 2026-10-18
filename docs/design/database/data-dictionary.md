# Data Dictionary

Source: SRS section 2.4. **Bold + "proposed"** = not in the SRS
Types are Postgres design-level types, not final. Column names use snake_case; table names are lowercase plural (`users`, `leads`, ...).

Conventions to agree on and then keep identical everywhere:
- Primary keys: `bigint` generated identity (simple, fast, easy to read in logs)
- All timestamps: `timestamptz` (store UTC)
- Status-like text columns: restrict to allowed values (see "Allowed values" below)

---

## users (Milestone 1)
| Column | Type | Null | Notes |
|--------|------|------|-------|
| user_id | bigint | no | PK |
| name | text | no | |
| email | text | no | unique |
| role | text | no | allowed values below |
| department | text | yes | |
| created_at | timestamptz | no | default now |

## leads (Milestone 1)
| Column | Type | Null | Notes |
|--------|------|------|-------|
| lead_id | bigint | no | PK |
| **owner_user_id** (proposed) | bigint | yes | FK users.user_id. Needed for REQ "reps see only assigned leads" (SRS 2.3) |
| company_name | text | no | |
| industry | text | yes | |
| contact_name | text | yes | |
| **contact_title** (proposed) | text | yes | Needed for decision-maker alignment (REQ-M2-03, REQ-M4-02) |
| email | text | no | unique (dedupe rule, see README open question 2) |
| phone | text | yes | |
| lead_status | text | no | one of the 5 stages; default `New Leads` (REQ-M1-03) |
| **source** (proposed) | text | no | which ingestion vector: CRM, Website Form, LinkedIn, Sales Entry, CSV (REQ-M1-02) |
| **company_size** (proposed) | text | yes | e.g. `250-500` (REQ-M1-02) |
| **annual_revenue** (proposed) | text | yes | e.g. `$45M-$60M` (REQ-M1-02) |
| **funding_stage** (proposed) | text | yes | e.g. `Series C` |
| **funding_raised** (proposed) | text | yes | e.g. `$28M` |
| **location** (proposed) | text | yes | e.g. `San Francisco, CA` |
| **tech_stack** (proposed) | jsonb | yes | list of strings, e.g. AWS, Python, PostgreSQL |
| created_at | timestamptz | no | default now |
| **updated_at** (proposed) | timestamptz | no | for audit and "last changed" display |

## company_insights (Milestone 1)
| Column | Type | Null | Notes |
|--------|------|------|-------|
| insight_id | bigint | no | PK |
| lead_id | bigint | no | FK leads.lead_id |
| business_needs | text | yes | |
| opportunities | text | yes | the flagged opportunities (ERP Modernization, Cloud Migration, Process Automation, Digital Transformation; REQ-M2-02) |
| industry_analysis | text | yes | |
| **qualification_score** (proposed) | int | yes | 0-100; REQ-M2-03 outputs this (e.g. 92). Different from Lead_Scores (Module 4) |
| **growth_indicators** (proposed) | text | yes | High Growth Potential signals (REQ-M2-03) |
| **tech_alignment** (proposed) | text | yes | Tech Alignment metrics (REQ-M2-03) |
| **decision_maker_summary** (proposed) | text | yes | Decision Maker identification (REQ-M2-03) |
| generated_at | timestamptz | no | default now |

## lead_scores (Milestone 2)
| Column | Type | Null | Notes |
|--------|------|------|-------|
| score_id | bigint | no | PK |
| lead_id | bigint | no | FK leads.lead_id |
| lead_score | int | no | 0-100 |
| conversion_probability | numeric | no | percentage, e.g. 78 |
| generated_at | timestamptz | no | history is kept, newest row = current score |

## outreach_campaigns (Milestone 2)
| Column | Type | Null | Notes |
|--------|------|------|-------|
| campaign_id | bigint | no | PK |
| lead_id | bigint | no | FK leads.lead_id |
| email_subject | text | yes | |
| email_content | text | yes | |
| campaign_status | text | no | e.g. draft, sent (values decided in Milestone 2) |
| created_at | timestamptz | no | default now |

## sales_interactions (Milestone 3)
| Column | Type | Null | Notes |
|--------|------|------|-------|
| interaction_id | bigint | no | PK |
| lead_id | bigint | no | FK leads.lead_id |
| interaction_type | text | no | call, meeting, email... |
| summary | text | yes | |
| action_items | text | yes | assignee + due date per item (REQ-M5-02); may need its own table later |
| interaction_date | timestamptz | no | |

## crm_sync_logs (Milestone 3)
| Column | Type | Null | Notes |
|--------|------|------|-------|
| sync_id | bigint | no | PK |
| lead_id | bigint | no | FK leads.lead_id |
| crm_platform | text | no | Salesforce, HubSpot |
| sync_status | text | no | |
| timestamp | timestamptz | no | |

(REQ-M5-03 also wants log types such as Contact / Activity / Deal Stage / Task; consider an `event_type` column when Milestone 3 starts.)

## sales_analytics (Milestone 4)
| Column | Type | Null | Notes |
|--------|------|------|-------|
| analytics_id | bigint | no | PK |
| user_id | bigint | no | FK users.user_id |
| conversion_rate | numeric | yes | |
| pipeline_value | numeric | yes | |
| generated_at | timestamptz | no | |

---

## Allowed values
- **users.role**: Sales Representative, BDR, Sales Manager, RevOps (SRS 2.3)
- **leads.lead_status**: New Leads, Qualified, Proposal, Negotiation, Closed Won (REQ-M1-03)
- **leads.source**: CRM, Website Form, LinkedIn, Sales Entry, CSV (REQ-M1-02)

## Relationships
| Parent | Child | Cardinality | On parent delete |
|--------|-------|-------------|------------------|
| users | leads (owner_user_id) | 1 : N (proposed) | set null |
| users | sales_analytics | 1 : N | cascade or restrict (decide) |
| leads | lead_scores | 1 : N | cascade |
| leads | company_insights | 1 : N | cascade |
| leads | sales_interactions | 1 : N | cascade |
| leads | outreach_campaigns | 1 : N | cascade |
| leads | crm_sync_logs | 1 : N | cascade (or keep, audit logs may need to survive) |
