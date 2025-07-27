"""
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
        lines = content.split('\n')
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
            return "\n".join(relevant_lines[:50])  # จำกัดไม่เกิน 50 บรรทัด
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
            
            return f"พบข้อมูลที่เกี่ยวข้อง:\n{content[start:end]}..."
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
