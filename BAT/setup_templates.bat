@echo off
echo ===================================
echo  MESSAGE TEMPLATES MIGRATION
echo ===================================
echo.

cd /d "%~dp0"

echo เริ่มต้น Database Migration สำหรับ Message Templates...
echo.

cd backend
echo เปิดใช้งาน Python Environment...
call ..\env\Scripts\activate.bat

echo.
echo 🗃️ Creating Message Templates tables...
python ..\migrate_templates.py

echo.
echo 📝 Adding sample templates...
python ..\add_sample_templates.py

echo.
echo ✅ Migration เสร็จสิ้น!
echo.
echo กด Enter เพื่อปิดหน้าต่าง...
pause > nul
