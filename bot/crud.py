from sqlalchemy.orm import Session
from sqlalchemy import or_
import uuid
import re
from datetime import datetime, timezone, timedelta

from shared.models import Conversation, Message, Contact, SourceField, ExtractionMethod, ValidationStatus

def get_or_create_conversation(db: Session, session_id: str, channel: str = "web"):
    conversation = db.query(Conversation).filter(
        Conversation.session_id == session_id,
        Conversation.channel == channel
    ).first()

    if not conversation:
        conversation = Conversation(session_id=session_id, channel=channel, estado="ABIERTA")
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
    
    return conversation

def update_conversation_state(db: Session, conversation_id: uuid.UUID, estado: str = "CONTACTADA"):
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if conversation:
        conversation.estado = estado
        db.commit()
        db.refresh(conversation)
    return conversation

def message_exists_by_whatsapp_id(db: Session, whatsapp_message_id: str) -> bool:
    if not whatsapp_message_id:
        return False
    return db.query(Message).filter(Message.whatsapp_message_id == whatsapp_message_id).first() is not None

def add_message(db: Session, conversation_id: uuid.UUID, role: str, content: str, whatsapp_message_id: str = None):
    ahora = datetime.now(timezone.utc)

    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
        created_at=ahora,
        whatsapp_message_id=whatsapp_message_id
    )

    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if conversation:
        conversation.updated_at = ahora

    db.add(message)
    db.commit()
    db.refresh(message)
    
    return message

def try_acquire_processing_lock(db: Session, conversation_id: uuid.UUID, timeout_seconds: int = 60) -> bool:
    now = datetime.now(timezone.utc)
    stale_threshold = now - timedelta(seconds=timeout_seconds)

    filas_actualizadas = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        or_(Conversation.processing_started_at.is_(None), Conversation.processing_started_at < stale_threshold)
    ).update({"processing_started_at": now}, synchronize_session=False)

    db.commit()
    return filas_actualizadas == 1

def release_processing_lock(db: Session, conversation_id: uuid.UUID):
    db.query(Conversation).filter(Conversation.id == conversation_id).update(
        {"processing_started_at": None}, synchronize_session=False
    )
    db.commit()

def get_pending_user_messages(db: Session, conversation_id: uuid.UUID):
    return db.query(Message).filter(
        Message.conversation_id == conversation_id,
        Message.role == "user",
        Message.processed == False
    ).order_by(Message.created_at.asc(), Message.id.asc()).all()

def mark_messages_processed(db: Session, message_ids: list):
    if not message_ids:
        return
    db.query(Message).filter(Message.id.in_(message_ids)).update(
        {"processed": True}, synchronize_session=False
    )
    db.commit()

def get_conversation_history(db: Session, conversation_id: uuid.UUID, limit: int = 20):
    messages = db.query(Message).filter(Message.conversation_id == conversation_id)\
                 .order_by(Message.created_at.desc(), Message.id.desc())\
                 .limit(limit).all()
    messages.reverse()

    history = [{"role": msg.role, "content": msg.content} for msg in messages]
    return history

def _validate_email(email: str) -> bool:
    if not email:
        return False
    clean_email = email.strip()
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, clean_email) is not None

def _validate_phone(phone: str) -> bool:
    if not phone:
        return False
    phone_str = str(phone).strip()
    cleaned = re.sub(r'[^\d+]', '', phone_str)
    return len(cleaned) >= 7

def normalize_phone_e164(phone) -> str:
    """Normaliza a E.164 con '+' (ej: +5493435551234).

    Caso Argentina: el wa_id que manda el webhook de Meta suele venir sin el "9"
    de celular (54 + 10 dígitos, en vez de 549 + 10 dígitos). Como todo número que
    llega por WhatsApp es, en la práctica, un celular, si detectamos esa forma le
    insertamos el "9". No distingue fijo de celular por longitud (ambos tienen
    10 dígitos después del "54"), así que un número fijo argentino ingresado a
    mano en el widget web podría normalizarse igual que un celular.
    """
    if not phone:
        return None

    digitos = re.sub(r'[^\d]', '', str(phone).strip())
    if not digitos:
        return None

    if digitos.startswith('54') and not digitos.startswith('549'):
        resto = digitos[2:]
        if len(resto) == 10:
            digitos = '549' + resto

    return '+' + digitos

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
    validated_email = email.strip() if email and _validate_email(email) else None
    validated_phone = normalize_phone_e164(phone) if phone and _validate_phone(phone) else None
    validated_name = name.strip() if name and isinstance(name, str) else None

    if not (validated_name or validated_email or validated_phone):
        return None

    contact = db.query(Contact).filter(Contact.conversation_id == conversation_id).first()

    if contact:
        if validated_name: contact.name = validated_name
        if validated_email: contact.email = validated_email
        if validated_phone: contact.phone = validated_phone
        contact.source_field = source_field
        contact.extraction_method = extraction_method
        contact.confidence_score = confidence_score
        contact.captured_by = "bot_gpt4"
    else:
        contact = Contact(
            conversation_id=conversation_id,
            name=validated_name,
            email=validated_email,
            phone=validated_phone,
            source_field=source_field,
            extraction_method=extraction_method,
            validation_status=ValidationStatus.PENDING,
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