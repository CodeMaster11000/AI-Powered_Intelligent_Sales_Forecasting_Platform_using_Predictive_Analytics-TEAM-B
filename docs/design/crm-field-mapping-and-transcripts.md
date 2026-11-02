# Day 20 Deliverable: CRM Field Mapping Notes & Sample Call Transcripts

**Project:** SalesGenie AI Platform  
**Milestone Focus:** Milestone 2 Closure & Milestone 3 Kickoff Preparation (Module 5)  
**Authors:** Varshitha Kota (Backend Developer) & Jayant Vaibhav (AI/ML Engineer)  
**Date:** 2026-10-31 (Day 20 SDLC Schedule Checkpoint)  
**Deliverable Status:** 🟢 Completed & Cleared  

---

## 1. Executive Summary & Milestone 2 Closure Log

As of Day 20 (31-Oct-2026), all development, testing, and documentation items for Milestone 2 (Module 3 AI Cold Outreach & Module 4 Predictive Lead Scoring) have been cleared with zero remaining blockers:

```text
┌─────────────────────────────────────────────────────────────┬──────────────┬────────────┐
│ Task / Milestone Item                                       │ Owner        │ Status     │
├─────────────────────────────────────────────────────────────┼──────────────┼────────────┤
│ Module 3: Multi-LLM Cold Outreach Generation Engine         │ Jayant (AI)  │ CLEARED    │
│ Module 3: AI Email Generator Studio (Streamlit)             │ Ekansh (FE)  │ CLEARED    │
│ Module 4: 4-Dimensional Predictive Lead Scoring Engine      │ Jayant (AI)  │ CLEARED    │
│ Module 4: Next-Best-Action (NBA) Recommendation Engine      │ Jayant (AI)  │ CLEARED    │
│ Module 4: Glass-Box Factor Breakdown in Scoring Hub         │ Full Team    │ CLEARED    │
│ Milestone 2 QA Test Report (Scoring Accuracy >= 85%)        │ Devendra(QA) │ CLEARED    │
│ Milestone 2 Backend, Frontend, and AI Technical Reports     │ Full Team    │ CLEARED    │
└─────────────────────────────────────────────────────────────┴──────────────┴────────────┘
```

This document serves as the preparatory architectural deliverable for **Module 5: Conversation Intelligence & CRM Integration**, scheduled to start on Day 22 (02-Nov-2026).

---

## 2. Salesforce CRM Integration Field Mapping

This mapping defines bidirectional synchronization between Salesforce standard objects and the SalesGenie internal database schema.

### 2.1 Salesforce `Lead` Object Mapping

| Salesforce API Field Name | SalesGenie Schema Column | Data Type | Sync Direction | Transformation / Notes |
|---|---|---|:---:|---|
| `Id` | `leads.crm_lead_id` (ext) | `VARCHAR(18)` | SFDC $\rightarrow$ SalesGenie | Salesforce 18-character Lead ID |
| `Company` | `leads.company_name` | `VARCHAR(255)` | Bidirectional | Required field in SalesGenie |
| `FirstName` + `LastName` | `leads.contact_name` | `VARCHAR(255)` | Bidirectional | Concatenated string |
| `Title` | `leads.contact_title` | `VARCHAR(255)` | Bidirectional | Executive role title |
| `Email` | `leads.email` | `VARCHAR(255)` | Bidirectional | Primary unique contact key |
| `Phone` | `leads.phone` | `VARCHAR(50)` | Bidirectional | E.164 phone formatting |
| `Status` | `leads.lead_status` | `VARCHAR(50)` | Bidirectional | Map SFDC `Open`/`Working` $\rightarrow$ `New Leads`; `Qualified` $\rightarrow$ `Qualified` |
| `LeadSource` | `leads.source` | `VARCHAR(50)` | SFDC $\rightarrow$ SalesGenie | Map SFDC sources to `["CRM", "Website Form", "LinkedIn", "Sales Entry", "CSV"]` |
| `NumberOfEmployees` | `leads.company_size` | `VARCHAR(50)` | SFDC $\rightarrow$ SalesGenie | Categorized into `Mid-Market`, `Enterprise`, etc. |
| `AnnualRevenue` | `leads.annual_revenue` | `VARCHAR(50)` | SFDC $\rightarrow$ SalesGenie | Formatted string (e.g. `$50M`) |
| `City` + `, ` + `State` | `leads.location` | `VARCHAR(255)` | SFDC $\rightarrow$ SalesGenie | Geographic location string |

