"""
Quick Test - ตรวจสอบระบบพื้นฐาน
"""
import sqlite3
import os
import json
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def test_database():
    """ตรวจสอบ Database"""
    print("1. ตรวจสอบ Database")
    print("-" * 40)
    
    db_path = "line_agent.db"
    if os.path.exists(db_path):
        print(f"✅ พบไฟล์ database: {db_path}")
        
        # เชื่อมต่อและตรวจสอบข้อมูล
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # นับ categories
        cursor.execute("SELECT COUNT(*) FROM message_categories")
        cat_count = cursor.fetchone()[0]
        print(f"✅ Categories: {cat_count} หมวดหมู่")
        
        # นับ templates
        cursor.execute("SELECT COUNT(*) FROM message_templates")
        temp_count = cursor.fetchone()[0]
        print(f"✅ Templates: {temp_count} templates")
        
        # แสดง categories
        cursor.execute("SELECT name FROM message_categories")
        categories = cursor.fetchall()
        print("\nหมวดหมู่ที่มี:")
        for cat in categories:
            print(f"  - {cat[0]}")
        
        conn.close()
    else:
        print("❌ ไม่พบไฟล์ database")

def test_env_file():
    """ตรวจสอบ .env"""
    print("\n2. ตรวจสอบ Environment Variables")
    print("-" * 40)
    
    if os.path.exists(".env"):
        print("✅ พบไฟล์ .env")
        
        # อ่านและตรวจสอบ keys
        with open(".env", "r") as f:
            content = f.read()
            
        required = ["LINE_ACCESS_TOKEN", "LINE_CHANNEL_SECRET", "GEMINI_API_KEY"]
        for key in required:
            if key in content:
                print(f"✅ {key}: มี")
            else:
                print(f"❌ {key}: ไม่มี")
    else:
        print("❌ ไม่พบไฟล์ .env")

def test_data_files():
    """ตรวจสอบไฟล์ข้อมูล"""
    print("\n3. ตรวจสอบไฟล์ข้อมูล HR")
    print("-" * 40)
    
    data_files = [
        "data/text/faq_hr.txt",
        "data/text/policies_hr.txt",
        "data/text/benefits.txt"
    ]
    
    for file in data_files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"✅ {file} ({size} bytes)")
        else:
            print(f"❌ {file} - ไม่พบ")

def test_main_py():
    """ตรวจสอบ main.py"""
    print("\n4. ตรวจสอบ System Prompt")
    print("-" * 40)
    
    main_file = "app/main.py"
    if os.path.exists(main_file):
        with open(main_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        if "คุณคือผู้ช่วย HR อัจฉริยะ" in content:
            print("✅ System Prompt อัพเดทแล้ว (V2)")
        else:
            print("⚠️ System Prompt ยังเป็นเวอร์ชันเก่า")
    else:
        print("❌ ไม่พบไฟล์ main.py")

def main():
    print("🧪 Quick Test - ตรวจสอบระบบ HR Bot")
    print("="*60)
    
    test_database()
    test_env_file()
    test_data_files()
    test_main_py()
    
    print("\n" + "="*60)
    print("✅ การตรวจสอบเสร็จสิ้น")
    print("\n💡 ขั้นตอนถัดไป:")
    print("1. รัน RUN_SYSTEM.bat เพื่อเริ่มระบบ")
    print("2. เปิด http://localhost:8000 (Backend)")
    print("3. เปิด http://localhost:5173 (Frontend)")
    print("4. ทดสอบส่งข้อความผ่าน LINE")

if __name__ == "__main__":
    main()
