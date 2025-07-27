#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
เพิ่ม HR Templates พื้นฐานสำหรับ Phase 1
"""
import sqlite3
import json
from datetime import datetime

def add_hr_templates_phase1():
    conn = sqlite3.connect("line_agent.db")
    cursor = conn.cursor()
    
    try:
        # Get category IDs
        cursor.execute("SELECT id FROM message_categories WHERE name = 'การลา'")
        leave_cat_id = cursor.fetchone()[0]
        
        cursor.execute("SELECT id FROM message_categories WHERE name = 'สวัสดิการ'")
        welfare_cat_id = cursor.fetchone()[0]
        
        cursor.execute("SELECT id FROM message_categories WHERE name = 'ทักทาย'")
        greeting_cat_id = cursor.fetchone()[0]
        
        # HR Templates to add
        templates = [
            # การลา - Text with Quick Reply
            {
                "name": "เมนูการลา",
                "description": "แสดงเมนูเลือกประเภทการลา",
                "message_type": "text",
                "category_id": leave_cat_id,
                "content": json.dumps({
                    "type": "text",
                    "text": "📋 ข้อมูลการลา\n\nกรุณาเลือกประเภทการลาที่ต้องการทราบข้อมูล:",
                    "quickReply": {
                        "items": [
                            {"action": {"type": "message", "label": "ลาป่วย", "text": "ขอข้อมูลการลาป่วย"}},
                            {"action": {"type": "message", "label": "ลาพักผ่อน", "text": "ขอข้อมูลการลาพักผ่อน"}},
                            {"action": {"type": "message", "label": "ลากิจ", "text": "ขอข้อมูลการลากิจ"}},
                            {"action": {"type": "message", "label": "ลาคลอด", "text": "ขอข้อมูลการลาคลอด"}},
                            {"action": {"type": "message", "label": "สิทธิการลาทั้งหมด", "text": "ดูสิทธิการลาทั้งหมด"}}
                        ]
                    }
                })
            },
            
            # การลาป่วย - Flex Message
            {
                "name": "ข้อมูลการลาป่วย",
                "description": "รายละเอียดสิทธิการลาป่วย",
                "message_type": "flex",
                "category_id": leave_cat_id,
                "content": json.dumps({
                    "type": "flex",
                    "altText": "ข้อมูลการลาป่วย",
                    "contents": {
                        "type": "bubble",
                        "header": {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [{
                                "type": "text",
                                "text": "🏥 สิทธิการลาป่วย",
                                "weight": "bold",
                                "size": "lg",
                                "color": "#2196F3"
                            }]
                        },
                        "body": {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {"type": "text", "text": "📌 สิทธิการลา", "weight": "bold", "margin": "md"},
                                {"type": "text", "text": "• ลาได้เท่าที่ป่วยจริง", "wrap": True, "margin": "sm"},
                                {"type": "text", "text": "• ไม่เกิน 60 วันทำการ/ปี", "wrap": True, "margin": "sm"},
                                {"type": "separator", "margin": "lg"},
                                {"type": "text", "text": "📋 เงื่อนไข", "weight": "bold", "margin": "lg"},
                                {"type": "text", "text": "• เกิน 30 วัน ต้องมีใบรับรองแพทย์", "wrap": True, "margin": "sm"},
                                {"type": "text", "text": "• ได้รับเงินเดือนระหว่างลา", "wrap": True, "margin": "sm"},
                                {"type": "separator", "margin": "lg"},
                                {"type": "text", "text": "อ้างอิง: ระเบียบการลา พ.ศ. 2555", "size": "xs", "color": "#666666", "margin": "lg"}
                            ]
                        }
                    }
                })
            },
            
            # การลาพักผ่อน
            {
                "name": "ข้อมูลการลาพักผ่อน",
                "description": "รายละเอียดสิทธิการลาพักผ่อน",
                "message_type": "text",
                "category_id": leave_cat_id,
                "content": json.dumps({
                    "type": "text",
                    "text": "🏖️ สิทธิการลาพักผ่อนประจำปี\n\n"
                           "📌 สิทธิการลา:\n"
                           "• ทำงานครบ 6 เดือน: มีสิทธิ 10 วัน\n"
                           "• ทำงานครบ 1 ปีขึ้นไป: 10 วัน/ปี\n\n"
                           "📋 การสะสมวันลา:\n"
                           "• สะสมได้ไม่เกิน 20 วันทำการ\n"
                           "• วันที่เหลือจะถูกสะสมไปปีถัดไป\n\n"
                           "💡 หมายเหตุ: นับเฉพาะวันทำการ ไม่รวมวันหยุดราชการ"
                })
            },
            
            # สวัสดิการ - ค่ารักษาพยาบาล
            {
                "name": "สิทธิค่ารักษาพยาบาล",
                "description": "ข้อมูลการเบิกค่ารักษาพยาบาล",
                "message_type": "flex",
                "category_id": welfare_cat_id,
                "content": json.dumps({
                    "type": "flex",
                    "altText": "สิทธิค่ารักษาพยาบาล",
                    "contents": {
                        "type": "bubble",
                        "header": {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [{
                                "type": "text",
                                "text": "💊 สิทธิค่ารักษาพยาบาล",
                                "weight": "bold",
                                "size": "lg",
                                "color": "#4CAF50"
                            }]
                        },
                        "body": {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {"type": "text", "text": "📌 ผู้มีสิทธิ", "weight": "bold"},
                                {"type": "text", "text": "• ตนเอง", "margin": "sm"},
                                {"type": "text", "text": "• คู่สมรส", "margin": "sm"},
                                {"type": "text", "text": "• บิดามารดา", "margin": "sm"},
                                {"type": "text", "text": "• บุตรอายุไม่เกิน 20 ปี", "margin": "sm"},
                                {"type": "separator", "margin": "lg"},
                                {"type": "text", "text": "💰 วงเงิน: เบิกได้ตามจริง", "weight": "bold", "margin": "lg"},
                                {"type": "text", "text": "📍 สถานพยาบาล: รัฐและเอกชนที่กำหนด", "margin": "sm", "wrap": True}
                            ]
                        }
                    }
                })
            },
            
            # ทักทาย HR Bot
            {
                "name": "ทักทาย HR Bot",
                "description": "ข้อความต้อนรับสำหรับ HR Bot",
                "message_type": "text",
                "category_id": greeting_cat_id,
                "content": json.dumps({
                    "type": "text",
                    "text": "สวัสดีค่ะ 🙏\n\n"
                           "ยินดีต้อนรับสู่ระบบ HR Bot\n"
                           "กองบริหารทรัพยากรบุคคล กระทรวงยุติธรรม\n\n"
                           "มีอะไรให้ช่วยเหลือคะ?",
                    "quickReply": {
                        "items": [
                            {"action": {"type": "message", "label": "📋 การลา", "text": "ขอข้อมูลการลา"}},
                            {"action": {"type": "message", "label": "💊 สวัสดิการ", "text": "ขอข้อมูลสวัสดิการ"}},
                            {"action": {"type": "message", "label": "💰 เงินเดือน", "text": "ขอข้อมูลเงินเดือน"}},
                            {"action": {"type": "message", "label": "📞 ติดต่อ HR", "text": "ติดต่อ HR"}}
                        ]
                    }
                })
            },
            
            # สิทธิการลาทั้งหมด
            {
                "name": "สิทธิการลาทั้งหมด",
                "description": "สรุปสิทธิการลาทุกประเภท",
                "message_type": "text",
                "category_id": leave_cat_id,
                "content": json.dumps({
                    "type": "text",
                    "text": "📋 สิทธิการลาข้าราชการ (สรุป)\n\n"
                           "🏥 ลาป่วย: 60 วัน/ปี\n"
                           "🏖️ ลาพักผ่อน: 10 วัน/ปี\n"
                           "📝 ลากิจส่วนตัว: 45 วัน/ปี\n"
                           "🤰 ลาคลอดบุตร: 90 วัน\n"
                           "👶 ลาช่วยภริยาคลอด: 15 วัน\n"
                           "🎓 ลาศึกษาต่อ: ตามที่ได้รับอนุมัติ\n"
                           "⛪ ลาอุปสมบท: 120 วัน\n\n"
                           "💡 หมายเหตุ: สิทธิอาจแตกต่างตามอายุราชการ"
                })
            }
        ]
        
        # Insert templates
        for template in templates:
            cursor.execute("""
                INSERT INTO message_templates 
                (name, description, message_type, category_id, content, is_active, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, 1, ?, ?)
            """, (
                template['name'],
                template['description'],
                template['message_type'],
                template['category_id'],
                template['content'],
                datetime.now(),
                datetime.now()
            ))
        
        conn.commit()
        print(f"✅ เพิ่ม HR Templates สำเร็จ {len(templates)} รายการ")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    add_hr_templates_phase1()