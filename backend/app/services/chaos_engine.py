from typing import Dict, List, Any
from app.services.graph_engine import GraphEngine

FAILURE_BASE = {
    "server_failure": {"target": "failed", "dependent": "failed", "recovery": 120},
    "database_failure": {"target": "failed", "dependent": "warning", "recovery": 180},
    "network_latency": {"target": "warning", "dependent": "warning", "recovery": 60},
    "packet_loss": {"target": "warning", "dependent": "warning", "recovery": 75},
    "cpu_overload": {"target": "warning", "dependent": "warning", "recovery": 90},
    "memory_exhaustion": {"target": "failed", "dependent": "warning", "recovery": 150},
    "api_timeout": {"target": "warning", "dependent": "warning", "recovery": 70},
    "service_dependency_failure": {"target": "failed", "dependent": "warning", "recovery": 100},
}


def _status_after(base: str, severity: int, critical_edge: bool) -> str:
    if base == "failed":
        return "failed" if severity >= 3 or critical_edge else "warning"
    # warning base
    if severity >= 4 and critical_edge:
        return "failed"
    if severity >= 2:
        return "warning"
    return "healthy"


class ChaosSimulationEngine:
    def simulate(self, nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]], experiment: Dict[str, Any]) -> Dict[str, Any]:
        ge = GraphEngine(nodes, edges)
        target = experiment["target_node_key"]
        ftype = experiment["experiment_type"]
        severity = int(experiment.get("severity", 3))
        cfg = FAILURE_BASE.get(ftype, {"target": "failed", "dependent": "warning", "recovery": 90})

        statuses = {n["node_key"]: "healthy" for n in nodes}
        events = []
        if target not in statuses:
            raise ValueError(f"Target node '{target}' not found")

        statuses[target] = _status_after(cfg["target"], severity, True)
        events.append({"type": "initial_failure", "node": target, "failure_type": ftype, "severity": severity, "status": statuses[target]})

        propagation = ge.propagation_order(target)
        affected = []
        for step in propagation:
            dep = step["to_node"]
            critical_edge = step.get("edge_critical", True)
            # async non-critical edges dampen impact
            dep_status = _status_after(cfg["dependent"], severity, critical_edge)
            if not critical_edge and dep_status == "failed":
                dep_status = "warning"
            # don't downgrade a worse status
            rank = {"healthy":0,"recovering":1,"warning":2,"failed":3}
            if rank[dep_status] > rank[statuses[dep]]:
                statuses[dep] = dep_status
            if statuses[dep] in ("warning","failed"):
                affected.append(dep)
            events.append({"type":"propagation","order":step["order"],"from":step["from_node"],"to":dep,"status":statuses[dep],"reason":step["reason"]})

        affected = list(dict.fromkeys(affected))
        total = max(len(nodes), 1)
        failed = sum(1 for s in statuses.values() if s == "failed")
        warning = sum(1 for s in statuses.values() if s == "warning")
        healthy = sum(1 for s in statuses.values() if s == "healthy")
        availability = max(0.0, round((healthy * 1.0 + warning * 0.45) / total * 100, 2))
        recovery = int(cfg["recovery"] * (1 + (severity - 3) * 0.25) + len(affected) * 15)

        return {
            "initial_failure": target,
            "node_statuses": statuses,
            "affected_nodes": affected,
            "propagation_path": [{k:v for k,v in s.items() if k!="edge_critical" and k!="depth"} for s in propagation],
            "impact": {
                "availability_pct": availability,
                "affected_count": len(affected) + (1 if statuses[target] in ("warning","failed") else 0),
                "estimated_recovery_sec": max(recovery, 30),
                "total_nodes": total,
                "failed_count": failed,
                "warning_count": warning,
                "healthy_count": healthy,
            },
            "events": events,
        }
