# LINE Agent LangChain - คู่มือการใช้งาน

## 🚀 วิธี Run ระบบ (Port 8000)

### วิธีที่ 1: Run ทั้งหมดพร้อมกัน (แนะนำ)
```batch
run_all_8000.bat
```
หรือ
```batch
run_all.bat
```

### วิธีที่ 2: Run แยกกัน
**Terminal 1 - Backend:**
```batch
run_backend_fixed.bat
```

**Terminal 2 - Frontend:**
```batch
run_frontend.bat
```

## 🔗 การเข้าใช้งาน

- **Frontend (Admin Panel)**: http://localhost:5173
- **Backend API Docs**: http://localhost:8000/docs

## 🛠️ หากมีปัญหา

1. **Port 8000 ถูกใช้งาน**: 
   - ตรวจสอบด้วย `netstat -ano | findstr :8000`
   - ปิด process ที่ใช้ port นั้น

2. **Module not found**: 
   - Run `fix_dependencies.bat`
   - หรือ `troubleshoot.bat`

3. **ติดตั้ง dependencies ครั้งแรก**:
   - Run `troubleshoot.bat` ก่อน

## 📁 ไฟล์สำคัญ

- `run_all_8000.bat` - Run ทั้ง Backend และ Frontend (Port 8000)
- `run_backend_fixed.bat` - Run เฉพาะ Backend
- `run_frontend.bat` - Run เฉพาะ Frontend
- `troubleshoot.bat` - ตรวจสอบและติดตั้ง dependencies
- `fix_dependencies.bat` - แก้ไข dependencies

## 🔧 การตั้งค่า

ไฟล์ `.env` ใน backend folder มี:
- LINE_ACCESS_TOKEN และ LINE_CHANNEL_SECRET
- GEMINI_API_KEY
- DATABASE_URL
- TELEGRAM_BOT_TOKEN (optional)

---
Updated: July 26, 2025