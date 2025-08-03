#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for JSON search functionality
ทดสอบระบบค้นหาจากไฟล์ JSON ใหม่
"""
import os
import sys
import json

# Add the backend app to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(current_dir, 'backend')
sys.path.insert(0, backend_dir)

def test_json_files():
    """ทดสอบการอ่านไฟล์ JSON"""
    print("[TEST] ทดสอบการอ่านไฟล์ JSON...")
    
    # Test FAQ JSON
    faq_file = os.path.join("backend", "data", "json", "faq.json")
    if os.path.exists(faq_file):
        print("[OK] พบไฟล์ faq.json")
        try:
            with open(faq_file, 'r', encoding='utf-8') as f:
                faq_data = json.load(f)
                categories = faq_data.get('categories', [])
                total_faqs = sum(len(cat.get('faqs', [])) for cat in categories)
                print(f"   - จำนวน categories: {len(categories)}")
                print(f"   - จำนวน FAQ ทั้งหมด: {total_faqs}")
        except Exception as e:
            print(f"   [ERROR] Error reading FAQ JSON: {e}")
    else:
        print("[ERROR] ไม่พบไฟล์ faq.json")
    
    # Test Culture JSON
    culture_file = os.path.join("backend", "data", "json", "culture_org.json")
    if os.path.exists(culture_file):
        print("[OK] พบไฟล์ culture_org.json")
        try:
            with open(culture_file, 'r', encoding='utf-8') as f:
                culture_data = json.load(f)
                core_values = culture_data.get('core_values', {}).get('values', [])
                culture_elements = culture_data.get('organizational_culture', {}).get('elements', [])
                print(f"   - จำนวน core values: {len(core_values)}")
                print(f"   - จำนวน culture elements: {len(culture_elements)}")
        except Exception as e:
            print(f"   [ERROR] Error reading Culture JSON: {e}")
    else:
        print("[ERROR] ไม่พบไฟล์ culture_org.json")

def test_search_functions():
    """ทดสอบฟังก์ชันค้นหา"""
    print("\n[TEST] ทดสอบฟังก์ชันค้นหา...")
    
    try:
        from app.hr_tools import search_hr_faq_json, search_culture_values_json, search_all_hr_data
        print("[OK] Import ฟังก์ชันสำเร็จ")
        
        # Test FAQ search
        print("\n[FAQ] ทดสอบค้นหา FAQ:")
        test_queries = ["ติดต่อ", "โทรศัพท์", "ลาป่วย"]
        
        for query in test_queries:
            print(f"\n[SEARCH] ค้นหา: '{query}'")
            try:
                result = search_hr_faq_json(query)
                if "ไม่พบข้อมูล" not in result and "Error" not in result:
                    print("[OK] พบผลลัพธ์")
                    lines = result.split('\n')
                    for line in lines[:3]:
                        if line.strip() and not line.startswith('🔍'):
                            print(f"   {line}")
                else:
                    print("[NOT_FOUND] ไม่พบผลลัพธ์")
            except Exception as e:
                print(f"[ERROR] {e}")
        
        # Test Culture search  
        print("\n[CULTURE] ทดสอบค้นหาวัฒนธรรมองค์กร:")
        culture_queries = ["สุจริต", "JUSTICE", "ค่านิยม"]
        
        for query in culture_queries:
            print(f"\n[SEARCH] ค้นหา: '{query}'")
            try:
                result = search_culture_values_json(query)
                if "ไม่พบข้อมูล" not in result and "Error" not in result:
                    print("[OK] พบผลลัพธ์")
                    lines = result.split('\n')
                    for line in lines[:3]:
                        if line.strip() and not line.startswith('🏛️'):
                            print(f"   {line}")
                else:
                    print("[NOT_FOUND] ไม่พบผลลัพธ์")
            except Exception as e:
                print(f"[ERROR] {e}")
                
    except ImportError as e:
        print(f"[ERROR] ไม่สามารถ import ฟังก์ชัน: {e}")
        print("[INFO] ตรวจสอบ Python path และ dependencies")

def main():
    """ฟังก์ชันหลัก"""
    print("===== ระบบทดสอบการค้นหาข้อมูล HR จากไฟล์ JSON =====")
    
    # เปลี่ยนไปยัง directory ที่ถูกต้อง
    os.chdir(current_dir)
    print(f"[INFO] Working directory: {current_dir}")
    
    # ทดสอบไฟล์ JSON
    test_json_files()
    
    # ทดสอบฟังก์ชันค้นหา
    test_search_functions()
    
    print("\n" + "=" * 50)
    print("[DONE] การทดสอบเสร็จสิ้น!")

if __name__ == "__main__":
    main()
