import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

print("=== Environment Variables Check ===")
print(f"SUPABASE_URL: {os.getenv('SUPABASE_URL')}")
print(f"SUPABASE_SERVICE_KEY: {os.getenv('SUPABASE_SERVICE_KEY')[:20]}..." if os.getenv('SUPABASE_SERVICE_KEY') else "SUPABASE_SERVICE_KEY: None")
print(f"LINE_ACCESS_TOKEN: {os.getenv('LINE_ACCESS_TOKEN')[:20]}..." if os.getenv('LINE_ACCESS_TOKEN') else "LINE_ACCESS_TOKEN: None")
print(f"GEMINI_API_KEY: {os.getenv('GEMINI_API_KEY')[:20]}..." if os.getenv('GEMINI_API_KEY') else "GEMINI_API_KEY: None")
print("================================")
