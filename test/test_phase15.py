"""
ทดสอบ HR Bot ที่ปรับปรุงแล้ว
"""
import os
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import HR tools ที่สร้างไว้
from app.hr_tools import search_hr_faq, search_hr_policies, check_leave_balance

def test_hr_tools():
    print("🧪 ทดสอบ HR Tools")
    print("="*60)
    
    # ทดสอบ FAQ search
    print("\n1️⃣ ทดสอบค้นหา FAQ:")
    result = search_hr_faq("ลาป่วย")
    print(f"ผลการค้นหา 'ลาป่วย':\n{result[:200]}...")
    
    # ทดสอบ Policy search
    print("\n2️⃣ ทดสอบค้นหานโยบาย:")
    result = search_hr_policies("การลา")
    print(f"ผลการค้นหา 'การลา':\n{result[:200]}...")
    
    # ทดสอบ check leave balance
    print("\n3️⃣ ทดสอบเช็ควันลา:")
    result = check_leave_balance("MOJ001")
    print(f"ผลการเช็ค MOJ001:\n{result}")
    
    result = check_leave_balance("MOJ999")
    print(f"ผลการเช็ค MOJ999:\n{result}")

def test_system_prompt():
    print("\n\n🤖 ตรวจสอบ System Prompt ที่อัพเดท")
    print("="*60)
    
    # อ่าน main.py เพื่อตรวจสอบ
    main_file = os.path.join("app", "main.py")
    with open(main_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # ตรวจสอบว่ามี prompt ใหม่หรือไม่
    if "คุณคือผู้ช่วย HR อัจฉริยะของกองบริหารทรัพยากรบุคคล" in content:
        print("✅ System Prompt อัพเดทเรียบร้อยแล้ว")
        
        # แสดงตัวอย่าง prompt
        start = content.find("HR_SYSTEM_PROMPT = ")
        if start != -1:
            end = content.find('"""', start + 50)
            sample = content[start:start+200]
            print(f"\nตัวอย่าง Prompt:\n{sample}...")
    else:
        print("❌ System Prompt ยังไม่ได้อัพเดท")

def create_test_messages():
    """สร้างตัวอย่างข้อความทดสอบ"""
    test_messages = [
        "สวัสดีครับ",
        "ขอทราบสิทธิการลาป่วย",
        "ลาพักผ่อนได้กี่วัน",
        "วิธีเบิกค่ารักษาพยาบาล",
        "เช็ควันลา MOJ001",
        "ดาวน์โหลดแบบฟอร์มลา",
        "ติดต่อ HR ยังไง",
        "วันหยุดราชการปีนี้",
        "การแต่งกายวันศุกร์"
    ]
    
    print("\n\n📝 ตัวอย่างข้อความทดสอบ:")
    print("="*60)
    for i, msg in enumerate(test_messages, 1):
        print(f"{i}. {msg}")
    
    return test_messages

def main():
    print("🔬 Phase 1.5 - ทดสอบระบบที่ปรับปรุงแล้ว")
    print("="*60)
    
    # ทดสอบ tools
    test_hr_tools()
    
    # ตรวจสอบ system prompt
    test_system_prompt()
    
    # แสดงข้อความทดสอบ
    create_test_messages()
    
    print("\n\n✅ การทดสอบเสร็จสมบูรณ์!")
    print("\n💡 ขั้นตอนถัดไป:")
    print("1. รัน RUN_SYSTEM.bat เพื่อทดสอบ Bot จริง")
    print("2. ทดสอบด้วยข้อความตัวอย่าง")
    print("3. ตรวจสอบการตอบกลับ")

if __name__ == "__main__":
    main()
