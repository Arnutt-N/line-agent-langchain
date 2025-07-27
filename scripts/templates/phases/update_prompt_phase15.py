"""
Phase 1.5: ปรับปรุง System Prompt สำหรับ HR Bot
"""
import os
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# HR System Prompt ที่ปรับปรุงใหม่
HR_SYSTEM_PROMPT_V2 = """คุณคือผู้ช่วย HR อัจฉริยะของกองบริหารทรัพยากรบุคคล สำนักงานปลัดกระทรวงยุติธรรม

## บทบาทและหน้าที่:
1. ให้บริการข้อมูลด้าน HR แก่บุคลากรในสังกัดกระทรวงยุติธรรม
2. ตอบคำถามเกี่ยวกับการลา สวัสดิการ เงินเดือน ระเบียบ และข้อมูล HR ทั่วไป
3. ช่วยค้นหาข้อมูลจากระเบียบ กฎหมาย คำสั่ง และประกาศที่เกี่ยวข้อง
4. แนะนำขั้นตอนการปฏิบัติงานด้าน HR

## แหล่งข้อมูลที่มี:
1. **Templates (เร็วที่สุด)** - ข้อความสำเร็จรูป 20+ แบบ ครอบคลุมคำถามที่พบบ่อย
2. **ไฟล์ข้อมูล HR** - FAQ, นโยบาย, สวัสดิการ ในโฟลเดอร์ data/text/
3. **ความรู้พื้นฐาน** - ข้อมูลทั่วไปเกี่ยวกับระบบราชการไทย

## หลักการตอบคำถาม:
1. **เลือกแหล่งข้อมูลอัจฉริยะ**:
   - Templates: สำหรับคำถามทั่วไป ทักทาย ข้อมูลพื้นฐาน
   - ไฟล์ข้อมูล: สำหรับรายละเอียดเพิ่มเติม คำถามเฉพาะ
   - ความรู้ทั่วไป: สำหรับข้อมูลที่ไม่มีในระบบ

2. **รูปแบบการตอบ**:
   - ใช้ภาษาราชการที่สุภาพ เป็นทางการ
   - ตอบตรงประเด็น กระชับ ชัดเจน
   - ใช้ emoji เพื่อให้อ่านง่าย (📋 📌 ✅ 💡)
   - แบ่งหัวข้อชัดเจนด้วย bullet points
   - อ้างอิงระเบียบ/กฎหมายเมื่อตอบเรื่องสิทธิ

3. **ข้อมูลที่ให้บริการ**:
   - การลา: ลาป่วย ลาพักผ่อน ลากิจ ลาคลอด ลาอุปสมบท
   - สวัสดิการ: ค่ารักษาพยาบาล ค่าเล่าเรียนบุตร เงินกู้ ประกันกลุ่ม
   - เงินเดือน: การเลื่อนเงินเดือน ค่าตอบแทน
   - ระเบียบ: เวลาราชการ การแต่งกาย วันหยุด
   - ทั่วไป: ติดต่อ HR ดาวน์โหลดแบบฟอร์ม วิธีเช็ควันลา

## ตัวอย่างการตอบ:
คำถาม: "ขอทราบสิทธิการลาป่วย"
คำตอบ: "📋 สิทธิการลาป่วย:
• ลาได้เท่าที่ป่วยจริง (ไม่เกิน 60 วันทำการ/ปี)
• เกิน 30 วัน ต้องมีใบรับรองแพทย์
• ได้รับเงินเดือนระหว่างลา
📌 อ้างอิง: ระเบียบการลาของข้าราชการ พ.ศ. 2555"

## ข้อจำกัดและคำแนะนำ:
- หากไม่แน่ใจในคำตอบ ให้แนะนำติดต่อ HR โดยตรง
- ไม่ให้คำปรึกษาเรื่องส่วนตัวหรือกรณีพิเศษ
- ไม่เปิดเผยข้อมูลส่วนบุคคลของเจ้าหน้าที่
- เมื่อถูกถามนอกเหนือจาก HR ให้บอกว่าเป็นผู้ช่วย HR โดยเฉพาะ

## Special Commands:
- "เช็ควันลา [รหัสพนักงาน]" - ดูวันลาคงเหลือ
- "ดาวน์โหลดแบบฟอร์ม" - แสดงลิงก์แบบฟอร์ม
- "ติดต่อ HR" - แสดงช่องทางติดต่อ"""

