#!/usr/bin/env python3
"""
Test LINE Loading Animation
ทดสอบการใช้งาน LINE Loading Animation
"""

import requests
import os
from dotenv import load_dotenv
import time

load_dotenv()

LINE_ACCESS_TOKEN = os.getenv('LINE_ACCESS_TOKEN')

def test_loading_animation(user_id: str):
    """ทดสอบ loading animation"""
    if not LINE_ACCESS_TOKEN:
        print("❌ LINE_ACCESS_TOKEN not found in .env file")
        return
    
    if not user_id:
        print("❌ Please provide user_id")
        return
    
    print(f"🔄 Testing loading animation for user: {user_id}")
    
    # Start loading animation
    print("▶️  Starting loading animation...")
    start_url = "https://api.line.me/v2/bot/chat/loading/start"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {LINE_ACCESS_TOKEN}'
    }
    start_data = {
        "chatId": user_id,
        "loadingSeconds": 10
    }
    
    try:
        response = requests.post(start_url, headers=headers, json=start_data)
        if response.status_code == 202:
            print("✅ Loading animation started successfully")
        else:
            print(f"❌ Failed to start loading: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Wait for 5 seconds
    print("⏳ Waiting 5 seconds...")
    time.sleep(5)
    
    # Stop loading animation
    print("⏹️  Stopping loading animation...")
    stop_url = "https://api.line.me/v2/bot/chat/loading/stop"
    stop_data = {
        "chatId": user_id
    }
    
    try:
        response = requests.post(stop_url, headers=headers, json=stop_data)
        if response.status_code == 200:
            print("✅ Loading animation stopped successfully")
        else:
            print(f"❌ Failed to stop loading: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    # ใส่ USER_ID ของ LINE ที่ต้องการทดสอบ
    # หา USER_ID ได้จากการส่งข้อความมาที่บอทและดูใน log
    test_user_id = input("Enter LINE User ID to test (or press Enter to skip): ").strip()
    
    if test_user_id:
        test_loading_animation(test_user_id)
    else:
        print("ℹ️  Test skipped. To test, run the script and provide a LINE User ID.")
        print("ℹ️  You can get User ID from the admin panel or bot logs.")
