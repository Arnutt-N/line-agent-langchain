#!/usr/bin/env python3
"""
Check script for LINE loading animation functionality
"""

import os
import sys
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', 'backend', '.env'))

def check_environment():
    """Check if environment is properly configured"""
    print("🔍 Checking Environment Configuration")
    print("=" * 40)
    
    issues = []
    
    # Check LINE tokens
    line_token = os.getenv('LINE_ACCESS_TOKEN')
    if not line_token or 'your_' in line_token:
        issues.append("❌ LINE_ACCESS_TOKEN not configured")
    else:
        print(f"✅ LINE_ACCESS_TOKEN: {line_token[:10]}...")
    
    line_secret = os.getenv('LINE_CHANNEL_SECRET')
    if not line_secret or 'your_' in line_secret:
        issues.append("❌ LINE_CHANNEL_SECRET not configured")
    else:
        print(f"✅ LINE_CHANNEL_SECRET: {line_secret[:10]}...")
    
    return len(issues) == 0, issues

def check_imports():
    """Check if required modules can be imported"""
    print("\n🔍 Checking Module Imports")
    print("=" * 40)
    
    issues = []
    
    try:
        from linebot.models import IndicatorAction
        print("✅ IndicatorAction imported successfully")
    except ImportError as e:
        issues.append(f"❌ Cannot import IndicatorAction: {e}")
    
    try:
        import requests
        print("✅ requests module available")
    except ImportError as e:
        issues.append(f"❌ Cannot import requests: {e}")
    
    try:
        from app.main import start_loading_animation, show_typing_indicator
        print("✅ Loading animation functions available")
    except ImportError as e:
        issues.append(f"❌ Cannot import loading functions: {e}")
    
    return len(issues) == 0, issues

def check_code_implementation():
    """Check if the code implementation looks correct"""
    print("\n🔍 Checking Code Implementation")
    print("=" * 40)
    
    issues = []
    
    try:
        # Read main.py to check implementation
        main_file = os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'app', 'main.py')
        with open(main_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for key functions
        if 'show_typing_indicator' in content:
            print("✅ show_typing_indicator function found")
        else:
            issues.append("❌ show_typing_indicator function not found")
        
        if 'IndicatorAction' in content:
            print("✅ IndicatorAction import found")
        else:
            issues.append("❌ IndicatorAction import not found")
        
        if 'start_loading_animation(user_id' in content and 'handle_message' in content:
            print("✅ Loading animation called in message handler")
        else:
            issues.append("❌ Loading animation not properly integrated")
            
    except Exception as e:
        issues.append(f"❌ Error checking code: {e}")
    
    return len(issues) == 0, issues

def main():
    """Run all checks"""
    print("🧪 LINE Loading Animation Health Check")
    print("=" * 50)
    
    # Run checks
    env_ok, env_issues = check_environment()
    import_ok, import_issues = check_imports()
    code_ok, code_issues = check_code_implementation()
    
    print(f"\n📊 Check Results:")
    print(f"Environment: {'✅ PASS' if env_ok else '❌ FAIL'}")
    print(f"Imports: {'✅ PASS' if import_ok else '❌ FAIL'}")
    print(f"Code Implementation: {'✅ PASS' if code_ok else '❌ FAIL'}")
    
    # Show issues
    all_issues = env_issues + import_issues + code_issues
    if all_issues:
        print(f"\n⚠️ Issues Found:")
        for issue in all_issues:
            print(f"  {issue}")
    
    if env_ok and import_ok and code_ok:
        print(f"\n🎉 All checks passed! Loading animation should work.")
        print(f"\n📱 Next Steps:")
        print(f"1. Start the backend server: python backend/app/main.py")
        print(f"2. Send a message to your LINE bot")
        print(f"3. Look for typing indicator before bot replies")
        print(f"4. Check backend logs for loading animation messages")
        print(f"\n🔧 Debug Tools:")
        print(f"- scripts/testing/test_loading_animation.py")
        print(f"- scripts/debugging/debug_loading_animation.py")
    else:
        print(f"\n❌ Please fix the issues above before testing.")

if __name__ == "__main__":
    main()