def save_updated_prompt():
    """บันทึก System Prompt ที่ปรับปรุงแล้ว"""
    prompt_file = "hr_system_prompt_v2.txt"
    with open(prompt_file, 'w', encoding='utf-8') as f:
        f.write(HR_SYSTEM_PROMPT_V2)
    print(f"✅ บันทึก System Prompt ใหม่ที่: {prompt_file}")
    return prompt_file

def create_backup_main():
    """สร้าง backup ของ main.py ก่อนแก้ไข"""
    import shutil
    from datetime import datetime
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"main_backup_{timestamp}.py"
    
    # ใช้ path แบบเต็ม
    source = os.path.join(os.path.dirname(__file__), "app", "main.py")
    dest = os.path.join(os.path.dirname(__file__), "app", backup_file)
    
    shutil.copy(source, dest)
    print(f"✅ สร้าง backup: app/{backup_file}")
    return backup_file

def update_main_prompt():
    """อัพเดท System Prompt ใน main.py"""
    main_file = os.path.join(os.path.dirname(__file__), "app", "main.py")
    
    # อ่านไฟล์ main.py
    with open(main_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # หา System Prompt เดิม
    old_prompt_start = content.find('HR_SYSTEM_PROMPT = """')
    if old_prompt_start == -1:
        print("❌ ไม่พบ HR_SYSTEM_PROMPT ในไฟล์ main.py")
        return False
    
    # หาตำแหน่งสิ้นสุดของ prompt
    old_prompt_end = content.find('"""', old_prompt_start + 22) + 3
    
    # แทนที่ด้วย prompt ใหม่
    new_content = (
        content[:old_prompt_start] + 
        f'HR_SYSTEM_PROMPT = """{HR_SYSTEM_PROMPT_V2}"""' +
        content[old_prompt_end:]
    )
    
    # เขียนกลับ
    with open(main_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ อัพเดท System Prompt ใน main.py เรียบร้อย")
    return True

def create_tools_file():
    """สร้างไฟล์ tools เพิ่มเติมสำหรับค้นหาข้อมูล"""
    tools_content = '''"""
HR Bot Tools - เครื่องมือเพิ่มเติมสำหรับ HR Bot
"""
from langchain.tools import tool
import os
import json

@tool
def search_hr_faq(query: str) -> str:
    """ค้นหาคำตอบจากไฟล์ FAQ HR"""
    try:
        faq_file = os.path.join("data", "text", "faq_hr.txt")
        if not os.path.exists(faq_file):
            return "ไม่พบไฟล์ FAQ"
        
        with open(faq_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # ค้นหาคำตอบที่เกี่ยวข้อง
        lines = content.split('\\n')
        relevant_lines = []
        
        for i, line in enumerate(lines):
            if query.lower() in line.lower():
                # เอาบริบท 3 บรรทัดก่อนและหลัง
                start = max(0, i-3)
                end = min(len(lines), i+4)
                context = lines[start:end]
                relevant_lines.extend(context)
                relevant_lines.append("---")
        
        if relevant_lines:
            return "\\n".join(relevant_lines[:50])  # จำกัดไม่เกิน 50 บรรทัด
        else:
            return "ไม่พบข้อมูลที่เกี่ยวข้องใน FAQ"
            
    except Exception as e:
        return f"เกิดข้อผิดพลาดในการค้นหา: {str(e)}"

@tool
def search_hr_policies(query: str) -> str:
    """ค้นหานโยบาย HR ที่เกี่ยวข้อง"""
    try:
        policy_file = os.path.join("data", "text", "policies_hr.txt")
        if not os.path.exists(policy_file):
            return "ไม่พบไฟล์นโยบาย"
        
        with open(policy_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # ค้นหานโยบายที่เกี่ยวข้อง
        if query.lower() in content.lower():
            # หาตำแหน่งที่พบคำค้นหา
            pos = content.lower().find(query.lower())
            start = max(0, pos - 200)
            end = min(len(content), pos + 500)
            
            return f"พบข้อมูลที่เกี่ยวข้อง:\\n{content[start:end]}..."
        else:
            return "ไม่พบนโยบายที่เกี่ยวข้องกับคำค้นหา"
            
    except Exception as e:
        return f"เกิดข้อผิดพลาดในการค้นหา: {str(e)}"

@tool
def check_leave_balance(employee_id: str) -> str:
    """ตรวจสอบวันลาคงเหลือ (Mock data)"""
    # ในระบบจริงจะเชื่อมต่อกับ database
    mock_data = {
        "MOJ001": {"sick": 45, "vacation": 10, "personal": 30},
        "MOJ002": {"sick": 60, "vacation": 5, "personal": 45},
        "MOJ003": {"sick": 30, "vacation": 8, "personal": 20}
    }
    
    if employee_id in mock_data:
        balance = mock_data[employee_id]
        return f"""📊 ยอดวันลาคงเหลือ ({employee_id}):
• ลาป่วย: {balance['sick']} วัน
• ลาพักผ่อน: {balance['vacation']} วัน
• ลากิจส่วนตัว: {balance['personal']} วัน"""
    else:
        return "❌ ไม่พบข้อมูลพนักงาน กรุณาตรวจสอบรหัสพนักงาน"
'''
    
    tools_file = os.path.join(os.path.dirname(__file__), "app", "hr_tools.py")
    with open(tools_file, 'w', encoding='utf-8') as f:
        f.write(tools_content)
    
    print(f"✅ สร้างไฟล์ tools เพิ่มเติม: app/hr_tools.py")
    return tools_file

def main():
    print("🤖 Phase 1.5: ปรับปรุง System Prompt สำหรับ HR")
    print("="*60)
    
    # 1. บันทึก System Prompt ใหม่
    print("\n1️⃣ บันทึก System Prompt ใหม่...")
    prompt_file = save_updated_prompt()
    
    # 2. สร้าง backup
    print("\n2️⃣ สร้าง backup ของ main.py...")
    backup_file = create_backup_main()
    
    # 3. อัพเดท main.py
    print("\n3️⃣ อัพเดท System Prompt ใน main.py...")
    updated = update_main_prompt()
    
    # 4. สร้าง tools เพิ่มเติม
    print("\n4️⃣ สร้าง HR tools เพิ่มเติม...")
    tools_file = create_tools_file()
    
    # สรุป
    print("\n" + "="*60)
    print("📊 สรุปผล Phase 1.5:")
    print("="*60)
    print(f"✅ System Prompt V2 บันทึกที่: {prompt_file}")
    print(f"✅ Backup main.py ที่: app/{backup_file}")
    print(f"✅ อัพเดท main.py: {'สำเร็จ' if updated else 'ไม่สำเร็จ'}")
    print(f"✅ HR Tools เพิ่มเติมที่: {tools_file}")
    
    print("\n💡 ขั้นตอนถัดไป:")
    print("1. ตรวจสอบการทำงานของ Bot")
    print("2. ทดสอบการตอบคำถาม HR")
    print("3. ปรับแต่งเพิ่มเติมตามความต้องการ")
    
    print("\n✅ Phase 1.5 เสร็จสมบูรณ์!")

if __name__ == "__main__":
    main()
