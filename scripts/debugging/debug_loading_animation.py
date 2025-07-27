#!/usr/bin/env python3
"""
Debug script for LINE loading animation
Test with real user ID
"""

import os
import sys
import time
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', 'backend', '.env'))

def test_with_user():
    """Test loading animation with real user"""
    from app.main import start_loading_animation, stop_loading_animation, show_typing_indicator, line_bot_api
    from linebot.models import TextSendMessage
    
    print("🔄 Loading Animation Debug Tool")
    print("=" * 40)
    
    # Get user ID from input
    user_id = input("Enter LINE User ID to test with: ").strip()
    if not user_id:
        print("❌ No user ID provided")
        return
    
    print(f"🎯 Testing with user: {user_id}")
    
    try:
        print("\n1️⃣ Sending typing indicator...")
        typing_result = show_typing_indicator(user_id)
        print(f"   Result: {'✅ Success' if typing_result else '❌ Failed'}")
        
        print("\n2️⃣ Starting loading animation...")
        loading_result = start_loading_animation(user_id, 10)
        print(f"   Result: {'✅ Success' if loading_result else '❌ Failed'}")
        
        # Wait a bit
        print("\n⏳ Waiting 3 seconds...")
        time.sleep(3)
        
        print("\n3️⃣ Sending test message...")
        test_message = "🤖 This is a test message with loading animation!"
        line_bot_api.push_message(user_id, TextSendMessage(text=test_message))
        print("   Message sent!")
        
        print("\n4️⃣ Stopping loading animation...")
        stop_result = stop_loading_animation(user_id)
        print(f"   Result: {'✅ Success' if stop_result else '❌ Failed'}")
        
        print(f"\n✨ Test completed! Check your LINE app for the typing indicator and message.")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")

def show_instructions():
    """Show usage instructions"""
    print("📱 How to test loading animation:")
    print("1. Run this script")
    print("2. Enter your LINE User ID")
    print("3. Watch your LINE app for:")
    print("   - Typing indicator (3 dots)")
    print("   - Loading animation")
    print("   - Test message")
    print()
    print("💡 To get your User ID:")
    print("1. Send any message to your bot")
    print("2. Check backend logs for 'User ID: ...'")
    print("3. Copy the User ID and use it here")

if __name__ == "__main__":
    show_instructions()
    print()
    test_with_user()