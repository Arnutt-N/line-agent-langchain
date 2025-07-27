# 🔧 Batch Files

โฟลเดอร์นี้เก็บไฟล์ batch scripts ทั้งหมดของโปรเจกต์

## 📂 หมวดหมู่

### 🚀 Main Runners
- `run_all.bat` - รันระบบทั้งหมด
- `run_backend.bat` - รัน backend server
- `run_frontend.bat` - รัน frontend server
- `START.bat` - เริ่มระบบ
- `RESTART_ALL.bat` - รีสตาร์ทระบบ
- `CLEAN_START.bat` - เริ่มใหม่แบบ clean

### 🧪 Testing
- `test_backend.bat` - ทดสอบ backend
- `test_loading.bat` - ทดสอบ loading animation
- `test_templates.bat` - ทดสอบ templates
- `test_phase16.bat` - ทดสอบ phase 1.6

### 🔧 Utilities
- `check_dependencies.bat` - ตรวจสอบ dependencies
- `fix_dependencies.bat` - แก้ไข dependencies
- `troubleshoot.bat` - แก้ปัญหาระบบ
- `setup_templates.bat` - ติดตั้ง templates

### 📝 Phase Scripts
- `phase_1_1_check.bat` ถึง `phase_1_3_summary.bat`

## ⚠️ หมายเหตุสำคัญ
ไฟล์ batch บางไฟล์อาจต้องแก้ไข path หลังจากย้ายมาที่โฟลเดอร์นี้
โดยเฉพาะไฟล์ที่เรียกใช้ไฟล์ batch อื่นๆ

## 💡 วิธีใช้
เรียกใช้จาก root directory:
```
BAT\ชื่อไฟล์.bat
```
