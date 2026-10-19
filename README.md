# SalesGenie Platform — B2B Lead Intelligence & Account Profiling System

> **Infosys Batch-4 Capstone Project**  
> **Standard Compliance**: IEEE Std 830-1998  
> **Milestone 1 Status**: COMPLETED & VERIFIED (Day 8 / Day 9 Checkpoint — 19-Oct-2026)  
> **AI/ML Engineer**: Jayant Vaibhav

---

## 📌 Executive Summary (सरल शब्दों में सारांश)

SalesGenie AI एक एंटरप्राइज B2B सेल्स इंटेलिजेंस और अकाउंट प्रोफाइलिंग प्लेटफॉर्म है।  
आज (Day 8 / Milestone 1) तक **Module 1 (Lead Management)** और **Module 2 (AI Lead Intelligence & Company Analysis)** का पूरा एंड-टू-एंड सिस्टम डेवलप, टेस्ट और लाइव कर दिया गया है।

---

## 👥 Team Roles & Responsibilities

| # | Role | Member | Modules Owned |
|---|---|---|---|
| 1 | Project Lead & DevOps | Ekansh Agnihotri | Sprint Planning, PostgreSQL DB, CI/CD |
| 2 | Backend Developer | Varshitha Kota | FastAPI endpoints, CRUD APIs, Integration Layer |
| 3 | **AI/ML Engineer** | **Jayant Vaibhav** | **LangGraph Multi-Agent Engine, Module 2 (Lead Intelligence), Module 3 (Outreach), Module 4 (Scoring), Module 5 (Summarization)** |
| 4 | QA / Test Engineer | Devendra Bisne | Test Suites, Acceptance Benchmarks, UAT |

---

## 🚀 Quick Start — How to Run the Project (प्रोजेक्ट कैसे चलाएं)

### 1. One-Click Dual Microservice Launcher (सबसे आसान तरीका):
सिर्फ एक कमांड से बैकएंड (FastAPI) और फ्रंटएंड (Streamlit) दोनों एक साथ चालू हो जाते हैं:

```bash
python run_demo.py
```

