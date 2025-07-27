#!/usr/bin/env python3
"""
Test Message Templates System
ทดสอบระบบ Message Templates
"""

import requests
import json

def test_templates_api():
    """ทดสอบ Templates API"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Message Templates API...")
    
    # Test categories
    print("\n📁 Testing Categories...")
    try:
        response = requests.get(f"{base_url}/api/categories")
        if response.status_code == 200:
            categories = response.json()
            print(f"✅ Found {len(categories)} categories")
            for cat in categories:
                print(f"  - {cat['name']}: {cat['description']}")
        else:
            print(f"❌ Categories API failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Categories API error: {e}")
    
    # Test templates
    print("\n📨 Testing Templates...")
    try:
        response = requests.get(f"{base_url}/api/templates")
        if response.status_code == 200:
            templates = response.json()
            print(f"✅ Found {len(templates)} templates")
            for template in templates:
                print(f"  - {template['name']} ({template['message_type']}): Priority {template['priority']}")
        else:
            print(f"❌ Templates API failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Templates API error: {e}")
    
    # Test template selection
    print("\n🎯 Testing Template Selection...")
    try:
        selection_request = {
            "context": "user greeting",
            "user_message": "สวัสดี",
            "category": None,
            "message_type": None,
            "tags": ["greeting"]
        }
        
        response = requests.post(f"{base_url}/api/templates/select", json=selection_request)
        if response.status_code == 200:
            result = response.json()
            if result.get("template"):
                template = result["template"]
                print(f"✅ Selected template: {template['name']}")
                print(f"   Content: {json.dumps(template['content'], ensure_ascii=False, indent=2)}")
            else:
                print("⚠️ No template selected")
        else:
            print(f"❌ Template selection failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Template selection error: {e}")

def test_database():
    """ทดสอบฐานข้อมูล"""
    import sqlite3
    import os
    
    print("\n🗃️ Testing Database...")
    
    db_path = "backend/line_agent.db"
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check tables
    tables = ["message_categories", "message_templates", "template_usage_logs"]
    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"✅ Table {table}: {count} records")
        except Exception as e:
            print(f"❌ Table {table}: {e}")
    
    conn.close()

if __name__ == "__main__":
    print("🧪 MESSAGE TEMPLATES SYSTEM TESTING")
    print("=" * 50)
    
    test_database()
    test_templates_api()
    
    print("\n🎉 Testing completed!")
    print("\n💡 Tips:")
    print("- กรุณาตรวจสอบว่า backend server กำลังทำงานอยู่")
    print("- รัน setup_templates.bat หาก database ยังไม่พร้อม")
    print("- เปิด http://localhost:5173/templates.html เพื่อจัดการ templates")
