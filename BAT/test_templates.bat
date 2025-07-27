@echo off
echo ===================================
echo  TEST MESSAGE TEMPLATES SYSTEM
echo ===================================
echo.

cd /d "%~dp0"

echo เริ่มต้นทดสอบระบบ Message Templates...
echo.

cd backend
echo เปิดใช้งาน Python Environment...
call ..\env\Scripts\activate.bat

echo.
echo 🧪 ทำการทดสอบระบบ...
python ..\test_templates.py

echo.
echo กด Enter เพื่อปิดหน้าต่าง...
pause > nul
