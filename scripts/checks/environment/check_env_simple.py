import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv

# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)

print("🔐 Phase 1.2: ตรวจสอบ Environment Variables")
print("="*60)

# ตรวจสอบ Required Keys
print("\n✅ Required Keys:")
print(f"  LINE_ACCESS_TOKEN: {'✅ มีค่าแล้ว' if os.getenv('LINE_ACCESS_TOKEN') and not 'your_' in os.getenv('LINE_ACCESS_TOKEN', '') else '❌ ยังไม่มี'}")
print(f"  LINE_CHANNEL_SECRET: {'✅ มีค่าแล้ว' if os.getenv('LINE_CHANNEL_SECRET') and not 'your_' in os.getenv('LINE_CHANNEL_SECRET', '') else '❌ ยังไม่มี'}")
print(f"  GEMINI_API_KEY: {'✅ มีค่าแล้ว' if os.getenv('GEMINI_API_KEY') and not 'your_' in os.getenv('GEMINI_API_KEY', '') else '❌ ยังไม่มี'}")

# ตรวจสอบ Optional Keys
print("\n📌 Optional Keys:")
print(f"  DATABASE_URL: {'✅ มีค่าแล้ว' if os.getenv('DATABASE_URL') else '⚪ ไม่มี (optional)'}")
print(f"  TELEGRAM_BOT_TOKEN: {'✅ มีค่าแล้ว' if os.getenv('TELEGRAM_BOT_TOKEN') else '⚪ ไม่มี (optional)'}")

# แสดงค่า config อื่นๆ
print("\n⚙️ Configuration:")
print(f"  GEMINI_MODEL: {os.getenv('GEMINI_MODEL', 'Not set')}")
print(f"  GEMINI_TEMPERATURE: {os.getenv('GEMINI_TEMPERATURE', 'Not set')}")
print(f"  GEMINI_MAX_TOKENS: {os.getenv('GEMINI_MAX_TOKENS', 'Not set')}")

print("\n✅ Phase 1.2 เสร็จสมบูรณ์!")
