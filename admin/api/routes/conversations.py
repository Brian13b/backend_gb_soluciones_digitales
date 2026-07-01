from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from shared.models import Conversation, Message
from shared.schemas import ConversationListSchema, ConversationDetailSchema, MessageSchema
from admin.api.deps import get_db, get_current_user
from datetime import datetime
from uuid import UUID
 
router = APIRouter()
 
@router.get("/conversations", response_model=list[ConversationListSchema])
def list_conversations(
    estado: str = Query(None, description="Filtrar por estado: abierta, contactado, cerrada"),
    channel: str = Query(None, description="Filtrar por canal: web, whatsapp"),
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Listar conversaciones con filtros"""
    query = db.query(Conversation)
    
    if estado:
        query = query.filter(Conversation.estado == estado)
    if channel:
        query = query.filter(Conversation.channel == channel)
    
    # Eager load messages to avoid N+1 query problem
    conversations = query.options(joinedload(Conversation.messages)).order_by(desc(Conversation.updated_at)).offset(skip).limit(limit).all()

    result = []
    for conv in conversations:
        # Extract last message from already-loaded messages (no DB query needed)
        last_message = max(conv.messages, key=lambda m: m.created_at) if conv.messages else None

        result.append(ConversationListSchema(
            id=conv.id,
            session_id=conv.session_id,
            channel=conv.channel,
            contact_name=conv.contact_name,
            contact_phone=conv.contact_phone,
            contact_email=conv.contact_email,
            estado=conv.estado,
            message_count=len(conv.messages),
            last_message_at=last_message.created_at if last_message else None,
            created_at=conv.created_at,
            updated_at=conv.updated_at
        ))

    return result
 
@router.get("/conversations/{conversation_id}", response_model=ConversationDetailSchema)
def get_conversation(
    conversation_id: UUID, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Ver detalles completos de una conversación"""
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")
    
    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at).all()
    
    return ConversationDetailSchema(
        id=conversation.id,
        session_id=conversation.session_id,
        channel=conversation.channel,
        contact_name=conversation.contact_name,
        contact_phone=conversation.contact_phone,
        contact_email=conversation.contact_email,
        estado=conversation.estado,
        messages=[MessageSchema.from_orm(m) for m in messages],
        created_at=conversation.created_at,
        updated_at=conversation.updated_at
    )
 
@router.patch("/conversations/{conversation_id}/estado")
def update_conversation_estado(
    conversation_id: UUID,
    estado: str = Query(..., description="Nuevo estado: abierta, contactado, cerrada"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Cambiar estado de una conversación"""
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")
    
    conversation.estado = estado
    conversation.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(conversation)
    
    return {"message": f"Estado actualizado a: {estado}", "conversation_id": conversation_id}