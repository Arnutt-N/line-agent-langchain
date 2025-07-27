@echo off
echo ===================================
echo  ADD PURE TEXT TEMPLATES
echo ===================================
echo.

cd /d "%~dp0"

echo เพิ่ม Pure Text Templates (ไม่มี Quick Reply)...
echo.

cd backend
echo เปิดใช้งาน Python Environment...
call ..\env\Scripts\activate.bat

echo.
echo 📝 Adding pure text templates...
python ..\add_pure_text_templates.py

echo.
echo ✅ เพิ่ม Pure Text Templates เสร็จแล้ว!
echo.
echo กด Enter เพื่อปิดหน้าต่าง...
pause > nul
