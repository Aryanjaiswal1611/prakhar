from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from datetime import datetime
from app.db.session import Base


class WebsiteTestRun(Base):
    __tablename__ = "website_test_runs"
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False)
    test_mode = Column(String, default="safe_external")  # safe_external | simulated
    status = Column(String, default="completed")
    overall_score = Column(Float, default=0.0)
    classification = Column(String, default="Unknown")
    result_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=datetime.utcnow)
