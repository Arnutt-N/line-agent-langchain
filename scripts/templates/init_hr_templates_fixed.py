#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script สำหรับเพิ่ม HR Categories และ Templates - Fixed Version
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app.database import SessionLocal, engine
from app.models import Base, MessageCategory, MessageTemplate
import json

def add_hr_data():
    db = SessionLocal()
    
    # Add categories
    categories = [
        {"name": "ทักทาย", "description": "ข้อความทักทายและแนะนำตัว", "color": "#4CAF50"},
        {"name": "การลา", "description": "ข้อมูลเกี่ยวกับการลาประเภทต่างๆ", "color": "#2196F3"},
        {"name": "สวัสดิการ", "description": "สิทธิประโยชน์และสวัสดิการ", "color": "#FF9800"},
        {"name": "เงินเดือน", "description": "ข้อมูลเกี่ยวกับเงินเดือนและค่าตอบแทน", "color": "#9C27B0"},
        {"name": "ระเบียบ", "description": "ระเบียบและข้อบังคับ", "color": "#E91E63"},
        {"name": "ทั่วไป", "description": "คำถามทั่วไปเกี่ยวกับ HR", "color": "#607D8B"}
    ]
    
    print("Adding Categories...")
    for cat_data in categories:
        existing = db.query(MessageCategory).filter_by(name=cat_data["name"]).first()
        if not existing:
            category = MessageCategory(**cat_data)
            db.add(category)
    db.commit()
    
    # Get category mapping
    cat_map = {cat.name: cat.id for cat in db.query(MessageCategory).all()}
    
    # Templates data with comma-separated tags
    templates = [
        # ทักทาย
        {
            "name": "ทักทายทั่วไป",
            "description": "ข้อความทักทายพื้นฐาน", 
            "message_type": "text",
            "category_id": cat_map["ทักทาย"],
            "content": json.dumps({
                "type": "text",
                "text": "สวัสดีค่ะ 🙏\n\nยินดีให้บริการข้อมูล HR\nกองบริหารทรัพยากรบุคคล\nสำนักงานปลัดกระทรวงยุติธรรม\n\nมีอะไรให้ช่วยเหลือคะ?"
            }),
            "tags": "greeting,welcome,สวัสดี",
            "priority": 10
        },
        {
            "name": "แนะนำบริการ",
            "description": "แนะนำบริการที่มี",
            "message_type": "text_with_quickreply",
            "category_id": cat_map["ทักทาย"],
            "content": json.dumps({
                "type": "text",
                "text": "บริการข้อมูล HR ที่ให้บริการ:\n\n📋 การลา\n💰 สวัสดิการ\n📊 เงินเดือน\n📖 ระเบียบ\n\nเลือกหัวข้อที่ต้องการค่ะ",
                "quickReply": {
                    "items": [
                        {"type": "action", "action": {"type": "message", "label": "การลา", "text": "ขอข้อมูลการลา"}},
                        {"type": "action", "action": {"type": "message", "label": "สวัสดิการ", "text": "ขอข้อมูลสวัสดิการ"}},
                        {"type": "action", "action": {"type": "message", "label": "เงินเดือน", "text": "ขอข้อมูลเงินเดือน"}},
                        {"type": "action", "action": {"type": "message", "label": "ระเบียบ", "text": "ขอข้อมูลระเบียบ"}}
                    ]
                }
            }),
            "tags": "menu,services,บริการ",
            "priority": 8
        },
        # การลา
        {
            "name": "สิทธิการลาทั้งหมด",
            "description": "แสดงสิทธิการลาทุกประเภท",
            "message_type": "flex",
            "category_id": cat_map["การลา"],
            "content": json.dumps({
                "type": "flex",
                "altText": "สิทธิการลาประจำปี",
                "contents": {
                    "type": "bubble",
                    "header": {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {"type": "text", "text": "📋 สิทธิการลาประจำปี", "weight": "bold", "size": "xl", "color": "#2196F3"}
                        ]
                    },
                    "body": {
                        "type": "box",
                        "layout": "vertical",
                        "spacing": "md",
                        "contents": [
                            {"type": "text", "text": "🏥 ลาป่วย: 60 วันทำการ/ปี", "wrap": True},
                            {"type": "text", "text": "🏖️ ลาพักผ่อน: 10 วันทำการ/ปี", "wrap": True},
                            {"type": "text", "text": "📝 ลากิจส่วนตัว: 45 วันทำการ/ปี", "wrap": True},
                            {"type": "text", "text": "👶 ลาคลอดบุตร: 90 วัน", "wrap": True},
                            {"type": "separator", "margin": "md"},
                            {"type": "text", "text": "📌 อ้างอิง: ระเบียบการลาฯ พ.ศ. 2555", "size": "xs", "color": "#999999"}
                        ]
                    }
                }
            }),
            "tags": "leave,all,สิทธิ,ลา",
            "priority": 10
        },
        {
            "name": "ลาป่วย",
            "description": "ข้อมูลการลาป่วย",
            "message_type": "text",
            "category_id": cat_map["การลา"],
            "content": json.dumps({
                "type": "text",
                "text": "🏥 การลาป่วย\n\n✅ สิทธิ: ลาได้เท่าที่ป่วยจริง (ไม่เกิน 60 วันทำการ/ปี)\n✅ ได้รับเงินเดือนระหว่างลา\n\n📋 เงื่อนไข:\n• ลาติดต่อเกิน 3 วัน ต้องมีใบรับรองแพทย์\n• ลาเกิน 30 วัน ต้องมีใบรับรองแพทย์จากโรงพยาบาลรัฐ\n\n📌 ระเบียบการลาฯ พ.ศ. 2555"
            }),
            "tags": "sick,ป่วย,ลาป่วย",
            "priority": 9
        },
        {
            "name": "ลาพักผ่อน", 
            "description": "ข้อมูลการลาพักผ่อน",
            "message_type": "text",
            "category_id": cat_map["การลา"],
            "content": json.dumps({
                "type": "text",
                "text": "🏖️ การลาพักผ่อน\n\n✅ สิทธิ:\n• ทำงานครบ 6 เดือน: มีสิทธิลา 10 วันทำการ\n• ปีต่อไป: 10 วันทำการ/ปี\n\n📋 การสะสม:\n• สะสมได้ไม่เกิน 20 วันทำการ\n• รวมปีปัจจุบันไม่เกิน 30 วันทำการ\n\n💡 หมายเหตุ: ต้องขออนุมัติล่วงหน้า"
            }),
            "tags": "vacation,พักผ่อน,ลาพักผ่อน",
            "priority": 9
        },
        # สวัสดิการ
        {
            "name": "สวัสดิการทั้งหมด",
            "description": "ภาพรวมสวัสดิการ",
            "message_type": "text",
            "category_id": cat_map["สวัสดิการ"],
            "content": json.dumps({
                "type": "text",
                "text": "💰 สวัสดิการข้าราชการ\n\n✅ ค่ารักษาพยาบาล (ตนเอง+ครอบครัว)\n✅ ค่าเล่าเรียนบุตร\n✅ เงินช่วยเหลือบุตร\n✅ ค่าเช่าบ้าน\n✅ เงินกู้สวัสดิการ\n✅ บำเหน็จบำนาญ\n✅ เครื่องราชอิสริยาภรณ์\n\n📞 สอบถามรายละเอียด: 02-123-4567"
            }),
            "tags": "welfare,สวัสดิการ,สิทธิ",
            "priority": 10
        },
        {
            "name": "ค่ารักษาพยาบาล",
            "description": "สิทธิค่ารักษาพยาบาล",
            "message_type": "text",
            "category_id": cat_map["สวัสดิการ"],
            "content": json.dumps({
                "type": "text",
                "text": "💊 สิทธิค่ารักษาพยาบาล\n\n✅ ผู้มีสิทธิ:\n• ข้าราชการ\n• คู่สมรส\n• บุตรไม่เกิน 3 คน (อายุไม่เกิน 20 ปี)\n• บิดามารดา\n\n📋 เบิกได้:\n• ค่ารักษาตามจริง\n• ค่าห้อง/ค่าอาหาร ตามสิทธิ\n• ค่าอุปกรณ์ตามประกาศ\n\n📑 เอกสาร: ใบเสร็จ + ใบรับรองแพทย์"
            }),
            "tags": "medical,รักษา,หมอ",
            "priority": 9
        },
        # เงินเดือน
        {
            "name": "การเลื่อนเงินเดือน",
            "description": "หลักเกณฑ์การเลื่อนเงินเดือน",
            "message_type": "text",
            "category_id": cat_map["เงินเดือน"],
            "content": json.dumps({
                "type": "text",
                "text": "💰 การเลื่อนเงินเดือน\n\n📅 รอบการประเมิน:\n• รอบที่ 1: 1 ต.ค. - 31 มี.ค.\n• รอบที่ 2: 1 เม.ย. - 30 ก.ย.\n\n📊 เกณฑ์:\n• ดีเด่น: 3.00-6.00%\n• ดีมาก: 2.00-4.00%\n• ดี: 1.50-3.00%\n• พอใช้: 1.00-2.00%\n\n⚠️ เงื่อนไข: ทำงานไม่น้อยกว่า 4 เดือน"
            }),
            "tags": "salary,เงินเดือน,เลื่อน",
            "priority": 9
        },
        # ระเบียบ
        {
            "name": "เวลาราชการ",
            "description": "เวลาทำงานราชการ",
            "message_type": "text",
            "category_id": cat_map["ระเบียบ"],
            "content": json.dumps({
                "type": "text", 
                "text": "⏰ เวลาราชการ\n\n📅 วันจันทร์ - วันศุกร์:\n• เวลา 08:30 - 16:30 น.\n• พักกลางวัน 12:00 - 13:00 น.\n\n📋 การลงเวลา:\n• สาย: หลัง 08:30 น.\n• ขาด: ไม่มาทำงานโดยไม่ลา\n• ออกก่อน: ต้องได้รับอนุญาต\n\n⚠️ สายเกิน 3 ครั้ง/เดือน มีผลต่อการประเมิน"
            }),
            "tags": "time,เวลา,ทำงาน",
            "priority": 8
        },
        # ทั่วไป
        {
            "name": "ติดต่อ HR",
            "description": "ช่องทางติดต่อ HR",
            "message_type": "text",
            "category_id": cat_map["ทั่วไป"],
            "content": json.dumps({
                "type": "text",
                "text": "📞 ติดต่อกองบริหารทรัพยากรบุคคล\n\n🏢 ที่อยู่:\nสำนักงานปลัดกระทรวงยุติธรรม\nชั้น 5 อาคาร A\n\n☎️ โทรศัพท์:\n• สายใน: 1234\n• สายนอก: 02-123-4567\n\n📧 Email: hr@moj.go.th\n\n⏰ เวลาทำการ:\nจันทร์-ศุกร์ 08:30-16:30 น."
            }),
            "tags": "contact,ติดต่อ,hr",
            "priority": 7
        }
    ]
    
    print("\nAdding Templates...")
    added = 0
    for t in templates:
        existing = db.query(MessageTemplate).filter_by(name=t["name"]).first()
        if not existing:
            template = MessageTemplate(**t)
            db.add(template)
            added += 1
            print(f"✅ Added: {t['name']}")
    
    db.commit()
    
    # Show summary
    print(f"\n📊 Summary:")
    print(f"Categories: {db.query(MessageCategory).count()}")
    print(f"Templates: {db.query(MessageTemplate).count()}")
    print(f"New templates added: {added}")
    
    db.close()

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    add_hr_data()
    print("\n✅ HR Templates initialization completed!")
