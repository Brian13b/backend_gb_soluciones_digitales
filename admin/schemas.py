from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from shared.schemas import (

    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,

    UserCreate,
    UserResponse,

    MessageCreate,
    MessageSchema,

    ConversationListSchema,
    ConversationDetailSchema,
    ConversationSchema,

    ContactAttemptCreate,
    ContactAttemptSchema,

    ChatWebRequest,
    ChatResponse,
    WhatsAppMessage,
    WhatsAppPayload,
)

class ClientCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    company_name: Optional[str] = Field(None, max_length=255)
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=30)
    status: str = Field(default="lead", max_length=50)
    notes: Optional[str] = None
    source: str = Field(default="manual", max_length=50)
    conversation_id: Optional[UUID] = None

class ClientUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    company_name: Optional[str] = Field(None, max_length=255)
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=30)
    status: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None
    source: Optional[str] = Field(None, max_length=50)

class ClientResponse(BaseModel):
    id: UUID
    name: str
    company_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    status: str
    notes: Optional[str] = None
    source: str
    conversation_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ClientListResponse(BaseModel):
    id: UUID
    name: str
    company_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ProjectCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=255)
    short_description: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    status: str = Field(default="idea", max_length=50)
    is_published: bool = False
    is_own_project: bool = False
    is_featured: bool = False
    client_id: Optional[UUID] = None
    technologies: Optional[str] = Field(None, max_length=500)
    category: Optional[str] = Field(None, max_length=100)
    thumbnail_url: Optional[str] = Field(None, max_length=500)
    demo_url: Optional[str] = Field(None, max_length=500)
    repo_url: Optional[str] = Field(None, max_length=500)
    result_metric: Optional[str] = Field(None, max_length=255)
    display_order: float = 0
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    deployment_info: Optional[dict] = {}

class ProjectUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    slug: Optional[str] = Field(None, min_length=1, max_length=255)
    short_description: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    status: Optional[str] = Field(None, max_length=50)
    is_published: Optional[bool] = None
    is_own_project: Optional[bool] = None
    is_featured: Optional[bool] = None
    client_id: Optional[UUID] = None
    technologies: Optional[str] = Field(None, max_length=500)
    category: Optional[str] = Field(None, max_length=100)
    thumbnail_url: Optional[str] = Field(None, max_length=500)
    demo_url: Optional[str] = Field(None, max_length=500)
    repo_url: Optional[str] = Field(None, max_length=500)
    result_metric: Optional[str] = Field(None, max_length=255)
    display_order: Optional[float] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    deployment_info: Optional[dict] = None

class ProjectResponse(BaseModel):
    id: UUID
    title: str
    slug: str
    short_description: Optional[str] = None
    description: Optional[str] = None
    status: str
    is_published: bool
    is_own_project: bool
    is_featured: bool
    client_id: Optional[UUID] = None
    technologies: Optional[str] = None
    category: Optional[str] = None
    thumbnail_url: Optional[str] = None
    demo_url: Optional[str] = None
    repo_url: Optional[str] = None
    result_metric: Optional[str] = None
    display_order: float
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    deployment_info: Optional[dict] = None  
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ProjectListResponse(BaseModel):
    id: UUID
    title: str
    slug: str
    short_description: Optional[str] = None
    status: str
    is_published: bool
    is_featured: bool
    client_id: Optional[UUID] = None
    category: Optional[str] = None
    thumbnail_url: Optional[str] = None
    display_order: float
    created_at: datetime

    class Config:
        from_attributes = True

__all__ = [
    "LoginRequest",
    "TokenResponse",
    "RefreshTokenRequest",

    "UserCreate",
    "UserResponse",

    "MessageCreate",
    "MessageSchema",

    "ConversationListSchema",
    "ConversationDetailSchema",
    "ConversationSchema",

    "ContactAttemptCreate",
    "ContactAttemptSchema",

    "ChatWebRequest",
    "ChatResponse",
    "WhatsAppMessage",
    "WhatsAppPayload",

    "ClientCreate",
    "ClientUpdate",
    "ClientResponse",
    "ClientListResponse",

    "ProjectCreate",
    "ProjectUpdate",
    "ProjectResponse",
    "ProjectListResponse",
]
