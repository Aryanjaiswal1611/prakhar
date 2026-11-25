import time, socket, ssl
from urllib.parse import urlparse
from typing import Dict, Any, List
import httpx

# Hard per-request limits; overall budget enforced by engine.
REQUEST_TIMEOUT = httpx.Timeout(connect=3.0, read=5.0, write=3.0, pool=3.0)
PROBE_TIMEOUT = httpx.Timeout(connect=2.0, read=3.0, write=2.0, pool=2.0)
TLS_TIMEOUT_SEC = 3.0
OVERALL_TEST_BUDGET_SEC = 20.0
MAX_RESPONSE_BYTES = 65536

WEIGHTS = {
    "server_availability": 0.20,
    "api_reliability": 0.20,
    "network_resilience": 0.15,
    "backend_reliability": 0.20,
    "performance_stability": 0.15,
    "security_configuration": 0.10,
}


def classify(score: float) -> str:
    if score >= 90: return "Excellent Resilience"
    if score >= 75: return "Good Resilience"
    if score >= 50: return "Moderate Resilience"
    if score >= 25: return "Weak Resilience"
    return "Critical Resilience"


def _remaining_budget(started: float) -> float:
    return OVERALL_TEST_BUDGET_SEC - (time.time() - started)


def _budget_exceeded(started: float) -> bool:
    return _remaining_budget(started) <= 0


def _safe_get(url: str, timeout: httpx.Timeout = REQUEST_TIMEOUT, started: float | None = None) -> Dict[str, Any]:
    t0 = time.time()
    if started is not None and _budget_exceeded(started):
        return {"ok": False, "status": None, "elapsed_ms": 0.0, "headers": {}, "error": "Overall test budget exceeded", "bytes_read": 0}
    try:
        with httpx.Client(follow_redirects=True, timeout=timeout, headers={"User-Agent": "ChaosBrainAI-ResilienceCheck/1.0"}) as c:
            with c.stream("GET", url) as r:
                bytes_read = 0
                for chunk in r.iter_bytes():
                    bytes_read += len(chunk)
                    if bytes_read >= MAX_RESPONSE_BYTES:
                        break
                    if started is not None and _budget_exceeded(started):
                        return {"ok": False, "status": r.status_code, "elapsed_ms": round((time.time()-t0)*1000,2), "headers": dict(r.headers), "error": "Overall test budget exceeded", "bytes_read": bytes_read}
                return {"ok": True, "status": r.status_code, "elapsed_ms": round((time.time()-t0)*1000,2), "headers": dict(r.headers), "error": None, "bytes_read": bytes_read}
    except httpx.TimeoutException:
        return {"ok": False, "status": None, "elapsed_ms": round((time.time()-t0)*1000,2), "headers": {}, "error": "Request timed out", "bytes_read": 0}
    except httpx.RequestError as e:
        return {"ok": False, "status": None, "elapsed_ms": round((time.time()-t0)*1000,2), "headers": {}, "error": str(e), "bytes_read": 0}
    except Exception as e:
        return {"ok": False, "status": None, "elapsed_ms": round((time.time()-t0)*1000,2), "headers": {}, "error": str(e), "bytes_read": 0}


def _check_https(url: str, started: float) -> Dict[str, Any]:
    p = urlparse(url)
    https = p.scheme == "https"
    cert_ok = None
    cert_err = None
    if https:
        if _budget_exceeded(started):
            return {"https": True, "cert_ok": False, "cert_err": "Overall test budget exceeded"}
        try:
            ctx = ssl.create_default_context()
            with socket.create_connection((p.hostname, p.port or 443), timeout=min(TLS_TIMEOUT_SEC, max(0.5, _remaining_budget(started)))) as sock:
                with ctx.wrap_socket(sock, server_hostname=p.hostname) as ssock:
                    cert_ok = True
                    ssock.getpeercert()
        except socket.timeout:
            cert_ok = False
            cert_err = "TLS connection timed out"
        except Exception as e:
            cert_ok = False
            cert_err = str(e)
    return {"https": https, "cert_ok": cert_ok, "cert_err": cert_err}


