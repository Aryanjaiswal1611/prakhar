from typing import Dict, List, Any
from app.services.graph_engine import GraphEngine


def classify(score: float) -> str:
    if score >= 90: return "Excellent"
    if score >= 75: return "Good"
    if score >= 50: return "Moderate"
    if score >= 25: return "Weak"
    return "Critical"


class ResilienceAnalysisEngine:
    def analyze(self, nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]], simulation: Dict[str, Any]) -> Dict[str, Any]:
        ge = GraphEngine(nodes, edges)
        statuses = simulation["node_statuses"]
        impact = simulation["impact"]
        total = max(len(nodes), 1)
        failed = impact.get("failed_count", 0)
        warning = impact.get("warning_count", 0)
        healthy = impact.get("healthy_count", 0)

        health_score = (healthy / total) * 40
        failure_penalty = (failed / total) * 25 + (warning / total) * 10
        critical_failures = 0
        for n in nodes:
            if statuses.get(n["node_key"]) == "failed" and int(n.get("criticality",1)) >= 4:
                critical_failures += 1
        critical_penalty = min(15, critical_failures * 5)
        spofs = ge.single_points_of_failure()
        spof_penalty = min(10, len(spofs) * 3)
        # redundancy bonus: nodes with replicas>1
        redundant = sum(1 for n in nodes if int(n.get("metadata",{}).get("replicas",1)) > 1)
        redundancy_bonus = min(10, redundant * 3)
        recovery_bonus = max(0, 10 - min(10, impact.get("estimated_recovery_sec",0) / 60))
        propagation_penalty = min(10, (len(simulation.get("affected_nodes",[])) / total) * 10)

        raw = 50 + health_score + redundancy_bonus + recovery_bonus - failure_penalty - critical_penalty - spof_penalty - propagation_penalty
        score = round(max(0, min(100, raw)), 2)

        recommendations = []
        if any(n.get("type") == "database" and statuses.get(n["node_key"]) == "failed" for n in nodes):
            recommendations.append("Add database replication and automated failover.")
        if spofs:
            recommendations.append("Reduce single points of failure by adding redundancy for critical dependencies.")
        if impact.get("availability_pct", 100) < 80:
            recommendations.append("Introduce load balancing and health-based routing.")
        recommendations.append("Implement circuit breakers and retry mechanisms for critical service calls.")
        if not any(int(n.get("metadata",{}).get("replicas",1)) > 1 for n in nodes):
            recommendations.append("Increase service replicas for critical backend components.")
        recommendations.append("Improve observability with health checks, alerts, and SLO monitoring.")

        # unique preserve order
        seen=set(); recs=[]
        for r in recommendations:
            if r not in seen: seen.add(r); recs.append(r)

        return {
            "score": score,
            "classification": classify(score),
            "factors": {
                "health_score": round(health_score,2),
                "failure_penalty": round(failure_penalty,2),
                "critical_penalty": round(critical_penalty,2),
                "spof_penalty": round(spof_penalty,2),
                "redundancy_bonus": round(redundancy_bonus,2),
                "recovery_bonus": round(recovery_bonus,2),
                "propagation_penalty": round(propagation_penalty,2),
                "healthy_components": healthy,
                "failed_components": failed,
                "warning_components": warning,
                "total_components": total,
            },
            "single_points_of_failure": spofs,
            "recommendations": recs,
        }
