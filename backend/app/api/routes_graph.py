import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.infrastructure import Infrastructure, GraphNode, GraphEdge
from app.schemas.graph import InfrastructureCreate, InfrastructureUpdate, InfrastructureOut, NodeBase, EdgeBase, GraphImport

router = APIRouter(prefix="/api/graphs", tags=["graphs"])


def _to_out(infra: Infrastructure) -> InfrastructureOut:
    return InfrastructureOut(
        id=infra.id, name=infra.name, description=infra.description or "",
        nodes=[NodeBase(node_key=n.node_key,name=n.name,type=n.type,status=n.status,criticality=n.criticality,x=n.x,y=n.y,metadata=json.loads(n.metadata_json or "{}")) for n in infra.nodes],
        edges=[EdgeBase(edge_key=e.edge_key,source_key=e.source_key,target_key=e.target_key,dependency_type=e.dependency_type,critical=bool(e.critical)) for e in infra.edges],
    )


def _replace_graph(db: Session, infra: Infrastructure, payload):
    db.query(GraphNode).filter(GraphNode.infrastructure_id==infra.id).delete()
    db.query(GraphEdge).filter(GraphEdge.infrastructure_id==infra.id).delete()
    for n in payload.nodes:
        db.add(GraphNode(infrastructure_id=infra.id,node_key=n.node_key,name=n.name,type=n.type,status=n.status,criticality=n.criticality,x=n.x,y=n.y,metadata_json=json.dumps(n.metadata)))
    for e in payload.edges:
        db.add(GraphEdge(infrastructure_id=infra.id,edge_key=e.edge_key,source_key=e.source_key,target_key=e.target_key,dependency_type=e.dependency_type,critical=e.critical))
    db.commit(); db.refresh(infra)
    return infra


@router.get("", response_model=list[InfrastructureOut])
def list_graphs(db: Session = Depends(get_db)):
    return [_to_out(i) for i in db.query(Infrastructure).order_by(Infrastructure.id.desc()).all()]


@router.post("", response_model=InfrastructureOut)
def create_graph(payload: InfrastructureCreate, db: Session = Depends(get_db)):
    infra = Infrastructure(name=payload.name, description=payload.description)
    db.add(infra); db.commit(); db.refresh(infra)
    _replace_graph(db, infra, payload)
    return _to_out(infra)


@router.get("/{graph_id}", response_model=InfrastructureOut)
def get_graph(graph_id: int, db: Session = Depends(get_db)):
    infra = db.query(Infrastructure).filter(Infrastructure.id==graph_id).first()
    if not infra: raise HTTPException(404, "Graph not found")
    return _to_out(infra)


@router.put("/{graph_id}", response_model=InfrastructureOut)
def update_graph(graph_id: int, payload: InfrastructureUpdate, db: Session = Depends(get_db)):
    infra = db.query(Infrastructure).filter(Infrastructure.id==graph_id).first()
    if not infra: raise HTTPException(404, "Graph not found")
    infra.name = payload.name; infra.description = payload.description
    db.commit()
    _replace_graph(db, infra, payload)
    return _to_out(infra)


@router.delete("/{graph_id}")
def delete_graph(graph_id: int, db: Session = Depends(get_db)):
    infra = db.query(Infrastructure).filter(Infrastructure.id==graph_id).first()
    if not infra: raise HTTPException(404, "Graph not found")
    db.delete(infra); db.commit()
    return {"ok": True}


@router.get("/{graph_id}/export")
def export_graph(graph_id: int, db: Session = Depends(get_db)):
    infra = db.query(Infrastructure).filter(Infrastructure.id==graph_id).first()
    if not infra: raise HTTPException(404, "Graph not found")
    return _to_out(infra).model_dump()


@router.post("/import", response_model=InfrastructureOut)
def import_graph(payload: GraphImport, db: Session = Depends(get_db)):
    return create_graph(InfrastructureCreate(**payload.model_dump()), db)
