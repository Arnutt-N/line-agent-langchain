from sqlalchemy.orm import Session
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import datetime
from typing import List, Optional, Dict, Any
from .models import MessageCategory, MessageTemplate, TemplateUsageLog
from .schemas import (
    MessageCategoryCreate, MessageCategoryUpdate,
    MessageTemplateCreate, MessageTemplateUpdate,
    TemplateSelectionRequest
)

# Message Categories CRUD
def create_message_category(db: Session, category: MessageCategoryCreate):
    db_category = MessageCategory(**category.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

def get_message_categories(db: Session, skip: int = 0, limit: int = 100):
    return db.query(MessageCategory).offset(skip).limit(limit).all()

def get_message_category(db: Session, category_id: int):
    return db.query(MessageCategory).filter(MessageCategory.id == category_id).first()

def update_message_category(db: Session, category_id: int, category_update: MessageCategoryUpdate):
    db_category = get_message_category(db, category_id)
    if db_category:
        update_data = category_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_category, field, value)
        db.commit()
        db.refresh(db_category)
    return db_category

def delete_message_category(db: Session, category_id: int):
    db_category = get_message_category(db, category_id)
    if db_category:
        db.delete(db_category)
        db.commit()
    return db_category

# Message Templates CRUD
def create_message_template(db: Session, template: MessageTemplateCreate):
    db_template = MessageTemplate(**template.dict())
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template

def get_message_templates(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    category_id: Optional[int] = None,
    message_type: Optional[str] = None,
    is_active: Optional[bool] = True,
    search: Optional[str] = None
):
    query = db.query(MessageTemplate)
    
    if category_id:
        query = query.filter(MessageTemplate.category_id == category_id)
    if message_type:
        query = query.filter(MessageTemplate.message_type == message_type)
    if is_active is not None:
        query = query.filter(MessageTemplate.is_active == is_active)
    if search:
        query = query.filter(or_(
            MessageTemplate.name.contains(search),
            MessageTemplate.description.contains(search),
            MessageTemplate.tags.contains(search)
        ))
    
    return query.order_by(MessageTemplate.priority.desc(), MessageTemplate.created_at.desc()).offset(skip).limit(limit).all()

def get_message_template(db: Session, template_id: int):
    return db.query(MessageTemplate).filter(MessageTemplate.id == template_id).first()

def update_message_template(db: Session, template_id: int, template_update: MessageTemplateUpdate):
    db_template = get_message_template(db, template_id)
    if db_template:
        update_data = template_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_template, field, value)
        db_template.updated_at = datetime.now()
        db.commit()
        db.refresh(db_template)
    return db_template

def delete_message_template(db: Session, template_id: int):
    db_template = get_message_template(db, template_id)
    if db_template:
        db.delete(db_template)
        db.commit()
    return db_template

def log_template_usage(db: Session, template_id: int, line_user_id: str, context: str = None, success: bool = True):
    # Create usage log
    usage_log = TemplateUsageLog(
        template_id=template_id,
        line_user_id=line_user_id,
        context=context,
        success=success
    )
    db.add(usage_log)
    
    # Update template usage stats
    template = get_message_template(db, template_id)
    if template:
        template.usage_count += 1
        template.last_used = datetime.now()
    
    db.commit()
    return usage_log
