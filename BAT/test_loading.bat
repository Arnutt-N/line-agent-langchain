@echo off
echo ===================================
echo  TEST LINE Loading Animation
echo ===================================
echo.

cd /d "%~dp0"
cd backend

echo เปิดใช้งาน Python Environment...
call ..\env\Scripts\activate.bat

echo.
echo ทดสอบ LINE Loading Animation...
echo กรุณาใส่ LINE User ID ที่ต้องการทดสอบ
echo (สามารถหา User ID ได้จาก Admin Panel หรือ Log ของบอท)
echo.

python ..\test_loading.py

echo.
echo กด Enter เพื่อปิดหน้าต่าง...
pause > nul
