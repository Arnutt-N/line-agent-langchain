"""
Phase 1.6: ทดสอบระบบ HR Bot เบื้องต้น
"""
import os
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
LINE_WEBHOOK = f"{BASE_URL}/webhook"
API_BASE = f"{BASE_URL}/api"

def check_backend_running():
    """ตรวจสอบว่า Backend ทำงานหรือไม่"""
    print("1️⃣ ตรวจสอบ Backend Server")
    print("-" * 40)
    
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Backend server กำลังทำงาน")
            return True
        else:
            print(f"⚠️ Backend ตอบกลับ status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ ไม่สามารถเชื่อมต่อ Backend ได้")
        print("💡 กรุณารัน: RUN_SYSTEM.bat")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_api_endpoints():
    """ตรวจสอบ API Endpoints"""
    print("\n2️⃣ ตรวจสอบ API Endpoints")
    print("-" * 40)
    
    endpoints = [
        ("/api/users", "GET", "รายชื่อผู้ใช้"),
        ("/api/templates", "GET", "Templates"),
        ("/api/categories", "GET", "Categories"),
        ("/api/statistics", "GET", "สถิติ")
    ]
    
    results = []
    for endpoint, method, desc in endpoints:
        try:
            url = f"{BASE_URL}{endpoint}"
            response = requests.request(method, url)
            
            if response.status_code == 200:
                print(f"✅ {endpoint} - {desc}")
                results.append(True)
            else:
                print(f"❌ {endpoint} - Status: {response.status_code}")
                results.append(False)
        except Exception as e:
            print(f"❌ {endpoint} - Error: {str(e)[:50]}")
            results.append(False)
    
    return all(results)

