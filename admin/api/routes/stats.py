from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from shared.models import Conversation
from admin.api.deps import get_db, get_current_user
 
router = APIRouter()
 
@router.get("/stats")
def get_stats(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Estadísticas rápidas del panel"""
    total_conversations = db.query(Conversation).count()
    
    open_conversations = db.query(Conversation).filter(Conversation.estado == "ABIERTA").count()
    contacted = db.query(Conversation).filter(Conversation.estado == "CONTACTADA").count()
    closed = db.query(Conversation).filter(Conversation.estado == "FINALIZADA").count()
    
    web_conversations = db.query(Conversation).filter(Conversation.channel == "web").count()
    whatsapp_conversations = db.query(Conversation).filter(Conversation.channel == "whatsapp").count()
    
    return {
        "total_conversations": total_conversations,
        "open": open_conversations,
        "contacted": contacted,
        "closed": closed,
        "by_channel": {
            "web": web_conversations,
            "whatsapp": whatsapp_conversations
        }
    }