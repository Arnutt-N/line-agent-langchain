"""
Phase 1.3: ตรวจสอบ Database และ Categories
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine
from app.models import Base, MessageCategory, MessageTemplate, LineUser, ChatMessage
from sqlalchemy import inspect, text
import sqlite3

def check_database_structure():
    """ตรวจสอบโครงสร้าง Database"""
    print("🗄️ Phase 1.3: ตรวจสอบ Database และ Categories")
    print("="*60)
    
    # ตรวจสอบไฟล์ database
    db_path = os.path.join(os.path.dirname(__file__), 'line_agent.db')
    if os.path.exists(db_path):
        print(f"✅ Database file exists: {db_path}")
        file_size = os.path.getsize(db_path) / 1024 / 1024  # MB
        print(f"📊 Size: {file_size:.2f} MB")
    else:
        print("❌ Database file not found!")
        return False
    
    # ตรวจสอบ tables
    print("\n📋 ตรวจสอบ Tables:")
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    required_tables = [
        'line_users',
        'chat_messages',
        'event_logs',
        'message_categories',
        'message_templates',
        'template_usage_logs'
    ]
    
    for table in required_tables:
        if table in tables:
            print(f"  ✅ {table}")
        else:
            print(f"  ❌ {table} - ไม่พบ!")
    
    return True

def check_existing_categories():
    """ตรวจสอบ Categories ที่มีอยู่"""
    print("\n📁 Categories ที่มีอยู่:")
    
    db = SessionLocal()
    try:
        categories = db.query(MessageCategory).all()
        
        if categories:
            print(f"พบ {len(categories)} categories:")
            for cat in categories:
                print(f"  📌 {cat.name} - {cat.description} ({cat.color})")
        else:
            print("  ⚠️ ยังไม่มี categories ใดๆ")
            
        return len(categories)
    finally:
        db.close()

def check_existing_templates():
    """ตรวจสอบ Templates ที่มีอยู่"""
    print("\n📝 Templates ที่มีอยู่:")
    
    db = SessionLocal()
    try:
        # นับ templates ตาม category
        categories = db.query(MessageCategory).all()
        
        total_templates = 0
        for cat in categories:
            template_count = db.query(MessageTemplate).filter(
                MessageTemplate.category_id == cat.id
            ).count()
            if template_count > 0:
                print(f"  📁 {cat.name}: {template_count} templates")
                total_templates += template_count
        
        print(f"\n📊 รวมทั้งหมด: {total_templates} templates")
        return total_templates
    finally:
        db.close()

def check_database_stats():
    """แสดงสถิติ Database"""
    print("\n📊 สถิติ Database:")
    
    db = SessionLocal()
    try:
        users_count = db.query(LineUser).count()
        messages_count = db.query(ChatMessage).count()
        categories_count = db.query(MessageCategory).count()
        templates_count = db.query(MessageTemplate).count()
        
        print(f"  👥 Users: {users_count}")
        print(f"  💬 Messages: {messages_count}")
        print(f"  📁 Categories: {categories_count}")
        print(f"  📝 Templates: {templates_count}")
        
    finally:
        db.close()

def create_summary():
    """สรุปผลการตรวจสอบ"""
    print("\n" + "="*60)
    print("📊 สรุปผล Phase 1.3:")
    print("="*60)
    
    # ตรวจสอบทุกอย่าง
    db_ok = check_database_structure()
    cat_count = check_existing_categories()
    temp_count = check_existing_templates()
    check_database_stats()
    
    print("\n🎯 สถานะ:")
    if db_ok and cat_count > 0 and temp_count > 0:
        print("✅ Database พร้อมใช้งาน มี Categories และ Templates แล้ว!")
        print("💡 ไม่จำเป็นต้องสร้างใหม่ สามารถใช้งานได้เลย")
    elif db_ok and cat_count == 0:
        print("⚠️ Database พร้อม แต่ยังไม่มี Categories")
        print("💡 ควรรัน: python init_hr_templates.py")
    else:
        print("❌ ต้องสร้าง Database ใหม่")
        print("💡 รัน: python init_db.py")

if __name__ == "__main__":
    create_summary()
    print("\n✅ Phase 1.3 - การตรวจสอบเสร็จสมบูรณ์!")
