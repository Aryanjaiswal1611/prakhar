import json, networkx as nx
from typing import Dict, List, Any

class GraphEngine:
    def __init__(self, nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]):
        self.nodes = {n["node_key"]: n for n in nodes}
        self.edges = edges
        self.g = nx.DiGraph()
        for k, n in self.nodes.items():
            self.g.add_node(k, **n)
        for e in edges:
            if e["source_key"] in self.nodes and e["target_key"] in self.nodes:
                self.g.add_edge(e["source_key"], e["target_key"], **e)

    def dependents(self, node_key: str) -> List[str]:
        # edges are source depends on target? In our model: frontend->gateway means frontend depends on gateway.
        # Failure propagates to components that depend on failed component: predecessors in dependency graph.
        return list(self.g.predecessors(node_key))

    def dependencies(self, node_key: str) -> List[str]:
        return list(self.g.successors(node_key))

    def propagation_order(self, start: str) -> List[Dict[str, Any]]:
        # BFS over reverse dependency direction (who depends on me)
        visited = {start}
        queue = [(start, 0)]
        steps = []
        order = 1
        while queue:
            current, depth = queue.pop(0)
            for dep in self.dependents(current):
                if dep in visited:
                    continue
                visited.add(dep)
                edge = self.g.get_edge_data(dep, current) or {}
                steps.append({
                    "order": order,
                    "from_node": current,
                    "to_node": dep,
                    "reason": f"{dep} depends on {current} ({edge.get('dependency_type','sync')})",
                    "edge_critical": bool(edge.get("critical", True)),
                    "depth": depth + 1,
                })
                order += 1
                queue.append((dep, depth + 1))
        return steps

    def single_points_of_failure(self) -> List[Dict[str, Any]]:
        spofs = []
        for k, n in self.nodes.items():
            deps = self.dependents(k)
            critical_dependents = [d for d in deps if (self.g.get_edge_data(d, k) or {}).get("critical", True)]
            if len(critical_dependents) >= 2 and n.get("metadata", {}).get("replicas", 1) <= 1:
                spofs.append({
                    "node_key": k,
                    "name": n.get("name", k),
                    "reason": f"{len(critical_dependents)} critical dependents and no redundancy",
                    "affected_dependents": critical_dependents,
                })
        return spofs

    def health_summary(self, statuses: Dict[str, str]) -> Dict[str, int]:
        summary = {"healthy":0,"warning":0,"failed":0,"recovering":0}
        for k in self.nodes:
            s = statuses.get(k, self.nodes[k].get("status","healthy"))
            summary[s] = summary.get(s,0)+1
        return summary
