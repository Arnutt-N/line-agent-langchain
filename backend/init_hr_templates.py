#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script สำหรับเพิ่ม HR Categories และ Templates
Phase 1 - Quick Setup
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app.database import SessionLocal, engine
from app.models import Base, MessageCategory, MessageTemplate
from sqlalchemy.orm import Session
import json
from datetime import datetime

def init_hr_categories(db: Session):
    """เพิ่ม Categories สำหรับระบบ HR"""
    categories = [
        {"name": "ทักทาย", "description": "ข้อความทักทายและแนะนำตัว", "color": "#4CAF50"},
        {"name": "การลา", "description": "ข้อมูลเกี่ยวกับการลาประเภทต่างๆ", "color": "#2196F3"},
        {"name": "สวัสดิการ", "description": "สิทธิประโยชน์และสวัสดิการ", "color": "#FF9800"},
        {"name": "เงินเดือน", "description": "ข้อมูลเกี่ยวกับเงินเดือนและค่าตอบแทน", "color": "#9C27B0"},
        {"name": "ระเบียบ", "description": "ระเบียบและข้อบังคับ", "color": "#E91E63"},
        {"name": "ทั่วไป", "description": "คำถามทั่วไปเกี่ยวกับ HR", "color": "#607D8B"}
    ]
    
    for cat_data in categories:
        # Check if category exists
        existing = db.query(MessageCategory).filter_by(name=cat_data["name"]).first()
        if not existing:
            category = MessageCategory(**cat_data)
            db.add(category)
            print(f"✅ เพิ่ม Category: {cat_data['name']}")
        else:
            print(f"⏭️  Category '{cat_data['name']}' มีอยู่แล้ว")
    
    db.commit()
    return db.query(MessageCategory).all()

