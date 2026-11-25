from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional


class NodeBase(BaseModel):
    node_key: str
    name: str
    type: str
    status: str = "healthy"
    criticality: int = 1
    x: float = 0
    y: float = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)


class EdgeBase(BaseModel):
    edge_key: str
    source_key: str
    target_key: str
    dependency_type: str = "sync"
    critical: bool = True


class InfrastructureCreate(BaseModel):
    name: str
    description: str = ""
    nodes: List[NodeBase] = Field(default_factory=list)
    edges: List[EdgeBase] = Field(default_factory=list)


class InfrastructureUpdate(InfrastructureCreate):
    pass


class InfrastructureOut(BaseModel):
    id: int
    name: str
    description: str
    nodes: List[NodeBase]
    edges: List[EdgeBase]

    class Config:
        from_attributes = True


class GraphImport(BaseModel):
    name: str
    description: str = ""
    nodes: List[NodeBase]
    edges: List[EdgeBase]
