from app.services.chaos_engine import ChaosSimulationEngine

NODES=[
 {"node_key":"frontend","name":"Frontend","type":"frontend","criticality":2,"metadata":{}},
 {"node_key":"backend","name":"Backend","type":"backend","criticality":4,"metadata":{}},
 {"node_key":"database","name":"DB","type":"database","criticality":5,"metadata":{}},
]
EDGES=[
 {"edge_key":"e1","source_key":"frontend","target_key":"backend","dependency_type":"sync","critical":True},
 {"edge_key":"e2","source_key":"backend","target_key":"database","dependency_type":"sync","critical":True},
]

def test_db_failure_propagates():
    sim=ChaosSimulationEngine().simulate(NODES,EDGES,{"experiment_type":"database_failure","target_node_key":"database","severity":4})
    assert sim["node_statuses"]["database"]=="failed"
    assert sim["node_statuses"]["backend"] in ("warning","failed")
    assert sim["node_statuses"]["frontend"] in ("warning","failed")
    assert sim["impact"]["affected_count"]>=2
