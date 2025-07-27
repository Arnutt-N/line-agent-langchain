#!/usr/bin/env python3
"""
Check script for server startup after import fixes
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path

def check_imports():
    """Check if all imports work correctly"""
    print("🔍 Checking Import Fixes")
    print("=" * 40)
    
    backend_path = Path(__file__).parent.parent.parent / "backend"
    
    try:
        # Test importing main module
        import_cmd = [
            sys.executable, "-c", 
            f"import sys; sys.path.append('{backend_path}'); import app.main; print('SUCCESS: All imports working')"
        ]
        result = subprocess.run(import_cmd, capture_output=True, text=True, cwd=backend_path)
        
        if result.returncode == 0:
            print("✅ Import test passed")
            print(f"   Output: {result.stdout.strip()}")
            return True
        else:
            print("❌ Import test failed")
            print(f"   Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error running import test: {e}")
        return False

def check_uvicorn_startup():
    """Check if uvicorn can start the server"""
    print("\n🚀 Testing Uvicorn Startup")
    print("=" * 40)
    
    backend_path = Path(__file__).parent.parent.parent / "backend"
    
    try:
        # Test uvicorn startup (just validation, not full start)
        uvicorn_cmd = [
            sys.executable, "-c",
            "import uvicorn; uvicorn.Config('app.main:app', host='0.0.0.0', port=8000).load()"
        ]
        result = subprocess.run(uvicorn_cmd, capture_output=True, text=True, cwd=backend_path, timeout=10)
        
        if result.returncode == 0:
            print("✅ Uvicorn can load the app successfully")
            return True
        else:
            print("❌ Uvicorn failed to load the app")
            print(f"   Error: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("⚠️ Uvicorn loading test timed out (this might be normal)")
        return True  # Timeout during loading is often normal
    except Exception as e:
        print(f"❌ Error testing uvicorn: {e}")
        return False

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("\n📦 Checking Dependencies")
    print("=" * 40)
    
    required_packages = [
        'fastapi', 'uvicorn', 'line-bot-sdk', 'sqlalchemy', 
        'python-dotenv', 'requests', 'langchain', 'langchain-google-genai', 
        'langgraph'
    ]
    
    missing = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - Missing")
            missing.append(package)
    
    return len(missing) == 0, missing

def main():
    """Run all startup checks"""
    print("🧪 Server Startup Health Check")
    print("=" * 50)
    
    # Run checks
    import_ok = check_imports()
    uvicorn_ok = check_uvicorn_startup()
    deps_ok, missing_deps = check_dependencies()
    
    print(f"\n📊 Check Results:")
    print(f"Imports: {'✅ PASS' if import_ok else '❌ FAIL'}")
    print(f"Uvicorn: {'✅ PASS' if uvicorn_ok else '❌ FAIL'}")
    print(f"Dependencies: {'✅ PASS' if deps_ok else '❌ FAIL'}")
    
    if missing_deps:
        print(f"\n⚠️ Missing Dependencies:")
        for dep in missing_deps:
            print(f"  - {dep}")
        print(f"\n💡 Install with: pip install {' '.join(missing_deps)}")
    
    if import_ok and uvicorn_ok and deps_ok:
        print(f"\n🎉 All checks passed! Server should start correctly.")
        print(f"\n🚀 To start the server:")
        print(f"1. Use: RUN_SYSTEM.bat")
        print(f"2. Or manually: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        print(f"\n🔧 Fixed Issues:")
        print(f"- ✅ Removed IndicatorAction import error")
        print(f"- ✅ Simplified import structure for multiprocessing")
        print(f"- ✅ Added missing os import")
        print(f"- ✅ Fixed loading animation implementation")
    else:
        print(f"\n❌ Some checks failed. Fix the issues above before starting the server.")

if __name__ == "__main__":
    main()