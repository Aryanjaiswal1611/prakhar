import json
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.simulation import SimulationRun, RemediationRecord
from app.models.website_test import WebsiteTestRun
from app.remediation.rule_based import rule_based_remediation
from app.services.patch_validation import validate_patch
from app.core.config import settings


def _from_website_test(test: Dict[str, Any], language: str) -> Dict[str, Any]:
    factors = test.get("factors", {})
    weak = sorted([(k, v.get("score", 0)) for k, v in factors.items()], key=lambda x: x[1])
    worst = weak[0][0] if weak else "server_availability"
    affected = [k for k, v in factors.items() if v.get("score", 100) < 75]
    critical = test.get("critical_issues", [])
    recs = test.get("recommendations", [])
    lang = language if language in ("python", "javascript", "java") else "python"
    patches = {
        "python": "import requests\nfrom tenacity import retry, stop_after_attempt, wait_exponential\n\n@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8))\ndef resilient_get(url, timeout=5):\n    r = requests.get(url, timeout=timeout)\n    r.raise_for_status()\n    return r\n",
        "javascript": "export async function resilientFetch(url, retries=3, timeoutMs=5000){\n  let last; for(let i=0;i<retries;i++){ const c=new AbortController(); const t=setTimeout(()=>c.abort(),timeoutMs);\n    try{ const r=await fetch(url,{signal:c.signal}); clearTimeout(t); if(!r.ok) throw new Error(`HTTP ${r.status}`); return r; }\n    catch(e){ last=e; clearTimeout(t); await new Promise(r=>setTimeout(r,500*Math.pow(2,i))); }\n  } throw last;\n}\n",
        "java": "public class ResilientHttp {\n  public static java.net.http.HttpResponse<String> get(String url) throws Exception {\n    var client = java.net.http.HttpClient.newBuilder().connectTimeout(java.time.Duration.ofSeconds(5)).build();\n    Exception last=null; for(int i=0;i<3;i++){ try {\n      var req = java.net.http.HttpRequest.newBuilder(java.net.URI.create(url)).timeout(java.time.Duration.ofSeconds(5)).GET().build();\n      var res = client.send(req, java.net.http.HttpResponse.BodyHandlers.ofString());\n      if(res.statusCode()<500) return res; last=new RuntimeException(\"HTTP \"+res.statusCode());\n    } catch(Exception e){ last=e; } Thread.sleep((long)(500*Math.pow(2,i))); } throw last;\n  }\n}\n",
    }
    return {
        "source": "rule",
        "failure_description": f"Website resilience issues detected for {test.get('url')}: weakest factor {worst.replace('_',' ')}.",
        "root_cause": "; ".join(critical[:2]) if critical else f"Low score in {worst.replace('_',' ')} based on actual test evidence.",
        "affected_components": affected,
        "recommendation": recs[0] if recs else "Apply retries, timeouts, monitoring, and harden failing components.",
        "patch_language": lang,
        "patch_text": patches[lang],
        "expected_improvement": "Expected resilience improvement: +5 to +15 after addressing the highest-impact failed checks.",
    }


class RemediationService:
    def generate_for_run(self, db: Session, run_id: int, language: str) -> RemediationRecord:
        run = db.query(SimulationRun).filter(SimulationRun.id == run_id).first()
        if not run:
            raise ValueError("Simulation run not found")
        result = json.loads(run.result_json or "{}")
        data = rule_based_remediation(result, language)
        if settings.llm_provider and settings.llm_api_key:
            data["recommendation"] = "[LLM provider configured, adapter not enabled in this build] " + data["recommendation"]
        validation = validate_patch(data["patch_language"], data["patch_text"])
        rec = RemediationRecord(run_id=run_id, website_test_id=None, url=run.url or "", source=data["source"], failure_description=data["failure_description"], root_cause=data["root_cause"], affected_components_json=json.dumps(data["affected_components"]), recommendation=data["recommendation"], patch_language=data["patch_language"], patch_text=data["patch_text"], expected_improvement=data["expected_improvement"], validation_status=validation["status"], validation_json=json.dumps(validation), approved=False)
        db.add(rec); db.commit(); db.refresh(rec)
        return rec

    def generate_for_website_test(self, db: Session, website_test_id: int, language: str) -> RemediationRecord:
        run = db.query(WebsiteTestRun).filter(WebsiteTestRun.id == website_test_id).first()
        if not run:
            raise ValueError("Website test not found")
        result = json.loads(run.result_json or "{}")
        data = _from_website_test(result, language)
        if settings.llm_provider and settings.llm_api_key:
            data["source"] = "llm-configured-fallback"
            data["recommendation"] = "[LLM provider configured, adapter not enabled in this build] " + data["recommendation"]
        validation = validate_patch(data["patch_language"], data["patch_text"])
        rec = RemediationRecord(run_id=None, website_test_id=website_test_id, url=run.url, source=data["source"], failure_description=data["failure_description"], root_cause=data["root_cause"], affected_components_json=json.dumps(data["affected_components"]), recommendation=data["recommendation"], patch_language=data["patch_language"], patch_text=data["patch_text"], expected_improvement=data["expected_improvement"], validation_status=validation["status"], validation_json=json.dumps(validation), approved=False)
        db.add(rec); db.commit(); db.refresh(rec)
        return rec

    def validate(self, db: Session, rec: RemediationRecord) -> RemediationRecord:
        validation = validate_patch(rec.patch_language, rec.patch_text)
        rec.validation_status = validation["status"]
        rec.validation_json = json.dumps(validation)
        db.commit(); db.refresh(rec)
        return rec
