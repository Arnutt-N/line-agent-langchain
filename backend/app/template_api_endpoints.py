# Message Templates API Endpoints
# Add these to main.py

from .template_crud import (
    create_message_category, get_message_categories, get_message_category,
    update_message_category, delete_message_category,
    create_message_template, get_message_templates, get_message_template,
    update_message_template, delete_message_template
)
from .schemas import (
    MessageCategoryCreate, MessageCategoryUpdate, MessageCategorySchema,
    MessageTemplateCreate, MessageTemplateUpdate, MessageTemplateSchema,
    TemplateSelectionRequest
)
from .template_selector import TemplateSelector
from .message_builder import LineMessageBuilder

# Categories
@app.post("/api/categories", response_model=MessageCategorySchema)
def create_category(category: MessageCategoryCreate, db: Session = Depends(get_db)):
    return create_message_category(db, category)

@app.get("/api/categories", response_model=List[MessageCategorySchema])
def list_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_message_categories(db, skip, limit)

@app.get("/api/categories/{category_id}", response_model=MessageCategorySchema)
def get_category(category_id: int, db: Session = Depends(get_db)):
    category = get_message_category(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@app.put("/api/categories/{category_id}", response_model=MessageCategorySchema)
def update_category(category_id: int, category_update: MessageCategoryUpdate, db: Session = Depends(get_db)):
    category = update_message_category(db, category_id, category_update)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@app.delete("/api/categories/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db)):
    category = delete_message_category(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"message": "Category deleted successfully"}

# Templates
@app.post("/api/templates", response_model=MessageTemplateSchema)
def create_template(template: MessageTemplateCreate, db: Session = Depends(get_db)):
    return create_message_template(db, template)

@app.get("/api/templates", response_model=List[MessageTemplateSchema])
def list_templates(
    skip: int = 0, 
    limit: int = 100,
    category_id: Optional[int] = None,
    message_type: Optional[str] = None,
    is_active: Optional[bool] = True,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    return get_message_templates(db, skip, limit, category_id, message_type, is_active, search)

@app.get("/api/templates/{template_id}", response_model=MessageTemplateSchema)
def get_template(template_id: int, db: Session = Depends(get_db)):
    template = get_message_template(db, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template
