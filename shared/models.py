import uuid
from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey, func, Float, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime, timezone
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
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    contact_attempts = relationship("ContactAttempt", back_populates="developer")

    def __repr__(self):
        return f"<User(email='{self.email}', is_active={self.is_active})>"

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String(255), unique=True, nullable=False, index=True)
    channel = Column(String(50), nullable=False)

    estado = Column(String(50), default="ABIERTA", index=True)
    proyecto_id = Column(UUID(as_uuid=True), nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    processing_started_at = Column(DateTime(timezone=True), nullable=True)

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
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    processed = Column(Boolean, nullable=False, default=False)
    whatsapp_message_id = Column(String(255), nullable=True, unique=True)

    conversation = relationship("Conversation", back_populates="messages")

    def __repr__(self):
        return f"<Message(conversation_id='{self.conversation_id}', role='{self.role}')>"

class Contact(Base):
    __tablename__ = "contacts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, unique=True)

    name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True, index=True)
    phone = Column(String(30), nullable=True, index=True)

    contact_type = Column(Enum(ContactType), default=ContactType.PRIMARY)
    source_field = Column(Enum(SourceField), nullable=False)
    extraction_method = Column(Enum(ExtractionMethod), nullable=False)
    validation_status = Column(Enum(ValidationStatus), default=ValidationStatus.PENDING)
    confidence_score = Column(Float, default=0.0)

    captured_by = Column(String(50), nullable=False)
    captured_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    validated_at = Column(DateTime(timezone=True), nullable=True)

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
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    conversation = relationship("Conversation", back_populates="contact_attempts")
    developer = relationship("User", back_populates="contact_attempts")

    def __repr__(self):
        return f"<ContactAttempt(developer_id='{self.developer_id}', method='{self.method}')>"

class Client(Base):
    __tablename__ = "clients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    company_name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True, index=True)
    phone = Column(String(30), nullable=True, index=True)
    status = Column(String(50), default="lead", index=True)
    notes = Column(Text, nullable=True)
    source = Column(String(50), default="manual")
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    conversation = relationship("Conversation")
    projects = relationship("Project", back_populates="client")

    def __repr__(self):
        return f"<Client(name='{self.name}', email='{self.email}', status='{self.status}')>"

class Project(Base):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    short_description = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="idea", index=True)
    is_published = Column(Boolean, default=False, index=True)
    is_own_project = Column(Boolean, default=False)
    is_featured = Column(Boolean, default=False)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id", ondelete="SET NULL"), nullable=True)
    technologies = Column(String(500), nullable=True)
    category = Column(String(100), nullable=True)
    thumbnail_url = Column(String(500), nullable=True)
    demo_url = Column(String(500), nullable=True)
    repo_url = Column(String(500), nullable=True)
    result_metric = Column(String(255), nullable=True)
    display_order = Column(Float, default=0)
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    deployment_info = Column(JSONB, default=dict)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    client = relationship("Client", back_populates="projects")

    def __repr__(self):
        return f"<Project(title='{self.title}', slug='{self.slug}', status='{self.status}')>"