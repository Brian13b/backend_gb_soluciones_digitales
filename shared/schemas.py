from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime

class ChatWebRequest(BaseModel):
    session_id: str = Field(..., description="El ID único del visitante anónimo")
    mensaje: str = Field(..., description="El texto escrito por el usuario")

class ChatResponse(BaseModel):
    respuesta: str
    estado_actual: str

class WhatsAppMessage(BaseModel):
    from_number: str
    text: str

class WhatsAppPayload(BaseModel):
    object: str
    entry: List[dict]

class ContactSchema(BaseModel):
    id: UUID
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    contact_type: str
    validation_status: str
    
    class Config:
        from_attributes = True

class MessageCreate(BaseModel):
    role: str
    content: str

class MessageSchema(BaseModel):
    id: UUID
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True

class ConversationListSchema(BaseModel):
    id: UUID
    session_id: str
    channel: str
    estado: str
    message_count: int = 0
    contacts: List[ContactSchema] = []
    last_message_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ConversationDetailSchema(BaseModel):
    id: UUID
    session_id: str
    channel: str
    estado: str
    contacts: List[ContactSchema] = []
    messages: List[MessageSchema] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ConversationSchema(ConversationDetailSchema):
    pass

class ContactAttemptCreate(BaseModel):
    method: str = Field(..., description="Metodo de contacto: whatsapp, email, llamada")
    notes: Optional[str] = Field(None, description="Notas adicionales sobre el intento")

class ContactAttemptSchema(BaseModel):
    id: UUID
    developer_id: UUID
    method: str
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: UUID
    email: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: UUID
    email: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str