### 2.2 SalesGenie Intelligence & Scoring Push to Salesforce

| SalesGenie AI Output | Target Salesforce Custom Field | SFDC Data Type | Description |
|---|---|---|---|
| `lead_scores.lead_score` | `SalesGenie_Score__c` | `Number(3, 0)` | 0–100 composite predictive score |
| `lead_scores.conversion_probability` | `SalesGenie_Win_Prob__c` | `Percent(5, 2)` | Calibrated win likelihood percentage |
| `priority` (`hot`/`warm`/`cold`) | `SalesGenie_Tier__c` | `Picklist` | Values: `Hot`, `Warm`, `Cold` |
| `company_insights.business_needs` | `SalesGenie_Pain_Points__c` | `LongTextArea` | Extracted operational bottlenecks |
| `transformation_opportunities` | `SalesGenie_Opportunities__c` | `LongTextArea` | Detected modernization opportunities |
| `next_best_action` | `SalesGenie_Next_Action__c` | `Text(255)` | AI recommended channel & directive |

---

## 3. HubSpot CRM Integration Field Mapping

### 3.1 HubSpot `Contacts` & `Companies` Object Mapping

| HubSpot Internal Property Name | SalesGenie Schema Column | Data Type | Sync Direction | Notes |
|---|---|---|:---:|---|
| `hs_object_id` | `leads.crm_contact_id` | `VARCHAR(64)` | HubSpot $\rightarrow$ SalesGenie | HubSpot Contact Unique Identifier |
| `company` (associated company) | `leads.company_name` | `VARCHAR(255)` | Bidirectional | Associated Company name |
| `firstname` + ` ` + `lastname` | `leads.contact_name` | `VARCHAR(255)` | Bidirectional | Full contact name |
| `jobtitle` | `leads.contact_title` | `VARCHAR(255)` | Bidirectional | Decision maker title |
| `email` | `leads.email` | `VARCHAR(255)` | Bidirectional | Unique matching key |
| `phone` | `leads.phone` | `VARCHAR(50)` | Bidirectional | Primary phone |
| `lifecyclestage` | `leads.lead_status` | `VARCHAR(50)` | Bidirectional | `lead` $\rightarrow$ `New Leads`, `opportunity` $\rightarrow$ `Proposal` |
| `hs_lead_status` | `leads.lead_status` | `VARCHAR(50)` | Bidirectional | Secondary lifecycle sync |
| `num_associated_deals` | Internal metadata | `Integer` | HubSpot $\rightarrow$ SalesGenie | Account engagement metric |

---

## 4. Sample Sales Interaction Transcripts for Conversation Intelligence (Module 5)

These high-fidelity transcripts are prepared for Day 24 (04-Nov) to train and evaluate the AI Conversation Summarization and Action-Item Extraction Agent.

---

### 🎙️ Transcript 1: Enterprise Cloud & Infrastructure Modernization Discovery

**Account:** CloudPulse Technologies  
**Participants:**  
- **Alex Mercer** — Senior Account Executive, SalesGenie AI  
- **David Vance** — VP of Infrastructure & Platform Engineering, CloudPulse Technologies  
**Duration:** 18 minutes | **Date:** 2026-10-30  

