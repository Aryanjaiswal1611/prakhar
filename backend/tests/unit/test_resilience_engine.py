from app.services.chaos_engine import ChaosSimulationEngine
from app.services.resilience_engine import ResilienceAnalysisEngine

NODES=[
 {"node_key":"frontend","name":"Frontend","type":"frontend","criticality":2,"metadata":{}},
 {"node_key":"backend","name":"Backend","type":"backend","criticality":4,"metadata":{}},
 {"node_key":"database","name":"DB","type":"database","criticality":5,"metadata":{"replicas":1}},
]
EDGES=[
 {"edge_key":"e1","source_key":"frontend","target_key":"backend","dependency_type":"sync","critical":True},
 {"edge_key":"e2","source_key":"backend","target_key":"database","dependency_type":"sync","critical":True},
]

def test_resilience_score_range_and_classification():
    sim=ChaosSimulationEngine().simulate(NODES,EDGES,{"experiment_type":"database_failure","target_node_key":"database","severity":5})
    analysis=ResilienceAnalysisEngine().analyze(NODES,EDGES,sim)
    assert 0 <= analysis["score"] <= 100
    assert analysis["classification"] in {"Excellent","Good","Moderate","Weak","Critical"}
    assert analysis["recommendations"]
