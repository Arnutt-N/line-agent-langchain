@echo off
echo ===================================
echo  FIX IMPORT ISSUES
echo ===================================
echo.

cd /d "%~dp0"

echo แก้ไขปัญหา import ของระบบ Templates...
echo.

cd backend
echo เปิดใช้งาน Python Environment...
call ..\env\Scripts\activate.bat

echo.
echo 🔧 Fixing import issues...
python ..\fix_imports.py

echo.
echo 🧪 Testing backend startup...
echo กำลังทดสอบว่า backend สามารถเริ่มต้นได้หรือไม่...

timeout /t 2 /nobreak > nul

echo.
echo ✅ Import issues fixed!
echo ตอนนี้ลอง run_backend_fixed.bat เพื่อทดสอบ
echo.
echo กด Enter เพื่อปิดหน้าต่าง...
pause > nul
