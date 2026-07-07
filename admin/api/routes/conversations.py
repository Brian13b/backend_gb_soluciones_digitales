from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, func
from typing import List
from shared.models import Conversation, Message
from shared.schemas import ConversationListSchema, ConversationDetailSchema, MessageSchema
from admin.api.deps import get_db, get_current_user
from datetime import datetime
from uuid import UUID
from shared.models import ContactType
 
router = APIRouter()
 
@router.get("/conversations", response_model=List[ConversationListSchema])
def list_conversations(limit: int = 50, estado: str = None, channel: str = None, db: Session = Depends(get_db)):
    query = db.query(Conversation).options(
        joinedload(Conversation.contacts)
    )

    if estado:
        query = query.filter(Conversation.estado == estado)
    if channel:
        query = query.filter(Conversation.channel == channel)

    conversations = query.order_by(Conversation.updated_at.desc()).limit(limit).all()

    conversation_ids = [c.id for c in conversations]
    if conversation_ids:
        message_counts = db.query(
            Message.conversation_id,
            func.count(Message.id).label('count')
        ).filter(Message.conversation_id.in_(conversation_ids)).group_by(
            Message.conversation_id
        ).all()
        counts_map = {cid: count for cid, count in message_counts}

        for conversation in conversations:
            conversation.message_count = counts_map.get(conversation.id, 0)
    else:
        for conversation in conversations:
            conversation.message_count = 0

    return conversations
 
@router.get("/conversations/{conversation_id}", response_model=ConversationDetailSchema)
def get_conversation(conversation_id: UUID, db: Session = Depends(get_db)):
    conversation = db.query(Conversation).options(
        joinedload(Conversation.contacts),
        joinedload(Conversation.messages)
    ).filter(Conversation.id == conversation_id).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")
        
    return conversation
 
@router.patch("/conversations/{conversation_id}/estado")
def update_conversation_estado(conversation_id: UUID, estado: str, db: Session = Depends(get_db)):
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")
        
    conversation.estado = estado
    db.commit()
    db.refresh(conversation)
    
    return {"message": "Estado actualizado exitosamente", "estado": conversation.estado}

@router.delete("/conversations/{conversation_id}")
def delete_conversation(conversation_id: UUID, db: Session = Depends(get_db)):
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")

    db.delete(conversation)
    db.commit()

    return {"message": "Conversación eliminada exitosamente"}

@router.post("/conversations/{conversation_id}/convert-to-client")
def convert_conversation_to_client(conversation_id: UUID, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    from shared.models import Client

    conversation = db.query(Conversation).options(
        joinedload(Conversation.contacts)
    ).filter(Conversation.id == conversation_id).first()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")

    existing_client = db.query(Client).filter(Client.conversation_id == conversation_id).first()
    if existing_client:
        raise HTTPException(
            status_code=409,
            detail="Esta conversación ya fue convertida a cliente",
            headers={"X-Client-ID": str(existing_client.id)}
        )

    primary_contact = next((c for c in conversation.contacts if c.contact_type.value == "PRIMARY"), None)

    if not primary_contact or not (primary_contact.name or primary_contact.email or primary_contact.phone):
        raise HTTPException(
            status_code=400,
            detail="La conversación debe tener un contacto primario con nombre, email o teléfono"
        )

    new_client = Client(
        name=primary_contact.name or f"Cliente {conversation_id}",
        email=primary_contact.email,
        phone=primary_contact.phone,
        conversation_id=conversation_id,
        status="lead",
        source="conversation"
    )

    db.add(new_client)
    db.commit()
    db.refresh(new_client)

    return {
        "message": "Conversación convertida a cliente exitosamente",
        "client_id": str(new_client.id),
        "client": {
            "id": new_client.id,
            "name": new_client.name,
            "email": new_client.email,
            "phone": new_client.phone,
            "status": new_client.status
        }
    }