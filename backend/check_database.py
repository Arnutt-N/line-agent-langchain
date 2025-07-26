#!/usr/bin/env python3
"""
Test script เพื่อตรวจสอบข้อมูลในฐานข้อมูล
"""
import sqlite3
import os

def check_database():
    db_path = "line_agent.db"
    
    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found!")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check line_users table
        cursor.execute("SELECT COUNT(*) FROM line_users")
        user_count = cursor.fetchone()[0]
        print(f"Total users in database: {user_count}")
        
        # Show recent users
        cursor.execute("SELECT line_id, name, mode, added_at FROM line_users ORDER BY added_at DESC LIMIT 5")
        recent_users = cursor.fetchall()
        print("\nRecent users:")
        for user in recent_users:
            print(f"  {user[0]} - {user[1]} - {user[2]} - {user[3]}")
        
        # Check chat_messages table
        cursor.execute("SELECT COUNT(*) FROM chat_messages")
        message_count = cursor.fetchone()[0]
        print(f"\nTotal messages in database: {message_count}")
        
        # Show recent messages
        cursor.execute("SELECT line_user_id, message, is_from_user, timestamp FROM chat_messages ORDER BY timestamp DESC LIMIT 5")
        recent_messages = cursor.fetchall()
        print("\nRecent messages:")
        for msg in recent_messages:
            sender = "User" if msg[2] else "Bot"
            print(f"  {msg[0]} ({sender}): {msg[1][:50]}... - {msg[3]}")
            
    except Exception as e:
        print(f"Error checking database: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_database()
