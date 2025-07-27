"""
Phase 1.2: ตรวจสอบความพร้อมของ Environment Variables
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
import requests
from linebot import LineBotApi
from linebot.exceptions import LineBotApiError
import google.generativeai as genai

# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)

def check_env_keys():
    """ตรวจสอบว่ามี environment keys ครบหรือไม่"""
    print("🔐 Phase 1.2: ตรวจสอบ Environment Variables")
    print("="*60)
    
    required_keys = {
        "LINE_ACCESS_TOKEN": "LINE Bot Access Token",
        "LINE_CHANNEL_SECRET": "LINE Channel Secret",
        "GEMINI_API_KEY": "Google Gemini API Key"
    }
    
    optional_keys = {
        "TELEGRAM_BOT_TOKEN": "Telegram Bot Token",
        "TELEGRAM_CHAT_ID": "Telegram Chat ID",
        "DATABASE_URL": "Database URL"
    }
    
    print("\n✅ Required Keys:")
    all_required_present = True
    for key, description in required_keys.items():
        value = os.getenv(key)
        if value and not ("your_" in value or "_here" in value):
            print(f"  ✅ {key}: มีค่าแล้ว ({description})")
        else:
            print(f"  ❌ {key}: ยังไม่มีค่าหรือเป็น placeholder")
            all_required_present = False
    
    print("\n📌 Optional Keys:")
    for key, description in optional_keys.items():
        value = os.getenv(key)
        if value and not ("your_" in value or "_here" in value):
            print(f"  ✅ {key}: มีค่าแล้ว ({description})")
        else:
            print(f"  ⚪ {key}: ไม่มีค่า (optional)")
    
    return all_required_present

def test_line_api():
    """ทดสอบ LINE API"""
    print("\n🔧 ทดสอบ LINE API:")
    try:
        line_bot_api = LineBotApi(os.getenv('LINE_ACCESS_TOKEN'))
        # ทดสอบดึงข้อมูล bot
        bot_info = line_bot_api.get_bot_info()
        print(f"  ✅ LINE API ทำงานปกติ")
        print(f"  📌 Bot Name: {bot_info.display_name}")
        print(f"  📌 Bot ID: {bot_info.user_id}")
        return True
    except LineBotApiError as e:
        print(f"  ❌ LINE API Error: {e.message}")
        return False
    except Exception as e:
        print(f"  ❌ Error: {str(e)}")
        return False

def test_gemini_api():
    """ทดสอบ Gemini API"""
    print("\n🔧 ทดสอบ Google Gemini API:")
    try:
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        model = genai.GenerativeModel(os.getenv('GEMINI_MODEL', 'gemini-2.5-flash'))
        
        # ทดสอบ generate content
        response = model.generate_content("สวัสดี ตอบสั้นๆ")
        if response.text:
            print(f"  ✅ Gemini API ทำงานปกติ")
            print(f"  📌 Test Response: {response.text[:50]}...")
            return True
    except Exception as e:
        print(f"  ❌ Gemini API Error: {str(e)}")
        return False

def check_database():
    """ตรวจสอบ Database"""
    print("\n🔧 ตรวจสอบ Database:")
    db_path = os.path.join(os.path.dirname(__file__), 'line_agent.db')
    if os.path.exists(db_path):
        print(f"  ✅ Database file exists: {db_path}")
        file_size = os.path.getsize(db_path) / 1024  # KB
        print(f"  📌 Size: {file_size:.2f} KB")
        return True
    else:
        print(f"  ⚠️ Database file not found")
        return False

def create_summary():
    """สรุปผลการตรวจสอบ"""
    print("\n" + "="*60)
    print("📊 สรุปผล Phase 1.2:")
    print("="*60)
    
    results = {
        "env_keys": check_env_keys(),
        "line_api": test_line_api(),
        "gemini_api": test_gemini_api(),
        "database": check_database()
    }
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n✅ ทุกอย่างพร้อมใช้งาน!")
        print("💡 สามารถดำเนินการ Phase 1.3 ต่อได้")
    else:
        print("\n⚠️ มีบางส่วนที่ต้องแก้ไข:")
        for key, status in results.items():
            if not status:
                print(f"  - {key}")
        print("\n💡 แก้ไขปัญหาแล้วรัน script นี้อีกครั้ง")

if __name__ == "__main__":
    create_summary()
    print("\n✅ Phase 1.2 - การตรวจสอบเสร็จสมบูรณ์!")
