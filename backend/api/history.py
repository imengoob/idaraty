from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import json
from pydantic import BaseModel
from database import get_db
from auth.utils import decode_token
from models import Conversation, Message

router = APIRouter(prefix="/history", tags=["History"])


class ConversationSummary(BaseModel):
    id: int
    title: str
    language: str
    message_count: int
    last_message: str
    created_at: str

    class Config:
        from_attributes = True


@router.get("/conversations", response_model=List[ConversationSummary])
def get_conversations(
    user_id: int = Depends(decode_token),
    db: Session = Depends(get_db)
):
    conversations = db.query(Conversation).filter(
        Conversation.user_id == user_id
    ).order_by(Conversation.updated_at.desc()).all()

    result = []
    for conv in conversations:
        last_msg = db.query(Message).filter(
            Message.conversation_id == conv.id
        ).order_by(Message.created_at.desc()).first()

        msg_count = db.query(Message).filter(
            Message.conversation_id == conv.id
        ).count()

        result.append({
            "id": conv.id,
            "title": conv.title or "Nouvelle conversation",
            "language": conv.language,
            "message_count": msg_count,
            "last_message": last_msg.content[:100] if last_msg else "",
            "created_at": conv.created_at.isoformat()
        })

    return result


@router.get("/conversation/{conversation_id}")
def get_conversation_messages(
    conversation_id: int,
    user_id: int = Depends(decode_token),
    db: Session = Depends(get_db)
):
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == user_id
    ).first()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at).all()

    return {
        "conversation": {
            "id": conversation.id,
            "title": conversation.title,
            "language": conversation.language
        },
        "messages": [
            {
                "id": msg.id,
                "role": msg.role.value,
                "content": msg.content,
                # ✅ Retourner maps_data parsé si présent
                "maps_data": json.loads(msg.maps_data) if msg.maps_data else None,
                "created_at": msg.created_at.isoformat()
            }
            for msg in messages
        ]
    }
# Ajouter ces lignes dans backend/api/history.py

@router.delete("/conversation/{conversation_id}")
def delete_conversation(
    conversation_id: int,
    user_id: int = Depends(decode_token),
    db: Session = Depends(get_db)
):
    """Supprimer une conversation et tous ses messages"""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == user_id
    ).first()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation introuvable")

    db.delete(conversation)  # cascade supprime aussi les messages
    db.commit()

    return {"success": True, "message": "Conversation supprimée"}