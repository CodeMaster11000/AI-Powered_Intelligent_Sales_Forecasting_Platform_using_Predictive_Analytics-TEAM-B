# SalesGenie AI Platform

AI Sales Assistant and Lead Intelligence Platform: lead management, company profiling, predictive lead scoring, personalized outreach, conversation intelligence and CRM sync. Specified in [docs/srs/SalesGenie_AI_SRS.pdf](docs/srs/SalesGenie_AI_SRS.pdf) (IEEE Std 830-1998).

## Tech stack

| Layer | Technology |
|-------|-----------|
| API | FastAPI + Uvicorn |
| UI | Streamlit |
| Database | PostgreSQL 16 (Docker) via SQLAlchemy |
| AI / agents (later milestones) | LangGraph, Gemini / OpenAI |

## Quick start

Full OS-specific steps (Linux, macOS, Windows) are in **[SETUP.md](SETUP.md)**. The short version:

```
git clone <repo-url> && cd salesgenie-ai
python -m venv venv            # python3 on Linux/macOS
# activate the venv (see SETUP.md for your OS)
pip install -r requirements-dev.txt
cp .env.example .env           # Copy-Item on Windows PowerShell
docker compose up -d
uvicorn backend.main:app --reload       # terminal 1 -> http://localhost:8000/docs
streamlit run frontend/app.py           # terminal 2 -> http://localhost:8501
```

## Repository layout

```
.
├── backend/              FastAPI service
│   ├── main.py           app entry point
│   ├── database/         models + connection
│   ├── modules/          one file per SRS module
│   └── tests/            pytest tests
├── frontend/             Streamlit app
├── data/sample/          fake sample datasets (CSV)
├── docs/
│   ├── srs/              the SRS
│   ├── design/           database, wireframes, agent architecture
│   ├── api/              API contract
│   ├── testing/          test plan + reports
│   └── milestones/       per-milestone checklists
├── docker-compose.yml    PostgreSQL (+ optional pgAdmin)
├── requirements*.txt     core / dev / AI dependencies
└── SETUP.md
```

## Milestones

| # | Weeks | Focus | Checklist |
|---|-------|-------|-----------|
| 1 | 1-2 | Lead management and intelligence engine | [docs/milestones/milestone-1.md](docs/milestones/milestone-1.md) |
| 2 | 3-4 | Outreach generation and lead scoring | |
| 3 | 5-6 | CRM integration and conversation intelligence | |
| 4 | 7-8 | Dashboard, automation and deployment | |

## Team workflow

- `main` is always runnable. Never push to it directly.
- Branch names: `feature/<short-name>`, `fix/<short-name>`, `docs/<short-name>`.
- Every change goes through a pull request (template included); reference the requirement ID, e.g. `REQ-M1-02`.
- Change an endpoint or table? Update `docs/api/api-contract.md` or `docs/design/database/` in the same PR.
- Never commit `.env`. Only `.env.example` is tracked.
- AI packages are separate: `pip install -r requirements-ai.txt` when the AI milestones start.
