# คู่มือทดสอบ LINE Bot ในเครื่อง Local ด้วย ngrok

## สิ่งที่แก้ไขแล้ว ✅
1. **แก้ไขปัญหา Supabase**: Downgrade จาก version 2.3.0 เป็น 1.2.0
2. **Backend ทำงานได้สมบูรณ์**: ตอนนี้ backend รันได้ที่ http://localhost:8000

## ขั้นตอนการทดสอบ

### 1. ติดตั้ง ngrok (ถ้ายังไม่มี)
```bash
# วิธีที่ 1: ดาวน์โหลดจาก https://ngrok.com/download
# วิธีที่ 2: ใช้ winget
winget install ngrok.ngrok
# วิธีที่ 3: ใช้ Chocolatey
choco install ngrok
```

### 2. ตั้งค่า ngrok authtoken
1. สมัครบัญชีฟรีที่ https://dashboard.ngrok.com/signup
2. คัดลอก authtoken จาก https://dashboard.ngrok.com/get-started/your-authtoken
3. รันคำสั่ง:
```bash
ngrok config add-authtoken YOUR_AUTH_TOKEN_HERE
```

### 3. รัน Backend (ถ้ายังไม่ได้รัน)
```bash
# เปิด terminal แรก
cd D:\genAI\line-agent-langchain\backend
D:\genAI\line-agent-langchain\env\Scripts\python -m uvicorn app.main:app --reload --port 8000
```

### 4. รัน ngrok
```bash
# เปิด terminal ที่สอง
ngrok http 8000
```

### 5. ตั้งค่า LINE Webhook
1. คัดลอก URL จาก ngrok (เช่น `https://abcd-1234.ngrok-free.app`)
2. ไปที่ [LINE Developers Console](https://developers.line.biz/console/)
3. เลือก Channel ของคุณ
4. ไปที่ **Messaging API > Webhook settings**
5. ใส่ Webhook URL: `https://abcd-1234.ngrok-free.app/webhook`
6. เปิด **Use webhook**
7. คลิก **Verify** เพื่อทดสอบการเชื่อมต่อ

### 6. ทดสอบ Bot
1. เพิ่มบอทเป็นเพื่อนใน LINE
2. ส่งข้อความทดสอบ เช่น "สวัสดี"
3. ดู logs ใน terminal ที่รัน backend
4. ดู requests ที่ http://localhost:4040 (ngrok dashboard)

## Scripts สำหรับรันอัตโนมัติ

### start_test.bat
```batch
@echo off
echo Starting LINE Bot Testing Environment...

REM Start Backend
start "Backend" cmd /k "cd /d D:\genAI\line-agent-langchain\backend && D:\genAI\line-agent-langchain\env\Scripts\python -m uvicorn app.main:app --reload --port 8000"

timeout /t 5

REM Start ngrok
start "ngrok" cmd /k "ngrok http 8000"

echo.
echo ========================================
echo LINE Bot Testing Started!
echo ========================================
echo 1. Backend: http://localhost:8000
echo 2. API Docs: http://localhost:8000/docs
echo 3. ngrok Dashboard: http://localhost:4040
echo.
echo Next: Copy ngrok URL and update LINE webhook
echo ========================================
pause
```

### stop_test.bat
```batch
@echo off
taskkill /F /IM ngrok.exe 2>nul
taskkill /F /IM python.exe 2>nul
echo All processes stopped.
pause
```

## URL ที่สำคัญ
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **ngrok Dashboard**: http://localhost:4040
- **Admin Panel**: http://localhost:5173 (ถ้ารัน frontend)

## Troubleshooting

### ปัญหาที่พบบ่อย:
1. **"No module named 'app'"**: ตรวจสอบว่าอยู่ใน directory `backend` ก่อนรัน uvicorn
2. **"Supabase proxy error"**: ใช้ supabase version 1.2.0 แทน
3. **"LINE webhook verification failed"**: ตรวจสอบว่า backend รันอยู่และ ngrok URL ถูกต้อง

### Debug Tips:
- ดู logs ใน terminal ที่รัน backend
- ตรวจสอบ requests ที่ http://localhost:4040
- ดู health check ที่ http://localhost:8000/health

## หมายเหตุ
- URL ของ ngrok จะเปลี่ยนทุกครั้งที่รันใหม่ (แบบฟรี)
- ต้องอัพเดท Webhook URL ใน LINE Console ทุกครั้ง
- สามารถใช้ ngrok paid plan เพื่อ URL คงที่

---
พร้อมทดสอบ LINE Bot ของคุณแล้ว! 🚀
