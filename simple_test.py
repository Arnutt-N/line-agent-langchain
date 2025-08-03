#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple test script for JSON search without dependencies
"""
import os
import sys
import json

def simple_search_test():
    """ทดสอบการค้นหาแบบง่าย"""
    print("===== ทดสอบการค้นหา JSON แบบง่าย =====")
    
    # Test FAQ JSON
    faq_file = os.path.join("backend", "data", "json", "faq.json")
    if not os.path.exists(faq_file):
        print("ERROR: ไม่พบไฟล์ faq.json")
        return
    
    with open(faq_file, 'r', encoding='utf-8') as f:
        faq_data = json.load(f)
    
    # Simple search function
    def search_faq(query):
        results = []
        query_lower = query.lower()
        
        for category in faq_data.get('categories', []):
            for faq in category.get('faqs', []):
                score = 0
                
                # Check keywords
                for keyword in faq.get('keywords', []):
                    if query_lower in keyword.lower():
                        score += 10
                
                # Check question
                questions = faq.get('question', [])
                if isinstance(questions, str):
                    questions = [questions]
                
                for question in questions:
                    if query_lower in question.lower():
                        score += 5
                
                # Check answer
                if query_lower in faq.get('answer', '').lower():
                    score += 3
                
                if score > 0:
                    results.append({
                        'faq': faq,
                        'category': category.get('name', ''),
                        'score': score
                    })
        
        results.sort(key=lambda x: x['score'], reverse=True)
        return results
    
    # Test queries
    test_queries = [
        "ติดต่อ",
        "โทรศัพท์", 
        "email",
        "ลาป่วย",
        "กองบริหาร"
    ]
    
    for query in test_queries:
        print(f"\n[SEARCH] ค้นหา: '{query}'")
        results = search_faq(query)
        
        if results:
            print(f"[OK] พบ {len(results)} ผลลัพธ์")
            for i, result in enumerate(results[:2]):  # แสดง 2 ผลลัพธ์แรก
                faq = result['faq']
                questions = faq.get('question', [])
                if isinstance(questions, str):
                    questions = [questions]
                
                print(f"  {i+1}. คะแนน: {result['score']}")
                print(f"     หมวด: {result['category']}")
                print(f"     คำถาม: {questions[0][:100]}...")
                print(f"     คำตอบ: {faq.get('answer', '')[:100]}...")
        else:
            print("[NOT_FOUND] ไม่พบผลลัพธ์")

def test_culture_search():
    """ทดสอบการค้นหาวัฒนธรรม"""
    print("\n===== ทดสอบการค้นหาวัฒนธรรมองค์กร =====")
    
    culture_file = os.path.join("backend", "data", "json", "culture_org.json")
    if not os.path.exists(culture_file):
        print("ERROR: ไม่พบไฟล์ culture_org.json")
        return
    
    with open(culture_file, 'r', encoding='utf-8') as f:
        culture_data = json.load(f)
    
    def search_culture(query):
        results = []
        query_lower = query.lower()
        
        # Search in core values
        for value in culture_data.get('core_values', {}).get('values', []):
            score = 0
            
            # Check name
            if query_lower in value.get('name', '').lower():
                score += 10
            
            # Check keywords
            for keyword in value.get('keywords', []):
                if query_lower in keyword.lower():
                    score += 8
            
            # Check definition
            if query_lower in value.get('definition', '').lower():
                score += 5
            
            if score > 0:
                results.append({
                    'type': 'core_value',
                    'data': value,
                    'score': score
                })
        
        # Search in culture elements
        for element in culture_data.get('organizational_culture', {}).get('elements', []):
            score = 0
            
            # Check word/meaning
            if query_lower in element.get('word', '').lower():
                score += 10
            if query_lower in element.get('meaning', '').lower():
                score += 8
            
            # Check keywords
            for keyword in element.get('keywords', []):
                if query_lower in keyword.lower():
                    score += 6
            
            if score > 0:
                results.append({
                    'type': 'culture_element',
                    'data': element,
                    'score': score
                })
        
        results.sort(key=lambda x: x['score'], reverse=True)
        return results
    
    # Test culture queries
    culture_queries = [
        "สุจริต",
        "จิตบริการ", 
        "ยุติธรรม",
        "JUSTICE",
        "Innovation"
    ]
    
    for query in culture_queries:
        print(f"\n[SEARCH] ค้นหา: '{query}'")
        results = search_culture(query)
        
        if results:
            print(f"[OK] พบ {len(results)} ผลลัพธ์")
            for i, result in enumerate(results[:2]):
                data = result['data']
                print(f"  {i+1}. คะแนน: {result['score']} ประเภท: {result['type']}")
                
                if result['type'] == 'core_value':
                    print(f"     ชื่อ: {data.get('name', '')} ({data.get('name_en', '')})")
                    print(f"     ความหมาย: {data.get('definition', '')[:100]}...")
                else:
                    print(f"     {data.get('letter', '')} - {data.get('word', '')}")
                    print(f"     ความหมาย: {data.get('meaning', '')}")
        else:
            print("[NOT_FOUND] ไม่พบผลลัพธ์")

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    simple_search_test()
    test_culture_search()
    print("\n===== การทดสอบเสร็จสิ้น =====")

if __name__ == "__main__":
    main()
