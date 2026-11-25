import json, logging, os, time
from urllib.parse import urlparse
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.infrastructure import Infrastructure, GraphNode, GraphEdge
from app.models.simulation import SimulationRun, CustomSimulation
from app.schemas.chaos import SimulationRequest, SimulationResult, CustomSimulationCreate
from app.services.chaos_engine import ChaosSimulationEngine
from app.services.resilience_engine import ResilienceAnalysisEngine
from app.services.discovery_service import discover_infrastructure

logger = logging.getLogger("chaosbrain.chaos")
router = APIRouter(prefix="/api/chaos", tags=["chaos"])
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "predefined_experiments.json")


def _validate_url(raw: str | None) -> str | None:
    if raw is None: return None
    url = raw.strip()
    if not url: return None
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url
    p = urlparse(url)
    if p.scheme not in ("http", "https") or not p.netloc:
        raise HTTPException(status_code=400, detail="Invalid URL. Please enter a valid http/https URL.")
    return url


def _infra_from_discovery(db: Session, url: str) -> Infrastructure:
    g = discover_infrastructure(url)
    infra = Infrastructure(name=f"Discovered: {url}", description=g.get("summary", ""))
    db.add(infra); db.commit(); db.refresh(infra)
    for n in g.get("nodes", []):
        db.add(GraphNode(infrastructure_id=infra.id, node_key=n["node_key"], name=n["name"], type=n.get("type", "service"), status=n.get("status", "unknown"), criticality=int(n.get("criticality", 1)), x=float(n.get("x", 0)), y=float(n.get("y", 0)), metadata_json=json.dumps(n.get("metadata", {}))))
    for e in g.get("edges", []):
        db.add(GraphEdge(infrastructure_id=infra.id, edge_key=e["edge_key"], source_key=e["source_key"], target_key=e["target_key"], dependency_type=e.get("dependency_type", "sync"), critical=bool(e.get("critical", True))))
    db.commit(); db.refresh(infra)
    return infra


@router.get("/experiments/predefined")
def predefined_experiments():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@router.get("/custom")
def list_custom(db: Session = Depends(get_db)):
    rows = db.query(CustomSimulation).order_by(CustomSimulation.id.desc()).limit(100).all()
    return [{
        "id": r.id, "name": r.name, "description": r.description, "url": r.url,
        "experiment_type": r.experiment_type, "target_node_key": r.target_node_key,
        "severity": r.severity, "duration_sec": r.duration_sec, "target_endpoint": r.target_endpoint,
        "params": json.loads(r.params_json or "{}"), "created_at": r.created_at.isoformat(),
    } for r in rows]


@router.post("/custom")
def create_custom(req: CustomSimulationCreate, db: Session = Depends(get_db)):
    url = _validate_url(req.url)
    row = CustomSimulation(name=req.name.strip() or "Custom Simulation", description=req.description or "", url=url or "", experiment_type=req.experiment_type, target_node_key=req.target_node_key or "website", severity=req.severity, duration_sec=req.duration_sec, target_endpoint=req.target_endpoint or "", params_json=json.dumps(req.params or {}))
    db.add(row); db.commit(); db.refresh(row)
    return {"id": row.id, "name": row.name, "description": row.description, "url": row.url, "experiment_type": row.experiment_type, "target_node_key": row.target_node_key, "severity": row.severity, "duration_sec": row.duration_sec, "target_endpoint": row.target_endpoint, "params": json.loads(row.params_json or "{}")}


