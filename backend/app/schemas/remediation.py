from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class RemediationGenerateRequest(BaseModel):
    run_id: Optional[int] = None
    website_test_id: Optional[int] = None
    url: Optional[str] = None
    language: str = "python"  # python|javascript|java


class PatchValidation(BaseModel):
    status: str
    checks: List[Dict[str, Any]] = Field(default_factory=list)
    logs: List[str] = Field(default_factory=list)


class RemediationOut(BaseModel):
    id: int
    run_id: Optional[int] = None
    website_test_id: Optional[int] = None
    url: Optional[str] = None
    source: str
    failure_description: str
    root_cause: str
    affected_components: List[str]
    recommendation: str
    patch_language: str
    patch_text: str
    expected_improvement: str
    validation: PatchValidation
    approved: bool

    class Config:
        from_attributes = True
