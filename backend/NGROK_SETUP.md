# Setup ngrok สำหรับ Testing LINE Bot ในเครื่อง Local

## 1. ติดตั้ง ngrok

### วิธีที่ 1: ดาวน์โหลดจาก website
1. ไปที่ https://ngrok.com/download
2. ดาวน์โหลด ngrok สำหรับ Windows
3. แตกไฟล์ zip และวาง ngrok.exe ไว้ใน folder ที่ต้องการ

### วิธีที่ 2: ใช้ Chocolatey (ถ้ามี)
```powershell
choco install ngrok
```

### วิธีที่ 3: ใช้ winget
```powershell
winget install ngrok.ngrok
```

## 2. สมัครบัญชี ngrok (ฟรี)
1. ไปที่ https://dashboard.ngrok.com/signup
2. สมัครบัญชี
3. ไปที่ https://dashboard.ngrok.com/get-started/your-authtoken
4. คัดลอก authtoken

## 3. ตั้งค่า authtoken
```bash
ngrok config add-authtoken YOUR_AUTH_TOKEN_HERE
```

## 4. รัน Backend ของคุณ
```bash
cd D:\genAI\line-agent-langchain\backend
python -m uvicorn app.main:app --reload --port 8000
```

## 5. รัน ngrok
เปิด terminal ใหม่แล้วรัน:
```bash
ngrok http 8000
```

## 6. ตั้งค่า LINE Webhook
1. คัดลอก URL จาก ngrok (เช่น https://abcd-1234.ngrok.io)
2. ไปที่ LINE Developers Console
3. เลือก channel ของคุณ
4. ในส่วน Messaging API > Webhook settings
5. ใส่ Webhook URL: https://abcd-1234.ngrok.io/webhook
6. เปิด "Use webhook"
7. คลิก "Verify" เพื่อทดสอบ

## 7. ทดสอบ
- เพิ่มบอทเป็นเพื่อนใน LINE
- ส่งข้อความทดสอบ
- ดู logs ใน terminal ที่รัน backend

## หมายเหตุ
- URL ของ ngrok จะเปลี่ยนทุกครั้งที่รันใหม่ (ถ้าใช้แบบฟรี)
- ต้องอัพเดท Webhook URL ใน LINE Developers Console ทุกครั้ง
- สามารถดู requests ที่เข้ามาได้ที่ http://localhost:4040

## Scripts สำหรับรันอัตโนมัติ

### start_local_test.bat
```batch
@echo off
echo Starting LINE Bot Backend...
start cmd /k "cd /d D:\genAI\line-agent-langchain\backend && python -m uvicorn app.main:app --reload --port 8000"

echo.
echo Waiting for backend to start...
timeout /t 5

echo.
echo Starting ngrok...
start cmd /k "ngrok http 8000"

echo.
echo ================================
echo LINE Bot is starting...
echo ================================
echo.
echo 1. Wait for ngrok to start
echo 2. Copy the https URL from ngrok
echo 3. Update webhook URL in LINE Developers Console
echo 4. Your webhook URL will be: https://[ngrok-url]/webhook
echo.
echo ngrok dashboard: http://localhost:4040
echo.
pause
```

### stop_local_test.bat
```batch
@echo off
taskkill /F /IM ngrok.exe 2>nul
taskkill /F /IM python.exe 2>nul
echo All processes stopped.
pause
```
