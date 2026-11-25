# Demo Workflow

1. Start backend (Terminal 1, from repo root): `cd backend; python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt; uvicorn app.main:app --reload --port 8000`
2. Start frontend (Terminal 2): `cd frontend; npm install; npm run dev`
3. Open `http://localhost:5173`.
4. Go to Infrastructure Graph - sample topology is preloaded.
5. Go to Chaos Experiments, select `PostgreSQL Database`, choose `database_failure`, severity 4, run.
6. Observe propagation, impact, and resilience score.
7. Go to Resilience Analysis for SPOFs and recommendations.
8. Go to AI Remediation, generate Python/JS/Java patch, review validation and approve.
9. Check Simulation History and reload a prior run.
10. Reset by reloading sample infra or editing graph.

> Note: Do not run npm commands in `backend/` (Python FastAPI). Do not run pip/uvicorn in `frontend/`.
