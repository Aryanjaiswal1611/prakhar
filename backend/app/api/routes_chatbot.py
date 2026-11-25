from fastapi import APIRouter
from app.schemas.website_test import WebsiteTestRequest  # not needed
from pydantic import BaseModel
from typing import Optional, Dict, Any
from app.services.chatbot_service import rule_based
from app.core.config import settings

router = APIRouter(prefix="/api/chatbot", tags=["chatbot"])


class ChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None


@router.post("/ask")
def ask(req: ChatRequest):
    # LLM hook: if configured, a real provider adapter can be added here.
    # For MVP/safety, we return explicit rule-based fallback unless adapter implemented.
    answer = rule_based(req.message, req.context)
    source = "rule-based-fallback"
    if settings.llm_provider and settings.llm_api_key:
        answer = "[LLM provider configured, adapter not enabled in this MVP build] " + answer
    return {"answer": answer, "source": source}