def init_hr_templates(db: Session, categories):
    """เพิ่ม HR Templates พื้นฐาน 20+ รายการ"""
    # Create category mapping
    cat_map = {cat.name: cat.id for cat in categories}
    
    templates = [
        # ทักทาย (3)
        {
            "name": "ทักทายทั่วไป",
            "description": "ข้อความทักทายพื้นฐาน",
            "message_type": "text",
            "category_id": cat_map["ทักทาย"],
            "content": json.dumps({
                "type": "text",
                "text": "สวัสดีค่ะ 🙏\n\nยินดีให้บริการข้อมูล HR\nกองบริหารทรัพยากรบุคคล\nสำนักงานปลัดกระทรวงยุติธรรม\n\nมีอะไรให้ช่วยเหลือคะ?"
            }),
            "tags": "greeting,welcome,สวัสดี"  # Changed from list to comma-separated string
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
            "tags": ["menu", "services", "บริการ"]
        },
        {
            "name": "ขอบคุณ",
            "description": "ตอบกลับคำขอบคุณ",
            "message_type": "text",
            "category_id": cat_map["ทักทาย"],
            "content": json.dumps({
                "type": "text",
                "text": "ยินดีค่ะ 😊\nหากมีคำถามเพิ่มเติมสามารถสอบถามได้ตลอดเวลานะคะ"
            }),
            "tags": ["thanks", "ขอบคุณ"]
        },
        
        # การลา (7)
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
                            {"type": "text", "text": "👨‍👩‍👦 ลาเพื่อดูแลภรรยาคลอด: 15 วัน", "wrap": True},
                            {"type": "separator", "margin": "md"},
                            {"type": "text", "text": "📌 อ้างอิง: ระเบียบการลาฯ พ.ศ. 2555", "size": "xs", "color": "#999999"}
                        ]
                    }
                }
            }),
            "tags": ["leave", "all", "สิทธิ", "ลา"]
        },
        {
            "name": "ลาป่วย",
            "description": "ข้อมูลการลาป่วย",
            "message_type": "text",
            "category_id": cat_map["การลา"],
            "content": json.dumps({
                "type": "text",
                "text": "🏥 การลาป่วย\n\n✅ สิทธิ: ลาได้เท่าที่ป่วยจริง (ไม่เกิน 60 วันทำการ/ปี)\n✅ ได้รับเงินเดือนระหว่างลา\n\n📋 เงื่อนไข:\n• ลาติดต่อเกิน 3 วัน ต้องมีใบรับรองแพทย์\n• ลาเกิน 30 วัน ต้องมีใบรับรองแพทย์จากโรงพยาบาลรัฐ\n\n📌 ระเบียบการลาฯ พ.ศ. 2555 ข้อ 18-20"
            }),
            "tags": ["sick", "ป่วย", "ลาป่วย"]
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
            "tags": ["vacation", "พักผ่อน", "ลาพักผ่อน"]
        },
        {
            "name": "ลากิจส่วนตัว",
            "description": "ข้อมูลการลากิจส่วนตัว",
            "message_type": "text",
            "category_id": cat_map["การลา"],
            "content": json.dumps({
                "type": "text",
                "text": "📝 การลากิจส่วนตัว\n\n✅ สิทธิ: 45 วันทำการ/ปี\n❌ ไม่ได้รับเงินเดือนระหว่างลา\n\n📋 เงื่อนไข:\n• ต้องขออนุมัติล่วงหน้า\n• ผู้บังคับบัญชามีสิทธิไม่อนุญาตได้\n• ไม่สามารถสะสมได้\n\n💡 ใช้เมื่อมีธุระจำเป็นที่ไม่ใช่การลาประเภทอื่น"
            }),
            "tags": ["personal", "กิจ", "ลากิจ"]
        },
        {
            "name": "ลาคลอดบุตร",
            "description": "ข้อมูลการลาคลอดบุตร",
            "message_type": "text",
            "category_id": cat_map["การลา"],
            "content": json.dumps({
                "type": "text",
                "text": "👶 การลาคลอดบุตร\n\n✅ สิทธิ: 90 วัน\n✅ ได้รับเงินเดือนระหว่างลา\n\n📋 เงื่อนไข:\n• ลาได้ไม่เกิน 90 วัน/ครรภ์\n• นับรวมวันหยุดราชการ\n• ลาก่อนคลอดได้ไม่เกิน 45 วัน\n\n💡 สามีมีสิทธิลาเพื่อดูแลภรรยา 15 วันทำการ"
            }),
            "tags": ["maternity", "คลอด", "ท้อง"]
        },
        {
            "name": "ลาศึกษาต่อ",
            "description": "ข้อมูลการลาศึกษาต่อ",
            "message_type": "text",
            "category_id": cat_map["การลา"],
            "content": json.dumps({
                "type": "text",
                "text": "🎓 การลาศึกษาต่อ\n\n📋 เงื่อนไข:\n• รับราชการมาแล้วไม่น้อยกว่า 1 ปี\n• ต้องได้รับอนุมัติจากหน่วยงาน\n• ศึกษาในสาขาที่เป็นประโยชน์ต่อราชการ\n\n📑 เอกสาร:\n• แบบคำขอลา (แบบ ศต.1)\n• หนังสือตอบรับจากสถานศึกษา\n• หลักสูตรการศึกษา\n\n⏱️ ยื่นล่วงหน้า 60 วัน"
            }),
            "tags": ["study", "ศึกษา", "เรียนต่อ"]
        },
        {
            "name": "ขั้นตอนการลา",
            "description": "ขั้นตอนการยื่นใบลา",
            "message_type": "text",
            "category_id": cat_map["การลา"],
            "content": json.dumps({
                "type": "text",
                "text": "📋 ขั้นตอนการลา\n\n1️⃣ กรอกใบลาตามแบบฟอร์ม\n2️⃣ ยื่นผ่านหัวหน้างานโดยตรง\n3️⃣ รอการอนุมัติ\n4️⃣ แจ้งผลการอนุมัติ\n\n⏱️ ระยะเวลา:\n• ลาป่วย: ยื่นวันแรกที่กลับมาทำงาน\n• ลาพักผ่อน/กิจ: ยื่นล่วงหน้า 3-7 วัน\n\n📞 สอบถาม: กลุ่มงานทรัพยากรบุคคล"
            }),
            "tags": ["process", "ขั้นตอน", "วิธี"]
        },
        
        # สวัสดิการ (5)
        {
            "name": "สวัสดิการทั้งหมด",
            "description": "ภาพรวมสวัสดิการ",
            "message_type": "text",
            "category_id": cat_map["สวัสดิการ"],
            "content": json.dumps({
                "type": "text",
                "text": "💰 สวัสดิการข้าราชการ\n\n✅ ค่ารักษาพยาบาล (ตนเอง+ครอบครัว)\n✅ ค่าเล่าเรียนบุตร\n✅ เงินช่วยเหลือบุตร\n✅ ค่าเช่าบ้าน\n✅ เงินกู้สวัสดิการ\n✅ บำเหน็จบำนาญ\n✅ เครื่องราชอิสริยาภรณ์\n\n📞 สอบถามรายละเอียด: 02-123-4567"
            }),
            "tags": ["welfare", "สวัสดิการ", "สิทธิ"]
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
            "tags": ["medical", "รักษา", "หมอ"]
        },
        {
            "name": "ค่าเล่าเรียนบุตร",
            "description": "สิทธิค่าเล่าเรียนบุตร",
            "message_type": "text",
            "category_id": cat_map["สวัสดิการ"],
            "content": json.dumps({
                "type": "text",
                "text": "🎓 ค่าเล่าเรียนบุตร\n\n✅ เบิกได้:\n• อนุบาล - ปริญญาตรี\n• บุตรไม่เกิน 3 คน\n• อายุไม่เกิน 25 ปี\n\n💰 อัตราเบิก:\n• รัฐบาล: เต็มจำนวน\n• เอกชน: ตามประกาศ กค.\n\n📑 เอกสาร:\n• ใบเสร็จค่าเทอม\n• หนังสือรับรองการศึกษา"
            }),
            "tags": ["education", "เรียน", "ค่าเทอม"]
        },
        {
            "name": "เงินกู้สวัสดิการ",
            "description": "เงินกู้สำหรับข้าราชการ",
            "message_type": "text",
            "category_id": cat_map["สวัสดิการ"],
            "content": json.dumps({
                "type": "text",
                "text": "💵 เงินกู้สวัสดิการ\n\n✅ ประเภท:\n• กู้เพื่อเหตุฉุกเฉิน\n• กู้เพื่อการศึกษา\n• กู้เพื่อที่อยู่อาศัย\n\n📋 เงื่อนไข:\n• รับราชการมาแล้ว 1 ปี\n• ไม่มีหนี้ค้างชำระ\n• มีผู้ค้ำประกัน\n\n💰 วงเงิน: ตามประเภทการกู้\n📞 ติดต่อ: สหกรณ์ออมทรัพย์"
            }),
            "tags": ["loan", "กู้", "ยืม"]
        },
        {
            "name": "บำเหน็จบำนาญ",
            "description": "สิทธิบำเหน็จบำนาญ",
            "message_type": "text",
            "category_id": cat_map["สวัสดิการ"],
            "content": json.dumps({
                "type": "text",
                "text": "🏦 บำเหน็จบำนาญ\n\n✅ สิทธิ:\n• รับราชการ 10 ปีขึ้นไป\n• อายุครบ 60 ปี\n• เกษียณอายุราชการ\n\n💰 การคำนวณ:\n• บำนาญ = เงินเดือนสุดท้าย x จำนวนปี x 0.02\n• บำเหน็จ = เงินเดือนสุดท้าย x จำนวนปี\n\n📑 เตรียมเอกสารล่วงหน้า 6 เดือน"
            }),
            "tags": ["pension", "เกษียณ", "บำนาญ"]
        },
        
        # เงินเดือน (2)
        {
            "name": "การเลื่อนเงินเดือน",
            "description": "หลักเกณฑ์การเลื่อนเงินเดือน",
            "message_type": "text",
            "category_id": cat_map["เงินเดือน"],
            "content": json.dumps({
                "type": "text",
                "text": "💰 การเลื่อนเงินเดือน\n\n📅 รอบการประเมิน:\n• รอบที่ 1: 1 ต.ค. - 31 มี.ค.\n• รอบที่ 2: 1 เม.ย. - 30 ก.ย.\n\n📊 เกณฑ์:\n• ดีเด่น: 3.00-6.00%\n• ดีมาก: 2.00-4.00%\n• ดี: 1.50-3.00%\n• พอใช้: 1.00-2.00%\n\n⚠️ เงื่อนไข: ทำงานไม่น้อยกว่า 4 เดือน"
            }),
            "tags": ["salary", "เงินเดือน", "เลื่อน"]
        },
        {
            "name": "เงินเพิ่มพิเศษ",
            "description": "เงินเพิ่มและค่าตอบแทนพิเศษ",
            "message_type": "text",
            "category_id": cat_map["เงินเดือน"],
            "content": json.dumps({
                "type": "text",
                "text": "💵 เงินเพิ่มพิเศษ\n\n✅ ประเภท:\n• ค.ต.ส. (ค่าตอบแทนพิเศษ)\n• เงินประจำตำแหน่ง\n• เงินค่าตอบแทนนอกเวลา\n• เงินเพิ่มพิเศษสำหรับการสู้รบ (พ.ส.ร.)\n\n📋 เงื่อนไข: ตามประเภทตำแหน่งและภารกิจ\n\n📞 สอบถาม: กลุ่มงานการเงิน"
            }),
            "tags": ["extra", "พิเศษ", "ค่าตอบแทน"]
        },
        
        # ระเบียบ (2)
        {
            "name": "ระเบียบการแต่งกาย",
            "description": "ระเบียบการแต่งกายข้าราชการ",
            "message_type": "text",
            "category_id": cat_map["ระเบียบ"],
            "content": json.dumps({
                "type": "text",
                "text": "👔 ระเบียบการแต่งกาย\n\n📅 วันจันทร์-พฤหัส:\n• ชุดข้าราชการ/ชุดสุภาพ\n\n📅 วันศุกร์:\n• ผ้าไทย/ผ้าพื้นเมือง\n\n📅 วันสำคัญ:\n• ตามที่ทางราชการกำหนด\n\n⚠️ ห้าม:\n• กางเกงยีนส์\n• รองเท้าแตะ\n• เสื้อยืดไม่มีปก"
            }),
            "tags": ["dress", "แต่งกาย", "เครื่องแบบ"]
        },
        {
            "name": "เวลาราชการ",
            "description": "เวลาทำงานราชการ",
            "message_type": "text",
            "category_id": cat_map["ระเบียบ"],
            "content": json.dumps({
                "type": "text",
                "text": "⏰ เวลาราชการ\n\n📅 วันจันทร์ - วันศุกร์:\n• เวลา 08:30 - 16:30 น.\n• พักกลางวัน 12:00 - 13:00 น.\n\n📋 การลงเวลา:\n• สาย: หลัง 08:30 น.\n• ขาด: ไม่มาทำงานโดยไม่ลา\n• ออกก่อน: ต้องได้รับอนุญาต\n\n⚠️ สายเกิน 3 ครั้ง/เดือน มีผลต่อการประเมิน"
            }),
            "tags": ["time", "เวลา", "ทำงาน"]
        },
        
        # ทั่วไป (1)
        {
            "name": "ติดต่อ HR",
            "description": "ช่องทางติดต่อ HR",
            "message_type": "text",
            "category_id": cat_map["ทั่วไป"],
            "content": json.dumps({
                "type": "text",
                "text": "📞 ติดต่อกองบริหารทรัพยากรบุคคล\n\n🏢 ที่อยู่:\nสำนักงานปลัดกระทรวงยุติธรรม\nชั้น 5 อาคาร A\n\n☎️ โทรศัพท์:\n• สายใน: 1234\n• สายนอก: 02-123-4567\n\n📧 Email: hr@moj.go.th\n\n⏰ เวลาทำการ:\nจันทร์-ศุกร์ 08:30-16:30 น."
            }),
            "tags": ["contact", "ติดต่อ", "hr"]
        }
    ]
    
    added_count = 0
    for template_data in templates:
        # Check if template exists
        existing = db.query(MessageTemplate).filter_by(name=template_data["name"]).first()
        if not existing:
            template = MessageTemplate(**template_data)
            db.add(template)
            added_count += 1
            print(f"✅ เพิ่ม Template: {template_data['name']}")
        else:
            print(f"⏭️  Template '{template_data['name']}' มีอยู่แล้ว")
    
    db.commit()
    print(f"\n📊 สรุป: เพิ่ม Templates ใหม่ {added_count} รายการ")
    return added_count

