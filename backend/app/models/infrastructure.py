from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.session import Base


class Infrastructure(Base):
    __tablename__ = "infrastructures"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    nodes = relationship("GraphNode", back_populates="infrastructure", cascade="all, delete-orphan")
    edges = relationship("GraphEdge", back_populates="infrastructure", cascade="all, delete-orphan")


class GraphNode(Base):
    __tablename__ = "graph_nodes"
    id = Column(Integer, primary_key=True, index=True)
    infrastructure_id = Column(Integer, ForeignKey("infrastructures.id"), index=True)
    node_key = Column(String, index=True)  # stable client-facing id
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    status = Column(String, default="healthy")
    criticality = Column(Integer, default=1)
    x = Column(Float, default=0.0)
    y = Column(Float, default=0.0)
    metadata_json = Column(Text, default="{}")

    infrastructure = relationship("Infrastructure", back_populates="nodes")


class GraphEdge(Base):
    __tablename__ = "graph_edges"
    id = Column(Integer, primary_key=True, index=True)
    infrastructure_id = Column(Integer, ForeignKey("infrastructures.id"), index=True)
    edge_key = Column(String, index=True)
    source_key = Column(String, index=True)
    target_key = Column(String, index=True)
    dependency_type = Column(String, default="sync")
    critical = Column(Boolean, default=True)

    infrastructure = relationship("Infrastructure", back_populates="edges")
