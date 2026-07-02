import uuid
from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey, func, Float, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
import enum

class ContactType(str, enum.Enum):
    PRIMARY = "PRIMARY"
    ALTERNATIVE = "ALTERNATIVE"

class SourceField(str, enum.Enum):
    FROM_MESSAGE = "FROM_MESSAGE"
    FROM_WHATSAPP_HEADER = "FROM_WHATSAPP_HEADER"
    FROM_FORM = "FROM_FORM"
    MANUAL = "MANUAL"

class ExtractionMethod(str, enum.Enum):
    REGEX = "REGEX"
    EXPLICIT_QUESTION = "EXPLICIT_QUESTION"
    USER_INPUT = "USER_INPUT"
    ADMIN_MANUAL = "ADMIN_MANUAL"

class ValidationStatus(str, enum.Enum):
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    INVALID = "INVALID"

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    contact_attempts = relationship("ContactAttempt", back_populates="developer")

    def __repr__(self):
        return f"<User(email='{self.email}', is_active={self.is_active})>"

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String(255), unique=True, nullable=False, index=True)
    channel = Column(String(50), nullable=False)

    estado = Column(String(50), default="A", index=True)
    proyecto_id = Column(UUID(as_uuid=True), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    contacts = relationship("Contact", back_populates="conversation", cascade="all, delete-orphan")
    contact_attempts = relationship("ContactAttempt", back_populates="conversation", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Conversation(session_id='{self.session_id}', channel='{self.channel}', estado='{self.estado}')>"

class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    conversation = relationship("Conversation", back_populates="messages")

    def __repr__(self):
        return f"<Message(conversation_id='{self.conversation_id}', role='{self.role}')>"

class Contact(Base):
    __tablename__ = "contacts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)

    name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True, index=True)
    phone = Column(String(30), nullable=True, index=True)

    contact_type = Column(Enum(ContactType), default=ContactType.PRIMARY)
    source_field = Column(Enum(SourceField), nullable=False)
    extraction_method = Column(Enum(ExtractionMethod), nullable=False)
    validation_status = Column(Enum(ValidationStatus), default=ValidationStatus.PENDING)
    confidence_score = Column(Float, default=0.0)

    captured_by = Column(String(50), nullable=False)
    captured_at = Column(DateTime, default=datetime.utcnow)
    validated_at = Column(DateTime, nullable=True)

    conversation = relationship("Conversation", back_populates="contacts")

    def __repr__(self):
        return f"<Contact(id='{self.id}', email='{self.email}', phone='{self.phone}', validation_status='{self.validation_status}')>"

class ContactAttempt(Base):
    __tablename__ = "contact_attempts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    developer_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    method = Column(String(50), nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    conversation = relationship("Conversation", back_populates="contact_attempts")
    developer = relationship("User", back_populates="contact_attempts")

    def __repr__(self):
        return f"<ContactAttempt(developer_id='{self.developer_id}', method='{self.method}')>"
