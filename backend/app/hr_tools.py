"""
HR Bot Tools - เครื่องมือเพิ่มเติมสำหรับ HR Bot
"""
from langchain.tools import tool
import os
import json
import re
from typing import List, Dict, Any

def search_json_by_keywords(data: Dict[Any, Any], query: str) -> List[Dict[str, Any]]:
    """ค้นหาข้อมูลใน JSON โดยใช้ keywords และ fuzzy matching"""
    results = []
    query_lower = query.lower()
    
    def extract_text_recursive(obj, parent_key=""):
        """ดึงข้อความจากโครงสร้าง JSON แบบ recursive"""
        texts = []
        if isinstance(obj, dict):
            for key, value in obj.items():
                texts.extend(extract_text_recursive(value, key))
        elif isinstance(obj, list):
            for item in obj:
                texts.extend(extract_text_recursive(item, parent_key))
        elif isinstance(obj, str):
            texts.append((parent_key, obj))
        return texts
    
    def calculate_relevance_score(item: Dict[str, Any], query: str) -> float:
        """คำนวณคะแนนความเกี่ยวข้อง"""
        score = 0.0
        query_words = query.lower().split()
        
        # ตรวจสอบใน keywords (คะแนนสูงสุด)
        if 'keywords' in item:
            for keyword in item.get('keywords', []):
                for word in query_words:
                    if word in keyword.lower():
                        score += 10
                    elif keyword.lower() in query.lower():
                        score += 8
        
        # ตรวจสอบใน question
        if 'question' in item:
            questions = item['question'] if isinstance(item['question'], list) else [item['question']]
            for question in questions:
                for word in query_words:
                    if word in question.lower():
                        score += 5
                    # Exact phrase match
                    if query.lower() in question.lower():
                        score += 15
        
        # ตรวจสอบใน answer
        if 'answer' in item:
            for word in query_words:
                if word in item['answer'].lower():
                    score += 3
        
        # ตรวจสอบใน name, title
        for field in ['name', 'title', 'meaning']:
            if field in item:
                for word in query_words:
                    if word in str(item[field]).lower():
                        score += 7
        
        return score    
    # ค้นหาใน FAQ categories
    if 'categories' in data:
        for category in data['categories']:
            if 'faqs' in category:
                for faq in category['faqs']:
                    score = calculate_relevance_score(faq, query)
                    if score > 0:
                        result = {
                            'type': 'faq',
                            'category': category.get('name', ''),
                            'id': faq.get('id', ''),
                            'question': faq.get('question', ''),
                            'answer': faq.get('answer', ''),
                            'keywords': faq.get('keywords', []),
                            'link': faq.get('link', ''),
                            'links': faq.get('links', []),
                            'contacts': faq.get('contacts', {}),
                            'score': score
                        }
                        results.append(result)
    
    # ค้นหาใน core values
    if 'core_values' in data and 'values' in data['core_values']:
        for value in data['core_values']['values']:
            score = calculate_relevance_score(value, query)
            if score > 0:
                result = {
                    'type': 'core_value',
                    'id': value.get('id', ''),
                    'name': value.get('name', ''),
                    'name_en': value.get('name_en', ''),
                    'definition': value.get('definition', ''),
                    'keywords': value.get('keywords', []),
                    'behaviors': value.get('behaviors', []),
                    'score': score
                }
                results.append(result)
    
    # ค้นหาใน organizational culture
    if 'organizational_culture' in data and 'elements' in data['organizational_culture']:
        for element in data['organizational_culture']['elements']:
            score = calculate_relevance_score(element, query)
            if score > 0:
                result = {
                    'type': 'culture_element',
                    'id': element.get('id', ''),
                    'letter': element.get('letter', ''),
                    'word': element.get('word', ''),
                    'meaning': element.get('meaning', ''),
                    'description': element.get('description', ''),
                    'keywords': element.get('keywords', []),
                    'behaviors': element.get('behaviors', []),
                    'score': score
                }
                results.append(result)
    
    # เรียงลำดับตามคะแนน
    results.sort(key=lambda x: x['score'], reverse=True)
    return results
