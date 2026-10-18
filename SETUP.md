
# Setup Guide

Pick your operating system: [Linux](#linux-ubuntu--debian) | [macOS](#macos) | [Windows](#windows-10--11). Then continue with [Running the project](#running-the-project) and [Troubleshooting](#troubleshooting).

**What you will have at the end:** A Python virtual environment with the project dependencies installed, PostgreSQL running in Docker, and the API and UI ready to run locally.

Docker is used for the database so everyone gets the same PostgreSQL setup without installing or configuring PostgreSQL manually.

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
newgrp docker
```

Check the installations:

```bash
python3 --version
git --version
docker --version
docker compose version
```

Python 3.11 or 3.12 is recommended.

### 2. Get the code

```bash
git clone https://github.com/CodeMaster11000/AI-Powered_Intelligent_Sales_Forecasting_Platform_using_Predictive_Analytics-TEAM-B.git salesgenie-ai
cd salesgenie-ai
```

Configure Git if you have not already done so:

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

### 3. Set up Python

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements-dev.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

### 5. Start the database

```bash
docker compose up -d db
docker compose ps
```

Wait until the database is healthy.

Follow the [Database Setup Guide](backend/database/SETUP.md) to initialize the database schema.

Continue to [Running the project](#running-the-project).

---

## macOS

### 1. Install tools

Install [Homebrew](https://brew.sh) if you do not already have it.

```bash
brew install python@3.12 git
brew install --cask docker
```

Open Docker Desktop from Applications and wait until it is running.

Check the installations:

```bash
python3 --version
git --version
docker --version
docker compose version
```

### 2. Get the code

```bash
git clone https://github.com/CodeMaster11000/AI-Powered_Intelligent_Sales_Forecasting_Platform_using_Predictive_Analytics-TEAM-B.git salesgenie-ai
cd salesgenie-ai
```

Configure Git if needed:

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

### 3. Set up Python

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements-dev.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

### 5. Start the database

```bash
docker compose up -d db
docker compose ps
```

Wait until the database is healthy.

Follow the [Database Setup Guide](backend/database/SETUP.md) to initialize the database schema.

Continue to [Running the project](#running-the-project).

---

## Windows 10 / 11

Use PowerShell for the commands below.

### 1. Install tools

Install the following:

1. **Python 3.12:** https://www.python.org/downloads/  
   Enable "Add python.exe to PATH" during installation.
2. **Git:** https://git-scm.com/download/win
3. **Docker Desktop:** https://www.docker.com/products/docker-desktop/  
   Enable WSL 2 if prompted, restart if required, and open Docker Desktop.
4. **VS Code (optional):** https://code.visualstudio.com/

Close and reopen PowerShell, then check:

```powershell
python --version
git --version
docker --version
docker compose version
```

### 2. Get the code

```powershell
git clone https://github.com/CodeMaster11000/AI-Powered_Intelligent_Sales_Forecasting_Platform_using_Predictive_Analytics-TEAM-B.git salesgenie-ai
cd salesgenie-ai
```

Configure Git if needed:

```powershell
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

### 3. Set up Python

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks activation because of the execution policy, run:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

Activate the environment again, then install dependencies:

```powershell
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
```

### 4. Configure environment variables

```powershell
Copy-Item .env.example .env
```

### 5. Start the database

```powershell
docker compose up -d db
docker compose ps
```

Wait until the database is healthy.

Follow the [Database Setup Guide](backend/database/SETUP.md) to initialize the database schema.

Continue to [Running the project](#running-the-project).

---

## Running the project

Run all commands from the repository root with the Python virtual environment activated.

Use separate terminals for the API and UI.

### Terminal 1: API

```bash
uvicorn backend.main:app --reload
```

API documentation: http://localhost:8000/docs

### Terminal 2: UI

```bash
streamlit run frontend/app.py
```

UI: http://localhost:8501

The API and UI commands require their respective application files to be implemented.

### Checking the database

To open a PostgreSQL shell:

```bash
docker compose exec db psql -U salesgenie -d salesgenie
```

Inside the shell:

- `\dt` lists tables.
- `\d leads` describes the `leads` table.
- `\q` exits PostgreSQL.

For database initialization and schema changes, see the [Database Setup Guide](backend/database/SETUP.md).

### Optional: pgAdmin

If pgAdmin is configured in the Compose file, start it with:

```bash
docker compose --profile tools up -d pgadmin
```

Open http://localhost:5050 and sign in using the credentials configured in your Compose setup.

### Every session

1. Open a terminal in the repository root.
2. Activate the Python virtual environment.
3. Start the required services:

   ```bash
   docker compose up -d
   ```

4. Start the API and UI in separate terminals when they are ready.

You only need to initialize the database schema once, or when new migrations have been added. See the [Database Setup Guide](backend/database/SETUP.md).

### Stopping and resetting

| Goal | Command |
|---|---|
| Stop containers and keep database data | `docker compose down` |
| Stop containers and delete database volumes | `docker compose down -v` |
| View database logs | `docker compose logs -f db` |

**Warning:** `docker compose down -v` deletes associated volumes and can permanently remove your database data.

### Optional: AI packages

If a later milestone requires AI dependencies:

```bash
pip install -r requirements-ai.txt
```

Add your API key to `.env` if required:

```ini
OPENAI_API_KEY=your-api-key
```

Never commit `.env` or API keys to Git.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `port is already allocated` | Another process is using the port. Stop the conflicting process or configure a different host port in `.env`. |
| `docker: permission denied` on Linux | Check Docker group permissions and log out and back in if necessary. |
| Cannot connect to Docker | Start Docker Desktop on Windows/macOS or start the Docker service on Linux. |
| Database is unhealthy | Run `docker compose logs db` and check the database configuration. |
| `python` not found on Windows | Reinstall Python with "Add to PATH" enabled, then reopen PowerShell. |
| `python` not found on Linux/macOS | Use `python3` outside the virtual environment. |
| `No module named ...` | Activate the virtual environment and install the project dependencies. |
| Port 8000 or 8501 is already in use | Stop the other process or configure a different API/UI port. |
| Database tables are missing | Follow the [Database Setup Guide](backend/database/SETUP.md) and apply pending migrations. |

---

For database-specific instructions, see [`backend/database/SETUP.md`](backend/database/SETUP.md).
