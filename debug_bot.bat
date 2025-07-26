@echo off
echo ===================================
echo  DEBUG LINE Bot System
echo ===================================
echo.

cd /d "%~dp0"

echo เริ่มต้น Debug...
echo.

cd backend
echo เปิดใช้งาน Python Environment...
call ..\env\Scripts\activate.bat

echo.
echo ทำการ Debug และตรวจสอบระบบ...
python ..\debug_bot.py

echo.
echo กด Enter เพื่อปิดหน้าต่าง...
pause > nul
