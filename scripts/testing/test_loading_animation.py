#!/usr/bin/env python3
"""
Test script for LINE loading animation functionality
"""

import os
import sys
import requests
import time
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', 'backend', '.env'))

def test_loading_animation_api():
    """Test the loading animation API endpoints"""
    print("🧪 Testing LINE Loading Animation API")
    print("=" * 50)
    
    line_access_token = os.getenv('LINE_ACCESS_TOKEN')
    if not line_access_token or 'your_' in line_access_token:
        print("❌ LINE_ACCESS_TOKEN not properly configured")
        return False
    
    print(f"✅ LINE_ACCESS_TOKEN configured: {line_access_token[:10]}...")
    
    # Test Chat Loading API
    test_user_id = "test_user_123"  # This will fail but we can check the response
    
    print(f"\n📡 Testing Chat Loading Start API...")
    url = "https://api.line.me/v2/bot/chat/loading/start"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {line_access_token}'
    }
    data = {
        "chatId": test_user_id,
        "loadingSeconds": 5
    }
    
    response = requests.post(url, headers=headers, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 202:
        print("✅ Loading animation API working correctly")
        
        # Test stop
        print(f"\n📡 Testing Chat Loading Stop API...")
        stop_url = "https://api.line.me/v2/bot/chat/loading/stop"
        stop_data = {"chatId": test_user_id}
        
        stop_response = requests.post(stop_url, headers=headers, json=stop_data)
        print(f"Stop Status Code: {stop_response.status_code}")
        print(f"Stop Response: {stop_response.text}")
        
        return True
    else:
        print(f"❌ Loading animation API failed: {response.status_code} - {response.text}")
        return False

def test_backend_api():
    """Test the backend loading animation endpoints"""
    print(f"\n🔧 Testing Backend Loading Animation Endpoints...")
    
    base_url = "http://localhost:8000"
    test_user_id = "test_user_123"
    
    try:
        # Test start loading
        response = requests.post(f"{base_url}/api/loading/start/{test_user_id}", json={"loading_seconds": 5})
        print(f"Backend Start Status: {response.status_code}")
        print(f"Backend Start Response: {response.json()}")
        
        time.sleep(2)
        
        # Test stop loading
        response = requests.post(f"{base_url}/api/loading/stop/{test_user_id}")
        print(f"Backend Stop Status: {response.status_code}")
        print(f"Backend Stop Response: {response.json()}")
        
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Backend server not running. Start it with: python backend/app/main.py")
        return False
    except Exception as e:
        print(f"❌ Backend test failed: {e}")
        return False

def main():
    """Run all loading animation tests"""
    print("🔄 LINE Loading Animation Test Suite")
    print("=" * 60)
    
    # Test API directly
    api_result = test_loading_animation_api()
    
    # Test backend endpoints
    backend_result = test_backend_api()
    
    print(f"\n📊 Test Results:")
    print(f"LINE API Test: {'✅ PASS' if api_result else '❌ FAIL'}")
    print(f"Backend API Test: {'✅ PASS' if backend_result else '❌ FAIL'}")
    
    if api_result and backend_result:
        print(f"\n🎉 All tests passed! Loading animation should work correctly.")
    else:
        print(f"\n⚠️ Some tests failed. Check the configuration and backend server.")
        
    print(f"\n💡 To test with real user:")
    print(f"1. Send a message to your LINE bot")
    print(f"2. Watch for typing indicator before bot replies")
    print(f"3. Check backend logs for loading animation messages")

if __name__ == "__main__":
    main()