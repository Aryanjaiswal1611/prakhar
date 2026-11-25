import json, logging, time
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.website_test import WebsiteTestRun
from app.models.simulation import InfrastructureSnapshot
from app.schemas.website_test import WebsiteTestRequest
from app.services.website_test_engine import WebsiteResilienceTester
from app.services.discovery_service import discover_infrastructure

logger = logging.getLogger("chaosbrain.website_tests")
router = APIRouter(prefix="/api/website-tests", tags=["website-tests"])
tester = WebsiteResilienceTester()
EXECUTOR = ThreadPoolExecutor(max_workers=4)
ROUTE_DEADLINE_SEC = 35.0


def _to_result(r: WebsiteTestRun) -> dict:
    data = json.loads(r.result_json or "{}")
    data.update({"id": r.id, "url": r.url, "test_mode": r.test_mode, "created_at": r.created_at.isoformat(), "overall_score": r.overall_score, "classification": r.classification})
    return data


def _validate_url(raw: str) -> str:
    url = (raw or "").strip()
    if not url: raise HTTPException(status_code=400, detail="URL is required.")
    if not url.startswith("http://") and not url.startswith("https://"): url = "https://" + url
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc: raise HTTPException(status_code=400, detail="Invalid URL. Please enter a valid http/https URL.")
    host = parsed.hostname or ""
    if "." not in host and host.lower() not in ("localhost",): raise HTTPException(status_code=400, detail="Invalid URL host.")
    return url


def _run_all(url: str, mode: str, include_api_endpoint: str | None):
    result = tester.run(url=url, mode=mode, include_api_endpoint=include_api_endpoint)
    try:
        result["discovered_infrastructure"] = discover_infrastructure(url)
    except Exception as e:
        result["discovered_infrastructure"] = {"url": url, "nodes": [], "edges": [], "partial": True, "summary": f"Discovery failed: {e}", "evidence": [{"check":"discovery","ok":False,"error":str(e)}]}
    return result


@router.post("/run")
def run_test(req: WebsiteTestRequest, request: Request, db: Session = Depends(get_db)):
    t0 = time.time()
    origin = request.headers.get("origin")
    logger.info("website_test start origin=%s url=%s mode=%s", origin, req.url, req.mode)
    url = _validate_url(req.url)
    future = EXECUTOR.submit(_run_all, url, req.mode, req.include_api_endpoint)
    try:
        result = future.result(timeout=ROUTE_DEADLINE_SEC)
    except FuturesTimeoutError:
        future.cancel()
        logger.warning("website_test deadline_exceeded url=%s duration_ms=%s", url, int((time.time()-t0)*1000))
        raise HTTPException(status_code=504, detail={"error":"timeout","message":"Website resilience test exceeded the backend execution deadline.","url":url,"deadline_sec":ROUTE_DEADLINE_SEC})
    except Exception as e:
        logger.exception("website_test failed url=%s", url)
        raise HTTPException(status_code=500, detail=f"Resilience test failed: {str(e)}")

    if not isinstance(result, dict) or "overall_score" not in result or not isinstance(result.get("tests"), list):
        raise HTTPException(status_code=500, detail="Backend returned invalid test result structure.")

    try:
        di = result.get("discovered_infrastructure")
        if di:
            db.add(InfrastructureSnapshot(url=url, source="test", graph_json=json.dumps(di)))
        run = WebsiteTestRun(url=url, test_mode=req.mode, status="completed", overall_score=float(result.get("overall_score", 0.0)), classification=str(result.get("classification", "Unknown")), result_json=json.dumps(result))
        db.add(run); db.commit(); db.refresh(run)
        out = _to_result(run)
    except Exception as e:
        db.rollback(); logger.exception("website_test persist_failed url=%s", url)
        raise HTTPException(status_code=500, detail=f"Failed to persist website test result: {str(e)}")

    logger.info("website_test done url=%s score=%s duration_ms=%s", url, out.get("overall_score"), int((time.time()-t0)*1000))
    return out


@router.get("")
def list_tests(db: Session = Depends(get_db)):
    runs = db.query(WebsiteTestRun).order_by(WebsiteTestRun.id.desc()).limit(50).all()
    return [{"id":r.id,"url":r.url,"test_mode":r.test_mode,"overall_score":r.overall_score,"classification":r.classification,"created_at":r.created_at.isoformat()} for r in runs]


@router.get("/{run_id}")
def get_test(run_id: int, db: Session = Depends(get_db)):
    r = db.query(WebsiteTestRun).filter(WebsiteTestRun.id == run_id).first()
    if not r: raise HTTPException(404, "Test run not found")
    return _to_result(r)


@router.get("/{run_id}/report")
def get_report(run_id: int, db: Session = Depends(get_db)):
    r = db.query(WebsiteTestRun).filter(WebsiteTestRun.id == run_id).first()
    if not r: raise HTTPException(404, "Test run not found")
    return {"report": _to_result(r), "format": "json"}
