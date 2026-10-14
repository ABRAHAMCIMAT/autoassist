from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session

from .config import get_settings
from .database import Base, engine, get_db
from .models import Conversation, Escalation, Message
from .schemas import ChatRequest, ChatResponse, EscalationView
from .services.agent import AutoAssistAgent
from .services.llm import GroundedGenerator
from .services.rag import LocalKnowledgeBase


settings = get_settings()
app = FastAPI(title=settings.app_name, version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
agent = AutoAssistAgent(
    LocalKnowledgeBase(settings.knowledge_dir),
    settings.escalation_threshold,
    GroundedGenerator(
        api_key=settings.llm_api_key,
        model=settings.llm_model,
        base_url=settings.llm_base_url,
        temperature=settings.llm_temperature,
        max_tokens=settings.llm_max_tokens,
        app_url=settings.llm_app_url,
        app_name=settings.llm_app_name,
    ),
)


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(engine)


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": settings.app_name,
        "llm": {
            "configured": agent.generator.configured,
            "model": settings.llm_model,
        },
    }


@app.post("/api/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, db: Session = Depends(get_db)) -> ChatResponse:
    conversation = db.get(Conversation, payload.conversation_id) if payload.conversation_id else None
    if payload.conversation_id and not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if not conversation:
        conversation = Conversation()
        db.add(conversation)
        db.flush()

    db.add(Message(conversation_id=conversation.id, role="user", content=payload.message))
    result = agent.run(payload.message)
    citations = result.citations or []
    conversation.intent = result.intent
    conversation.confidence = result.confidence
    conversation.status = "escalated" if result.escalated else "open"
    db.add(Message(conversation_id=conversation.id, role="assistant", content=result.answer, citations=citations))

    if result.escalated:
        db.flush()
        history = db.scalars(
            select(Message).where(Message.conversation_id == conversation.id).order_by(Message.created_at)
        ).all()
        evidence = {
            "intent": result.intent,
            "confidence": result.confidence,
            "summary": result.answer,
            "conversation": [{"role": item.role, "content": item.content} for item in history],
            "tool_results": result.tool_results or [],
            "citations": citations,
            "recommended_next_action": "Revisar evidencia y contactar al cliente",
        }
        escalation = db.scalar(select(Escalation).where(Escalation.conversation_id == conversation.id))
        if escalation:
            escalation.reason = result.reason or "Escalamiento"
            escalation.evidence = evidence
        else:
            db.add(Escalation(conversation_id=conversation.id, reason=result.reason or "Escalamiento", evidence=evidence))

    db.commit()
    return ChatResponse(
        conversation_id=conversation.id,
        answer=result.answer,
        intent=result.intent,
        confidence=result.confidence,
        escalated=result.escalated,
        citations=citations,
    )


@app.get("/api/escalations", response_model=list[EscalationView])
def list_escalations(db: Session = Depends(get_db)):
    return db.scalars(select(Escalation).order_by(Escalation.created_at.desc())).all()