def check_current_status(db: Session):
    """ตรวจสอบสถานะปัจจุบัน"""
    print("\n📊 สถานะปัจจุบันของระบบ:")
    print("-" * 50)
    
    # Check categories
    categories = db.query(MessageCategory).all()
    print(f"✅ Categories ทั้งหมด: {len(categories)} หมวดหมู่")
    for cat in categories:
        template_count = db.query(MessageTemplate).filter_by(category_id=cat.id).count()
        print(f"   - {cat.name}: {template_count} templates")
    
    # Check templates
    total_templates = db.query(MessageTemplate).count()
    print(f"\n✅ Templates ทั้งหมด: {total_templates} รายการ")
    
    # Check users
    from app.models import LineUser
    users = db.query(LineUser).count()
    print(f"✅ Users ทั้งหมด: {users} คน")
    
    # Check messages
    from app.models import ChatMessage
    messages = db.query(ChatMessage).count()
    print(f"✅ Messages ทั้งหมด: {messages} ข้อความ")
    
    print("-" * 50)

def main():
    """Main function"""
    print("🚀 เริ่มต้น Phase 1: Quick Setup - HR Templates")
    print("=" * 50)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Get database session
    db = SessionLocal()
    
    try:
        # 1. Add HR categories
        print("\n📁 Step 1: เพิ่ม HR Categories...")
        categories = init_hr_categories(db)
        
        # 2. Add HR templates
        print("\n📝 Step 2: เพิ่ม HR Templates...")
        init_hr_templates(db, categories)
        
        # 3. Check status
        check_current_status(db)
        
        print("\n✅ Phase 1 เสร็จสมบูรณ์!")
        print("🎯 ระบบพร้อมใช้งานสำหรับ HR Bot")
        
    except Exception as e:
        print(f"\n❌ เกิดข้อผิดพลาด: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
