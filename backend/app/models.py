from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, func, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class LineUser(Base):
    __tablename__ = "line_users"
    id = Column(Integer, primary_key=True, index=True)
    line_id = Column(String, unique=True, index=True)
    name = Column(String)
    picture = Column(String)
    mode = Column(String, default="bot")  # bot or manual
    added_at = Column(DateTime, default=func.now())
    blocked_at = Column(DateTime, nullable=True)

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(Integer, primary_key=True, index=True)
    line_user_id = Column(String, index=True)
    message = Column(String)
    is_from_user = Column(Boolean)
    timestamp = Column(DateTime, default=func.now())

class EventLog(Base):
    __tablename__ = "event_logs"
    id = Column(Integer, primary_key=True, index=True)
    line_user_id = Column(String, index=True)
    event_type = Column(String)  # add, block, renew
    timestamp = Column(DateTime, default=func.now())

# Message Templates System
class MessageCategory(Base):
    __tablename__ = "message_categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(Text)
    color = Column(String, default="#3B82F6")  # Hex color for UI
    created_at = Column(DateTime, default=func.now())
    
    # Relationship
    templates = relationship("MessageTemplate", back_populates="category")

class MessageTemplate(Base):
    __tablename__ = "message_templates"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    message_type = Column(String, index=True)  # text, sticker, image, video, etc.
    category_id = Column(Integer, ForeignKey("message_categories.id"))
    
    # Template content (JSON format for flexibility)
    content = Column(JSON)
    
    # Metadata
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=0)  # Higher priority = more likely to be selected
    tags = Column(String)  # Comma-separated tags for searching
    
    # Usage tracking
    usage_count = Column(Integer, default=0)
    last_used = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    category = relationship("MessageCategory", back_populates="templates")
    usage_logs = relationship("TemplateUsageLog", back_populates="template")

class TemplateUsageLog(Base):
    __tablename__ = "template_usage_logs"
    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("message_templates.id"))
    line_user_id = Column(String, index=True)
    context = Column(Text)  # What triggered this template
    success = Column(Boolean, default=True)  # Was it sent successfully
    timestamp = Column(DateTime, default=func.now())
    
    # Relationship
    template = relationship("MessageTemplate", back_populates="usage_logs")