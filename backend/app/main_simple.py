# Simplified main.py for Cloud Run deployment
import os
import sys
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# LINE Bot imports
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    FollowEvent, UnfollowEvent, StickerMessage, StickerSendMessage
)

# Google Gemini
import google.generativeai as genai

# Database
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize LINE Bot
LINE_ACCESS_TOKEN = os.getenv('LINE_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')

if LINE_ACCESS_TOKEN and LINE_CHANNEL_SECRET:
    line_bot_api = LineBotApi(LINE_ACCESS_TOKEN)
    handler = WebhookHandler(LINE_CHANNEL_SECRET)
    logger.info("✅ LINE Bot initialized")
else:
    logger.error("❌ LINE Bot credentials missing")
    line_bot_api = None
    handler = None

# Initialize Supabase
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

supabase: Optional[Client] = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("✅ Supabase initialized")
    except Exception as e:
        logger.error(f"❌ Supabase init error: {e}")

# Initialize Gemini
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(
        model_name=os.getenv('GEMINI_MODEL', 'gemini-2.5-flash'),
        generation_config={
            "temperature": float(os.getenv('GEMINI_TEMPERATURE', '0.7')),
            "max_output_tokens": int(os.getenv('GEMINI_MAX_TOKENS', '500')),
        }
    )
    logger.info("✅ Gemini initialized")
else:
    model = None
    logger.error("❌ Gemini API key missing")

# FastAPI app
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 LINE Bot Backend starting up...")
    yield
    logger.info("🛑 LINE Bot Backend shutting down...")

app = FastAPI(
    title="LINE Bot Backend",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/health")
async def health_check():
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "line-bot-backend",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "production"),
        "components": {}
    }
    
    # Check database
    if supabase:
        try:
            result = supabase.table('line_users').select("count").execute()
            health_status["components"]["database"] = {
                "status": "healthy",
                "type": "supabase"
            }
        except Exception as e:
            health_status["components"]["database"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            health_status["status"] = "degraded"
    
    # Check environment
    health_status["components"]["environment"] = {
        "line_token": "✅" if LINE_ACCESS_TOKEN else "❌",
        "line_secret": "✅" if LINE_CHANNEL_SECRET else "❌",
        "gemini_key": "✅" if GEMINI_API_KEY else "❌",
        "supabase_url": "✅" if SUPABASE_URL else "❌",
        "supabase_key": "✅" if SUPABASE_KEY else "❌"
    }
    
    return health_status

# Root endpoint
@app.get("/")
async def root():
    return {"message": "LINE Bot Backend API", "status": "running"}

# Webhook endpoint
@app.post("/webhook")
async def handle_webhook(request: Request):
    signature = request.headers.get('X-Line-Signature', '')
    body = await request.body()
    body_str = body.decode('utf-8')
    
    logger.info(f"Received webhook: {body_str[:200]}...")
    
    try:
        handler.handle(body_str, signature)
        return JSONResponse(content={"status": "OK"})
    except InvalidSignatureError as e:
        logger.error(f"Invalid signature: {e}")
        raise HTTPException(status_code=400, detail="Invalid signature")
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return JSONResponse(content={"status": "Error", "detail": str(e)}, status_code=500)

# Register handlers
if handler:
    @handler.add(MessageEvent, message=TextMessage)
    def handle_text_message(event):
        try:
            user_id = event.source.user_id
            user_message = event.message.text
            
            logger.info(f"Message from {user_id}: {user_message}")
            
            # Save to database
            if supabase:
                try:
                    # Save user
                    supabase.table('line_users').upsert({
                        'line_id': user_id,
                        'last_activity': datetime.now().isoformat()
                    }).execute()
                    
                    # Save message
                    supabase.table('chat_messages').insert({
                        'line_user_id': user_id,
                        'message': user_message,
                        'is_from_user': True,
                        'timestamp': datetime.now().isoformat()
                    }).execute()
                except Exception as e:
                    logger.error(f"Database error: {e}")
            
            # Generate response
            response_text = "ขอโทษครับ ระบบกำลังอยู่ในช่วงทดสอบ"
            
            if model:
                try:
                    prompt = f"""คุณเป็นผู้ช่วย HR ที่เป็นมิตร ตอบคำถามนี้: {user_message}
                    
ตอบสั้นๆ กระชับ ไม่เกิน 2-3 ประโยค"""
                    
                    response = model.generate_content(prompt)
                    response_text = response.text
                except Exception as e:
                    logger.error(f"Gemini error: {e}")
                    response_text = "ขออภัยครับ ไม่สามารถประมวลผลได้ในขณะนี้"
            
            # Save bot response
            if supabase:
                try:
                    supabase.table('chat_messages').insert({
                        'line_user_id': user_id,
                        'message': response_text,
                        'is_from_user': False,
                        'timestamp': datetime.now().isoformat()
                    }).execute()
                except Exception as e:
                    logger.error(f"Database error: {e}")
            
            # Send response
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=response_text)
            )
            
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            try:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="ขออภัยครับ เกิดข้อผิดพลาด กรุณาลองใหม่")
                )
            except:
                pass
    
    @handler.add(FollowEvent)
    def handle_follow(event):
        try:
            user_id = event.source.user_id
            
            # Get user profile
            profile = line_bot_api.get_profile(user_id)
            
            # Save to database
            if supabase:
                try:
                    supabase.table('line_users').upsert({
                        'line_id': user_id,
                        'name': profile.display_name,
                        'picture': profile.picture_url,
                        'added_at': datetime.now().isoformat()
                    }).execute()
                    
                    supabase.table('event_logs').insert({
                        'line_user_id': user_id,
                        'event_type': 'add',
                        'timestamp': datetime.now().isoformat()
                    }).execute()
                except Exception as e:
                    logger.error(f"Database error: {e}")
            
            # Send welcome message
            welcome_message = f"สวัสดีครับคุณ {profile.display_name} 👋\n\nยินดีต้อนรับสู่ HR Assistant!\n\nผมสามารถช่วยตอบคำถามเกี่ยวกับ:\n• การลา\n• สวัสดิการ\n• กฎระเบียบ\n• และอื่นๆ\n\nพิมพ์คำถามได้เลยครับ 😊"
            
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=welcome_message)
            )
            
        except Exception as e:
            logger.error(f"Error handling follow: {e}")
    
    @handler.add(UnfollowEvent)
    def handle_unfollow(event):
        try:
            user_id = event.source.user_id
            
            # Update database
            if supabase:
                try:
                    supabase.table('line_users').update({
                        'blocked_at': datetime.now().isoformat()
                    }).eq('line_id', user_id).execute()
                    
                    supabase.table('event_logs').insert({
                        'line_user_id': user_id,
                        'event_type': 'block',
                        'timestamp': datetime.now().isoformat()
                    }).execute()
                except Exception as e:
                    logger.error(f"Database error: {e}")
                    
        except Exception as e:
            logger.error(f"Error handling unfollow: {e}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
