from sqlalchemy.orm import Session
import uuid

from shared.models import Conversation, Message

def get_or_create_conversation(db: Session, session_id: str, channel: str = "web"):
    """
    Busca la conversación por session_id. Si no existe, la crea.
    Esto permite la 'omnipresencia' del bot en cualquier sesión que envíes.
    """
    conversation = db.query(Conversation).filter(
        Conversation.session_id == session_id,
        Conversation.channel == channel
    ).first()

    if not conversation:
        conversation = Conversation(session_id=session_id, channel=channel)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
    
    return conversation

def update_conversation_state(db: Session, conversation_id: uuid.UUID, contact_info: str = None, estado: str = "B"):
    """
    Actualiza la conversación cuando se detecta un cambio de estado o se captura el lead.
    """
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if conversation:
        if contact_info:
            conversation.contact_info = contact_info
        if estado:
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