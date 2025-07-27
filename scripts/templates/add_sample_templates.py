#!/usr/bin/env python3
"""
Sample Templates Data
ข้อมูลตัวอย่าง Message Templates
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.database import SessionLocal
from backend.app.template_crud import create_message_template, get_message_categories
from backend.app.schemas import MessageTemplateCreate

def add_sample_templates():
    """เพิ่ม sample templates"""
    db = SessionLocal()
    
    # Get categories
    categories = get_message_categories(db)
    category_map = {cat.name: cat.id for cat in categories}
    
    sample_templates = [
        # Text Messages
        {
            "name": "Welcome Message",
            "description": "ข้อความต้อนรับสำหรับผู้ใช้ใหม่",
            "message_type": "text",
            "category_id": category_map.get("Greeting"),
            "content": {
                "text": "สวัสดีครับ! ยินดีต้อนรับสู่บริการของเรา 🎉\n\nหากต้องการความช่วยเหลือ กรุณาพิมพ์ 'help' ได้เลยครับ",
                "quick_reply": {
                    "items": [
                        {"action": {"type": "message", "label": "Help", "text": "help"}},
                        {"action": {"type": "message", "label": "Services", "text": "services"}},
                        {"action": {"type": "message", "label": "Contact", "text": "contact"}}
                    ]
                }
            },
            "priority": 10,
            "tags": "welcome, greeting, new user"
        },
        
        # Sticker Messages
        {
            "name": "Happy Sticker",
            "description": "สติกเกอร์แสดงความยินดี",
            "message_type": "sticker",
            "category_id": category_map.get("Entertainment"),
            "content": {
                "package_id": "11537",
                "sticker_id": "52002734"
            },
            "priority": 5,
            "tags": "happy, celebration, emotion"
        },
        
        # Information Message
        {
            "name": "Business Hours",
            "description": "ข้อมูลเวลาทำการ",
            "message_type": "text",
            "category_id": category_map.get("Information"),
            "content": {
                "text": "⏰ เวลาทำการของเรา\n\n📅 จันทร์ - ศุกร์: 09:00 - 18:00\n📅 เสาร์ - อาทิตย์: 10:00 - 16:00\n\n📞 สามารถติดต่อสอบถามได้ตลอด 24 ชั่วโมง"
            },
            "priority": 8,
            "tags": "hours, time, information, contact"
        },
        
        # Support Message
        {
            "name": "How Can I Help",
            "description": "ข้อความสอบถามความต้องการ",
            "message_type": "text",
            "category_id": category_map.get("Support"),
            "content": {
                "text": "มีอะไรให้ช่วยเหลือไหมครับ? 🤔\n\nสามารถเลือกหัวข้อที่สนใจได้เลยครับ",
                "quick_reply": {
                    "items": [
                        {"action": {"type": "message", "label": "📋 Services", "text": "show services"}},
                        {"action": {"type": "message", "label": "💰 Pricing", "text": "show pricing"}},
                        {"action": {"type": "message", "label": "📞 Contact", "text": "contact info"}},
                        {"action": {"type": "message", "label": "❓ FAQ", "text": "faq"}}
                    ]
                }
            },
            "priority": 9,
            "tags": "help, support, assistance, menu"
        }
    ]
    
    print("📝 Adding sample templates...")
    
    for template_data in sample_templates:
        try:
            template = MessageTemplateCreate(**template_data)
            created = create_message_template(db, template)
            print(f"✅ Created template: {template_data['name']}")
        except Exception as e:
            print(f"❌ Failed to create template {template_data['name']}: {e}")
    
    db.close()
    print("✅ Sample templates added!")

if __name__ == "__main__":
    print("📨 Adding Sample Message Templates")
    print("=" * 50)
    add_sample_templates()
