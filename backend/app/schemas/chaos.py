from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class ChaosExperiment(BaseModel):
    experiment_type: str
    target_node_key: str
    severity: int = Field(default=3, ge=1, le=5)
    params: Dict[str, Any] = Field(default_factory=dict)


class SimulationRequest(BaseModel):
    infrastructure_id: Optional[int] = None
    url: Optional[str] = None
    experiment: ChaosExperiment
    custom: bool = False
    name: Optional[str] = None
    description: Optional[str] = None


class CustomSimulationCreate(BaseModel):
    name: str
    description: str = ""
    url: Optional[str] = None
    experiment_type: str
    target_node_key: str = "website"
    severity: int = Field(default=3, ge=1, le=5)
    duration_sec: int = Field(default=30, ge=1, le=300)
    target_endpoint: Optional[str] = None
    params: Dict[str, Any] = Field(default_factory=dict)


class PropagationStep(BaseModel):
    order: int
    from_node: str
    to_node: str
    reason: str
    resulting_status: str


class SimulationImpact(BaseModel):
    availability_pct: float
    affected_count: int
    estimated_recovery_sec: int
    total_nodes: int
    failed_count: int = 0
    warning_count: int = 0
    healthy_count: int = 0


class SimulationResult(BaseModel):
    run_id: int
    infrastructure_id: int
    experiment: ChaosExperiment
    initial_failure: str
    node_statuses: Dict[str, str]
    affected_nodes: List[str]
    propagation_path: List[PropagationStep]
    impact: SimulationImpact
    resilience: Dict[str, Any]
    recommendations: List[str]
    events: List[Dict[str, Any]]
    status: str = "completed"
    error: Optional[str] = None
    error_type: Optional[str] = None
    url: Optional[str] = None
    baseline: Optional[Dict[str, Any]] = None
    verification: Optional[Dict[str, Any]] = None
    comparison: Optional[Dict[str, Any]] = None
    report: Optional[Dict[str, Any]] = None
