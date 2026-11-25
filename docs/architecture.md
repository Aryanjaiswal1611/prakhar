# Architecture

## Components
- **Frontend (React+TS+Vite)**: Dashboard, React Flow graph editor, chaos controls, resilience charts, remediation review.
- **FastAPI Backend**: REST API, orchestration, persistence.
- **Graph Engine (NetworkX)**: dependency graph, propagation traversal (BFS), SPOF heuristic.
- **Chaos Engine**: controlled failure models, severity-based status degradation, impact estimation.
- **Resilience Engine**: weighted score (0-100), classification, recommendations.
- **Remediation Engine**: rule-based fallback + LLM adapter hook; patch templates for Python/JS/Java.
- **Patch Validation**: safe static/simulated checks only; no host execution.
- **SQLite/SQLAlchemy**: infrastructures, runs, remediations.

## Flow
Frontend -> FastAPI -> Graph/Chaos/Resilience/Remediation/Validation -> SQLite -> API response -> Dashboard.

## Safety
- Simulated failures only; no real infrastructure operations.
- Patches are review-only; explicit user approval required in UI.
- Validation rejects unsafe patterns and never executes patches on host.