@router.post("/simulate")
def simulate(req: SimulationRequest, request: Request, db: Session = Depends(get_db)):
    t0 = time.time()
    url = _validate_url(req.url)
    logger.info("chaos start origin=%s url=%s infra=%s type=%s target=%s", request.headers.get("origin"), url, req.infrastructure_id, req.experiment.experiment_type, req.experiment.target_node_key)
    try:
        infra = None
        if req.infrastructure_id:
            infra = db.query(Infrastructure).filter(Infrastructure.id == req.infrastructure_id).first()
            if not infra:
                raise HTTPException(status_code=404, detail="Infrastructure not found for simulation.")
        elif url:
            infra = _infra_from_discovery(db, url)
        else:
            raise HTTPException(status_code=400, detail="Provide infrastructure_id or website URL for simulation.")

        nodes = [{"node_key": n.node_key, "name": n.name, "type": n.type, "status": n.status, "criticality": n.criticality, "metadata": json.loads(n.metadata_json or "{}")} for n in infra.nodes]
        edges = [{"edge_key": e.edge_key, "source_key": e.source_key, "target_key": e.target_key, "dependency_type": e.dependency_type, "critical": bool(e.critical)} for e in infra.edges]
        if not nodes:
            raise HTTPException(status_code=400, detail="No infrastructure nodes available for simulation.")

        baseline = {"healthy": sum(1 for n in nodes if n.get("status") == "healthy"), "warning": sum(1 for n in nodes if n.get("status") == "warning"), "failed": sum(1 for n in nodes if n.get("status") == "failed"), "total": len(nodes)}
        sim = ChaosSimulationEngine().simulate(nodes, edges, req.experiment.model_dump())
        analysis = ResilienceAnalysisEngine().analyze(nodes, edges, sim)
        sim["resilience"] = analysis
        sim["recommendations"] = analysis["recommendations"]
        sim["url"] = url
        sim["name"] = req.name
        sim["baseline"] = baseline
        sim["verification"] = {"status": "completed", "checks": ["dependency propagation evaluated", "impact metrics computed", "recovery estimate generated"]}
        sim["comparison"] = {"baseline_healthy": baseline["healthy"], "post_failed": sim["impact"].get("failed_count", 0), "post_warning": sim["impact"].get("warning_count", 0), "availability_pct": sim["impact"].get("availability_pct", 0)}
        sim["report"] = {"summary": f"Simulated {req.experiment.experiment_type} on {req.experiment.target_node_key}.", "recovered": sim["impact"].get("failed_count", 0) == 0, "duration_sec": int(req.experiment.params.get("duration_sec", 30)), "mode": "controlled_simulation"}
        sim["status"] = "completed"
        sim["error"] = None
        sim["error_type"] = None

        run = SimulationRun(
            infrastructure_id=infra.id, experiment_type=req.experiment.experiment_type, target_node_key=req.experiment.target_node_key,
            severity=req.experiment.severity, status="completed", resilience_score=analysis["score"], classification=analysis["classification"],
            result_json=json.dumps({**sim, "experiment": req.experiment.model_dump()}), url=url or "", name=req.name or "", error_message=""
        )
        db.add(run); db.commit(); db.refresh(run)
        logger.info("chaos done run=%s duration_ms=%s", run.id, int((time.time()-t0)*1000))
        return {
            "run_id": run.id, "infrastructure_id": infra.id, "experiment": req.experiment.model_dump(), "initial_failure": sim["initial_failure"],
            "node_statuses": sim["node_statuses"], "affected_nodes": sim["affected_nodes"], "propagation_path": sim["propagation_path"],
            "impact": sim["impact"], "resilience": sim["resilience"], "recommendations": sim["recommendations"], "events": sim["events"],
            "status": sim["status"], "error": sim["error"], "error_type": sim["error_type"], "url": url, "baseline": sim["baseline"],
            "verification": sim["verification"], "comparison": sim["comparison"], "report": sim["report"]
        }
    except HTTPException as e:
        logger.warning("chaos http_error status=%s detail=%s", e.status_code, e.detail)
        raise
    except Exception as e:
        logger.exception("chaos failed")
        raise HTTPException(status_code=500, detail={"error": "simulation_engine_failure", "message": str(e), "recovery": "Check backend logs, verify URL/infrastructure exists, and retry."})
