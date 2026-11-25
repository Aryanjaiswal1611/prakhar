from app.services.graph_engine import GraphEngine

def sample():
    nodes=[{"node_key":"a","name":"A","type":"frontend","metadata":{}},{"node_key":"b","name":"B","type":"backend","metadata":{}},{"node_key":"c","name":"C","type":"database","metadata":{"replicas":1}}]
    edges=[{"edge_key":"e1","source_key":"a","target_key":"b","dependency_type":"sync","critical":True},{"edge_key":"e2","source_key":"b","target_key":"c","dependency_type":"sync","critical":True}]
    return nodes,edges

def test_propagation_order():
    n,e=sample(); ge=GraphEngine(n,e)
    steps=ge.propagation_order("c")
    assert [s["to_node"] for s in steps]==["b","a"]

def test_spof_detection():
    nodes=[{"node_key":"db","name":"DB","type":"database","metadata":{"replicas":1}},{"node_key":"b1","name":"B1","type":"backend","metadata":{}},{"node_key":"b2","name":"B2","type":"backend","metadata":{}}]
    edges=[{"edge_key":"e1","source_key":"b1","target_key":"db","critical":True,"dependency_type":"sync"},{"edge_key":"e2","source_key":"b2","target_key":"db","critical":True,"dependency_type":"sync"}]
    spofs=GraphEngine(nodes,edges).single_points_of_failure()
    assert len(spofs)==1 and spofs[0]["node_key"]=="db"
