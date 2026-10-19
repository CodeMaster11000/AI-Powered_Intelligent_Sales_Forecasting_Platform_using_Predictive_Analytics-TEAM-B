# ⚡ SalesGenie AI Platform

> **AI Sales Assistant & Lead Intelligence Platform**  
> Prepared in accordance with **IEEE Std 830-1998**  
> Infosys Batch-4 Capstone Project • **AI/ML Engineer**: Jayant Vaibhav

---

## 🚀 Quick Start (One-Click Demo Launch)

To launch the dual-microservice runtime (**FastAPI REST API** on port 8000 + **Streamlit UI** on port 8501):

```bash
python run_demo.py
```

Or run services individually:

```bash
# 1. Run FastAPI Backend Microservices
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload

# 2. Run Streamlit Presentation Dashboard
streamlit run frontend/app.py
```

Open your browser at: **[http://localhost:8501](http://localhost:8501)**

---

## 🧪 Running Milestone 1 Automated Acceptance Tests

To execute the automated IEEE 830 acceptance verification suite:

```bash
python -m pytest tests/test_milestone1_acceptance.py -v
```

---

## 👥 Team Roles & Responsibilities

| # | Role | Member | Primary Modules Owned |
|---|---|---|---|
| 1 | Project Lead & DevOps | Ekansh Agnihotri | Sprint Planning, PostgreSQL DB, CI/CD |
| 2 | Backend Developer | Varshitha Kota | FastAPI endpoints, CRUD APIs, Integration Layer |
| 3 | **AI/ML Engineer** | **Jayant Vaibhav** | **LangGraph Agents, Lead Intelligence (Mod 2), Outreach (Mod 3), Scoring (Mod 4), Summarization (Mod 5)** |
| 4 | QA / Test Engineer | Devendra Bisne | Test Suites, Acceptance Benchmarks, UAT |

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
│   │   │   ├── prompts.py              # Strict Grounding LLM Prompts
│   │   │   ├── llm_client.py           # Gemini/OpenAI wrapper with zero-failure fallback
│   │   │   ├── research_agent.py       # Module 2: Profiling & Transformation Detection
│   │   │   └── qualification_agent.py  # Module 2: Scoring (0-100) & Growth Signals
│   │   ├── services/
│   │   │   ├── lead_service.py         # Multi-vector ingestion & lifecycle stages
│   │   │   └── intelligence_service.py # LangGraph execution orchestrator
│   │   └── routes/
│   │       ├── leads.py                # Prospect REST endpoints
│   │       └── intelligence.py         # Lead Intelligence REST endpoints
├── frontend/
│   └── app.py                          # Streamlit Interactive Dashboard
├── data/
│   └── sample_leads.csv                # Ingestion seed dataset (TechCorp, DataFlow, etc.)
├── tests/
│   └── test_milestone1_acceptance.py   # Automated Acceptance Tests (6/6 Passing)
├── docs/
│   ├── LangGraph_Agent_Architecture.md # Day 3 Architecture Deliverable
│   └── Milestone1_Test_Report.md       # Day 7/8/9 Acceptance Test Report
├── run_demo.py                         # One-click dual microservice launcher
├── requirements.txt                    # Project dependencies
└── conftest.py                         # Pytest configuration
```

---

## 🎯 Milestone 1 Deliverables Summary (Completed up to Day 8)

* **Module 1 (Lead Management & Ingestion)**:
  * 8 Relational Database tables created (`Leads`, `Company_Insights`, etc.).
  * Multi-vector ingestion (CSV upload, manual form, automated seed).
  * 5 Lifecycle stages tracking (`New Leads`, `Qualified`, `Proposal`, `Negotiation`, `Closed Won`).
* **Module 2 (Lead Intelligence & Company Analysis - Jayant's Core Deliverable)**:
  * **REQ-M2-01**: Automated company profiling & 5-dimension tech stack categorization.
  * **REQ-M2-02**: Detection of 4 key transformation opportunities (*ERP Modernization, Cloud Migration, Process Automation, Digital Transformation*).
  * **REQ-M2-03**: Overall Qualification Score (0-100), Series C High Growth Potential signal detection, Tech Alignment metrics, Decision Maker persona profiling.
  * **LangGraph Multi-Agent StateGraph**: Research Agent $\to$ Qualification Agent pipeline executing with sub-second latency ($< 0.05$s vs $< 5.0$s SLA).
* **Evaluation & Testing**:
  * 6 automated acceptance test suites passing with 100% success rate.
  * Verified against Infosys Batch-4 Milestone 1 evaluation benchmarks.
