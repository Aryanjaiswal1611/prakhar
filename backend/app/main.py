import logging, time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.init_db import init_db, seed_if_empty
from app.api.routes_graph import router as graph_router
from app.api.routes_chaos import router as chaos_router
from app.api.routes_remediation import router as remediation_router
from app.api.routes_history import router as history_router
from app.api.routes_monitoring import router as monitoring_router
from app.api.routes_website_tests import router as website_tests_router
from app.api.routes_chatbot import router as chatbot_router
from app.api.routes_discovery import router as discovery_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger("chaosbrain")

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept", "Origin", "X-Requested-With"],
    expose_headers=["*"],
    max_age=600,
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    path = request.url.path
    method = request.method
    origin = request.headers.get("origin")
    try:
        response = await call_next(request)
        logger.info("req method=%s path=%s origin=%s status=%s duration_ms=%s", method, path, origin, response.status_code, int((time.time()-start)*1000))
        return response
    except Exception:
        logger.exception("req_failed method=%s path=%s origin=%s duration_ms=%s", method, path, origin, int((time.time()-start)*1000))
        raise

app.include_router(graph_router)
app.include_router(chaos_router)
app.include_router(remediation_router)
app.include_router(history_router)
app.include_router(monitoring_router)
app.include_router(website_tests_router)
app.include_router(chatbot_router)
app.include_router(discovery_router)


@app.on_event("startup")
def startup():
    init_db()
    seed_if_empty()
    logger.info("startup complete cors_origins=%s", settings.cors_origin_list)


@app.get("/api/health")
def health():
    return {"status": "ok", "app": settings.app_name}
