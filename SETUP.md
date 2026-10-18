# Setup Guide

Pick your operating system: [Linux](#linux-ubuntu--debian) | [macOS](#macos) | [Windows](#windows-10--11). Then continue with [Running the project](#running-the-project) and [Troubleshooting](#troubleshooting).

**What you will have at the end:** Python virtual environment with all packages, PostgreSQL running in Docker, and the API and UI running locally.

Why Docker for the database: everyone gets the identical PostgreSQL version and settings on any OS, and nobody installs or configures Postgres by hand.

---

## Linux (Ubuntu / Debian)

### 1. Install tools
```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git curl
```
Install Docker Engine and the Compose plugin:
```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
newgrp docker          # or log out and back in
```
Check:
```bash
python3 --version      # 3.11 or 3.12 recommended
git --version
docker --version
docker compose version
```

### 2. Get the code
```bash
git clone <repo-url> salesgenie-ai
cd salesgenie-ai
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

### 3. Python environment
```bash
python3 -m venv venv
source venv/bin/activate        # you should now see (venv) in your prompt
pip install --upgrade pip
pip install -r requirements-dev.txt
```

### 4. Configuration
```bash
cp .env.example .env
```

### 5. Start the database
```bash
docker compose up -d
docker compose ps               # STATUS should become "healthy"
```
Continue at [Running the project](#running-the-project).

---

## macOS

### 1. Install tools
Install Homebrew first if you don't have it (https://brew.sh), then:
```bash
brew install python@3.12 git
brew install --cask docker
```
Open **Docker Desktop** once from Applications and wait until it says it is running. Apple Silicon and Intel both work; the Postgres image supports both.

Check:
```bash
python3 --version
git --version
docker --version
docker compose version
```

### 2. Get the code
```bash
git clone <repo-url> salesgenie-ai
cd salesgenie-ai
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

### 3. Python environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements-dev.txt
```

### 4. Configuration
```bash
cp .env.example .env
```

### 5. Start the database
```bash
docker compose up -d
docker compose ps               # STATUS should become "healthy"
```
Continue at [Running the project](#running-the-project).

---

## Windows 10 / 11

Use **PowerShell** (not the old cmd) for everything below.

### 1. Install tools
1. **Python 3.12**: https://www.python.org/downloads/ . On the first installer screen tick **"Add python.exe to PATH"**, then Install Now.
2. **Git**: https://git-scm.com/download/win (defaults are fine).
3. **Docker Desktop**: https://www.docker.com/products/docker-desktop/ . Accept the WSL 2 option if asked, restart if prompted, then open Docker Desktop and wait until it says it is running.
4. **VS Code** (optional): https://code.visualstudio.com/ with the Python extension.

Close and reopen PowerShell, then check:
```powershell
python --version
git --version
docker --version
docker compose version
```

### 2. Get the code
```powershell
git clone <repo-url> salesgenie-ai
cd salesgenie-ai
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

### 3. Python environment
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```
If PowerShell refuses with an "execution policy" error, run this once and retry:
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```
You should see `(venv)` in your prompt. Then:
```powershell
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
```

### 4. Configuration
```powershell
Copy-Item .env.example .env
```

### 5. Start the database
```powershell
docker compose up -d
docker compose ps               # STATUS should become "healthy"
```
Continue at [Running the project](#running-the-project).

---

## Running the project

Run from the repository root with the virtual environment active. Use two terminals.

**Terminal 1: API**
```
uvicorn backend.main:app --reload
```
Docs at http://localhost:8000/docs

**Terminal 2: UI**
```
streamlit run frontend/app.py
```
UI at http://localhost:8501

> The two commands above only work once `backend/main.py` and `frontend/app.py` contain an app. Until then, the database check below is how you confirm your setup.

### Checking the database
```
docker compose exec db psql -U salesgenie -d salesgenie
```
Inside: `\dt` lists tables, `\d leads` describes a table, `\q` quits. (Use the user and database names from your `.env` if you changed them.)

Optional visual browser (pgAdmin):
```
docker compose --profile tools up -d
```
Open http://localhost:5050, log in with `admin@salesgenie.dev` / `admin`, and add a server with host `db`, port `5432`, and the user/password from `.env`.

### Every session
1. `cd` into the project and activate the venv
2. `docker compose up -d`
3. Start the API and the UI

### Stopping and resetting
| Goal | Command |
|------|---------|
| Stop the database, keep data | `docker compose down` |
| **Wipe all data** (clean demo / fresh start) | `docker compose down -v` then `docker compose up -d` |
| See database logs | `docker compose logs -f db` |

### Optional: AI packages (later milestones)
```
pip install -r requirements-ai.txt
```
Then put your key in `.env` as `OPENAI_API_KEY`. Never commit `.env`.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `port is already allocated` / port 5432 in use | A local Postgres is running. Stop it (Linux: `sudo systemctl stop postgresql`), or set `DB_PORT=5433` in `.env` **and** change the port in `DATABASE_URL` to match, then `docker compose up -d` again. |
| `docker: permission denied` (Linux) | You skipped `usermod -aG docker $USER`; run it, then log out and in. |
| `Cannot connect to the Docker daemon` | Docker Desktop (Windows/macOS) isn't running, or on Linux run `sudo systemctl start docker`. |
| Database stays "starting" or "unhealthy" | `docker compose logs db`. If you changed the password in `.env` after the first start, run `docker compose down -v` once so the volume is recreated. |
| `python` not found (Windows) | Reinstall Python with "Add to PATH" ticked, reopen PowerShell. |
| `python` not found (Linux/macOS) | Use `python3`. Inside an activated venv, `python` works too. |
| `No module named ...` | The venv isn't active (no `(venv)` in the prompt) or the install didn't finish. Activate, then `pip install -r requirements-dev.txt`. |
| `Address already in use` on 8000 / 8501 | Another instance is running. Stop it, or use `--port 8001` (uvicorn) / `--server.port 8502` (streamlit). |
| Weird "whole file changed" diffs | Line-ending mismatch. `.gitattributes` forces LF; run `git add --renormalize .` once. |
