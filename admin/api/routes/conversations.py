from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from shared.models import Conversation, Message
from shared.schemas import ConversationListSchema, ConversationDetailSchema, MessageSchema
from admin.api.deps import get_db, get_current_user
from datetime import datetime
from uuid import UUID
 
router = APIRouter()
 
@router.get("", response_model=List[ConversationListSchema])
def list_conversations(limit: int = 50, estado: str = None, channel: str = None, db: Session = Depends(get_db)):
    query = db.query(Conversation).options(joinedload(Conversation.contacts) )
    
    if estado:
        query = query.filter(Conversation.estado == estado)
    if channel:
        query = query.filter(Conversation.channel == channel)
        
    return query.order_by(Conversation.updated_at.desc()).limit(limit).all()
 
@router.get("/{conversation_id}", response_model=ConversationDetailSchema)
def get_conversation(conversation_id: str, db: Session = Depends(get_db)):
    conversation = db.query(Conversation).options(
        joinedload(Conversation.contacts),
        joinedload(Conversation.messages)
    ).filter(Conversation.id == conversation_id).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")
        
    return conversation
 
@router.patch("/{conversation_id}/estado")
def update_conversation_estado(conversation_id: str, estado: str, db: Session = Depends(get_db)):
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")
        
    conversation.estado = estado
    db.commit()
    db.refresh(conversation)
    
    return {"message": "Estado actualizado exitosamente", "estado": conversation.estado}


@router.delete("/{conversation_id}")
def delete_conversation(conversation_id: str, db: Session = Depends(get_db)):
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")
        
    db.delete(conversation)
    db.commit()
    
    return {"message": "Conversación eliminada exitosamente"}