```text
[00:00] Alex Mercer: David, thanks for making time today. I noticed CloudPulse just completed your Series C funding round—congratulations on that milestone.
[00:15] David Vance: Thanks Alex. Yes, things are moving rapidly here. We've scaled our engineering team by 40% in the last six months, but our pipeline visibility has actually degraded as a result.
[00:32] Alex Mercer: That's a very common scaling bottleneck. When we looked at your tech stack footprint, we saw heavy utilization of AWS EKS, Kafka, and Snowflake, but some legacy Postgres components in the middle. Where is the biggest operational drag right now?
[00:54] David Vance: Exactly where you pointed. Our transaction ingestion through Kafka is fine, but when customer success and revenue ops try to pull forecast reconciliations from Postgres and Snowflake, we're seeing up to 4-hour latencies. Our VP of Sales is forecasting based on numbers that are basically half a day stale.
[01:25] Alex Mercer: That lag directly creates deal slippage and pipeline variance. SalesGenie's predictive engine connects into your live event streams to compute conversion probabilities and account risks continuously, cutting that latency from hours to sub-minute updates.
[01:45] David Vance: That sounds compelling, but what does integration look like? We don't have engineering cycles to spend four weeks building custom ETL connectors.
[02:00] Alex Mercer: Zero custom ETL required. We have native REST connectors for both Snowflake and HubSpot/Salesforce, with OAuth authentication that deploys in under an hour.
[02:18] David Vance: That addresses my biggest concern. If we can verify that latency reduction on our staging pipeline without pulling our data engineers off their current sprint, I'd like to see a live benchmark.
[02:35] Alex Mercer: Absolutely. Let's set up a technical deep dive with our platform architect for next Thursday at 2 PM. I'll send over our staging connector documentation and security whitepaper this afternoon.
[02:50] David Vance: Perfect. Include Sarah Miller from our Data Platform team on that invite as well.
[03:00] Alex Mercer: Will do. Thanks David, speak next Thursday!
```

**Key Discussion Points to Extract (Ground Truth):**
1. CloudPulse scaled engineering 40% post-Series C, causing pipeline visibility degradation.
2. Ingestion latency between Kafka, Postgres, and Snowflake is causing 4-hour forecast delays for sales leadership.
3. VP of Infrastructure requires zero-ETL connector deployment that does not pull engineers off core sprints.

**Action Items to Extract (Ground Truth):**
1. [Alex Mercer] Send staging connector documentation and security whitepaper this afternoon.
2. [Alex Mercer] Schedule technical deep-dive demonstration for next Thursday at 2:00 PM EST.
3. [David Vance] Include Sarah Miller (Data Platform Lead) on the calendar invite.

---

### 🎙️ Transcript 2: Healthcare FHIR API & Interoperability Compliance

**Account:** HealthBridge Networks  
**Participants:**  
- **Rachel Thorne** — Strategic Enterprise Lead, SalesGenie AI  
- **Dr. Sarah Chen** — Chief Information Officer, HealthBridge Networks  
**Duration:** 14 minutes | **Date:** 2026-10-31  

```text
[00:00] Rachel Thorne: Good morning, Dr. Chen. Appreciate you joining us today.
[00:08] Dr. Sarah Chen: Good morning Rachel. Happy to connect. As you know, healthcare compliance doesn't give us much room for error, so I'm interested in how you handle clinical data boundaries.
[00:22] Rachel Thorne: Absolutely. When we reviewed HealthBridge's public architecture, we noted your team's expansion across Azure Health Data Services, Kubernetes, and FHIR API standards. Where are your account executives hitting the biggest friction during hospital onboarding?
[00:44] Dr. Sarah Chen: When our sales team qualifies regional hospital networks, they spend 3 to 4 days manually verifying whether the hospital's EHR system—usually Epic or Cerner—is compatible with our FHIR endpoints. That delay is killing our deal velocity.
[01:10] Rachel Thorne: That makes total sense. SalesGenie's Module 2 intelligence agent automatically categorizes EHR tech footprints, API versions, and compliance postures at ingestion, delivering a compatibility score before your rep even makes the first call.
[01:32] Dr. Sarah Chen: Can you enforce HIPAA compliance and ensure no protected health information (PHI) ever enters the generative outreach model?
[01:45] Rachel Thorne: Yes, 100%. We operate under strict IEEE SRS Section 4.3 FMEA rules. We only ingest firmographic and infrastructure metadata—zero patient records or PHI are permitted into the prompt payloads. We also provide full BAA execution.
[02:08] Dr. Sarah Chen: Excellent. That's the gatekeeper requirement for our legal team.
[02:15] Rachel Thorne: How about we conduct a privacy-reviewed trial with your legal team and run 20 anonymized hospital prospect profiles through the engine?
[02:30] Dr. Sarah Chen: That works. Send over your Business Associate Agreement (BAA) and SOC 2 Type II report. If legal signs off by Tuesday, we'll schedule the pilot onboarding for Friday.
[02:44] Rachel Thorne: Outstanding, Dr. Chen. You'll have both documents in your inbox within the hour.
```

