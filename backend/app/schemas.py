from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any, List

class LineUserSchema(BaseModel):
    line_id: str
    name: str
    picture: str | None
    mode: str
    added_at: datetime
    blocked_at: datetime | None

    class Config:
        from_attributes = True

class ChatMessageSchema(BaseModel):
    line_user_id: str
    message: str
    is_from_user: bool
    timestamp: datetime

    class Config:
        from_attributes = True

class DashboardStats(BaseModel):
    total_users: int
    daily_adds: int
    daily_blocks: int
    daily_renews: int

# Message Templates Schemas
class MessageCategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    color: str = "#3B82F6"

class MessageCategoryCreate(MessageCategoryBase):
    pass

class MessageCategoryUpdate(MessageCategoryBase):
    name: Optional[str] = None

class MessageCategorySchema(MessageCategoryBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class MessageTemplateBase(BaseModel):
    name: str
    description: Optional[str] = None
    message_type: str  # text, sticker, image, video, audio, location, template, flex, quick_reply
    category_id: Optional[int] = None
    content: Dict[str, Any]
    is_active: bool = True
    priority: int = 0
    tags: Optional[str] = None

class MessageTemplateCreate(MessageTemplateBase):
    pass

class MessageTemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    message_type: Optional[str] = None
    category_id: Optional[int] = None
    content: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    priority: Optional[int] = None
    tags: Optional[str] = None

class MessageTemplateSchema(MessageTemplateBase):
    id: int
    usage_count: int
    last_used: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    category: Optional[MessageCategorySchema] = None
    
    class Config:
        from_attributes = True

class TemplateUsageLogSchema(BaseModel):
    id: int
    template_id: int
    line_user_id: str
    context: Optional[str]
    success: bool
    timestamp: datetime
    
    class Config:
        from_attributes = True

# Template Selection Request
class TemplateSelectionRequest(BaseModel):
    context: str
    user_message: str
    category: Optional[str] = None
    message_type: Optional[str] = None
    tags: Optional[List[str]] = None