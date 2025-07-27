"""
Phase 1.4: เพิ่ม Templates เพิ่มเติมให้ครบ 20 ข้อ
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

def check_current_templates():
    """ตรวจสอบ Templates ที่มีอยู่"""
    db = SessionLocal()
    try:
        # นับ templates ทั้งหมด
        total = db.query(MessageTemplate).count()
        print(f"📊 Templates ที่มีอยู่: {total} templates")
        
        # แสดง templates แยกตาม category
        categories = db.query(MessageCategory).all()
        print("\n📁 Templates ในแต่ละหมวด:")
        
        existing_templates = []
        for cat in categories:
            templates = db.query(MessageTemplate).filter(
                MessageTemplate.category_id == cat.id
            ).all()
            
            if templates:
                print(f"\n{cat.name} ({len(templates)} templates):")
                for t in templates:
                    print(f"  - {t.name}")
                    existing_templates.append(t.name)
        
        return total, existing_templates
    finally:
        db.close()

def add_new_hr_templates():
    """เพิ่ม Templates ใหม่สำหรับ HR"""
    db = SessionLocal()
    try:
        # Get category IDs
        categories = {cat.name: cat.id for cat in db.query(MessageCategory).all()}
        
        # Templates ใหม่ที่จะเพิ่ม (10 ข้อ)
        new_templates = [
            # การลา (เพิ่ม 3 ข้อ)
            {
                "name": "ลากิจส่วนตัว",
                "description": "ข้อมูลการลากิจส่วนตัว",
                "message_type": "text",
                "category_id": categories.get("การลา"),
                "content": json.dumps({
                    "type": "text",
                    "text": "📋 สิทธิการลากิจส่วนตัว:\n\n• ลาได้ปีละไม่เกิน 45 วันทำการ\n• ปีแรกที่ทำงานไม่ครบ 6 เดือน ไม่มีสิทธิลากิจ\n• ต้องยื่นใบลาล่วงหน้าอย่างน้อย 1 วัน\n\n📌 อ้างอิง: ระเบียบการลาของข้าราชการ พ.ศ. 2555"
                }),
                "tags": ["ลากิจ", "ลากิจส่วนตัว", "personal leave"]
            },
            {
                "name": "ลาคลอดบุตร",
                "description": "ข้อมูลการลาคลอดบุตร",
                "message_type": "flex",
                "category_id": categories.get("การลา"),
                "content": json.dumps({
                    "type": "flex",
                    "altText": "ข้อมูลการลาคลอดบุตร",
                    "contents": {
                        "type": "bubble",
                        "header": {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {"type": "text", "text": "👶 การลาคลอดบุตร", "weight": "bold", "size": "lg"}
                            ]
                        },
                        "body": {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {"type": "text", "text": "สิทธิการลา:", "weight": "bold"},
                                {"type": "text", "text": "• ลาได้ 90 วัน", "wrap": True},
                                {"type": "text", "text": "• ได้รับเงินเดือนระหว่างลา", "wrap": True},
                                {"type": "text", "text": "• ลาก่อน/หลังคลอดได้", "wrap": True},
                                {"type": "separator", "margin": "md"},
                                {"type": "text", "text": "สามีลาช่วยภรรยาคลอด:", "weight": "bold", "margin": "md"},
                                {"type": "text", "text": "• ลาได้ 15 วันทำการ", "wrap": True}
                            ]
                        }
                    }
                }),
                "tags": ["ลาคลอด", "คลอดบุตร", "maternity"]
            },
            {
                "name": "ลาอุปสมบท",
                "description": "ข้อมูลการลาอุปสมบท",
                "message_type": "text",
                "category_id": categories.get("การลา"),
                "content": json.dumps({
                    "type": "text",
                    "text": "☸️ สิทธิการลาอุปสมบท:\n\n• ลาได้ไม่เกิน 120 วัน\n• ต้องทำงานมาแล้วไม่น้อยกว่า 1 ปี\n• ได้รับเงินเดือนระหว่างลาไม่เกิน 60 วัน\n• ยื่นใบลาล่วงหน้าไม่น้อยกว่า 60 วัน"
                }),
                "tags": ["ลาบวช", "อุปสมบท", "บวช"]
            },
            
            # สวัสดิการ (เพิ่ม 3 ข้อ)
            {
                "name": "ค่าเล่าเรียนบุตร",
                "description": "สิทธิเบิกค่าเล่าเรียนบุตร",
                "message_type": "text",
                "category_id": categories.get("สวัสดิการ"),
                "content": json.dumps({
                    "type": "text",
                    "text": "🎓 สิทธิเบิกค่าเล่าเรียนบุตร:\n\n• เบิกได้ตั้งแต่อนุบาล - ปริญญาตรี\n• บุตรคนที่ 1-3 เบิกได้เต็มจำนวน\n• สถานศึกษาของรัฐ: เบิกได้เต็มจำนวน\n• สถานศึกษาเอกชน: เบิกได้ตามเพดานที่กำหนด\n\n💡 ต้องยื่นเบิกภายใน 1 ปีนับจากวันเปิดเทอม"
                }),
                "tags": ["ค่าเล่าเรียน", "การศึกษาบุตร", "education"]
            },
            {
                "name": "เงินกู้สวัสดิการ",
                "description": "ข้อมูลเงินกู้สวัสดิการ",
                "message_type": "text",
                "category_id": categories.get("สวัสดิการ"),
                "content": json.dumps({
                    "type": "text",
                    "text": "💰 เงินกู้สวัสดิการ:\n\n• กู้เพื่อเหตุฉุกเฉิน: ไม่เกิน 3 เท่าของเงินเดือน\n• กู้เพื่อการศึกษา: ไม่เกิน 5 เท่าของเงินเดือน\n• กู้เพื่อที่อยู่อาศัย: ตามหลักเกณฑ์ ธอส.\n• อัตราดอกเบี้ย: ตามที่กระทรวงการคลังกำหนด\n\n📞 ติดต่อ: กลุ่มสวัสดิการ โทร.1234"
                }),
                "tags": ["เงินกู้", "สินเชื่อ", "loan"]
            },
            {
                "name": "ประกันสุขภาพกลุ่ม",
                "description": "ข้อมูลประกันสุขภาพกลุ่ม",
                "message_type": "text",
                "category_id": categories.get("สวัสดิการ"),
                "content": json.dumps({
                    "type": "text",
                    "text": "🏥 ประกันสุขภาพกลุ่ม:\n\n• คุ้มครองผู้ป่วยใน: 100,000 บาท/ปี\n• คุ้มครองผู้ป่วยนอก: 30,000 บาท/ปี\n• คุ้มครองทันตกรรม: 5,000 บาท/ปี\n• คุ้มครองอุบัติเหตุ: 200,000 บาท\n• ครอบคลุม: ตนเอง คู่สมรส บุตร\n\n📄 ดูรายละเอียด: www.moj-insurance.com"
                }),
                "tags": ["ประกัน", "ประกันสุขภาพ", "insurance"]
            },
            
            # ระเบียบ (เพิ่ม 2 ข้อ)
            {
                "name": "วันหยุดราชการ",
                "description": "วันหยุดราชการประจำปี",
                "message_type": "text",
                "category_id": categories.get("ระเบียบ"),
                "content": json.dumps({
                    "type": "text",
                    "text": "📅 วันหยุดราชการ ปี 2568:\n\n• วันหยุดประจำ: เสาร์-อาทิตย์\n• วันหยุดนักขัตฤกษ์: 18 วัน\n• วันหยุดชดเชย: ตามประกาศ\n\n🔍 ดูปฏิทินทั้งหมด: กดที่เมนู 'ปฏิทินวันหยุด'"
                }),
                "tags": ["วันหยุด", "ปฏิทิน", "holiday"]
            },
            {
                "name": "การแต่งกายราชการ",
                "description": "ระเบียบการแต่งกาย",
                "message_type": "text",
                "category_id": categories.get("ระเบียบ"),
                "content": json.dumps({
                    "type": "text",
                    "text": "👔 ระเบียบการแต่งกาย:\n\n• จันทร์-พฤหัส: ชุดข้าราชการ/ชุดสุภาพ\n• ศุกร์: ชุดผ้าไทย/ผ้าพื้นเมือง\n• งานพิธีการ: ชุดปกติขาว/ชุดกากี\n\n⚠️ ห้าม: กางเกงยีนส์, รองเท้าแตะ, เสื้อยืด\n\n📌 อ้างอิง: ระเบียบสำนักนายกฯ ว่าด้วยการแต่งกาย"
                }),
                "tags": ["แต่งกาย", "เครื่องแบบ", "dress code"]
            },
            
            # ทั่วไป (เพิ่ม 2 ข้อ)
            {
                "name": "ดาวน์โหลดแบบฟอร์ม",
                "description": "ลิงก์ดาวน์โหลดแบบฟอร์ม HR",
                "message_type": "text_with_uri",
                "category_id": categories.get("ทั่วไป"),
                "content": json.dumps({
                    "type": "text",
                    "text": "📥 ดาวน์โหลดแบบฟอร์ม HR:\n\nคลิกลิงก์ด้านล่างเพื่อดาวน์โหลด:\n\n📄 แบบฟอร์มลา: https://hr.moj.go.th/forms/leave\n📄 แบบขอสวัสดิการ: https://hr.moj.go.th/forms/welfare\n📄 แบบประเมิน: https://hr.moj.go.th/forms/evaluation"
                }),
                "tags": ["แบบฟอร์ม", "ดาวน์โหลด", "download", "forms"]
            },
            {
                "name": "วิธีเช็ควันลา",
                "description": "วิธีตรวจสอบวันลาคงเหลือ",
                "message_type": "text_with_quickreply",
                "category_id": categories.get("ทั่วไป"),
                "content": json.dumps({
                    "type": "text",
                    "text": "🔍 วิธีเช็ควันลาคงเหลือ:\n\n1. ผ่าน LINE: พิมพ์ 'เช็ควันลา' ตามด้วยรหัสพนักงาน\n   ตัวอย่าง: เช็ควันลา MOJ001\n\n2. ผ่านเว็บไซต์: https://hr.moj.go.th\n   Login ด้วย Username/Password\n\n3. ติดต่อ HR โดยตรง: โทร.1234",
                    "quickReply": {
                        "items": [
                            {"action": {"type": "message", "label": "เช็ควันลา", "text": "เช็ควันลา MOJ001"}},
                            {"action": {"type": "uri", "label": "เข้าเว็บไซต์", "uri": "https://hr.moj.go.th"}},
                            {"action": {"type": "message", "label": "ติดต่อ HR", "text": "ติดต่อ HR"}}
                        ]
                    }
                }),
                "tags": ["เช็ควันลา", "วันลาคงเหลือ", "check leave"]
            }
        ]
        
        # ตรวจสอบและเพิ่ม templates
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
                    content=template_data["content"],
                    is_active=True,
                    tags=template_data.get("tags", []),
                    created_at=datetime.now()
                )
                db.add(new_template)
                added_count += 1
                print(f"✅ เพิ่ม: {template_data['name']}")
            else:
                print(f"⚠️ มีอยู่แล้ว: {template_data['name']}")
        
        db.commit()
        print(f"\n✅ เพิ่ม Templates ใหม่: {added_count} templates")
        
        return added_count
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        return 0
    finally:
        db.close()

def main():
    print("📝 Phase 1.4: เพิ่ม Templates ให้ครบ 20 ข้อ")
    print("="*60)
    
    # ตรวจสอบ templates ที่มีอยู่
    current_count, existing = check_current_templates()
    
    if current_count >= 20:
        print(f"\n✅ มี Templates ครบ 20 ข้อแล้ว ({current_count} templates)")
        print("💡 ไม่จำเป็นต้องเพิ่มเติม")
    else:
        print(f"\n⚠️ ต้องเพิ่มอีก {20 - current_count} templates")
        print("\n🔄 กำลังเพิ่ม Templates ใหม่...")
        
        # เพิ่ม templates ใหม่
        added = add_new_hr_templates()
        
        # ตรวจสอบผลลัพธ์
        new_count, _ = check_current_templates()
        print(f"\n📊 สรุป: มี Templates ทั้งหมด {new_count} templates")
        
        if new_count >= 20:
            print("✅ Phase 1.4 เสร็จสมบูรณ์!")
        else:
            print(f"⚠️ ยังขาดอีก {20 - new_count} templates")

if __name__ == "__main__":
    main()
