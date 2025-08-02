# Local Development Setup Script
import os
import subprocess
import time
import webbrowser
import json
import requests

def check_ngrok():
    """Check if ngrok is installed"""
    try:
        subprocess.run(["ngrok", "version"], capture_output=True, check=True)
        print("✅ ngrok is installed")
        return True
    except:
        print("❌ ngrok not found!")
        print("Please download from: https://ngrok.com/download")
        return False

def start_backend():
    """Start the FastAPI backend"""
    print("🚀 Starting backend on port 8000...")
    backend_path = os.path.join(os.path.dirname(__file__), "backend")
    
    # Check if venv exists
    venv_path = os.path.join(backend_path, "venv")
    if not os.path.exists(venv_path):
        print("Creating virtual environment...")
        subprocess.run(["python", "-m", "venv", "venv"], cwd=backend_path)
        
        # Install requirements
        print("Installing dependencies...")
        pip_path = os.path.join(venv_path, "Scripts", "pip.exe")
        subprocess.run([pip_path, "install", "-r", "requirements.txt"], cwd=backend_path)
    
    # Start backend
    python_path = os.path.join(venv_path, "Scripts", "python.exe")
    subprocess.Popen([python_path, "-m", "uvicorn", "app.main:app", "--reload", "--port", "8000"], 
                     cwd=backend_path, 
                     creationflags=subprocess.CREATE_NEW_CONSOLE)

def start_ngrok():
    """Start ngrok tunnel"""
    print("🌐 Starting ngrok tunnel...")
    subprocess.Popen(["ngrok", "http", "8000"], 
                     creationflags=subprocess.CREATE_NEW_CONSOLE)
    
    # Wait for ngrok to start
    time.sleep(3)
    
    # Get ngrok URL
    try:
        response = requests.get("http://localhost:4040/api/tunnels")
        tunnels = response.json()["tunnels"]
        for tunnel in tunnels:
            if tunnel["proto"] == "https":
                url = tunnel["public_url"]
                print(f"\n✅ ngrok URL: {url}")
                print(f"📋 Webhook URL: {url}/webhook")
                return url
    except:
        print("⚠️ Could not get ngrok URL automatically")
        print("Check ngrok window or visit: http://localhost:4040")
    
    return None

def start_frontend():
    """Start the frontend (optional)"""
    print("💻 Starting frontend on port 5173...")
    frontend_path = os.path.join(os.path.dirname(__file__), "frontend")
    
    if os.path.exists(frontend_path):
        subprocess.Popen(["npm", "run", "dev"], 
                         cwd=frontend_path,
                         shell=True,
                         creationflags=subprocess.CREATE_NEW_CONSOLE)
    else:
        print("⚠️ Frontend directory not found")

def main():
    print("========================================")
    print("  LINE Bot Local Development Setup")
    print("========================================\n")
    
    # Check ngrok
    if not check_ngrok():
        return
    
    # Start services
    start_backend()
    time.sleep(5)  # Wait for backend to start
    
    ngrok_url = start_ngrok()
    
    # Optional: start frontend
    # start_frontend()
    
    print("\n========================================")
    print("  All services started!")
    print("========================================")
    print("\n📝 Next steps:")
    print("1. Copy the ngrok URL above")
    print("2. Go to LINE Developers Console")
    print("3. Update Webhook URL")
    print("4. Click Verify")
    print("\n🔍 Monitoring:")
    print("- Backend logs: Check backend console window")
    print("- ngrok dashboard: http://localhost:4040")
    print("- Health check: http://localhost:8000/health")
    
    # Open ngrok dashboard
    webbrowser.open("http://localhost:4040")
    
    input("\nPress Enter to stop all services...")

if __name__ == "__main__":
    main()