* **🖥️ Interactive UI Dashboard**: [http://localhost:8501](http://localhost:8501)
* **⚡ FastAPI REST API Docs (Swagger)**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **❤️ Health Check Endpoint**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

### 2. Run Automated Acceptance Tests (टेस्ट्स चेक करने के लिए):
```bash
python -m pytest tests/test_milestone1_acceptance.py -v
```

---

## 📅 Day-by-Day Work Breakdown (Day 1 से Day 8 तक क्या-क्या किया)

### Day 1 (Mon, 12-Oct): Requirements & Scope Baseline
* IEEE Std 830-1998 SRS डॉक्यूमेंट का रिव्यू और फाइनल स्कोप अप्रूवल।
* 6 कोर मॉड्यूल्स, 4 माइलस्टोन्स और डेटाबेस आर्किटेक्चर को फाइनलाइज़ किया गया।

### Day 2 (Tue, 13-Oct): Environment Setup & Git Baseline
* लोकल Git रिपॉजिटरी इनिशियलाइज़ की गई और `feature/module2-lead-intelligence` ब्रांच बनाई गई।
* Python 3.10, FastAPI, LangGraph, Streamlit और SQLAlchemy का एनवायरनमेंट सेटअप किया गया।
* Docker कंटेनराइज़ेशन के लिए `Dockerfile` और `docker-compose.yml` तैयार किए गए।

### Day 3 (Wed, 14-Oct): Database Schema & Multi-Agent Architecture
* **Database Models**: IEEE SRS Table 2.4-A के अनुसार सभी **8 टेबल्स** का रिलेशनल स्कीमा बनाया गया (`Users`, `Leads`, `Lead_Scores`, `Company_Insights`, `Sales_Interactions`, `Outreach_Campaigns`, `CRM_Sync_Logs`, `Sales_Analytics`)।
* **LangGraph Multi-Agent Architecture (Jayant's AI Work)**: रिसर्च एजेंट और क्वालिफिकेशन एजेंट का स्टेट ग्राफ आर्किटेक्चर डिजाइन किया गया ([LangGraph_Agent_Architecture.md](file:///c:/Users/PRASHANT%20VAIBHAV/Documents/infosis%20project/docs/LangGraph_Agent_Architecture.md))।

### Day 4 (Thu, 15-Oct): Research Agent & Profile Analysis Service
* `backend/app/ai_agents/research_agent.py` डेवलप किया गया।
* टेक स्टैक को 5 एंटरप्राइज कैटेगरीज में क्लासिफाई करने का लॉजिक बनाया गया (Cloud, Backend, Frontend, Data, DevOps)।
* 4 ट्रांसफॉर्मेशन अपॉर्चुनिटीज (ERP Modernization, Cloud Migration, Process Automation, Digital Transformation) का डिटेक्शन इंजन लिखा गया।

### Day 5 (Fri, 16-Oct): Qualification Agent & Ingestion Engine
* `backend/app/ai_agents/qualification_agent.py` डेवलप किया गया।
* **Predictive Score (0–100 Points)** और **High Growth Potential (Series C / Expansion Budget)** का स्कोरिंग कैलकुलेशन बनाया गया।
* डिसीजन मेकर पर्सोनास (जैसे CTO, VP Sales) के लिए पेन-पॉइंट्स और पर्सनलाइज्ड पिच एंगल जनरेटर लिखा गया।
* सिंगल और बैच लीड इनजेशन के लिए CRUD APIs और डुप्लिकेट डिटेक्शन तैयार किया गया।

### Day 6 (Sat, 17-Oct): Seed Dataset & Acceptance Unit Tests
* IEEE SRS में वर्णित रियल कंपनियों के साथ `data/sample_leads.csv` तैयार किया गया (TechCorp Solutions, DataFlow, CloudNine, Acme Corp, InnovateAI आदि)।
* डेटाबेस में सीडिंग और मल्टी-वेक्टर इनजेशन को वेरीफाई किया गया।

### Day 7 (Sun, 18-Oct): Leads UI Integration & Milestone 1 Test Report
* लीड मैनेजमेंट और लीड इंटेलिजेंस को फ्रंटएंड में इंटीग्रेट किया गया।
* माइलस्टोन 1 टेस्ट रिपोर्ट और इवैल्यूएशन बेंचमार्क डॉक्यूमेंट तैयार किया गया ([Milestone1_Test_Report.md](file:///c:/Users/PRASHANT%20VAIBHAV/Documents/infosis%20project/docs/Milestone1_Test_Report.md))।

### Day 8 (Mon, 19-Oct — आज!): Demo Build & Enterprise UI Polish
* **Button-Triggered Execution**: ऑटो-रन हटाकर क्लीन स्टेट बनाया गया — अब यूजर जब **"Run Lead Intelligence Pipeline"** बटन दबाता है, तभी लाइव प्रोग्रेस और स्कोर लोड होता है।
* **Enterprise SaaS Styling**: बचकाने AI इमोजी हटाकर असली कॉर्पोरेट B2B लुक दिया गया (Dark Navy थीम, 54px स्कोर डिस्प्ले कार्ड, टॉप 5% कन्वर्जन फिट बैज, क्लीन मैट्रिक्स)।
* **Milestone 1 Verification**: ऑटोमेटेड टेस्ट सुइट रन किया गया — सभी 6 टेस्ट्स 100% पास!

---

## 🧩 क्या-क्या तैयार हुआ है (Technical Deliverables Detail)

### 1. Module 1: Lead Management & Multi-Vector Ingestion
* **डेटाबेस**: 8 रिलेशनल टेबल्स SQLite / PostgreSQL पर पूरी तरह एक्टिव।
* **5 लाइफसाइकिल स्टेजेस**: `New Leads` $\to$ `Qualified` $\to$ `Proposal` $\to$ `Negotiation` $\to$ `Closed Won` में वन-क्लिक ट्रांजिशन।
* **मल्टी-वेक्टर इनजेशन**:
  - मैन्युअल फॉर्म इनजेशन
  - CSV बैच फाइल अपलोड (डुप्लीकेट डिटेक्शन के साथ)
  - वेरीफाइड सीड डेटासेट (9 मुख्य एकाउंट्स)

### 2. Module 2: AI Lead Intelligence & Company Analysis (Jayant's Core Work)
* **LangGraph Multi-Agent Bus**:
  - `ResearchAgent`: इंडस्ट्री डोमेन क्लासिफिकेशन और 4 ट्रांसफॉर्मेशन ड्राइवर्स स्कैन करता है।
  - `QualificationAgent`: 0-100 प्रेडिक्टिव स्कोर, हाई ग्रोथ सिग्नल और डिसीजन मेकर पर्सोना पिच मैप करता है।
* **डिटेक्ट की जाने वाली 4 ट्रांसफॉर्मेशन अपॉर्चुनिटीज (REQ-M2-02)**:
  1. *ERP Modernization Needs* (Legacy SAP/Oracle डिटेक्ट होने पर High Impact)
  2. *Cloud Migration Opportunities* (On-premise/hybrid वर्कलोड्स के लिए 35-40% इंफ्रा कॉस्ट कटिंग)
  3. *Process Automation Potential* (सेल्स रिसर्च फ्रिक्शन कम करने के लिए)
  4. *Digital Transformation Projects* (रियल-टाइम इंटेलिजेंस और स्केलिंग)
* **अल्ट्रा-फास्ट लेटेंसी**: LangGraph पाइपलाइन का एग्जीक्यूशन सिर्फ **0.03 से 0.05 सेकंड** में पूरा होता है (IEEE SLA रिक्वायरमेंट: `< 5.0 सेकंड`)।
* **ज़ीरो हैलुसिनेशन**: FMEA रिस्क मिटिगेशन के अनुसार डेटाबेस रिकॉर्ड्स से स्ट्रिक्टली ग्राउंडेड।

---

## 🧪 Milestone 1 Automated Acceptance Benchmark Results

```text
platform win32 -- Python 3.10.0, pytest-9.0.2

tests/test_milestone1_acceptance.py::test_ingestion_benchmark PASSED         [ 16%]
tests/test_milestone1_acceptance.py::test_langgraph_processing_latency PASSED     [ 33%]
tests/test_milestone1_acceptance.py::test_req_m2_01_tech_stack_components PASSED [ 50%]
tests/test_milestone1_acceptance.py::test_req_m2_02_transformation_opportunities PASSED [ 66%]
tests/test_milestone1_acceptance.py::test_req_m2_03_high_growth_and_qualification_score PASSED [ 83%]
tests/test_milestone1_acceptance.py::test_req_m1_03_lifecycle_stages PASSED     [100%]

============================== 6 passed in 1.32s ==============================
```

| क्राइटेरिया | टारगेट SLA | प्राप्त परिणाम | स्थिति |
|---|---|---|---|
| Multi-Vector Ingestion Rate | $\ge 95\%$ | **100% (9/9 Records)** | **PASS** ✅ |
| Field Corruption Errors | $0$ errors | **0 errors** | **PASS** ✅ |
| End-to-End Latency | $< 5.0$ seconds | **0.032 - 0.05 seconds** | **PASS** ✅ |
| REQ-M2-01 (Tech Categorization) | 5 Dimensions | Cloud, Backend, Frontend, Data, DevOps | **PASS** ✅ |
| REQ-M2-02 (4 Transformation Ops) | 4 Vectors | ERP, Cloud, Automation, Digital | **PASS** ✅ |
| REQ-M2-03 (Predictive Score) | 0–100 Scale | TechCorp: 98/100, Series C High Growth | **PASS** ✅ |

---

## 📂 Project Structure

```
infosis project/
├── backend/
│   ├── app/
│   │   ├── main.py                     # FastAPI REST Microservice
│   │   ├── config.py                   # App Configuration & LLM settings
│   │   ├── models/                     # SQLAlchemy 8 Tables (IEEE SRS Section 2.4)
│   │   │   ├── base.py
│   │   │   └── schema_models.py
│   │   ├── schemas/                    # Pydantic v2 schemas
│   │   │   ├── lead.py
│   │   │   └── intelligence.py
│   │   ├── ai_agents/                  # Jayant's Core AI/ML Layer
│   │   │   ├── state.py                # LangGraph AgentState TypedDict
│   │   │   ├── graph.py                # Multi-Agent Workflow (StateGraph)
│   │   │   ├── prompts.py              # Strict Grounding Prompts
│   │   │   ├── llm_client.py           # Gemini/OpenAI wrapper with smart fallback
│   │   │   ├── research_agent.py       # Module 2: Profiling & Transformation Detection
│   │   │   └── qualification_agent.py  # Module 2: Scoring (0-100) & Growth Signals
│   │   ├── services/
│   │   │   ├── lead_service.py         # Multi-vector ingestion & lifecycle stages
│   │   │   └── intelligence_service.py # LangGraph execution orchestrator
│   │   └── routes/
│   │       ├── leads.py                # Prospect REST endpoints
│   │       └── intelligence.py         # Lead Intelligence REST endpoints
├── frontend/
│   └── app.py                          # Streamlit Enterprise Presentation Layer
├── data/
│   └── sample_leads.csv                # Ingestion seed dataset (TechCorp, DataFlow, etc.)
├── tests/
│   └── test_milestone1_acceptance.py   # Automated Acceptance Tests (6/6 Passing)
├── docs/
│   ├── LangGraph_Agent_Architecture.md # Day 3 Architecture Deliverable
│   └── Milestone1_Test_Report.md       # Day 7/8/9 Acceptance Test Report
├── Dockerfile                          # Container baseline
├── docker-compose.yml                  # Container deployment
├── run_demo.py                         # One-click dual microservice launcher
├── requirements.txt                    # Project dependencies
└── conftest.py                         # Pytest configuration
```

---

## 🔮 Upcoming Milestones Roadmap (आगे का प्लान)

* **Milestone 2 (Weeks 3–4 / Days 10–19)**:
  - **Module 3**: AI Email Outreach Generator (पर्सनलाइज्ड कोल्ड ईमेल, आरओआई बेंचमार्क्स, टाइमिंग गाइडलाइन्स)।
  - **Module 4**: Predictive Lead Scoring & Next-Best-Action Recommendations।
* **Milestone 3 (Weeks 5–6 / Days 20–30)**:
  - **Module 5**: Conversation Intelligence (कॉल/मीटिंग समरी और एक्शन आइटम एक्सट्रैक्शन) और बाइ-डायरेक्शनल CRM सिंक (Salesforce / HubSpot)।
* **Milestone 4 (Weeks 7–8 / Days 31–40)**:
  - **Module 6**: एग्जीक्यूटिव सेल्स एनालिटिक्स डैशबोर्ड, एंड-टू-एंड ऑप्टिमाइजेशन और फाइनल डिप्लॉयमेंट।

---
*SalesGenie Platform • Prepared for Infosys Batch-4 Evaluation • All benchmarks verified.*
