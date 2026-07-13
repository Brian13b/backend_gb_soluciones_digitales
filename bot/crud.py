from sqlalchemy.orm import Session
import uuid
import re
from datetime import datetime, timezone, timedelta

from shared.models import Conversation, Message, Contact, SourceField, ExtractionMethod, ValidationStatus

def get_or_create_conversation(db: Session, session_id: str, channel: str = "web"):
    conversation = db.query(Conversation).filter(
        Conversation.session_id == session_id,
        Conversation.channel == channel
    ).order_by(Conversation.updated_at.desc()).first()

    now = datetime.now(timezone.utc)

    if conversation:
        time_diff = now - conversation.updated_at
        if time_diff < timedelta(hours=24):
            return conversation
        
    new_conversation = Conversation(session_id=session_id, channel=channel, estado="ABIERTA")
    db.add(new_conversation)
    db.commit()
    db.refresh(new_conversation)
    
    return new_conversation

def update_conversation_state(db: Session, conversation_id: uuid.UUID, estado: str = "CONTACTADA"):
    """
    Actualiza el estado de la conversación cuando se captura un lead.
    """
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if conversation:
        conversation.estado = estado
        db.commit()
        db.refresh(conversation)
    return conversation

def add_message(db: Session, conversation_id: uuid.UUID, role: str, content: str):
    """
    Guarda un mensaje individual (del usuario o del asistente).
    """
    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message

def get_conversation_history(db: Session, conversation_id: uuid.UUID, limit: int = 8):
    """
    Trae los últimos mensajes formateados exactamente como los pide OpenAI.
    Limitado a 8 para no gastar tokens innecesarios ni marear a GPT.
    """
    messages = db.query(Message).filter(Message.conversation_id == conversation_id)\
                 .order_by(Message.created_at.asc())\
                 .limit(limit).all()

    history = [{"role": msg.role, "content": msg.content} for msg in messages]
    return history


def _validate_email(email: str) -> bool:
    """Valida formato de email con regex tolerando espacios accidentales"""
    if not email:
        return False
    clean_email = email.strip()
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, clean_email) is not None


def _validate_phone(phone: str) -> bool:
    """Valida teléfono: mínimo 7 dígitos (con prefijos internacionales)"""
    if not phone:
        return False
    phone_str = str(phone).strip()
    cleaned = re.sub(r'[^\d+]', '', phone_str)
    return len(cleaned) >= 7


def save_contact(
    db: Session,
    conversation_id: uuid.UUID,
    name: str = None,
    email: str = None,
    phone: str = None,
    source_field: SourceField = SourceField.FROM_MESSAGE,
    extraction_method: ExtractionMethod = ExtractionMethod.REGEX,
    confidence_score: float = 0.0
) -> Contact:
    """Guarda contacto extraído con validación básica."""
    
    validated_email = email.strip() if email and _validate_email(email) else None
    validated_phone = str(phone).strip() if phone and _validate_phone(phone) else None
    validated_name = name.strip() if name and isinstance(name, str) else None

    if not (validated_name or validated_email or validated_phone):
        return None

    validation_status = ValidationStatus.PENDING

    contact = Contact(
        conversation_id=conversation_id,
        name=validated_name,
        email=validated_email,
        phone=validated_phone,
        source_field=source_field,
        extraction_method=extraction_method,
        validation_status=validation_status,
        confidence_score=confidence_score,
        captured_by="bot_gpt4"
    )

    db.add(contact)
    db.commit()
    db.refresh(contact)

    return contact


def extract_name_from_text(text: str) -> str:
    if not text or len(text) < 2:
        return None

    patterns = [
        r'(?:soy|me llamo|nombre es|es)\s+([A-Z][a-zá-ú]+(?:\s+[A-Z][a-zá-ú]+)?)',
        r'^([A-Z][a-zá-ú]+(?:\s+[A-Z][a-zá-ú]+)?)$'
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()

    return None


def extract_phone_from_text(text: str) -> str:
    if not text:
        return None

    phone_pattern = r'(?:\+\d{1,3}[\s-]?)?\d{7,15}'
    match = re.search(phone_pattern, text)

    if match:
        phone = match.group(0)
        cleaned = re.sub(r'[\s-]', '', phone)
        if _validate_phone(cleaned):
            return cleaned

    return None


def extract_email_from_text(text: str) -> str:
    if not text:
        return None

    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    match = re.search(email_pattern, text)

    if match:
        email = match.group(0)
        if _validate_email(email):
            return email

    return None
