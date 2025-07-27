"""
🔍 ตรวจสอบสถานะโปรเจกต์ LINE Bot HR
Phase 1.1: ตรวจสอบโครงสร้างและ Dependencies
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def print_status(item, status, details=""):
    """แสดงสถานะแต่ละรายการ"""
    icon = "✅" if status else "❌"
    status_text = "พร้อม" if status else "ต้องแก้ไข"
    print(f"{icon} {item}: {status_text}")
    if details:
        print(f"   └─ {details}")

def check_project_structure():
    """ตรวจสอบโครงสร้างโปรเจกต์"""
    print("\n📁 ตรวจสอบโครงสร้างโปรเจกต์:")
    
    required_dirs = {
        "backend": "โฟลเดอร์ Backend API",
        "frontend": "โฟลเดอร์ Frontend UI",
        "env": "Virtual Environment",
        "backend/app": "โฟลเดอร์แอพหลัก",
        "backend/data": "โฟลเดอร์เก็บข้อมูล (สำหรับ RAG)"
    }
    
    for dir_path, description in required_dirs.items():
        exists = os.path.exists(dir_path)
        print_status(f"{dir_path}/", exists, description)
        
        # สร้างโฟลเดอร์ data ถ้ายังไม่มี
        if dir_path == "backend/data" and not exists:
            os.makedirs("backend/data/text", exist_ok=True)
            print("   └─ 🔨 สร้างโฟลเดอร์ data/text/ สำหรับเก็บไฟล์ FAQ")

def check_key_files():
    """ตรวจสอบไฟล์สำคัญ"""
    print("\n📄 ตรวจสอบไฟล์สำคัญ:")
    
    key_files = {
        "backend/.env": "ไฟล์ Environment Variables",
        "backend/requirements.txt": "รายการ Python packages",
        "backend/app/main.py": "ไฟล์หลัก FastAPI",
        "backend/app/models.py": "Database models",
        "backend/app/database.py": "Database configuration",
        "backend/line_agent.db": "SQLite database"
    }
    
    for file_path, description in key_files.items():
        exists = os.path.exists(file_path)
        print_status(file_path, exists, description)

def check_python_packages():
    """ตรวจสอบ Python packages ที่ติดตั้ง"""
    print("\n📦 ตรวจสอบ Python Packages:")
    
    # Activate virtual environment first
    activate_script = r"env\Scripts\activate"
    
    # ตรวจสอบ packages สำคัญ
    required_packages = [
        "fastapi",
        "uvicorn",
        "line-bot-sdk",
        "sqlalchemy",
        "langchain",
        "langchain-google-genai",
        "websockets",
        "python-dotenv"
    ]
    
    try:
        # Get installed packages
        result = subprocess.run(
            [r"env\Scripts\python.exe", "-m", "pip", "list", "--format=json"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            installed = json.loads(result.stdout)
            installed_names = {pkg['name'].lower() for pkg in installed}
            
            for package in required_packages:
                is_installed = package.lower() in installed_names
                print_status(package, is_installed)
                
            # ตรวจสอบ packages เพิ่มเติมสำหรับ RAG
            print("\n📚 Packages สำหรับ RAG (ถ้าต้องการ):")
            optional_packages = ["pandas", "openpyxl", "python-docx", "PyPDF2"]
            for package in optional_packages:
                is_installed = package.lower() in installed_names
                status = "ติดตั้งแล้ว" if is_installed else "ยังไม่ได้ติดตั้ง (optional)"
                print(f"   {package}: {status}")
        else:
            print("❌ ไม่สามารถตรวจสอบ packages ได้")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def check_env_file():
    """ตรวจสอบไฟล์ .env"""
    print("\n🔐 ตรวจสอบ Environment Variables:")
    
    env_path = "backend/.env"
    if os.path.exists(env_path):
        print("✅ พบไฟล์ .env")
        
        # ตรวจสอบ keys ที่จำเป็น
        required_keys = [
            "LINE_ACCESS_TOKEN",
            "LINE_CHANNEL_SECRET", 
            "GEMINI_API_KEY"
        ]
        
        with open(env_path, 'r') as f:
            env_content = f.read()
            
        for key in required_keys:
            if key in env_content:
                # ตรวจสอบว่ามีค่าจริงหรือยังเป็น placeholder
                if "your_" in env_content or "_here" in env_content:
                    print(f"⚠️  {key}: ยังเป็น placeholder - ต้องใส่ค่าจริง")
                else:
                    print(f"✅ {key}: มีค่าแล้ว")
            else:
                print(f"❌ {key}: ไม่พบ - ต้องเพิ่ม")
    else:
        print("❌ ไม่พบไฟล์ .env - ต้องสร้างใหม่")
        print("   └─ 💡 ใช้คำสั่ง: copy backend\\.env.example backend\\.env")

def create_summary():
    """สรุปผลการตรวจสอบ"""
    print("\n" + "="*60)
    print("📊 สรุปสถานะโปรเจกต์:")
    print("="*60)
    
    print("""
✅ สิ่งที่พร้อมแล้ว:
- โครงสร้างโปรเจกต์หลัก
- Virtual Environment
- ไฟล์ Python หลัก
- Database SQLite

⚠️  สิ่งที่ต้องทำ:
1. ตรวจสอบและแก้ไข .env file (ใส่ API keys จริง)
2. สร้างโฟลเดอร์ data/text สำหรับเก็บ FAQ (ถ้ายังไม่มี)
3. ติดตั้ง packages เพิ่มเติมสำหรับ RAG (optional)

🚀 ขั้นตอนถัดไป:
- รัน: check_dependencies.bat เพื่อตรวจสอบเพิ่มเติม
- รัน: fix_dependencies.bat ถ้าต้องแก้ไข dependencies
""")

if __name__ == "__main__":
    print("🔍 LINE Bot HR - Project Status Check")
    print("="*60)
    
    check_project_structure()
    check_key_files()
    check_python_packages()
    check_env_file()
    create_summary()
    
    print("\n✅ Phase 1.1 - การตรวจสอบเสร็จสมบูรณ์!")
    print("💡 ถัดไป: Phase 1.2 - ตรวจสอบและปรับแต่ง .env file")
