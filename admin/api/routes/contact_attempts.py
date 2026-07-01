from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from shared.models import ContactAttempt, Conversation, User
from shared.schemas import ContactAttemptCreate, ContactAttemptSchema
from admin.api.deps import get_db, get_current_user
from uuid import UUID
 
router = APIRouter()
 
@router.post("/conversations/{conversation_id}/contact-attempt", response_model=ContactAttemptSchema)
def create_contact_attempt(
    conversation_id: UUID,
    attempt: ContactAttemptCreate,
    developer_id: UUID = Query(..., description="ID del desarrollador"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Registrar un intento de contacto"""
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")
    
    user = db.query(User).filter(User.id == developer_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    contact_attempt = ContactAttempt(
        conversation_id=conversation_id,
        developer_id=developer_id,
        method=attempt.method,
        notes=attempt.notes
    )
    
    db.add(contact_attempt)
    db.commit()
    db.refresh(contact_attempt)
    
    return ContactAttemptSchema.from_orm(contact_attempt)
 
@router.get("/conversations/{conversation_id}/contact-attempts", response_model=list[ContactAttemptSchema])
def get_contact_attempts(
    conversation_id: UUID, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Ver historial de intentos de contacto"""
    attempts = db.query(ContactAttempt).filter(
        ContactAttempt.conversation_id == conversation_id
    ).order_by(desc(ContactAttempt.created_at)).all()
    
    return [ContactAttemptSchema.from_orm(a) for a in attempts]