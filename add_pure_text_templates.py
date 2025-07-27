#!/usr/bin/env python3
"""
Add Pure Text Message Templates
เพิ่ม Templates สำหรับข้อความธรรมดา (ไม่มี Quick Reply)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.database import SessionLocal
from backend.app.template_crud import create_message_template, get_message_categories
from backend.app.schemas import MessageTemplateCreate

def add_pure_text_templates():
    """เพิ่ม Pure Text Templates"""
    db = SessionLocal()
    
    # Get categories
    categories = get_message_categories(db)
    category_map = {cat.name: cat.id for cat in categories}
    
    pure_text_templates = [
        # Simple Greetings
        {
            "name": "Simple Hello",
            "description": "การทักทายแบบเรียบง่าย",
            "message_type": "text",
            "category_id": category_map.get("Greeting"),
            "content": {
                "text": "สวัสดีครับ! 😊"
            },
            "priority": 7,
            "tags": "hello, simple, greeting"
        },
        
        # Thank You Messages
        {
            "name": "Thank You",
            "description": "ขอบคุณแบบสั้น ๆ",
            "message_type": "text",
            "category_id": category_map.get("Support"),
            "content": {
                "text": "ขอบคุณสำหรับการติดต่อครับ! 🙏"
            },
            "priority": 6,
            "tags": "thanks, gratitude, appreciation"
        },
        
        # Confirmation Messages
        {
            "name": "Received Confirmation",
            "description": "ยืนยันการรับข้อความ",
            "message_type": "text",
            "category_id": category_map.get("Support"),
            "content": {
                "text": "ได้รับข้อความของคุณแล้วครับ กำลังดำเนินการตรวจสอบ..."
            },
            "priority": 8,
            "tags": "confirmation, received, processing"
        },
        
        # Apology Messages
        {
            "name": "Simple Apology",
            "description": "ขอโทษแบบเรียบง่าย",
            "message_type": "text",
            "category_id": category_map.get("Support"),
            "content": {
                "text": "ขออภัยในความไม่สะดวกครับ 🙏"
            },
            "priority": 7,
            "tags": "sorry, apology, inconvenience"
        },
        
        # Waiting Messages
        {
            "name": "Please Wait",
            "description": "ข้อความให้รอสักครู่",
            "message_type": "text",
            "category_id": category_map.get("Information"),
            "content": {
                "text": "กรุณารอสักครู่นะครับ กำลังดำเนินการให้... ⏳"
            },
            "priority": 8,
            "tags": "wait, processing, loading"
        },
        
        # Completion Messages
        {
            "name": "Task Complete",
            "description": "แจ้งเสร็จสิ้นงาน",
            "message_type": "text",
            "category_id": category_map.get("Information"),
            "content": {
                "text": "เสร็จสิ้นแล้วครับ! ✅"
            },
            "priority": 6,
            "tags": "complete, done, finished"
        },
        
        # Error Messages
        {
            "name": "Simple Error",
            "description": "ข้อความแจ้งข้อผิดพลาดแบบสั้น",
            "message_type": "text",
            "category_id": category_map.get("Emergency"),
            "content": {
                "text": "เกิดข้อผิดพลาดครับ กรุณาลองใหม่อีกครั้ง ❌"
            },
            "priority": 9,
            "tags": "error, problem, retry"
        },
        
        # Good Bye Messages
        {
            "name": "Simple Goodbye",
            "description": "การอำลาแบบเรียบง่าย",
            "message_type": "text",
            "category_id": category_map.get("Greeting"),
            "content": {
                "text": "ขอบคุณครับ! หวังว่าจะได้พูดคุยกันอีก 👋"
            },
            "priority": 5,
            "tags": "goodbye, farewell, thanks"
        }
    ]
    
    print("📝 Adding Pure Text Templates...")
    
    for template_data in pure_text_templates:
        try:
            template = MessageTemplateCreate(**template_data)
            created = create_message_template(db, template)
            print(f"✅ Created pure text template: {template_data['name']}")
        except Exception as e:
            print(f"❌ Failed to create template {template_data['name']}: {e}")
    
    db.close()
    print("✅ Pure text templates added!")

if __name__ == "__main__":
    print("📨 Adding Pure Text Message Templates")
    print("=" * 50)
    add_pure_text_templates()
