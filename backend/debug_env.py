import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

# Force reload environment
from dotenv import load_dotenv
env_path = backend_path / '.env'
print(f"Loading .env from: {env_path}")
load_dotenv(env_path, override=True)

# Test imports
print("\n=== Testing Imports ===")
try:
    from app.database import SessionLocal, get_supabase, DatabaseManager
    print("✅ Successfully imported from database.py")
except Exception as e:
    print(f"❌ Error importing from database.py: {e}")

# Test environment variables
print("\n=== Environment Variables ===")
env_vars = {
    "SUPABASE_URL": os.getenv("SUPABASE_URL"),
    "SUPABASE_SERVICE_KEY": os.getenv("SUPABASE_SERVICE_KEY"),
    "LINE_ACCESS_TOKEN": os.getenv("LINE_ACCESS_TOKEN"),
    "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY")
}

for key, value in env_vars.items():
    if value:
        if "KEY" in key or "TOKEN" in key:
            print(f"{key}: {value[:20]}...{value[-4:]}")
        else:
            print(f"{key}: {value}")
    else:
        print(f"{key}: NOT SET ❌")

# Test Supabase connection
print("\n=== Testing Supabase Connection ===")
try:
    from supabase import create_client
    
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY")
    
    if url and key:
        client = create_client(url, key)
        result = client.table('line_users').select("count").execute()
        print(f"✅ Supabase connection successful! Count: {result}")
    else:
        print("❌ Missing Supabase credentials")
except Exception as e:
    print(f"❌ Supabase connection error: {e}")

print("\n=== Done ===")
