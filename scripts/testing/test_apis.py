import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from linebot import LineBotApi
import google.generativeai as genai

# Load .env
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)

print("Testing APIs...")
print("-" * 40)

# Test LINE API
try:
    line_bot_api = LineBotApi(os.getenv('LINE_ACCESS_TOKEN'))
    bot_info = line_bot_api.get_bot_info()
    print("[OK] LINE API - Bot Name:", bot_info.display_name)
except Exception as e:
    print("[ERROR] LINE API:", str(e))

# Test Gemini API
try:
    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
    model = genai.GenerativeModel('gemini-2.5-flash')
    response = model.generate_content("Say hello in Thai")
    print("[OK] Gemini API - Response:", response.text.strip()[:50])
except Exception as e:
    print("[ERROR] Gemini API:", str(e))

print("-" * 40)
print("Testing complete!")
