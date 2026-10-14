from datetime import datetime

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    conversation_id: str | None = None


class Citation(BaseModel):
    source: str
    excerpt: str


class ChatResponse(BaseModel):
    conversation_id: str
    answer: str
    intent: str
    confidence: float
    escalated: bool
    citations: list[Citation] = Field(default_factory=list)


class EscalationView(BaseModel):
    id: str
    conversation_id: str
    status: str
    reason: str
    evidence: dict
    created_at: datetime
