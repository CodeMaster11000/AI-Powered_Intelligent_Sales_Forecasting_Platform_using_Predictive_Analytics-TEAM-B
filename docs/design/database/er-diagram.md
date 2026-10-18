# ER Diagram

GitHub renders the diagram below directly. A styled export is in `er-diagram.png` / `er-diagram.svg` (source: `er-diagram.dot`, rebuild with `dot -Tpng er-diagram.dot -o er-diagram.png`).

Fields marked `"proposed"` are additions that are **not in the SRS**; see [README.md](README.md) for why each is proposed and which need team sign-off.

![ER diagram](er-diagram.png)

```mermaid
erDiagram
    USERS ||--o{ LEADS : "owns (proposed)"
    USERS ||--o{ SALES_ANALYTICS : "has"
    LEADS ||--o{ LEAD_SCORES : "scored over time"
    LEADS ||--o{ COMPANY_INSIGHTS : "analyzed over time"
    LEADS ||--o{ SALES_INTERACTIONS : "has"
    LEADS ||--o{ OUTREACH_CAMPAIGNS : "receives"
    LEADS ||--o{ CRM_SYNC_LOGS : "audited by"

    USERS {
        bigint user_id PK
        text name
        text email UK
        text role
        text department
        timestamptz created_at
    }
    LEADS {
        bigint lead_id PK
        bigint owner_user_id FK "proposed"
        text company_name
        text industry
        text contact_name
        text contact_title "proposed"
        text email UK
        text phone
        text lead_status "5 lifecycle stages"
        text source "proposed: 5 ingestion vectors"
        text company_size "proposed"
        text annual_revenue "proposed"
        text funding_stage "proposed"
        text funding_raised "proposed"
        text location "proposed"
        jsonb tech_stack "proposed"
        timestamptz created_at
        timestamptz updated_at "proposed"
    }
    COMPANY_INSIGHTS {
        bigint insight_id PK
        bigint lead_id FK
        text business_needs
        text opportunities
        text industry_analysis
        int qualification_score "proposed"
        text growth_indicators "proposed"
        text tech_alignment "proposed"
        text decision_maker_summary "proposed"
        timestamptz generated_at
    }
    LEAD_SCORES {
        bigint score_id PK
        bigint lead_id FK
        int lead_score
        numeric conversion_probability
        timestamptz generated_at
    }
    SALES_INTERACTIONS {
        bigint interaction_id PK
        bigint lead_id FK
        text interaction_type
        text summary
        text action_items
        timestamptz interaction_date
    }
    OUTREACH_CAMPAIGNS {
        bigint campaign_id PK
        bigint lead_id FK
        text email_subject
        text email_content
        text campaign_status
        timestamptz created_at
    }
    CRM_SYNC_LOGS {
        bigint sync_id PK
        bigint lead_id FK
        text crm_platform
        text sync_status
        timestamptz timestamp
    }
    SALES_ANALYTICS {
        bigint analytics_id PK
        bigint user_id FK
        numeric conversion_rate
        numeric pipeline_value
        timestamptz generated_at
    }
```
