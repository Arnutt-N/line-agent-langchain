import sqlite3
import json
import os
from datetime import datetime

def export_sqlite_data():
    """Export data from existing SQLite database"""
    
    # ระบุ path ของไฟล์ SQLite
    possible_paths = [
        "line_agent.db",
        "../line_agent.db", 
        "backend/line_agent.db",
        "app/line_agent.db"
    ]
    
    db_path = None
    for path in possible_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print("❌ ไม่พบไฟล์ SQLite database")
        print("📁 กรุณาระบุ path ของไฟล์ .db")
        return None
    
    print(f"📁 พบไฟล์ database: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        export_data = {}
        
        # Export ตารางต่างๆ
        tables = ['line_users', 'chat_messages', 'message_templates', 'message_categories']
        
        for table in tables:
            try:
                cursor.execute(f"SELECT * FROM {table}")
                rows = cursor.fetchall()
                export_data[table] = [dict(row) for row in rows]
                print(f"✅ Export {table}: {len(rows)} records")
            except sqlite3.OperationalError as e:
                print(f"⚠️ Table {table} not found: {e}")
                export_data[table] = []
        
        conn.close()
        
        # บันทึกเป็น JSON
        output_file = f"sqlite_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"\n🎉 Export สำเร็จ!")
        print(f"📄 ไฟล์: {output_file}")
        
        # สรุปข้อมูล
        total_records = sum(len(records) for records in export_data.values())
        print(f"\n📊 สรุป:")
        for table, records in export_data.items():
            if len(records) > 0:
                print(f"   📋 {table}: {len(records)} records")
        print(f"   📊 รวม: {total_records} records")
        
        return output_file
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        return None

if __name__ == "__main__":
    export_sqlite_data()