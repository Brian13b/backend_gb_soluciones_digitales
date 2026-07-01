"""
Unified SQLAlchemy ORM models for Bot and Admin services.
Single source of truth for database schema to prevent divergence.
"""

import uuid
from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()


# ==========================================
# MODEL: User (Admin Panel)
# ==========================================
class User(Base):
    """Admin user account for dashboard access."""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    contact_attempts = relationship("ContactAttempt", back_populates="developer")

    def __repr__(self):
        return f"<User(email='{self.email}', is_active={self.is_active})>"


# ==========================================
# MODEL: Conversation (Bot Visitors + Admin Data)
# ==========================================
class Conversation(Base):
    """
    Conversation between visitor/client and bot.
    Unified model with fields from both bot and admin services.
    """
    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String(255), unique=True, nullable=False, index=True)
    channel = Column(String(50), nullable=False)  # "web" or "whatsapp"

    # Contact information (captured during conversation)
    contact_info = Column(String, nullable=True)  # Legacy: simple contact field
    contact_name = Column(String(255), nullable=True)
    contact_phone = Column(String(20), nullable=True)
    contact_email = Column(String(255), nullable=True)

    # State tracking
    estado = Column(String(50), default="A", index=True)  # A (Exploration) or B (Lead Ready)
    proyecto_id = Column(UUID(as_uuid=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    contact_attempts = relationship("ContactAttempt", back_populates="conversation", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Conversation(session_id='{self.session_id}', channel='{self.channel}', estado='{self.estado}')>"


# ==========================================
# MODEL: Message (Chat History)
# ==========================================
class Message(Base):
    """
    Individual message in a conversation.
    Stores both user input and bot responses.
    """
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(50), nullable=False)  # "user" or "assistant"
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")

    def __repr__(self):
        return f"<Message(conversation_id='{self.conversation_id}', role='{self.role}')>"


# ==========================================
# MODEL: ContactAttempt (Admin Contact History)
# ==========================================
class ContactAttempt(Base):
    """
    Record of admin contact attempts with leads.
    Tracks who contacted which conversation and how.
    """
    __tablename__ = "contact_attempts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    developer_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    method = Column(String(50), nullable=False)  # "whatsapp", "email", "call", etc.
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    conversation = relationship("Conversation", back_populates="contact_attempts")
    developer = relationship("User", back_populates="contact_attempts")

    def __repr__(self):
        return f"<ContactAttempt(developer_id='{self.developer_id}', method='{self.method}')>"
