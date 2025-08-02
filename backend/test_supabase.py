import os
import sys
sys.path.append(r'D:\genAI\line-agent-langchain\backend')

from dotenv import load_dotenv
load_dotenv(r'D:\genAI\line-agent-langchain\backend\.env')

print("Testing Supabase connection...")
print(f"SUPABASE_URL: {os.getenv('SUPABASE_URL')}")
print(f"SUPABASE_SERVICE_KEY: {'*' * 10}...{os.getenv('SUPABASE_SERVICE_KEY')[-4:] if os.getenv('SUPABASE_SERVICE_KEY') else 'Not found'}")

try:
    from supabase import create_client
    print("[OK] Supabase module imported successfully")
    
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY")
    
    if url and key:
        client = create_client(url, key)
        print("[OK] Supabase client created successfully")
        
        # Test query
        result = client.table('line_users').select("*").limit(1).execute()
        print(f"[OK] Query successful! Found {len(result.data)} records")
    else:
        print("[ERROR] Missing SUPABASE_URL or SUPABASE_SERVICE_KEY")
        
except Exception as e:
    print(f"[ERROR] Error: {e}")
    import traceback
    traceback.print_exc()
