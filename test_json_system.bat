@echo off
chcp 65001 > nul
echo 🧪 ทดสอบระบบค้นหา JSON ใหม่
echo ================================

cd /d "D:\genAI\line-agent-langchain"

echo 📍 ตำแหน่งปัจจุบัน: %CD%

echo.
echo 🐍 ตรวจสอบ Python environment...
python --version

echo.
echo 📦 ตรวจสอบ dependencies...
pip show fastapi langchain langchain-google-genai > nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Dependencies พร้อมใช้งาน
) else (
    echo ⚠️ กำลังติดตั้ง dependencies...
    pip install -r backend\requirements.txt
)

echo.
echo 🧪 รันการทดสอบระบบ JSON...
python test_json_search.py

echo.
echo 🔄 หากต้องการรันระบบจริง กด Enter...
pause > nul

echo.
echo 🚀 เริ่มระบบ LINE Bot...
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause
