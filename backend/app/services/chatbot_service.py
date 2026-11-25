import json
from pydantic import BaseModel
from typing import Optional, Dict, Any
from app.core.config import settings

router_mod = None

class ChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None


def rule_based(msg: str, ctx: Dict[str, Any] | None) -> str:
    m = msg.lower()
    ctx = ctx or {}
    score = ctx.get("overall_score")
    cls = ctx.get("classification")
    factors = ctx.get("factors", {})
    url = ctx.get("url")
    critical = ctx.get("critical_issues", [])
    recs = ctx.get("recommendations", [])

    if any(k in m for k in ["what is chaosbrain", "about project", "explain project"]):
        return "ChaosBrain AI is a graph-driven resilience simulator and auto-remediation assistant. It tests website reliability, simulates/infers failures, analyzes propagation, calculates a weighted resilience score (0-100), and suggests improvements."
    if "score" in m and ("how" in m or "calculate" in m or "work" in m):
        return "Resilience Score = Server(20%) + API(20%) + Network(15%) + Backend(20%) + Performance(15%) + Security(10%). Each factor is 0-100; weighted sum gives 0-100. 90-100 Excellent, 75-89 Good, 50-74 Moderate, 25-49 Weak, 0-24 Critical."
    if "why" in m and "score" in m and score is not None:
        weak = sorted([(k,v.get("score",0)) for k,v in factors.items()], key=lambda x:x[1])[:2]
        weak_txt = ", ".join([f"{k.replace('_',' ')} ({s})" for k,s in weak]) if weak else "no factor data"
        return f"{url or 'The tested website'} received {score}/100 ({cls}) mainly due to lower factor scores in: {weak_txt}. Critical issues: {('; '.join(critical[:2])) if critical else 'none reported'}. Recommendation: {(recs[0] if recs else 'review factor details.')}"
    if "improve" in m or "recommend" in m:
        if recs: return "Top recommendations: " + " ".join([f"{i+1}. {r}" for i,r in enumerate(recs[:4])])
        return "Improve resilience with health checks, retries/circuit breakers, redundancy, caching, HTTPS/security headers, and monitoring."
    if score is not None:
        return f"Latest test for {url or 'website'}: {score}/100 ({cls}). Ask about server/API/network/backend/performance/security, or ask why this score was assigned."
    return "I'm ChaosBrain AI Assistant (rule-based fallback, no AI key configured). I can explain project, scores, failures, and recommendations."
