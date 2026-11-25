# ChaosBrain AI

Graph-driven continuous resilience simulator and auto-remediation patch generator.

## Project Structure

```text
PRAKHAR/
├── frontend/                 # React + Vite + TypeScript UI
│   ├── package.json
│   ├── vite.config.ts
│   └── src/
├── backend/                  # Python FastAPI backend
│   ├── main.py               # Convenience entrypoint (imports app.main:app)
│   ├── requirements.txt
│   ├── app/
│   │   ├── main.py           # FastAPI app
│   │   ├── api/
│   │   ├── services/
│   │   ├── models/
│   │   └── ...
│   └── tests/
├── docs/
├── .env.example
└── README.md
```

## Tech Stack
- **Frontend:** React.js, TypeScript, Vite, Tailwind CSS, React Flow, Recharts
- **Backend:** Python, FastAPI, SQLAlchemy, SQLite, Pydantic
- **Simulation/Graph:** NetworkX, custom chaos & resilience engines
- **Testing:** Pytest

## Prerequisites (Windows / VS Code)
- Python 3.11+ (tested with Python 3.13)
- Node.js 20+ and npm
- VS Code with PowerShell terminal

## Setup & Run Locally

Open two VS Code terminals (one for backend, one for frontend).

### 1) Backend (Python/FastAPI) - Terminal 1

> **Important:** The backend is Python, not Node.js. Do **not** run `npm install` or `npm run dev` inside `backend/`.

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Backend runs at: `http://localhost:8000`  
API docs: `http://localhost:8000/docs`

### 2) Frontend (React/Vite) - Terminal 2

```powershell
cd frontend
npm install
npm run dev
```

Frontend runs at: `http://localhost:5173`

## Environment Variables

Root `.env.example` contains backend defaults. Frontend has `frontend/.env.example`:

```env
VITE_API_URL=http://localhost:8000
```

If needed, copy to `.env` in the same folder. Defaults work for local development.

## Running Tests

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
pytest -q
```

## Common Issue: ENOENT package.json in backend

If you see:

```text
npm error enoent Could not read package.json ...\backend\package.json
```

it means `npm` was run in the `backend` folder. Fix: run npm commands only in `frontend`, and Python/pip/uvicorn commands only in `backend`.

## Safety & MVP Notes
- Chaos experiments are **simulated on the infrastructure graph model only**; no real infrastructure is modified.
- Generated patches are **review-only** and never auto-executed on the host system.
- Patch validation is static/simulated.
- Monitoring is simulated for the MVP.
- LLM remediation is optional: set `LLM_PROVIDER` and `LLM_API_KEY` in env to enable adapter hook; otherwise rule-based fallback is used.
