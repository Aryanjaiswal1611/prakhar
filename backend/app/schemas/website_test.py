from pydantic import BaseModel, Field, HttpUrl
from typing import List, Dict, Any, Optional


class WebsiteTestRequest(BaseModel):
    url: str
    mode: str = "safe_external"  # safe_external | simulated
    include_api_endpoint: Optional[str] = None


class FactorScore(BaseModel):
    score: float
    weight: float
    weighted_score: float
    passed: int = 0
    failed: int = 0
    details: List[Dict[str, Any]] = Field(default_factory=list)
    summary: str = ""


class WebsiteTestResult(BaseModel):
    id: int
    url: str
    test_mode: str
    created_at: str
    overall_score: float
    classification: str
    factors: Dict[str, FactorScore]
    tests: List[Dict[str, Any]]
    critical_issues: List[str]
    warnings: List[str]
    recommendations: List[str]
    graph: Dict[str, Any]
    report_summary: str
    safety_note: str
