from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Boolean
from datetime import datetime
from app.db.session import Base


class SimulationRun(Base):
    __tablename__ = "simulation_runs"
    id = Column(Integer, primary_key=True, index=True)
    infrastructure_id = Column(Integer, ForeignKey("infrastructures.id"), index=True)
    experiment_type = Column(String, nullable=False)
    target_node_key = Column(String, nullable=False)
    severity = Column(Integer, default=3)
    status = Column(String, default="completed")
    resilience_score = Column(Float, default=0.0)
    classification = Column(String, default="Unknown")
    result_json = Column(Text, default="{}")
    url = Column(String, default="")
    name = Column(String, default="")
    error_message = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)


class RemediationRecord(Base):
    __tablename__ = "remediation_records"
    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("simulation_runs.id"), index=True, nullable=True)
    website_test_id = Column(Integer, index=True, nullable=True)
    url = Column(String, default="")
    source = Column(String, default="rule")  # rule|llm
    failure_description = Column(Text, default="")
    root_cause = Column(Text, default="")
    affected_components_json = Column(Text, default="[]")
    recommendation = Column(Text, default="")
    patch_language = Column(String, default="python")
    patch_text = Column(Text, default="")
    expected_improvement = Column(Text, default="")
    validation_status = Column(String, default="pending")
    validation_json = Column(Text, default="{}")
    approved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class CustomSimulation(Base):
    __tablename__ = "custom_simulations"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, default="")
    url = Column(String, default="")
    experiment_type = Column(String, nullable=False)
    target_node_key = Column(String, default="website")
    severity = Column(Integer, default=3)
    duration_sec = Column(Integer, default=30)
    target_endpoint = Column(String, default="")
    params_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=datetime.utcnow)


class InfrastructureSnapshot(Base):
    __tablename__ = "infrastructure_snapshots"
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False, index=True)
    source = Column(String, default="discovery")
    graph_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=datetime.utcnow)
