#!/usr/bin/env python3
"""
Database Migration: Add Message Templates Tables
เพิ่มตารางสำหรับ Message Templates System
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.database import engine, Base
from backend.app.models import MessageCategory, MessageTemplate, TemplateUsageLog

def create_tables():
    """สร้างตารางใหม่สำหรับ Message Templates"""
    print("🔄 Creating Message Templates tables...")
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Message Templates tables created successfully!")
        
        # Insert default categories
        from backend.app.database import SessionLocal
        from backend.app.template_crud import create_message_category
        from backend.app.schemas import MessageCategoryCreate
        
        db = SessionLocal()
        
        default_categories = [
            {"name": "Greeting", "description": "การทักทาย", "color": "#10B981"},
            {"name": "Information", "description": "ข้อมูลทั่วไป", "color": "#3B82F6"},
            {"name": "Support", "description": "การสนับสนุน", "color": "#8B5CF6"},
            {"name": "Marketing", "description": "การตลาด", "color": "#F59E0B"},
            {"name": "Entertainment", "description": "ความบันเทิง", "color": "#EC4899"},
            {"name": "Emergency", "description": "กรณีฉุกเฉิน", "color": "#EF4444"},
        ]
        
        for cat_data in default_categories:
            try:
                category = MessageCategoryCreate(**cat_data)
                create_message_category(db, category)
                print(f"✅ Created category: {cat_data['name']}")
            except Exception as e:
                print(f"⚠️ Category {cat_data['name']} might already exist: {e}")
        
        db.close()
        print("✅ Default categories added!")
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")

if __name__ == "__main__":
    print("🗃️ Message Templates Database Migration")
    print("=" * 50)
    create_tables()
    print("\n🎉 Migration completed!")
