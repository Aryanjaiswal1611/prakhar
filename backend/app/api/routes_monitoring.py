from fastapi import APIRouter
from datetime import datetime
import random

router = APIRouter(prefix="/api/monitoring", tags=["monitoring"])
SETTINGS = {"interval_sec": 30, "enabled": True}


@router.get("/status")
def status():
    # simulated monitoring data for MVP
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "enabled": SETTINGS["enabled"],
        "interval_sec": SETTINGS["interval_sec"],
        "system_health": random.choice(["Healthy","Degraded","Healthy","Healthy"]),
        "active_failures": random.randint(0,2),
        "recovery_progress_pct": random.randint(60,100),
    }


@router.get("/settings")
def get_settings():
    return SETTINGS


@router.put("/settings")
def put_settings(payload: dict):
    SETTINGS["interval_sec"] = int(payload.get("interval_sec", SETTINGS["interval_sec"]))
    SETTINGS["enabled"] = bool(payload.get("enabled", SETTINGS["enabled"]))
    return SETTINGS
