from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json
from database import get_db
from auth.utils import decode_token
from models import Conversation, Message, MessageRole
from rag.engine_langgraph import LangGraphRAGEngine

router = APIRouter(prefix="/chat", tags=["Chat"])

print("🔧 Initialisation du moteur RAG LangGraph...")
langgraph_rag_engine = LangGraphRAGEngine()
print("✅ Moteur RAG initialisé")

class ChatRequest(BaseModel):
    question: str
    conversation_id: Optional[int] = None
    language: str = "fr"

class SaveMapsRequest(BaseModel):
    question: str
    maps_response: str
    maps_results: List[Dict[str, Any]] = []
    place_type: str
    city: str
    results_count: int = 0
    conversation_id: Optional[int] = None
    language: str = "fr"

@router.post("/ask")
def ask_question(
    data: ChatRequest,
    user_id: int = Depends(decode_token),
    db: Session = Depends(get_db)
):
    try:
        if data.conversation_id:
            conversation = db.query(Conversation).filter(
                Conversation.id == data.conversation_id,
                Conversation.user_id == user_id
            ).first()
            if not conversation:
                raise HTTPException(status_code=404, detail="Conversation not found")
        else:
            conversation = Conversation(user_id=user_id, title=data.question[:100], language=data.language)
            db.add(conversation)
            db.commit()
            db.refresh(conversation)

        messages = db.query(Message).filter(Message.conversation_id == conversation.id).order_by(Message.created_at).all()
        conversation_history = [{"role": m.role.value, "content": m.content} for m in messages]

        db.add(Message(conversation_id=conversation.id, role=MessageRole.user, content=data.question))

        rag_response = langgraph_rag_engine.ask(data.question, conversation_history)
        route = rag_response.get("route", "rag")

        extra_data = None
        if route == "documents" and rag_response.get("documents"):
            extra_data = json.dumps({"type": "documents", "results": rag_response["documents"]}, ensure_ascii=False)
        elif route == "maps" and rag_response.get("maps_results"):
            extra_data = json.dumps({"type": "maps", "results": rag_response["maps_results"]}, ensure_ascii=False)

        db.add(Message(
            conversation_id=conversation.id,
            role=MessageRole.assistant,
            content=rag_response["response"],
            matched_question=rag_response.get("matched_question"),
            similarity=rag_response.get("similarity"),
            maps_data=extra_data
        ))
        db.commit()

        return {
            "response":         rag_response["response"],
            "conversation_id":  conversation.id,
            "matched_question": rag_response.get("matched_question"),
            "similarity":       rag_response.get("similarity", 0.0),
            "route":            route,
            "documents":        rag_response.get("documents", []),
            "maps_results":     rag_response.get("maps_results", []),
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/save-maps")
def save_maps_conversation(
    data: SaveMapsRequest,
    user_id: int = Depends(decode_token),
    db: Session = Depends(get_db)
):
    try:
        if data.conversation_id:
            conversation = db.query(Conversation).filter(Conversation.id == data.conversation_id, Conversation.user_id == user_id).first()
            if not conversation:
                raise HTTPException(status_code=404, detail="Conversation not found")
        else:
            conversation = Conversation(user_id=user_id, title=f"{data.place_type.capitalize()} a {data.city}", language=data.language)
            db.add(conversation)
            db.commit()
            db.refresh(conversation)

        db.add(Message(conversation_id=conversation.id, role=MessageRole.user, content=data.question))
        db.add(Message(
            conversation_id=conversation.id,
            role=MessageRole.assistant,
            content=data.maps_response,
            matched_question=f"Maps: {data.place_type} a {data.city}",
            similarity=1.0,
            maps_data=json.dumps({"type": "maps", "place_type": data.place_type, "city": data.city, "results": data.maps_results}, ensure_ascii=False)
        ))
        db.commit()
        return {"success": True, "conversation_id": conversation.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))