import json, socket, ssl, time
from urllib.parse import urlparse
from typing import Dict, Any, List
import httpx
from app.services.website_test_engine import _safe_get, PROBE_TIMEOUT, OVERALL_TEST_BUDGET_SEC


def _status_from_score(score: float) -> str:
    if score >= 75: return "healthy"
    if score >= 50: return "warning"
    return "failed"


def discover_infrastructure(url: str) -> Dict[str, Any]:
    started = time.time()
    parsed = urlparse(url)
    host = parsed.hostname or parsed.netloc
    nodes: List[Dict[str, Any]] = []
    edges: List[Dict[str, Any]] = []
    evidence: List[Dict[str, Any]] = []

    def add_node(node_key, name, type_, status, criticality=2, meta=None, confidence="verified"):
        nodes.append({"node_key": node_key, "name": name, "type": type_, "status": status, "criticality": criticality, "x": 0, "y": 0, "metadata": {**(meta or {}), "confidence": confidence}})
    def add_edge(edge_key, source, target, dependency_type="sync", critical=True):
        edges.append({"edge_key": edge_key, "source_key": source, "target_key": target, "dependency_type": dependency_type, "critical": critical})

    base = _safe_get(url, timeout=PROBE_TIMEOUT, started=started)
    evidence.append({"check": "base_url", **base})
    web_status = "healthy" if base.get("ok") and (base.get("status") or 500) < 400 else "warning" if base.get("ok") else "failed"
    add_node("website", f"Website ({host})", "frontend", web_status, 4, {"url": url, "status_code": base.get("status"), "elapsed_ms": base.get("elapsed_ms")}, "verified")
    add_node("dns", f"DNS: {host}", "external", "unknown", 3, {"hostname": host}, "inferred")
    add_edge("e_dns_web", "website", "dns", "dns", True)

    ip = None
    try:
        ip = socket.gethostbyname(host)
        add_node("ip", f"IP: {ip}", "server", "healthy", 3, {"ip": ip}, "verified")
        add_edge("e_web_ip", "website", "ip", "network", True)
        nodes[1]["status"] = "healthy"
        nodes[1]["metadata"]["resolved_ip"] = ip
        evidence.append({"check": "dns_resolve", "ok": True, "ip": ip})
    except Exception as e:
        nodes[1]["status"] = "failed"
        nodes[1]["metadata"]["error"] = str(e)
        evidence.append({"check": "dns_resolve", "ok": False, "error": str(e)})

    headers = {k.lower(): v for k, v in (base.get("headers") or {}).items()}
    server_hdr = headers.get("server")
    powered = headers.get("x-powered-by")
    if server_hdr or powered:
        add_node("server", "Web Server/Platform", "backend", web_status, 4, {"server": server_hdr, "x_powered_by": powered}, "verified")
        add_edge("e_ip_server", "ip" if ip else "website", "server", "runtime", True)
        add_edge("e_server_web", "website", "server", "http", True)
    else:
        add_node("server", "Origin Server (inferred)", "backend", "unknown" if not base.get("ok") else "warning", 3, {}, "inferred")
        add_edge("e_web_server", "website", "server", "http", True)

    if parsed.scheme == "https":
        cert_ok = False
        cert_err = None
        try:
            ctx = ssl.create_default_context()
            with socket.create_connection((host, parsed.port or 443), timeout=3) as sock:
                with ctx.wrap_socket(sock, server_hostname=host) as ssock:
                    ssock.getpeercert()
                    cert_ok = True
        except Exception as e:
            cert_err = str(e)
        add_node("tls", "TLS/Certificate", "auth", "healthy" if cert_ok else "failed", 4, {"cert_ok": cert_ok, "error": cert_err}, "verified")
        add_edge("e_web_tls", "website", "tls", "tls", True)
        evidence.append({"check": "tls", "ok": cert_ok, "error": cert_err})

    # Safe API endpoint discovery
    for path, key, name in [("/api/health", "api_health", "API Health Endpoint"), ("/api", "api_root", "API Root"), ("/health", "health", "Health Endpoint")]:
        if time.time() - started > 12: break
        probe_url = url.rstrip("/") + path
        r = _safe_get(probe_url, timeout=PROBE_TIMEOUT, started=started)
        evidence.append({"check": "endpoint_probe", "url": probe_url, **r})
        if r.get("status") is not None:
            st = "healthy" if r.get("ok") and r["status"] < 400 else "warning" if r["status"] < 500 else "failed"
            add_node(key, name, "api", st, 3, {"url": probe_url, "status_code": r.get("status")}, "verified")
            add_edge(f"e_web_{key}", "website", key, "http", False)

    # layout
    for i, n in enumerate(nodes):
        n["x"] = 120 + (i % 4) * 260
        n["y"] = 80 + (i // 4) * 160

    return {
        "url": url,
        "host": host,
        "discovered_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "nodes": nodes,
        "edges": edges,
        "evidence": evidence,
        "partial": any(e.get("error") for e in evidence),
        "summary": f"Discovered {len(nodes)} components and {len(edges)} dependencies for {host}.",
    }
