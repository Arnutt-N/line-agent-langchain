#!/usr/bin/env python3
"""
Test imports for LINE Message Templates
ทดสอบการ import ไฟล์ต่าง ๆ ของระบบ Templates
"""

def test_imports():
    print("🧪 Testing imports...")
    
    try:
        print("1. Testing template_crud...")
        from backend.app.template_crud import create_message_template
        print("   ✅ template_crud imported successfully")
    except Exception as e:
        print(f"   ❌ template_crud error: {e}")
    
    try:
        print("2. Testing template_selector...")
        from backend.app.template_selector import TemplateSelector
        print("   ✅ template_selector imported successfully")
    except Exception as e:
        print(f"   ❌ template_selector error: {e}")
    
    try:
        print("3. Testing message_builder...")
        from backend.app.message_builder import LineMessageBuilder
        print("   ✅ message_builder imported successfully")
    except Exception as e:
        print(f"   ❌ message_builder error: {e}")
    
    try:
        print("4. Testing schemas...")
        from backend.app.schemas import MessageTemplateCreate
        print("   ✅ schemas imported successfully")
    except Exception as e:
        print(f"   ❌ schemas error: {e}")
    
    try:
        print("5. Testing models...")
        from backend.app.models import MessageTemplate
        print("   ✅ models imported successfully")
    except Exception as e:
        print(f"   ❌ models error: {e}")
    
    try:
        print("6. Testing main.py...")
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
        
        # Try to import main without running it
        import importlib.util
        spec = importlib.util.spec_from_file_location("main", "backend/app/main.py")
        main_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(main_module)
        print("   ✅ main.py imported successfully")
    except Exception as e:
        print(f"   ❌ main.py error: {e}")
        print(f"      Full error: {str(e)}")

if __name__ == "__main__":
    print("🔍 IMPORT TESTING")
    print("=" * 40)
    test_imports()
    print("\n✅ Import testing completed!")
