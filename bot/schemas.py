from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime

# ==========================================
# SCHEMAS PARA LA WEB (React Frontend)
# ==========================================
class ChatWebRequest(BaseModel):
    session_id: str = Field(..., description="El ID único del visitante anónimo")
    mensaje: str = Field(..., description="El texto escrito por el usuario")

class ChatResponse(BaseModel):
    respuesta: str
    estado_actual: str

# ==========================================
# SCHEMAS PARA WHATSAPP (Futuro)
# ==========================================
class WhatsAppMessage(BaseModel):
    from_number: str
    text: str

class WhatsAppPayload(BaseModel):
    object: str
    entry: List[dict] 

# ==========================================
# SCHEMAS PARA EL PANEL DE ADMIN (Lectura)
# ==========================================
class MessageSchema(BaseModel):
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True 

class ConversationSchema(BaseModel):
    id: UUID
    session_id: str
    channel: str
    contact_info: Optional[str]
    estado: str
    messages: List[MessageSchema] = []

    class Config:
        from_attributes = True