@tool
def search_hr_faq_json(query: str) -> str:
    """ค้นหาคำตอบจากไฟล์ FAQ JSON"""
    try:
        faq_file = os.path.join("data", "json", "faq.json")
        if not os.path.exists(faq_file):
            return "ไม่พบไฟล์ FAQ JSON"
        
        with open(faq_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        results = search_json_by_keywords(data, query)
        
        if not results:
            return "❌ ไม่พบข้อมูลที่เกี่ยวข้องใน FAQ"
        
        # จัดรูปแบบผลลัพธ์
        output = []
        output.append(f"🔍 ผลการค้นหา FAQ สำหรับ: '{query}'\n")
        
        # แสดงผลลัพธ์ที่ดีที่สุด (สูงสุด 3 รายการ)
        for i, result in enumerate(results[:3]):
            output.append(f"📋 ผลลัพธ์ที่ {i+1}:")
            output.append(f"หมวดหมู่: {result['category']}")
            
            # แสดง question(s)
            questions = result['question'] if isinstance(result['question'], list) else [result['question']]
            output.append(f"❓ คำถาม: {questions[0]}")
            
            output.append(f"✅ คำตอบ: {result['answer']}")
            
            # แสดง links หากมี
            if result.get('link'):
                output.append(f"🔗 ลิงก์: {result['link']}")
            
            if result.get('links'):
                output.append("🔗 ลิงก์ที่เกี่ยวข้อง:")
                for link in result['links'][:3]:  # แสดงแค่ 3 ลิงก์แรก
                    output.append(f"   • {link.get('name', '')}: {link.get('url', '')}")
            
            output.append("─" * 40)
        
        return "\n".join(output)
            
    except Exception as e:
        return f"❌ เกิดข้อผิดพลาดในการค้นหา FAQ: {str(e)}"
@tool
def search_culture_values_json(query: str) -> str:
    """ค้นหาข้อมูลวัฒนธรรมและค่านิยมองค์กรจากไฟล์ JSON"""
    try:
        culture_file = os.path.join("data", "json", "culture_org.json")
        if not os.path.exists(culture_file):
            return "ไม่พบไฟล์วัฒนธรรมองค์กร JSON"
        
        with open(culture_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        results = search_json_by_keywords(data, query)
        
        if not results:
            return "❌ ไม่พบข้อมูลวัฒนธรรมองค์กรที่เกี่ยวข้อง"
        
        output = []
        output.append(f"🏛️ ผลการค้นหาวัฒนธรรมองค์กรสำหรับ: '{query}'\n")
        
        # แสดงผลลัพธ์ที่ค้นพบ
        for i, result in enumerate(results[:3]):
            if result['type'] == 'core_value':
                output.append(f"💎 ค่านิยมที่ {i+1}: {result['name']} ({result['name_en']})")
                output.append(f"📖 ความหมาย: {result['definition']}")
                if result.get('behaviors'):
                    output.append("🎭 พฤติกรรมที่พึงประสงค์:")
                    for behavior in result['behaviors'][:4]:  # แสดงแค่ 4 อันแรก
                        output.append(f"   • {behavior}")
                
            elif result['type'] == 'culture_element':
                output.append(f"🎪 วัฒนธรรมองค์กร: {result['letter']} - {result['word']}")
                output.append(f"💫 ความหมาย: {result['meaning']}")
                output.append(f"📝 คำอธิบาย: {result['description']}")
                        
            output.append("─" * 40)
        
        return "\n".join(output)
            
    except Exception as e:
        return f"❌ เกิดข้อผิดพลาดในการค้นหาวัฒนธรรมองค์กร: {str(e)}"

@tool
def search_all_hr_data(query: str) -> str:
    """ค้นหาข้อมูล HR จากทุกแหล่งข้อมูล (JSON และ text files)"""
    try:
        results = []
        
        # ค้นหาจาก FAQ JSON
        faq_result = search_hr_faq_json(query)
        if "❌" not in faq_result:
            results.append(faq_result)
        
        # ค้นหาจาก Culture/Values JSON
        culture_result = search_culture_values_json(query)
        if "❌" not in culture_result:
            results.append(culture_result)
        
        if results:
            final_result = "\n\n".join(results)
            final_result += "\n\n💡 ติดต่อเพิ่มเติม:\n📞 021415192 📧 hrdata@moj.go.th"
            return final_result
        else:
            return "❌ ไม่พบข้อมูลที่เกี่ยวข้อง\n💡 ลองใช้คำค้นหาอื่น หรือติดต่อ 📞 021415192"
            
    except Exception as e:
        return f"❌ เกิดข้อผิดพลาดในการค้นหา: {str(e)}"
# Legacy functions for backward compatibility
@tool
def search_hr_faq(query: str) -> str:
    """ค้นหาคำตอบจากไฟล์ FAQ text (legacy)"""
    return search_hr_faq_json(query)  # Redirect to JSON version

@tool
def search_culture_org(query: str) -> str:
    """ค้นหาข้อมูลวัฒนธรรมองค์กร (legacy)"""
    return search_culture_values_json(query)  # Redirect to JSON version

@tool
def search_hr_policies(query: str) -> str:
    """ค้นหานโยบาย HR ที่เกี่ยวข้อง"""
    try:
        policy_file = os.path.join("data", "text", "policies.txt")
        if not os.path.exists(policy_file):
            return "ไม่พบไฟล์นโยบาย"
        
        with open(policy_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if query.lower() in content.lower():
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