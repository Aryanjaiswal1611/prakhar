import json, logging, time
from urllib.parse import urlparse
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.simulation import InfrastructureSnapshot
from app.services.discovery_service import discover_infrastructure

logger = logging.getLogger("chaosbrain.discovery")
router = APIRouter(prefix="/api/discovery", tags=["discovery"])


def _validate_url(raw: str) -> str:
    url = (raw or "").strip()
    if not url:
        raise HTTPException(status_code=400, detail="URL is required.")
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url
    p = urlparse(url)
    if p.scheme not in ("http", "https") or not p.netloc:
        raise HTTPException(status_code=400, detail="Invalid URL.")
    return url


@router.get("/infrastructure")
def infrastructure(url: str, request: Request, db: Session = Depends(get_db)):
    t0 = time.time()
    normalized = _validate_url(url)
    logger.info("discovery start origin=%s url=%s", request.headers.get("origin"), normalized)
    try:
        graph = discover_infrastructure(normalized)
    except Exception as e:
        logger.exception("discovery failed url=%s", normalized)
        raise HTTPException(status_code=500, detail=f"Infrastructure discovery failed: {str(e)}")
    snap = InfrastructureSnapshot(url=normalized, source="discovery", graph_json=json.dumps(graph))
    db.add(snap); db.commit(); db.refresh(snap)
    logger.info("discovery done url=%s nodes=%s duration_ms=%s", normalized, len(graph.get("nodes",[])), int((time.time()-t0)*1000))
    return {"snapshot_id": snap.id, **graph}


@router.get("/latest")
def latest(url: str, db: Session = Depends(get_db)):
    normalized = _validate_url(url)
    snap = db.query(InfrastructureSnapshot).filter(InfrastructureSnapshot.url == normalized).order_by(InfrastructureSnapshot.id.desc()).first()
    if not snap:
        raise HTTPException(404, "No infrastructure snapshot found for URL")
    data = json.loads(snap.graph_json or "{}")
    data["snapshot_id"] = snap.id
    return data
