"""
Phase 1.4: เพิ่ม Templates แบบง่าย (ไม่มี tags)
"""
import os
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import MessageCategory, MessageTemplate
import json
from datetime import datetime

def add_simple_hr_templates():
    """เพิ่ม Templates ใหม่แบบง่าย"""
    db = SessionLocal()
    try:
        # Get category IDs
        categories = {cat.name: cat.id for cat in db.query(MessageCategory).all()}
        
        # Templates ใหม่ที่จะเพิ่ม (แบบง่าย ไม่มี tags)
        new_templates = [
            # การลา
            {
                "name": "ลากิจส่วนตัว",
                "description": "ข้อมูลการลากิจส่วนตัว",
                "message_type": "text",
                "category_id": categories.get("การลา"),
                "content": {
                    "type": "text",
                    "text": "📋 สิทธิการลากิจส่วนตัว:\n\n• ลาได้ปีละไม่เกิน 45 วันทำการ\n• ปีแรกที่ทำงานไม่ครบ 6 เดือน ไม่มีสิทธิลากิจ\n• ต้องยื่นใบลาล่วงหน้าอย่างน้อย 1 วัน\n\n📌 อ้างอิง: ระเบียบการลาของข้าราชการ พ.ศ. 2555"
                }
            },
            {
                "name": "ลาคลอดบุตร",
                "description": "ข้อมูลการลาคลอดบุตร",
                "message_type": "text",
                "category_id": categories.get("การลา"),
                "content": {
                    "type": "text",
                    "text": "👶 การลาคลอดบุตร:\n\n• ข้าราชการหญิง: ลาได้ 90 วัน\n• ได้รับเงินเดือนระหว่างลา\n• ลาก่อน/หลังคลอดได้\n\n• สามีลาช่วยภรรยาคลอด: 15 วันทำการ\n• ได้รับเงินเดือนระหว่างลา"
                }
            },
            {
                "name": "ลาอุปสมบท",
                "description": "ข้อมูลการลาอุปสมบท",
                "message_type": "text",
                "category_id": categories.get("การลา"),
                "content": {
                    "type": "text",
                    "text": "☸️ สิทธิการลาอุปสมบท:\n\n• ลาได้ไม่เกิน 120 วัน\n• ต้องทำงานมาแล้วไม่น้อยกว่า 1 ปี\n• ได้รับเงินเดือนระหว่างลาไม่เกิน 60 วัน\n• ยื่นใบลาล่วงหน้าไม่น้อยกว่า 60 วัน"
                }
            },
            # สวัสดิการ
            {
                "name": "ค่าเล่าเรียนบุตร",
                "description": "สิทธิเบิกค่าเล่าเรียนบุตร",
                "message_type": "text",
                "category_id": categories.get("สวัสดิการ"),
                "content": {
                    "type": "text",
                    "text": "🎓 สิทธิเบิกค่าเล่าเรียนบุตร:\n\n• เบิกได้ตั้งแต่อนุบาล - ปริญญาตรี\n• บุตรคนที่ 1-3 เบิกได้เต็มจำนวน\n• สถานศึกษาของรัฐ: เบิกได้เต็มจำนวน\n• สถานศึกษาเอกชน: เบิกได้ตามเพดานที่กำหนด\n\n💡 ต้องยื่นเบิกภายใน 1 ปีนับจากวันเปิดเทอม"
                }
            },
            {
                "name": "เงินกู้สวัสดิการ",
                "description": "ข้อมูลเงินกู้สวัสดิการ",
                "message_type": "text",
                "category_id": categories.get("สวัสดิการ"),
                "content": {
                    "type": "text",
                    "text": "💰 เงินกู้สวัสดิการ:\n\n• กู้เพื่อเหตุฉุกเฉิน: ไม่เกิน 3 เท่าของเงินเดือน\n• กู้เพื่อการศึกษา: ไม่เกิน 5 เท่าของเงินเดือน\n• กู้เพื่อที่อยู่อาศัย: ตามหลักเกณฑ์ ธอส.\n• อัตราดอกเบี้ย: ตามที่กระทรวงการคลังกำหนด\n\n📞 ติดต่อ: กลุ่มสวัสดิการ โทร.1234"
                }
            },
            {
                "name": "ประกันสุขภาพกลุ่ม",
                "description": "ข้อมูลประกันสุขภาพกลุ่ม",
                "message_type": "text",
                "category_id": categories.get("สวัสดิการ"),
                "content": {
                    "type": "text",
                    "text": "🏥 ประกันสุขภาพกลุ่ม:\n\n• คุ้มครองผู้ป่วยใน: 100,000 บาท/ปี\n• คุ้มครองผู้ป่วยนอก: 30,000 บาท/ปี\n• คุ้มครองทันตกรรม: 5,000 บาท/ปี\n• คุ้มครองอุบัติเหตุ: 200,000 บาท\n• ครอบคลุม: ตนเอง คู่สมรส บุตร"
                }
            },
            # ระเบียบ
            {
                "name": "วันหยุดราชการ",
                "description": "วันหยุดราชการประจำปี",
                "message_type": "text",
                "category_id": categories.get("ระเบียบ"),
                "content": {
                    "type": "text",
                    "text": "📅 วันหยุดราชการ ปี 2568:\n\n• วันหยุดประจำ: เสาร์-อาทิตย์\n• วันหยุดนักขัตฤกษ์: 18 วัน\n• วันหยุดชดเชย: ตามประกาศ\n\n🔍 ดูปฏิทินทั้งหมดได้ที่เว็บไซต์ HR"
                }
            },
            {
                "name": "การแต่งกายราชการ",
                "description": "ระเบียบการแต่งกาย",
                "message_type": "text",
                "category_id": categories.get("ระเบียบ"),
                "content": {
                    "type": "text",
                    "text": "👔 ระเบียบการแต่งกาย:\n\n• จันทร์-พฤหัส: ชุดข้าราชการ/ชุดสุภาพ\n• ศุกร์: ชุดผ้าไทย/ผ้าพื้นเมือง\n• งานพิธีการ: ชุดปกติขาว/ชุดกากี\n\n⚠️ ห้าม: กางเกงยีนส์, รองเท้าแตะ, เสื้อยืด"
                }
            },
            # ทั่วไป
            {
                "name": "ดาวน์โหลดแบบฟอร์ม",
                "description": "ลิงก์ดาวน์โหลดแบบฟอร์ม HR",
                "message_type": "text",
                "category_id": categories.get("ทั่วไป"),
                "content": {
                    "type": "text",
                    "text": "📥 ดาวน์โหลดแบบฟอร์ม HR:\n\n📄 แบบฟอร์มลา:\nhr.moj.go.th/forms/leave\n\n📄 แบบขอสวัสดิการ:\nhr.moj.go.th/forms/welfare\n\n📄 แบบประเมิน:\nhr.moj.go.th/forms/evaluation"
                }
            },
            {
                "name": "วิธีเช็ควันลา",
                "description": "วิธีตรวจสอบวันลาคงเหลือ",
                "message_type": "text",
                "category_id": categories.get("ทั่วไป"),
                "content": {
                    "type": "text",
                    "text": "🔍 วิธีเช็ควันลาคงเหลือ:\n\n1. ผ่าน LINE: พิมพ์ 'เช็ควันลา' ตามด้วยรหัสพนักงาน\n   ตัวอย่าง: เช็ควันลา MOJ001\n\n2. ผ่านเว็บไซต์: hr.moj.go.th\n   Login ด้วย Username/Password\n\n3. ติดต่อ HR โดยตรง: โทร.1234"
                }
            }
        ]
        
        # เพิ่ม templates
        added_count = 0
        for template_data in new_templates:
            # ตรวจสอบว่ามี template นี้อยู่แล้วหรือไม่
            existing = db.query(MessageTemplate).filter(
                MessageTemplate.name == template_data["name"]
            ).first()
            
            if not existing and template_data["category_id"]:
                new_template = MessageTemplate(
                    name=template_data["name"],
                    description=template_data["description"],
                    message_type=template_data["message_type"],
                    category_id=template_data["category_id"],
                    content=json.dumps(template_data["content"], ensure_ascii=False),
                    is_active=True,
                    created_at=datetime.now()
                )
                db.add(new_template)
                added_count += 1
                print(f"✅ เพิ่ม: {template_data['name']}")
            elif existing:
                print(f"⚠️ มีอยู่แล้ว: {template_data['name']}")
        
        db.commit()
        print(f"\n✅ เพิ่ม Templates ใหม่: {added_count} templates")
        
        # นับ templates ทั้งหมด
        total = db.query(MessageTemplate).count()
        print(f"📊 Templates ทั้งหมด: {total} templates")
        
        return added_count
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        return 0
    finally:
        db.close()

def main():
    print("📝 Phase 1.4: เพิ่ม Templates แบบง่าย")
    print("="*60)
    
    # เพิ่ม templates
    added = add_simple_hr_templates()
    
    if added > 0:
        print("\n✅ Phase 1.4 เสร็จสมบูรณ์!")
    else:
        print("\n⚠️ ไม่มี Templates ใหม่ที่เพิ่ม")

if __name__ == "__main__":
    main()
