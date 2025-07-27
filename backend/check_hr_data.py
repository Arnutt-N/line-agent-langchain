#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script ตรวจสอบ HR Categories และ Templates ในฐานข้อมูล
"""
import sqlite3
import json
import sys
import io

# Fix encoding issue
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def check_hr_data():
    conn = sqlite3.connect("line_agent.db")
    cursor = conn.cursor()
    
    try:
        # Check categories
        cursor.execute("SELECT COUNT(*) FROM message_categories")
        cat_count = cursor.fetchone()[0]
        print(f"Categories Total: {cat_count}")
        
        cursor.execute("SELECT id, name, description FROM message_categories")
        categories = cursor.fetchall()
        print("\nCategories List:")
        for cat in categories:
            print(f"  [{cat[0]}] {cat[1]} - {cat[2]}")
        
        # Check templates
        cursor.execute("SELECT COUNT(*) FROM message_templates")
        template_count = cursor.fetchone()[0]
        print(f"\nTemplates Total: {template_count}")
        
        # Templates by category
        cursor.execute("""
            SELECT c.name, COUNT(t.id) 
            FROM message_categories c 
            LEFT JOIN message_templates t ON c.id = t.category_id 
            GROUP BY c.id, c.name
        """)
        template_stats = cursor.fetchall()
        print("\nTemplates by Category:")
        for stat in template_stats:
            print(f"  {stat[0]}: {stat[1]} templates")
        
        # Show some templates
        cursor.execute("""
            SELECT t.name, c.name, t.message_type
            FROM message_templates t
            LEFT JOIN message_categories c ON t.category_id = c.id
            LIMIT 10
        """)
        templates = cursor.fetchall()
        print("\nSample Templates:")
        for temp in templates:
            print(f"  - {temp[0]} ({temp[1]}) - Type: {temp[2]}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_hr_data()