**Key Discussion Points to Extract (Ground Truth):**
1. HealthBridge sales reps experience 3–4 day qualification delays manually verifying Epic/Cerner FHIR compatibility.
2. Compliance boundary: Zero PHI allowed into LLM prompts; strict BAA and SOC 2 Type II audit required.
3. Agreement on pilot test using 20 anonymized hospital prospect profiles.

**Action Items to Extract (Ground Truth):**
1. [Rachel Thorne] Deliver SalesGenie BAA and SOC 2 Type II compliance audit reports within 1 hour.
2. [Dr. Sarah Chen] Coordinate legal review by Tuesday deadline.
3. [Full Team] Schedule pilot onboarding session for Friday upon BAA execution.

---

### 🎙️ Transcript 3: High-Velocity FinTech Pipeline Variance Review

**Account:** PayFlow Systems  
**Participants:**  
- **Marcus Sterling** — Enterprise Sales Executive, SalesGenie AI  
- **Elena Rostova** — VP of Revenue Operations, PayFlow Systems  
**Duration:** 15 minutes | **Date:** 2026-10-31  

```text
[00:00] Marcus Sterling: Hi Elena, thanks for your time today.
[00:07] Elena Rostova: Hi Marcus. Let's get straight to it—our quarter ends in 45 days and our board forecast has fluctuated by 22% over the last two sprints. We need to stabilize our deal scoring.
[00:24] Marcus Sterling: A 22% variance in a Series B payment gateway is substantial. What's causing the drift?
[00:34] Elena Rostova: Reps are subjectively marking deals as 'Commit' based on positive calls, while our technical integration tickets show that the prospect hasn't even completed sandbox API testing. Our CRM data in HubSpot is essentially disconnected from engineering reality.
[01:00] Marcus Sterling: That is the textbook definition of the subjective qualification trap. SalesGenie's 4-dimensional scoring model automatically evaluates actual tech alignment, hiring signals, and buyer committee readiness—not just rep optimism.
[01:21] Elena Rostova: Can we see the factor breakdown so our sales managers can inspect why a deal is scored high or low?
[01:30] Marcus Sterling: Yes, we call it Glass-Box AI. In our Scoring Hub, every deal displays exact point breakdowns across Fit (30 pts), Intent (25 pts), Decision Readiness (25 pts), and Engagement (20 pts).
[01:48] Elena Rostova: That would completely change our weekly pipeline reviews. Can you integrate directly with our HubSpot instance?
[01:58] Marcus Sterling: Yes, our bidirectional HubSpot sync will push the predictive score and next-best-action directly to your HubSpot deal records.
[02:10] Elena Rostova: Send me a proposal for a 30-day pilot covering our mid-market sales pod of 8 reps. Let's review pricing on Monday morning at 10 AM.
[02:22] Marcus Sterling: Perfect. I'll have the tailored pilot proposal in your inbox before 5 PM today.
```

**Key Discussion Points to Extract (Ground Truth):**
1. PayFlow experiencing 22% quarterly board forecast variance due to subjective rep deal scoring.
2. Disconnect between HubSpot CRM deal stages and engineering sandbox API testing status.
3. Requirement for Glass-Box AI factor breakdown during weekly sales pipeline reviews.

**Action Items to Extract (Ground Truth):**
1. [Marcus Sterling] Deliver 30-day pilot proposal for 8-rep mid-market pod by 5:00 PM today.
2. [Marcus Sterling & Elena Rostova] Schedule pilot pricing review meeting for Monday at 10:00 AM.
3. [Elena Rostova] Share current HubSpot custom deal property schema prior to call.

---

## 5. Architectural Readiness for Milestone 3

With these field mappings and benchmark transcripts completed:
1. **FastAPI Endpoints (Days 22–23):** Ready to implement HubSpot and Salesforce OAuth and webhook listeners.
2. **Conversation Intelligence Service (Day 24):** Ready to implement LangGraph Summarization and Action Item Extraction Agent against benchmark transcripts.
3. **Conversations UI Tab (Day 25):** Ready to display CRM sync logs and meeting intelligence feeds.

