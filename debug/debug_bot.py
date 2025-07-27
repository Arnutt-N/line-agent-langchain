#!/usr/bin/env python3
"""
Debug และตรวจสอบสถานะของ LINE Bot
"""

import requests
import os
from dotenv import load_dotenv
import sqlite3

load_dotenv('backend/.env')

def check_database():
    """ตรวจสอบฐานข้อมูล"""
    print("🔍 ตรวจสอบฐานข้อมูล...")
    
    db_path = "backend/line_agent.db"
    if not os.path.exists(db_path):
        print(f"❌ ฐานข้อมูลไม่พบ: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check users
    cursor.execute("SELECT line_id, name, mode, blocked_at FROM line_users")
    users = cursor.fetchall()
    
    print(f"📊 ผู้ใช้ทั้งหมด: {len(users)} คน")
    for user in users:
        line_id, name, mode, blocked_at = user
        status = "❌ Blocked" if blocked_at else "✅ Active"
        print(f"  - {name} ({line_id}): {mode} mode - {status}")
    
    # Check recent messages
    cursor.execute("SELECT line_user_id, message, is_from_user, created_at FROM chat_messages ORDER BY created_at DESC LIMIT 5")
    messages = cursor.fetchall()
    
    print(f"\n💬 ข้อความล่าสุด {len(messages)} ข้อความ:")
    for msg in messages:
        user_id, message, is_from_user, created_at = msg
        sender = "User" if is_from_user else "Bot"
        print(f"  - {sender} ({user_id}): {message[:50]}... ({created_at})")
    
    conn.close()

def test_api():
    """ทดสอบ API endpoints"""
    print("\n🌐 ทดสอบ API endpoints...")
    
    base_url = "http://localhost:8000"
    
    # Test health
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health check: OK")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        return False
    
    # Test users endpoint
    try:
        response = requests.get(f"{base_url}/api/users")
        if response.status_code == 200:
            users = response.json()
            print(f"✅ Users API: {len(users)} users found")
            
            # Test mode change for first user if exists
            if users:
                test_user = users[0]
                user_id = test_user['line_id']
                current_mode = test_user['mode']
                new_mode = 'manual' if current_mode == 'bot' else 'bot'
                
                print(f"🔄 Testing mode change for {user_id}: {current_mode} → {new_mode}")
                
                mode_response = requests.post(f"{base_url}/api/mode/{user_id}?mode={new_mode}")
                if mode_response.status_code == 200:
                    result = mode_response.json()
                    print(f"✅ Mode change successful: {result}")
                    
                    # Change back
                    requests.post(f"{base_url}/api/mode/{user_id}?mode={current_mode}")
                    print(f"🔄 Reverted mode back to {current_mode}")
                else:
                    print(f"❌ Mode change failed: {mode_response.status_code} - {mode_response.text}")
        else:
            print(f"❌ Users API failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Users API error: {e}")
    
    return True

def check_env():
    """ตรวจสอบการตั้งค่า environment"""
    print("\n⚙️ ตรวจสอบการตั้งค่า...")
    
    required_vars = [
        'LINE_ACCESS_TOKEN',
        'LINE_CHANNEL_SECRET', 
        'GEMINI_API_KEY'
    ]
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {value[:10]}...{value[-10:] if len(value) > 20 else ''}")
        else:
            print(f"❌ {var}: ไม่พบ")

if __name__ == "__main__":
    print("🔧 LINE Bot Debug Tool")
    print("=" * 50)
    
    check_env()
    check_database()
    
    if test_api():
        print("\n🎉 การทดสอบเสร็จสิ้น!")
    else:
        print("\n❌ กรุณาเริ่มต้น API server ก่อน (run_backend_fixed.bat)")
    
    print("\n💡 Tips:")
    print("- หากบอทไม่ตอบ ลองเปลี่ยนโหมดเป็น 'bot' ใน Admin Panel")
    print("- ตรวจสอบ WebSocket connection ใน Browser Developer Tools")
    print("- ดู log ใน terminal ที่รัน backend")