def check_database_data():
    """ตรวจสอบข้อมูลใน Database"""
    print("\n3️⃣ ตรวจสอบข้อมูลใน Database")
    print("-" * 40)
    
    try:
        # ตรวจสอบ Categories
        response = requests.get(f"{API_BASE}/categories")
        if response.status_code == 200:
            categories = response.json()
            print(f"✅ Categories: {len(categories)} หมวดหมู่")
            
        # ตรวจสอบ Templates
        response = requests.get(f"{API_BASE}/templates")
        if response.status_code == 200:
            templates = response.json()
            print(f"✅ Templates: {len(templates)} templates")
            
            # นับตาม type
            types = {}
            for t in templates:
                msg_type = t.get('message_type', 'unknown')
                types[msg_type] = types.get(msg_type, 0) + 1
            
            print("   Template Types:")
            for t, count in types.items():
                print(f"   - {t}: {count}")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_webhook_simulation():
    """จำลองการส่งข้อความผ่าน webhook"""
    print("\n4️⃣ ทดสอบ Webhook (Simulation)")
    print("-" * 40)
    
    # Simulate LINE webhook payload
    test_payload = {
        "events": [
            {
                "type": "message",
                "timestamp": int(datetime.now().timestamp() * 1000),
                "source": {
                    "type": "user",
                    "userId": "TEST_USER_001"
                },
                "message": {
                    "type": "text",
                    "id": "test_msg_001",
                    "text": "สวัสดีครับ"
                }
            }
        ]
    }
    
    print("📤 ส่งข้อความทดสอบ: 'สวัสดีครับ'")
    
    try:
        # ต้องมี signature สำหรับ LINE webhook
        headers = {
            "Content-Type": "application/json",
            "X-Line-Signature": "test_signature"  # ในการทดสอบจริงต้องคำนวณ signature
        }
        
        response = requests.post(
            LINE_WEBHOOK,
            json=test_payload,
            headers=headers
        )
        
        if response.status_code == 400:
            print("⚠️ Webhook ตอบกลับ 400 - Invalid signature (ปกติสำหรับการทดสอบ)")
        elif response.status_code == 200:
            print("✅ Webhook ตอบกลับ 200 OK")
        else:
            print(f"❌ Webhook ตอบกลับ: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def check_admin_panel():
    """ตรวจสอบ Admin Panel"""
    print("\n5️⃣ ตรวจสอบ Admin Panel")
    print("-" * 40)
    
    try:
        # Frontend อาจจะรันที่ port อื่น
        frontend_url = "http://localhost:5173"
        response = requests.get(frontend_url)
        
        if response.status_code == 200:
            print(f"✅ Frontend Admin Panel: {frontend_url}")
            print("   - Dashboard: /")
            print("   - Templates: /templates.html")
        else:
            print(f"⚠️ Frontend status: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("⚠️ Frontend ยังไม่ได้รัน")
        print("💡 ถ้ารัน RUN_SYSTEM.bat แล้ว Frontend จะรันอัตโนมัติ")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_hr_scenarios():
    """ทดสอบ scenarios HR"""
    print("\n6️⃣ HR Scenarios ที่ควรทดสอบ")
    print("-" * 40)
    
    test_cases = [
        ("ทักทาย", ["สวัสดีครับ", "หวัดดี", "Hello"]),
        ("การลา", ["ขอทราบสิทธิการลาป่วย", "ลาพักผ่อนได้กี่วัน", "วิธีลากิจ"]),
        ("สวัสดิการ", ["เบิกค่ารักษาพยาบาล", "ค่าเล่าเรียนบุตร", "ประกันกลุ่ม"]),
        ("ทั่วไป", ["ติดต่อ HR", "ดาวน์โหลดแบบฟอร์ม", "เช็ควันลา MOJ001"])
    ]
    
    print("📝 Test Cases:")
    for category, messages in test_cases:
        print(f"\n{category}:")
        for msg in messages:
            print(f"  - {msg}")
    
    print("\n💡 วิธีทดสอบ:")
    print("1. เปิด LINE app")
    print("2. Add Friend: @your_bot_id")
    print("3. ส่งข้อความตาม test cases")
    print("4. ตรวจสอบการตอบกลับ")

def create_test_report():
    """สร้างรายงานผลการทดสอบ"""
    print("\n" + "="*60)
    print("📊 สรุปผลการทดสอบ Phase 1.6")
    print("="*60)
    
    # รวบรวมผลการทดสอบ
    results = {
        "Backend Server": check_backend_running(),
        "API Endpoints": False,  # จะอัพเดทจากผลจริง
        "Database Data": False,
        "Webhook": False,
        "Admin Panel": False
    }
    
    # คำนวณคะแนน
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    percentage = (passed / total) * 100
    
    print(f"\n✅ ผ่าน: {passed}/{total} ({percentage:.0f}%)")
    
    if percentage == 100:
        print("\n🎉 ระบบพร้อมใช้งาน 100%!")
    elif percentage >= 80:
        print("\n✅ ระบบพร้อมใช้งาน (มีบางส่วนที่ต้องปรับปรุง)")
    else:
        print("\n⚠️ ระบบยังไม่พร้อม ต้องแก้ไขปัญหา")
    
    # แนะนำขั้นตอนถัดไป
    print("\n💡 ขั้นตอนถัดไป:")
    if not results["Backend Server"]:
        print("1. รัน RUN_SYSTEM.bat เพื่อเริ่มระบบ")
    else:
        print("1. ทดสอบส่งข้อความผ่าน LINE")
        print("2. ตรวจสอบ Admin Panel")
        print("3. ดู logs เพื่อตรวจสอบการทำงาน")

def main():
    print("🧪 Phase 1.6: ทดสอบระบบ HR Bot เบื้องต้น")
    print("="*60)
    print(f"⏰ เวลาทดสอบ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # ทดสอบแต่ละส่วน
    backend_ok = check_backend_running()
    
    if backend_ok:
        check_api_endpoints()
        check_database_data()
        test_webhook_simulation()
        check_admin_panel()
        test_hr_scenarios()
    
    # สร้างรายงาน
    create_test_report()
    
    print("\n✅ Phase 1.6 - การทดสอบเสร็จสมบูรณ์!")

if __name__ == "__main__":
    main()
