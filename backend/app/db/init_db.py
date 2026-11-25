from app.db.session import Base, engine, SessionLocal
from app import models  # noqa: F401 - ensure models registered
from app.models.infrastructure import Infrastructure, GraphNode, GraphEdge
import json, os, logging

logger = logging.getLogger("chaosbrain.db")
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "sample_infrastructure.json")


def init_db():
    Base.metadata.create_all(bind=engine)
    try:
        with engine.connect() as conn:
            # simulation_runs additive columns
            sr_cols = [r[1] for r in conn.exec_driver_sql("PRAGMA table_info(simulation_runs)").fetchall()]
            for stmt in [
                "ALTER TABLE simulation_runs ADD COLUMN url TEXT DEFAULT ''",
                "ALTER TABLE simulation_runs ADD COLUMN name TEXT DEFAULT ''",
                "ALTER TABLE simulation_runs ADD COLUMN error_message TEXT DEFAULT ''",
            ]:
                col = stmt.split("ADD COLUMN ")[1].split(" ")[0]
                if col not in sr_cols:
                    conn.exec_driver_sql(stmt)
            rr_cols = [r[1] for r in conn.exec_driver_sql("PRAGMA table_info(remediation_records)").fetchall()]
            for stmt in [
                "ALTER TABLE remediation_records ADD COLUMN website_test_id INTEGER",
                "ALTER TABLE remediation_records ADD COLUMN url TEXT DEFAULT ''",
            ]:
                col = stmt.split("ADD COLUMN ")[1].split(" ")[0]
                if col not in rr_cols:
                    conn.exec_driver_sql(stmt)
            conn.commit()
    except Exception as e:
        logger.warning("db additive migration skipped: %s", e)


def seed_if_empty():
    db: SessionLocal = SessionLocal()
    try:
        if db.query(Infrastructure).count() > 0:
            return
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            sample = json.load(f)
        infra = Infrastructure(name=sample["name"], description=sample.get("description", ""))
        db.add(infra)
        db.commit()
        db.refresh(infra)
        for n in sample["nodes"]:
            db.add(GraphNode(
                infrastructure_id=infra.id, node_key=n["node_key"], name=n["name"], type=n["type"],
                status=n.get("status", "healthy"), criticality=n.get("criticality", 1),
                x=n.get("x", 0), y=n.get("y", 0), metadata_json=json.dumps(n.get("metadata", {}))
            ))
        for e in sample["edges"]:
            db.add(GraphEdge(
                infrastructure_id=infra.id, edge_key=e["edge_key"], source_key=e["source_key"],
                target_key=e["target_key"], dependency_type=e.get("dependency_type", "sync"), critical=e.get("critical", True)
            ))
        db.commit()
    finally:
        db.close()