class WebsiteResilienceTester:
    def run(self, url: str, mode: str = "safe_external", include_api_endpoint: str | None = None) -> Dict[str, Any]:
        started = time.time()
        tests: List[Dict[str, Any]] = []
        critical_issues = []
        warnings = []
        recommendations = []
        timed_out = False

        base = _safe_get(url, timeout=REQUEST_TIMEOUT, started=started)
        if base.get("error") == "Overall test budget exceeded":
            timed_out = True
        base_pass = base["ok"] and 200 <= (base["status"] or 0) < 500
        tests.append({"name": "Base URL availability", "category": "server_availability", "passed": base_pass, "detail": f"status={base['status']} elapsed_ms={base['elapsed_ms']} bytes_read={base.get('bytes_read',0)}", "error": base["error"]})

        server_score, sp, sf = 0, 0, 0
        if base["ok"]:
            server_score += 60; sp += 1
            if 200 <= (base["status"] or 0) < 400:
                server_score += 30; sp += 1
            else:
                sf += 1; warnings.append(f"Base URL returned HTTP {base['status']}.")
            if base["elapsed_ms"] < 1500:
                server_score += 10; sp += 1
            else:
                sf += 1; warnings.append("Server response time is high (>1.5s).")
        else:
            sf += 3
            critical_issues.append("Target URL unavailable or timed out.")
        server_score = min(100, server_score)

        api_targets = [url.rstrip("/") + "/api/health", url.rstrip("/") + "/api"]
        if include_api_endpoint:
            api_targets.insert(0, include_api_endpoint)
        # de-dup preserve order
        seen = set(); deduped = []
        for t in api_targets:
            if t not in seen:
                seen.add(t); deduped.append(t)
        api_targets = deduped[:3]

        api_pass = 0; api_fail = 0; api_details = []
        for t in api_targets:
            if _budget_exceeded(started):
                timed_out = True
                tests.append({"name": f"API probe {t}", "category": "api_reliability", "passed": False, "detail": "Skipped due to overall test budget", "error": "Overall test budget exceeded"})
                api_fail += 1
                api_details.append({"url": t, "status": None, "ok": False})
                continue
            r = _safe_get(t, timeout=PROBE_TIMEOUT, started=started)
            if r.get("error") == "Overall test budget exceeded":
                timed_out = True
            ok = r["ok"] and r["status"] is not None and r["status"] < 500
            tests.append({"name": f"API probe {t}", "category": "api_reliability", "passed": ok, "detail": f"status={r['status']} elapsed_ms={r['elapsed_ms']}", "error": r["error"]})
            if ok: api_pass += 1
            else: api_fail += 1
            api_details.append({"url": t, "status": r["status"], "ok": ok})
        api_score = 100 if api_pass == len(api_targets) and api_targets else 0
        if api_targets and api_pass != len(api_targets):
            api_score = max(20, round(api_pass / max(1, len(api_targets)) * 100))
        if api_fail: warnings.append("Some API probes failed, timed out, or returned server errors.")

        net_pass = 0; net_fail = 0
        lat = base["elapsed_ms"] if base["ok"] else 8000
        net_score = 100
        tests.append({"name": "Latency under normal conditions", "category": "network_resilience", "passed": lat < 2000, "detail": f"elapsed_ms={lat}", "error": None if lat < 2000 else "High latency"})
        if lat < 2000: net_pass += 1
        else: net_fail += 1; net_score -= 35
        tests.append({"name": "Simulated high-latency tolerance", "category": "network_resilience", "passed": lat < 3000, "detail": "Simulated: assumes timeout budget 3s", "error": None if lat < 3000 else "May fail under 3s timeout", "simulated": True})
        if lat < 3000: net_pass += 1
        else: net_fail += 1; net_score -= 25; warnings.append("Site may degrade under high latency.")
        tests.append({"name": "Simulated packet-loss resilience", "category": "network_resilience", "passed": base["ok"], "detail": "Simulated: retry/caching inferred from availability only", "error": None if base["ok"] else "Unavailable", "simulated": True})
        if base["ok"]: net_pass += 1
        else: net_fail += 1; net_score -= 30; critical_issues.append("Network interruption likely causes full outage.")
        net_score = max(0, min(100, net_score))

        back_pass = 0; back_fail = 0
        back_score = 100
        status = base["status"]
        if not base["ok"]:
            back_score = 10; back_fail += 2; critical_issues.append("Backend/service unreachable.")
            tests.append({"name": "Backend availability", "category": "backend_reliability", "passed": False, "detail": "No response", "error": base["error"]})
            tests.append({"name": "Backend error rate", "category": "backend_reliability", "passed": False, "detail": "Unavailable", "error": base["error"]})
        else:
            tests.append({"name": "Backend availability", "category": "backend_reliability", "passed": status < 500, "detail": f"status={status}", "error": None if status < 500 else "5xx"})
            if status < 500: back_pass += 1
            else: back_fail += 1; back_score -= 60; critical_issues.append(f"Backend returned server error {status}.")
            tests.append({"name": "Backend error rate", "category": "backend_reliability", "passed": status < 400, "detail": f"status={status}", "error": None if status < 400 else "4xx/5xx"})
            if status < 400: back_pass += 1
            else: back_fail += 1; back_score -= 20; warnings.append(f"Non-success status {status} observed.")
        back_score = max(0, min(100, back_score))

        perf_pass = 0; perf_fail = 0
        perf_score = 100
        ttfb = base["elapsed_ms"]
        tests.append({"name": "Response time", "category": "performance_stability", "passed": ttfb < 2000, "detail": f"{ttfb} ms", "error": None if ttfb < 2000 else "Slow"})
        if ttfb < 2000: perf_pass += 1
        else: perf_fail += 1; perf_score -= 35
        tests.append({"name": "Time-to-first-byte proxy", "category": "performance_stability", "passed": ttfb < 1200, "detail": f"{ttfb} ms (approx)", "error": None if ttfb < 1200 else "High TTFB"})
        if ttfb < 1200: perf_pass += 1
        else: perf_fail += 1; perf_score -= 25
        success_rate = 100 if base["ok"] and status and status < 400 else 0
        tests.append({"name": "Request success rate", "category": "performance_stability", "passed": success_rate == 100, "detail": f"{success_rate}% (single safe probe)", "error": None if success_rate == 100 else "Request failed"})
        if success_rate == 100: perf_pass += 1
        else: perf_fail += 1; perf_score -= 40
        perf_score = max(0, min(100, perf_score))

        sec = _check_https(url, started)
        if sec.get("cert_err") == "Overall test budget exceeded":
            timed_out = True
        sec_pass = 0; sec_fail = 0; sec_score = 0
        tests.append({"name": "HTTPS enabled", "category": "security_configuration", "passed": sec["https"], "detail": str(sec["https"]), "error": None if sec["https"] else "Not HTTPS"})
        if sec["https"]: sec_pass += 1; sec_score += 40
        else: sec_fail += 1; critical_issues.append("HTTPS not enabled.")
        if sec["https"]:
            tests.append({"name": "Certificate validity", "category": "security_configuration", "passed": bool(sec["cert_ok"]), "detail": "valid" if sec["cert_ok"] else str(sec["cert_err"]), "error": sec["cert_err"]})
            if sec["cert_ok"]: sec_pass += 1; sec_score += 30
            else: sec_fail += 1; warnings.append("Certificate validation issue.")
        else:
            tests.append({"name": "Certificate validity", "category": "security_configuration", "passed": False, "detail": "No HTTPS cert", "error": "HTTPS disabled"}); sec_fail += 1
        headers = {k.lower(): v for k, v in base.get("headers", {}).items()}
        needed = ["strict-transport-security", "content-security-policy", "x-frame-options", "x-content-type-options"]
        present = [h for h in needed if h in headers]
        tests.append({"name": "Security headers", "category": "security_configuration", "passed": len(present) >= 2, "detail": f"present={present}", "error": None if len(present) >= 2 else "Missing recommended headers"})
        if len(present) >= 2: sec_pass += 1; sec_score += 30 * (len(present) / len(needed))
        else: sec_fail += 1; warnings.append("Missing recommended security headers.")
        sec_score = max(0, min(100, round(sec_score)))

        factors = {}
        def pack(name, score, p, f, summary, details=None):
            factors[name] = {"score": round(score, 2), "weight": WEIGHTS[name], "weighted_score": round(score * WEIGHTS[name], 2), "passed": p, "failed": f, "summary": summary, "details": details or []}
        pack("server_availability", server_score, sp, sf, "Availability and response status from safe probe.")
        pack("api_reliability", api_score, api_pass, api_fail, "Safe low-volume API endpoint probes.", api_details)
        pack("network_resilience", net_score, net_pass, net_fail, "Observed latency plus clearly labeled simulated stress checks.")
        pack("backend_reliability", back_score, back_pass, back_fail, "Inferred from response status/errors.")
        pack("performance_stability", perf_score, perf_pass, perf_fail, "Response timing and single-probe success rate.")
        pack("security_configuration", sec_score, sec_pass, sec_fail, "HTTPS, certificate, and basic headers.")

        overall = round(sum(f["weighted_score"] for f in factors.values()), 2)
        if timed_out:
            warnings.append("Overall test budget exceeded; some checks were skipped or partial.")
            recommendations.append("Target was slow or unresponsive. Retry later or test a faster/health endpoint with permission.")
        if overall < 50: recommendations.append("Prioritize restoring availability and fixing 5xx/timeout errors.")
        if factors["api_reliability"]["score"] < 75: recommendations.append("Add API timeout handling, retries with backoff, and circuit breakers.")
        if factors["network_resilience"]["score"] < 75: recommendations.append("Use CDN/caching and graceful degradation for high-latency/packet-loss conditions.")
        if factors["backend_reliability"]["score"] < 75: recommendations.append("Add health checks, redundancy, and dependency isolation for backend services.")
        if factors["performance_stability"]["score"] < 75: recommendations.append("Optimize response time, enable caching, and monitor TTFB/SLOs.")
        if factors["security_configuration"]["score"] < 75: recommendations.append("Enable HTTPS, valid certificates, and recommended security headers.")
        if not recommendations: recommendations.append("Maintain monitoring, alerting, and periodic resilience testing.")
        recommendations = list(dict.fromkeys(recommendations))

        graph = self._build_graph(url, factors)
        duration_ms = int((time.time() - started) * 1000)
        return {
            "url": url, "test_mode": mode, "overall_score": overall, "classification": classify(overall),
            "factors": factors, "tests": tests, "critical_issues": list(dict.fromkeys(critical_issues)),
            "warnings": list(dict.fromkeys(warnings)), "recommendations": recommendations, "graph": graph,
            "report_summary": f"Tested {url} in {mode} mode with {len(tests)} checks in {duration_ms}ms. Overall resilience: {overall}/100 ({classify(overall)}).",
            "safety_note": "Safe, low-volume checks only. No DoS, no destructive attacks, no target modification. Network/backend failures beyond probes are simulated/labeled.",
            "timed_out": timed_out, "duration_ms": duration_ms,
        }

    def _build_graph(self, url: str, factors: Dict[str, Any]) -> Dict[str, Any]:
        def st(score):
            return "healthy" if score >= 75 else "warning" if score >= 50 else "failed"
        nodes = [
            {"node_key": "frontend", "name": "Frontend", "type": "frontend", "status": "healthy" if factors["performance_stability"]["score"] >= 50 else "warning"},
            {"node_key": "gateway", "name": "API Gateway", "type": "gateway", "status": st(factors["api_reliability"]["score"])},
            {"node_key": "backend", "name": "Backend Service", "type": "backend", "status": st(factors["backend_reliability"]["score"])},
            {"node_key": "server", "name": "Server/Hosting", "type": "backend", "status": st(factors["server_availability"]["score"])},
            {"node_key": "network", "name": "Network", "type": "external", "status": st(factors["network_resilience"]["score"])},
            {"node_key": "security", "name": "Security Config", "type": "auth", "status": st(factors["security_configuration"]["score"])},
        ]
        edges = [
            {"edge_key": "g1", "source_key": "frontend", "target_key": "gateway"},
            {"edge_key": "g2", "source_key": "gateway", "target_key": "backend"},
            {"edge_key": "g3", "source_key": "backend", "target_key": "server"},
            {"edge_key": "g4", "source_key": "frontend", "target_key": "network"},
            {"edge_key": "g5", "source_key": "gateway", "target_key": "security"},
        ]
        return {"label": "Inferred/Simulated Architecture", "url": url, "nodes": nodes, "edges": edges}
