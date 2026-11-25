# ChaosBrain AI API

Base URL: `http://localhost:8000`

## Health
- `GET /api/health`

## Graphs
- `GET /api/graphs`
- `POST /api/graphs`
- `GET /api/graphs/{id}`
- `PUT /api/graphs/{id}`
- `DELETE /api/graphs/{id}`
- `GET /api/graphs/{id}/export`
- `POST /api/graphs/import`

## Chaos
- `GET /api/chaos/experiments/predefined`
- `POST /api/chaos/simulate`
  - body: `{ "infrastructure_id": 1, "experiment": {"experiment_type":"database_failure","target_node_key":"database","severity":4} }`

## Remediation
- `POST /api/remediation/generate` `{ "run_id": 1, "language": "python" }`
- `POST /api/remediation/{id}/validate`
- `POST /api/remediation/{id}/approve`
- `GET /api/remediation/run/{run_id}`

## History
- `GET /api/history/runs`
- `GET /api/history/runs/{id}`

## Monitoring (simulated)
- `GET /api/monitoring/status`
- `GET /api/monitoring/settings`
- `PUT /api/monitoring/settings`
