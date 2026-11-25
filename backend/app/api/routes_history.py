import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.simulation import SimulationRun

router = APIRouter(prefix="/api/history", tags=["history"])


@router.get("/runs")
def list_runs(db: Session = Depends(get_db)):
    runs = db.query(SimulationRun).order_by(SimulationRun.id.desc()).limit(50).all()
    return [{
        "id": r.id, "infrastructure_id": r.infrastructure_id, "experiment_type": r.experiment_type,
        "target_node_key": r.target_node_key, "severity": r.severity, "resilience_score": r.resilience_score,
        "classification": r.classification, "created_at": r.created_at.isoformat()
    } for r in runs]


@router.get("/runs/{run_id}")
def get_run(run_id: int, db: Session = Depends(get_db)):
    r = db.query(SimulationRun).filter(SimulationRun.id==run_id).first()
    if not r: raise HTTPException(404, "Run not found")
    return {
        "id": r.id, "infrastructure_id": r.infrastructure_id, "experiment_type": r.experiment_type,
        "target_node_key": r.target_node_key, "severity": r.severity, "resilience_score": r.resilience_score,
        "classification": r.classification, "created_at": r.created_at.isoformat(),
        "result": json.loads(r.result_json or "{}")
    }
