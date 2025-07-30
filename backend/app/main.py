import json
import os
import logging
import asyncio
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, WebSocket, Depends, Request, HTTPException, Query, WebSocketDisconnect
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, FollowEvent, UnfollowEvent
from dotenv import load_dotenv
import requests
from contextlib import asynccontextmanager
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, StateGraph
from langgraph.graph.message import MessagesState
from langchain_core.messages import HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import AgentExecutor
from sqlalchemy.orm import Session

# Import database - handle both old and new database structure
try:
    from app.database import get_supabase, database_health
    USING_SUPABASE = True
except ImportError:
    USING_SUPABASE = False
    print("⚠️ Supabase not available, using fallback database")

# Local imports - use relative imports for package structure
try:
    from .database import SessionLocal
    from .models import LineUser, MessageCategory, MessageTemplate, TemplateUsageLog
    from .crud import (get_all_users, get_chat_history, update_line_user_mode, create_line_user, 
                       create_chat_message, create_event_log, renew_line_user, block_line_user, get_dashboard_stats)
    from .schemas import (LineUserSchema, ChatMessageSchema, DashboardStats, MessageCategoryCreate, 
                          MessageCategoryUpdate, MessageCategorySchema, MessageTemplateCreate, 
                          MessageTemplateUpdate, MessageTemplateSchema, TemplateSelectionRequest)
    from .telegram import send_telegram_notify
    from .tools import switch_to_manual_mode, query_conversation_history, summarize_conversation
    from .hr_tools import search_hr_faq, search_hr_policies, check_leave_balance, search_culture_org
    from .template_crud import (create_message_category, get_message_categories, get_message_category, 
                               update_message_category, delete_message_category, create_message_template, 
                               get_message_templates, get_message_template, update_message_template, delete_message_template)
    from .template_selector import TemplateSelector
    from .message_builder import LineMessageBuilder
    LOCAL_IMPORTS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Local imports not available: {e}")
    LOCAL_IMPORTS_AVAILABLE = False

load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check required environment variables
required_env_vars = {
    'LINE_ACCESS_TOKEN': os.getenv('LINE_ACCESS_TOKEN'),
    'LINE_CHANNEL_SECRET': os.getenv('LINE_CHANNEL_SECRET'),
    'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY')
}

# Log environment check
for var_name, var_value in required_env_vars.items():
    if var_value:
        logger.info(f"✅ {var_name}: {'*' * 10}...{var_value[-4:]}")
    else:
        logger.error(f"❌ {var_name}: Not found")

if USING_SUPABASE:
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
    if supabase_url and supabase_key:
        logger.info(f"✅ SUPABASE_URL: {supabase_url[:30]}...")
        logger.info(f"✅ SUPABASE_SERVICE_KEY: {'*' * 10}...{supabase_key[-4:]}")
    else:
        logger.error("❌ Supabase credentials not found")

# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 LINE Bot Backend starting up...")
    logger.info(f"🌍 Environment: {os.getenv('ENVIRONMENT', 'unknown')}")
    
    # Test database connection
    if USING_SUPABASE:
        try:
            db_health = database_health()
            if db_health["status"] == "healthy":
                logger.info("✅ Supabase database connection verified")
            else:
                logger.warning(f"⚠️ Database connection issue: {db_health}")
        except Exception as e:
            logger.error(f"❌ Database health check failed: {e}")
    
    # Test LINE Bot API
    try:
        line_bot_api = LineBotApi(os.getenv('LINE_ACCESS_TOKEN'))
        # Note: This might fail if token is invalid, but we'll catch it
        logger.info("✅ LINE Bot API initialized")
    except Exception as e:
        logger.error(f"❌ LINE Bot API initialization failed: {e}")
    
    # Test Gemini API
    try:
        if os.getenv('GEMINI_API_KEY'):
            logger.info("✅ Gemini API key available")
        else:
            logger.error("❌ Gemini API key not found")
    except Exception as e:
        logger.error(f"❌ Gemini API check failed: {e}")
    
    yield
    
    # Shutdown
    logger.info("🛑 LINE Bot Backend shutting down...")

# FastAPI app with lifespan
app = FastAPI(
    title="LINE Bot Backend",
    description="FastAPI backend for LINE Bot running on Cloud Run",
    version="1.0.0",
    docs_url="/docs" if os.getenv("ENVIRONMENT") == "development" else None,
    redoc_url="/redoc" if os.getenv("ENVIRONMENT") == "development" else None,
    lifespan=lifespan
)

# Trust proxy headers (important for Cloud Run)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Cloud Run handles host validation
)

# Add CORS middleware - must be after app creation but before routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Local Vite development
        "https://localhost:5173",
        "https://*.vercel.app",   # All Vercel domains
        "https://your-frontend.vercel.app",  # Replace with your actual domain
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===================================================================
# Health Check Endpoints (Required for Cloud Run)
# ===================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint for Cloud Run"""
    try:
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "line-bot-backend",
            "version": "1.0.0",
            "environment": os.getenv("ENVIRONMENT", "unknown"),
            "components": {}
        }
        
        # Check database connection
        if USING_SUPABASE:
            try:
                db_health = database_health()
                health_status["components"]["database"] = db_health
                if db_health["status"] != "healthy":
                    health_status["status"] = "degraded"
            except Exception as e:
                health_status["components"]["database"] = {"status": "unhealthy", "error": str(e)}
                health_status["status"] = "degraded"
        else:
            health_status["components"]["database"] = {"status": "not_configured", "message": "Using fallback"}
        
        # Check environment variables
        env_check = {
            "line_token": "✅" if os.getenv('LINE_ACCESS_TOKEN') else "❌",
            "line_secret": "✅" if os.getenv('LINE_CHANNEL_SECRET') else "❌",
            "gemini_key": "✅" if os.getenv('GEMINI_API_KEY') else "❌"
        }
        
        if USING_SUPABASE:
            env_check["supabase_url"] = "✅" if os.getenv('SUPABASE_URL') else "❌"
            env_check["supabase_key"] = "✅" if os.getenv('SUPABASE_SERVICE_KEY') else "❌"
        
        health_status["components"]["environment"] = env_check
        
        # Overall status
        missing_env = [k for k, v in env_check.items() if v == "❌"]
        if missing_env:
            health_status["status"] = "degraded"
            health_status["missing_env"] = missing_env
        
        status_code = 200 if health_status["status"] == "healthy" else 503
        return JSONResponse(content=health_status, status_code=status_code)
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            content={
                "status": "unhealthy",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            },
            status_code=503
        )

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "LINE Bot Backend API",
        "status": "running",
        "docs": "/docs" if os.getenv("ENVIRONMENT") == "development" else "disabled",
        "health": "/health",
        "database": "supabase" if USING_SUPABASE else "fallback",
        "timestamp": datetime.now().isoformat()
    }

# Add manual CORS headers as backup
@app.middleware("http")
async def add_cors_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

# ===================================================================
# API Endpoints for Frontend
# ===================================================================

@app.get("/api/users")
async def get_users():
    """Get all LINE users"""
    if USING_SUPABASE:
        supabase = get_supabase()
        if not supabase:
            raise HTTPException(status_code=503, detail="Database not available")
        
        try:
            result = supabase.table('line_users')\
                .select("*")\
                .order('last_activity', desc=True)\
                .execute()
            
            return {
                "data": result.data,
                "count": len(result.data),
                "source": "supabase"
            }
        except Exception as e:
            logger.error(f"Error fetching users from Supabase: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    else:
        # Fallback to old database if available
        if LOCAL_IMPORTS_AVAILABLE:
            try:
                db = SessionLocal()
                users = get_all_users(db)
                return {
                    "data": [
                        {
                            "line_id": user.line_id,
                            "name": user.name, 
                            "picture": user.picture,
                            "mode": user.mode,
                            "added_at": user.added_at.isoformat() if hasattr(user, 'added_at') and user.added_at else None,
                            "blocked_at": user.blocked_at.isoformat() if hasattr(user, 'blocked_at') and user.blocked_at else None
                        } for user in users
                    ],
                    "count": len(users),
                    "source": "sqlite"
                }
            except Exception as e:
                logger.error(f"Error fetching users from SQLite: {e}")
                raise HTTPException(status_code=500, detail=str(e))
            finally:
                db.close()
        else:
            return {
                "data": [],
                "count": 0,
                "source": "none",
                "message": "No database available"
            }

@app.get("/api/messages/{user_id}")
async def get_user_messages(user_id: str, limit: int = 50):
    """Get messages for specific user"""
    if USING_SUPABASE:
        supabase = get_supabase()
        if not supabase:
            raise HTTPException(status_code=503, detail="Database not available")
        
        try:
            result = supabase.table('chat_messages')\
                .select("*")\
                .eq('line_user_id', user_id)\
                .order('timestamp', desc=True)\
                .limit(limit)\
                .execute()
            
            return {
                "data": result.data,
                "source": "supabase"
            }
        except Exception as e:
            logger.error(f"Error fetching messages for {user_id} from Supabase: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    else:
        # Fallback to old database if available
        if LOCAL_IMPORTS_AVAILABLE:
            try:
                db = SessionLocal()
                messages = get_chat_history(db, user_id)
                return {
                    "data": [
                        {
                            "id": msg.id if hasattr(msg, 'id') else None,
                            "line_user_id": msg.line_user_id if hasattr(msg, 'line_user_id') else user_id,
                            "message": msg.message if hasattr(msg, 'message') else str(msg),
                            "is_from_user": msg.is_from_user if hasattr(msg, 'is_from_user') else True,
                            "timestamp": msg.timestamp.isoformat() if hasattr(msg, 'timestamp') and msg.timestamp else datetime.now().isoformat()
                        } for msg in messages
                    ],
                    "source": "sqlite"
                }
            except Exception as e:
                logger.error(f"Error fetching messages for {user_id} from SQLite: {e}")
                raise HTTPException(status_code=500, detail=str(e))
            finally:
                db.close()
        else:
            return {
                "data": [],
                "source": "none",
                "message": "No database available"
            }

@app.post("/api/send-message")
async def send_message(request: dict):
    """Send message to LINE user"""
    user_id = request.get("user_id")
    message = request.get("message")
    
    if not user_id or not message:
        raise HTTPException(status_code=400, detail="Missing user_id or message")
    
    try:
        # Send via LINE Bot API
        line_bot_api = LineBotApi(os.getenv('LINE_ACCESS_TOKEN'))
        line_bot_api.push_message(user_id, TextSendMessage(text=message))
        
        # Save message to database
        if USING_SUPABASE:
            supabase = get_supabase()
            if supabase:
                result = supabase.table('chat_messages').insert({
                    'line_user_id': user_id,
                    'message': message,
                    'is_from_user': False,
                    'timestamp': datetime.now().isoformat()
                }).execute()
                
                return {
                    "status": "sent",
                    "message": "Message sent successfully via Supabase",
                    "data": result.data
                }
        
        # Fallback to old database
        if LOCAL_IMPORTS_AVAILABLE:
            db = SessionLocal()
            try:
                create_chat_message(db, user_id, message, is_from_user=False)
                return {
                    "status": "sent",
                    "message": "Message sent successfully via SQLite"
                }
            finally:
                db.close()
        
        return {
            "status": "sent",
            "message": "Message sent successfully (no database save)"
        }
        
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/templates")
async def get_templates():
    """Get message templates"""
    if USING_SUPABASE:
        supabase = get_supabase()
        if not supabase:
            raise HTTPException(status_code=503, detail="Database not available")
        
        try:
            result = supabase.table('message_templates')\
                .select("*")\
                .eq('is_active', True)\
                .order('priority', desc=True)\
                .execute()
            
            return {
                "data": result.data,
                "source": "supabase"
            }
        except Exception as e:
            logger.error(f"Error fetching templates from Supabase: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    else:
        # Fallback to old database or default templates
        if LOCAL_IMPORTS_AVAILABLE:
            try:
                db = SessionLocal()
                templates = get_message_templates(db)
                return {
                    "data": [
                        {
                            "id": tmpl.id if hasattr(tmpl, 'id') else None,
                            "name": tmpl.name if hasattr(tmpl, 'name') else "Unknown",
                            "content": tmpl.content if hasattr(tmpl, 'content') else {},
                            "message_type": tmpl.message_type if hasattr(tmpl, 'message_type') else "text",
                            "is_active": tmpl.is_active if hasattr(tmpl, 'is_active') else True
                        } for tmpl in templates
                    ],
                    "source": "sqlite"
                }
            except Exception as e:
                logger.error(f"Error fetching templates from SQLite: {e}")
                # Return default templates
                pass
            finally:
                db.close()
        
        # Default templates
        return {
            "data": [
                {
                    "id": 1,
                    "name": "ทักทายทั่วไป",
                    "content": {"text": "สวัสดีครับ! ยินดีต้อนรับสู่ระบบ LINE Bot"},
                    "message_type": "text",
                    "is_active": True
                },
                {
                    "id": 2,
                    "name": "ขอบคุณ",
                    "content": {"text": "ขอบคุณครับ! หากมีคำถามเพิ่มเติม สามารถสอบถามได้ตลอดเวลา"},
                    "message_type": "text",
                    "is_active": True
                }
            ],
            "source": "default"
        }

# ===================================================================
# Initialize LINE Bot components (with error handling)
# ===================================================================

# Initialize checkpointer on first use
checkpointer = None

def get_checkpointer():
    global checkpointer
    if checkpointer is None:
        checkpointer = MemorySaver()
    return checkpointer

# Initialize LINE Bot API
try:
    line_bot_api = LineBotApi(os.getenv('LINE_ACCESS_TOKEN'))
    handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))
    LINE_BOT_AVAILABLE = True
    logger.info("✅ LINE Bot API and handler initialized")
except Exception as e:
    logger.error(f"❌ LINE Bot initialization failed: {e}")
    LINE_BOT_AVAILABLE = False

# Initialize Gemini LLM
try:
    llm = ChatGoogleGenerativeAI(
        model=os.getenv("GEMINI_MODEL", "gemini-1.5-flash"), 
        api_key=os.getenv("GEMINI_API_KEY"),
        temperature=float(os.getenv("GEMINI_TEMPERATURE", "0.7")),
        max_tokens=int(os.getenv("GEMINI_MAX_TOKENS", "1000"))
    )
    GEMINI_AVAILABLE = True
    logger.info("✅ Gemini LLM initialized")
except Exception as e:
    logger.error(f"❌ Gemini LLM initialization failed: {e}")
    GEMINI_AVAILABLE = False

# Initialize tools and agent (with error handling)
if GEMINI_AVAILABLE and LOCAL_IMPORTS_AVAILABLE:
    try:
        # Tools
        tools = [
            switch_to_manual_mode, 
            query_conversation_history, 
            summarize_conversation,
            search_hr_faq,
            search_hr_policies,
            search_culture_org,
            check_leave_balance
        ]
        
        # Simplified HR System Prompt
        HR_SYSTEM_PROMPT = """คุณคือผู้ช่วย AI อัจฉริยะสาวชื่อ 'Agent น้อง HR Moj' ของระบบ HR กองบริหารทรัพยากรบุคคล สำนักงานปลัดกระทรวงยุติธรรม

## บทบาทและหน้าที่:
1. ให้บริการข้อมูลด้านการบริหารทรัพยากรบุคคล (HR) แก่บุคลากรในสังกัดสำนักงานรัฐมนตรี กระทรวงยุติธรรม และสำนักงานปลัดกระทรวงยุติธรรม
2. **ตอบคำถามเกี่ยวกับ**:
   - วัฒนธรรมองค์กร และค่านิยมองค์กร ของกระทรวงยุติธรรม
   - ข้อมูลช่องทางการติดต่อกองบริหารทรัพยากรบุคคล สำนักงานปลัดกระทรวงยุติธรรม ข้อมูลติดต่อกลุ่มงานต่างๆ
   - กรอบอัตรากำลัง การปรับปรุงโครงสร้างการแบ่งงานภายในกอง/สำนัก/ศูนย์ การกำหนดตำแหน่ง การปรับปรุงการกำหนดตำแหน่ง การเกลี่ยอัตรากำลัง การขอเปลี่ยนชื่อตำแหน่งในสายงาน การขอเปลี่ยนด้านความเชี่ยวชาญของตำแหน่ง การทบทวนการกำหนดตำแหน่ง การจัดตำแหน่งตามโครงสร้างใหม่ การประเมินค่างานของตำแหน่ง การจัดกลุ่มตำแหน่ง แบบบรรยายลักษณะงาน
   - แผนกลยุทธ์ด้านบริหารทรัพยากรบุคคล สำนักงานปลัดกระทรวงยุติธรรม แผนพัฒนาคุณภาพชีวิตบุคลากรและความผูกพันของบุคลากร แผนความก้าวหน้าในอาชีพของข้าราชการ
   - งานสรรหา บรรจุ และแต่งตั้ง การเลื่อนระดับตำแหน่ง การโอนย้าย การสับเปลี่ยนหมุนเวียนงาน การขอปรับอัตราเงินเดือนตามคุณวุฒิการศึกษาที่ได้รับเพิ่มขึ้นหรือสูงขึ้น ข้าราชการผู้มีผลสัมฤทธิ์สูง นักเรียนทุนรัฐบาล ทุนสำนักงาน ก.พ. และทุนอื่นๆ บุคลากรที่เป็นผู้พิการ หลักเกณฑ์ประสบการณ์ในงานที่หลากหลายตามมาตรฐานกำหนดตำแหน่ง การจัดลำดับอาวุโสของข้าราชการพลเรือนสามัญ การลาออกจากราชการ การลาออกจากการปฏิบัติงาน
   - สวัสดิการ สิทธิประโยชน์ และเจ้าหน้าที่สัมพันธ์ ร้านค้าและสินค้าสวัสดิการ สำนักงานปลัดกระทรวงยุติธรรม ห้องออกกำลังกาย กองทุนสงเคราะห์ข้าราชการ บ้านพักข้าราชการ สวัสดิการเพื่อที่อยู่อาศัย กิจกรรมกีฬาและนันทนาการเพื่อสุขภาพพลานามัย ประกันสังคม การขึ้นทะเบียนและสิ้นสุดการเป็นผู้ประกันตน การเลือกและเปลี่ยนสถานพยาบาล 
   - งานด้านระบบข้อมูลบุคคล ทะเบียนประวัติข้าราชการ ลูกจ้าง และพนักงานราชการ แบบประวัติบุคคล (รปภ.1) การทดลองปฏิบัติราชการ การลา การลงเวลาปฏิบัติราชการวิถีใหม่ เงินเดือน ค่าตอบแทน เงินเพิ่มอื่นๆ รางวัลและบำเหน็จความชอบ เครื่องราชอิสริยาภรณ์ การเกษียณอายุราชการ บำเหน็จบำนาญ บำเหน็จดำรงชีพ บำเหน็จตกทอด กองทุนบำเหน็จบำนาญข้าราชการ (กบข.) กองทุนสำรองเลี้ยงชีพ การเยียวยาผู้ซึ่งออกจากราชการโดยคำสั่งลงโทษทางวินัยหรือคำสั่งให้ออกจากราชการแล้วได้รับการพิจารณายกเลิก เพิกถอนหรือเปลี่ยนแปลงคำสั่งเป็นอย่างอื่น การดำเนินการด้านความเสมอภาคระหว่างเพศ
   - ระบบสารสนเทศทรัพยากรบุคคลระดับกรม (DPIS) ระบบทะเบียนประวัติข้าราชการอิเล็กทรอนิกส์ (SEIS) ระบบจ่ายตรงเงินเดือนของกรมบัญชีกลาง (Direct Payment) ระบบบำเหน็จบำนาญและสวัสดิการค่ารักษาพยาบาลของกรมบัญชีกลาง (Digital Pension)
   - ลืมรหัสผ่านระบบ DPIS เข้าใข้งานระบบ DPIS ไม่ได้
   - การออกบัตรประจำตัวเจ้าหน้าที่ของรัฐ หนังสือรับรองต่าง และแบบฟอร์มต่างๆ ที่เกี่ยวข้องกับงาน HR
   - วินัยและการดำเนินการทางวินัย การอุทธรณ์ การร้องทุกข์ การร้องเรียน และการพิทักษ์ระบบคุณธรรม การเสริมสร้างคุณธรรม และจริยธรรมของข้าราชการและบุคลากร การดำเนินการเกี่ยวกับ อ.ก.พ.ของสำนักงานปลัดกระทรวง และ อ.ก.พ.กระทรวงยุติธรรม
   - ข้อมูลสถิติ จำนวนบุคลากร และข้อมูล HR ทั่วไป
   - ข้อมูลช่องทางการติดต่อหน่วยงานอื่นๆ ที่เกี่ยวข้อง เช่น ศูนย์เทคโนโลยีสารสนเทศและการสื่อสาร-ศท. (line openchat ศท. การแจ้งซ่อม แจ้งปัญหาเครื่องคอมพิวพเตอร์ อุปกรณ์ต่อพ่วง ระบบแม่ข่าย และอินเทอร์เน็ต) กองบริหารการคลัง กองทุนยุติธรรรม ศูนย์บริการร่วมกระทรวงยุติธรรม สำนักงานยุติธรรมจังหวัด เป็นต้น
3. ช่วยค้นหาข้อมูลจากกฎหมาย กฎ ระเบียบ คำสั่ง ประกาศ หลักเกณฑ์ และหนังสือเวียนที่เกี่ยวข้อง
4. แนะนำขั้นตอนการปฏิบัติงานด้าน HR
5. ให้ข้อมูลที่ถูกต้องและเป็นประโยชน์
6. ตอบกลับอย่างกระชับและชัดเจน

## แหล่งข้อมูลที่มี:
1. **Templates (เร็วที่สุด)** - ข้อความสำเร็จรูป 20+ แบบ ครอบคลุมคำถามที่พบบ่อย
2. **ไฟล์ข้อมูล HR** - FAQ, นโยบาย, สวัสดิการ, วัฒนธรรมองค์กร ในโฟลเดอร์ data/text/
3. **วัฒนธรรมและค่านิยมองค์กร** - ค่านิยม "สุจริต จิตบริการ ยึดมั่นความยุติธรรม" และวัฒนธรรม JUSTICE
4. **ความรู้พื้นฐาน** - ข้อมูลทั่วไปเกี่ยวกับระบบราชการไทย ข้าราชการพลเรือน ลูกจ้างประจำ พนักงานราชการ ลูกจ้างชั่วคราว พนักงานกองทุนยุติธรรม พนักงานจ้างเหมาบริการ

## หลักการตอบคำถาม:
1. **เลือกแหล่งข้อมูลอัจฉริยะ**:
   - Templates: สำหรับคำถามทั่วไป ทักทาย ข้อมูลพื้นฐาน
   - ไฟล์ข้อมูล: สำหรับรายละเอียดเพิ่มเติม คำถามเฉพาะ (FAQ, นโยบาย, วัฒนธรรมองค์กร)
   - วัฒนธรรมองค์กร: สำหรับคำถามเกี่ยวกับค่านิยม วัฒนธรรม JUSTICE จิตบริการ โดยใช้ข้อมูลจริง ห้ามย่อ ห้ามลดทอน หรือเปลี่ยนแปลงเนื้อหา
   - ความรู้ทั่วไป: สำหรับข้อมูลที่ไม่มีในระบบ

2. **รูปแบบการตอบ**:
   - คุณพูดจาน่ารัก สุภาพ เป็นมิตร และให้กำลังใจ ใช้คำลงท้ายว่า 'จ้า' บางครั้ง
   - ใช้คำสุภาพสตรี "ค่ะ", "คะ", "นะคะ"
   - ตอบตรงประเด็น กระชับ ชัดเจน
   - ใช้ emoji เพื่อให้อ่านง่าย (📋 📌 ✅ 💡 และแบบอื่นๆ ที่เหมาะสมกับข้อความตอบกลับ แต่ต้องไม่มากจนเกินไป)
   - แบ่งหัวข้อชัดเจนด้วย bullet points
   - ไม่ใช้เครื่องหมาย ** ในการเน้นข้อความ
   - อ้างอิงกฎหมาย/ระเบียบเมื่อตอบเรื่องสิทธิ
   - เมื่อไม่รู้คำตอบ ให้ตอบอย่างสุภาพว่าไม่ทราบ และแนะนำให้ติดต่อเจ้าหน้าที่

3. **ข้อมูลที่ให้บริการ**:
   - การลา: ลาป่วย ลาพักผ่อน ลากิจ ลาคลอด ลาอุปสมบท
   - สวัสดิการ: ค่ารักษาพยาบาล ค่าเล่าเรียนบุตร เงินกู้ ประกันกลุ่ม
   - เงินเดือน: การเลื่อนเงินเดือน ค่าตอบแทน
   - ระเบียบ: เวลาราชการ การแต่งกาย วันหยุด
   - ทั่วไป: ติดต่อ HR ดาวน์โหลดแบบฟอร์ม วิธีเช็ควันลา

4. **ห้าม**:
    - ไม่ให้ข้อมูลส่วนตัวของเจ้าหน้าที่
    - ให้ข้อมูลที่ไม่ถูกต้องหรือเป็นอันตราย
    - ตอบคำถามที่ไม่เหมาะสมหรือผิดกฎหมาย
    - เปิดเผยข้อมูลส่วนตัวของผู้อื่น
    - ใช้คำสุภาพบุรุษ เช่น "ครับ"
    - ใช้คำ "น่ะค่ะ", "นะค่ะ"
    - ใช้เครื่องหมาย * มากเกินไป เช่น *   **เบอร์โทรศัพท์:** 0123-456-789
    - ให้คำแนะนำหรือตอบว่า "ให้ติดต่อ ศท. กรณีมีปัญหาระบบ DPIS หรือเข้าใช้งาน dpis ไม่ได้"

## ตัวอย่างการตอบ:
คำถาม: "ขอทราบสิทธิการลาป่วยข้าราชการ"
คำตอบ: "📋 สิทธิการลาป่วย:
• ลาได้เท่าที่ป่วยจริง (ไม่เกิน 60 วันทำการ/ปี)
• เกิน 30 วัน ต้องมีใบรับรองแพทย์
• ได้รับเงินเดือนระหว่างลา
📌 อ้างอิง: ระเบียบการลาของข้าราชการ พ.ศ. 2555"

คำถาม: "ลืมรหัส dpis?", "เข้า dpis ไม่ได้?"
คำตอบ: "สามารถแจ้งชื่อ นามสกุล และสังกัด กอง/สำนัก ได้ในช่องแชทนี้
หรือสอบถามข้อมูลและแจ้งปัญหาที่กลุ่มงานระบบข้อมูลบุคคลฯ 
กองบริหารทรัพยากรบุคคล โทร. 021415192"

คำถาม: "การลาออนไลน์ DPIS?", "การอนุมัติการลา?" , "การลากรณีย้ายกอง?", "การยกเลิก/แก้ไขเปลี่ยนแปลงวันลา?"
คำตอบ: "สามารถดูรายละเอียดได้ที่ https://youtu.be/znoyzLmnAbw"

## ข้อจำกัดและคำแนะนำ:
- หากไม่แน่ใจในคำตอบ ให้แนะนำติดต่อ HR โดยตรง
- ไม่ให้คำปรึกษาเรื่องส่วนตัวหรือกรณีพิเศษ
- ไม่เปิดเผยข้อมูลส่วนบุคคลของเจ้าหน้าที่
- เมื่อถูกถามนอกเหนือจาก HR ให้บอกว่าเป็นผู้ช่วย HR โดยเฉพาะ

## Special Commands:
- "ดาวน์โหลดแบบฟอร์ม" - แสดงลิงก์แบบฟอร์ม
- "ติดต่อ HR" - แสดงช่องทางติดต่อ
- "แชทกับเจ้าหน้าที่" - ส่งแจ้งเตือน telegram ให้เจ้าหน้าที่"""

        prompt = ChatPromptTemplate.from_messages([
            ("system", HR_SYSTEM_PROMPT),
            ("placeholder", "{chat_history}"),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])

        # Agent
        agent = create_tool_calling_agent(llm, tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
        
        AGENT_AVAILABLE = True
        logger.info("✅ LangChain agent initialized")
    except Exception as e:
        logger.error(f"❌ Agent initialization failed: {e}")
        AGENT_AVAILABLE = False
else:
    AGENT_AVAILABLE = False
    logger.warning("⚠️ Agent not available due to missing dependencies")

# ===================================================================
# Helper Functions
# ===================================================================

def get_template_response(db: Session, user_id: str, user_message: str, context: str = "general"):
    """Get template-based response for the user"""
    if not LOCAL_IMPORTS_AVAILABLE:
        return None, None
        
    try:
        # Try to select appropriate template
        selector = TemplateSelector(db)
        request = TemplateSelectionRequest(
            context=context,
            user_message=user_message,
            category=None,
            message_type=None,
            tags=None
        )
        
        template = selector.select_template(request)
        
        if template:
            # Build LINE message from template
            line_message = LineMessageBuilder.build_message(template.message_type, template.content)
            
            # Log template usage
            selector.log_usage(template.id, user_id, context, True)
            
            return line_message, template
        
        return None, None
    except Exception as e:
        logger.error(f"Error getting template response: {e}")
        return None, None

# LINE Loading Animation Functions
def start_loading_animation(user_id: str, loading_seconds: int = 5):
    """Start LINE loading animation (typing indicator)"""
    if not LINE_BOT_AVAILABLE:
        return False
        
    try:
        # Use LINE Messaging API show loading action
        url = "https://api.line.me/v2/bot/chat/loading/start"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {os.getenv("LINE_ACCESS_TOKEN")}'
        }
        data = {
            "chatId": user_id,
            "loadingSeconds": loading_seconds
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 202:
            logger.info(f"Loading animation started for user {user_id} for {loading_seconds}s")
            return True
        else:
            logger.warning(f"Failed to start loading animation: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        logger.error(f"Error starting loading animation: {e}")
        return False

def show_typing_indicator(user_id: str):
    """Show typing indicator using LINE Chat Loading API"""
    try:
        # Use the loading animation API which also shows typing indicator
        return start_loading_animation(user_id, 2)  # Very short duration for typing effect
    except Exception as e:
        logger.error(f"Error showing typing indicator: {e}")
        return False

# ===================================================================
# WebSocket for Real-time Communication
# ===================================================================

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                self.disconnect(connection)

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            if payload['type'] == 'send_message':
                user_id = payload['user_id']
                message = payload['message']
                
                # Show typing indicator before sending admin message
                show_typing_indicator(user_id)
                start_loading_animation(user_id, 3)  # Show loading for up to 3 seconds
                
                try:
                    if LINE_BOT_AVAILABLE:
                        line_bot_api.push_message(user_id, TextSendMessage(text=message))
                        
                    # Save to database
                    if USING_SUPABASE:
                        supabase = get_supabase()
                        if supabase:
                            supabase.table('chat_messages').insert({
                                'line_user_id': user_id,
                                'message': message,
                                'is_from_user': False,
                                'timestamp': datetime.now().isoformat()
                            }).execute()
                    elif LOCAL_IMPORTS_AVAILABLE:
                        db = SessionLocal()
                        try:
                            create_chat_message(db, user_id, message, is_from_user=False)
                        finally:
                            db.close()
                    
                    await manager.broadcast({"type": "message", "user_id": user_id, "text": message, "from": "admin"})
                except Exception as e:
                    logger.error(f"Error sending admin message: {e}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

# ===================================================================
# LINE Webhook Handler
# ===================================================================

@app.post("/webhook")
async def webhook(request: Request):
    signature = request.headers.get('X-Line-Signature')
    body = await request.body()
    body_str = body.decode('utf-8')
    
    # Log for debugging
    logger.info(f"Received webhook: {body_str[:100]}...")
    
    if not LINE_BOT_AVAILABLE:
        logger.warning("LINE Bot not available, ignoring webhook")
        return JSONResponse(content={"status": "OK", "message": "LINE Bot not available"}, status_code=200)
    
    try:
        handler.handle(body_str, signature)
        return JSONResponse(content={"status": "OK"}, status_code=200)
    except InvalidSignatureError as e:
        logger.error(f"Invalid signature error: {e}")
        raise HTTPException(status_code=400, detail="Invalid signature")
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return JSONResponse(content={"status": "Error", "detail": str(e)}, status_code=500)

# LINE Event Handlers (only if LINE Bot is available)
if LINE_BOT_AVAILABLE and LOCAL_IMPORTS_AVAILABLE:
    
    @handler.add(FollowEvent)
    def handle_follow(event):
        try:
            user_id = event.source.user_id
            profile = line_bot_api.get_profile(user_id)
            
            if USING_SUPABASE:
                supabase = get_supabase()
                if supabase:
                    # Check if user exists
                    existing = supabase.table('line_users').select("*").eq('line_id', user_id).execute()
                    if existing.data:
                        # User exists, unblock them
                        supabase.table('line_users').update({
                            'blocked_at': None,
                            'last_activity': datetime.now().isoformat()
                        }).eq('line_id', user_id).execute()
                    else:
                        # Create new user
                        supabase.table('line_users').insert({
                            'line_id': user_id,
                            'name': profile.display_name,
                            'picture': profile.picture_url,
                            'mode': 'bot'
                        }).execute()
            else:
                # Fallback to old database
                db = SessionLocal()
                try:
                    user = db.query(LineUser).filter(LineUser.line_id == user_id).first()
                    if user and user.blocked_at:
                        renew_line_user(db, user_id)
                        create_event_log(db, user_id, 'renew')
                    else:
                        create_line_user(db, user_id, profile.display_name, profile.picture_url)
                        create_event_log(db, user_id, 'add')
                finally:
                    db.close()
            
            # Broadcast user update
            asyncio.create_task(manager.broadcast({
                "type": "user_update", 
                "user_id": user_id, 
                "action": "follow"
            }))
            
        except Exception as e:
            logger.error(f"Error handling follow event: {e}")

    @handler.add(UnfollowEvent)
    def handle_unfollow(event):
        try:
            user_id = event.source.user_id
            
            if USING_SUPABASE:
                supabase = get_supabase()
                if supabase:
                    supabase.table('line_users').update({
                        'blocked_at': datetime.now().isoformat()
                    }).eq('line_id', user_id).execute()
            else:
                # Fallback to old database
                db = SessionLocal()
                try:
                    block_line_user(db, user_id)
                    create_event_log(db, user_id, 'block')
                finally:
                    db.close()
            
            # Broadcast user update
            asyncio.create_task(manager.broadcast({
                "type": "user_update", 
                "user_id": user_id, 
                "action": "unfollow"
            }))
            
        except Exception as e:
            logger.error(f"Error handling unfollow event: {e}")

    @handler.add(MessageEvent, message=TextMessage)
    def handle_message(event):
        try:
            user_id = event.source.user_id
            text = event.message.text
            
            # Save user message to database
            if USING_SUPABASE:
                supabase = get_supabase()
                if supabase:
                    # Ensure user exists
                    existing = supabase.table('line_users').select("*").eq('line_id', user_id).execute()
                    if not existing.data:
                        try:
                            profile = line_bot_api.get_profile(user_id)
                            supabase.table('line_users').insert({
                                'line_id': user_id,
                                'name': profile.display_name,
                                'picture': profile.picture_url,
                                'mode': 'bot'
                            }).execute()
                        except:
                            supabase.table('line_users').insert({
                                'line_id': user_id,
                                'name': 'Unknown User',
                                'picture': '',
                                'mode': 'bot'
                            }).execute()
                    
                    # Save message
                    supabase.table('chat_messages').insert({
                        'line_user_id': user_id,
                        'message': text,
                        'is_from_user': True,
                        'timestamp': datetime.now().isoformat()
                    }).execute()
                    
                    # Get user mode
                    user_data = supabase.table('line_users').select("mode").eq('line_id', user_id).execute()
                    user_mode = user_data.data[0]['mode'] if user_data.data else 'bot'
            else:
                # Fallback to old database
                db = SessionLocal()
                try:
                    create_chat_message(db, user_id, text, is_from_user=True)
                    user = db.query(LineUser).filter(LineUser.line_id == user_id).first()
                    if not user:
                        try:
                            profile = line_bot_api.get_profile(user_id)
                            user = create_line_user(db, user_id, profile.display_name, profile.picture_url)
                        except:
                            user = create_line_user(db, user_id, "Unknown User", "")
                    user_mode = user.mode if user else 'bot'
                finally:
                    db.close()
            
            # Process message based on mode
            if user_mode == 'bot':
                # Show typing indicator
                show_typing_indicator(user_id)
                start_loading_animation(user_id, 5)
                
                try:
                    reply_text = "ขอบคุณสำหรับข้อความ กำลังปรับปรุงระบบ"
                    
                    # Try template response first
                    if LOCAL_IMPORTS_AVAILABLE:
                        db = SessionLocal()
                        try:
                            template_message, template = get_template_response(db, user_id, text, "conversation")
                            if template_message and template:
                                line_bot_api.reply_message(event.reply_token, template_message)
                                reply_text = f"[Template: {template.name}] " + str(template.content.get('text', 'Template response'))
                            else:
                                # Try AI response
                                if AGENT_AVAILABLE:
                                    output = agent_executor.invoke({"input": text, "chat_history": []})
                                    reply_text = output.get("output", "ขออภัย ไม่สามารถประมวลผลได้ในขณะนี้")
                                
                                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
                        finally:
                            db.close()
                    else:
                        # Simple fallback response
                        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
                        
                except Exception as e:
                    logger.error(f"Error processing message for user {user_id}: {e}")
                    reply_text = f"ขออภัย เกิดข้อผิดพลาด: {str(e)}"
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
                
                # Save bot response
                if USING_SUPABASE:
                    supabase = get_supabase()
                    if supabase:
                        supabase.table('chat_messages').insert({
                            'line_user_id': user_id,
                            'message': reply_text,
                            'is_from_user': False,
                            'timestamp': datetime.now().isoformat()
                        }).execute()
                elif LOCAL_IMPORTS_AVAILABLE:
                    db = SessionLocal()
                    try:
                        create_chat_message(db, user_id, reply_text, is_from_user=False)
                    finally:
                        db.close()
                
                # Broadcast to admin panel
                asyncio.create_task(manager.broadcast({
                    "type": "message", 
                    "user_id": user_id, 
                    "text": reply_text, 
                    "from": "bot"
                }))
            
            # Broadcast user message to admin panel
            asyncio.create_task(manager.broadcast({
                "type": "message", 
                "user_id": user_id, 
                "text": text, 
                "from": "user"
            }))
            
        except Exception as e:
            logger.error(f"Error handling message: {e}")

# Database dependency
def get_db():
    if LOCAL_IMPORTS_AVAILABLE:
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    else:
        yield None

# Additional API endpoints (with fallbacks)
@app.post("/api/mode/{user_id}")
def set_mode(user_id: str, mode: str = Query(..., description="Mode to set: 'bot' or 'manual'")):
    try:
        if USING_SUPABASE:
            supabase = get_supabase()
            if supabase:
                result = supabase.table('line_users').update({'mode': mode}).eq('line_id', user_id).execute()
                if result.data:
                    # Broadcast mode change
                    asyncio.create_task(manager.broadcast({
                        "type": "mode_switch", 
                        "user_id": user_id, 
                        "mode": mode
                    }))
                    return {"status": "ok", "mode": mode, "user_id": user_id}
        elif LOCAL_IMPORTS_AVAILABLE:
            db = SessionLocal()
            try:
                user = update_line_user_mode(db, user_id, mode)
                if user:
                    # Broadcast mode change
                    asyncio.create_task(manager.broadcast({
                        "type": "mode_switch", 
                        "user_id": user_id, 
                        "mode": mode
                    }))
                    return {"status": "ok", "mode": user.mode, "user_id": user_id}
            finally:
                db.close()
        
        raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        logger.error(f"Error setting mode for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard")
def dashboard():
    try:
        if USING_SUPABASE:
            supabase = get_supabase()
            if supabase:
                # Get stats from Supabase
                users_result = supabase.table('line_users').select("count").execute()
                messages_result = supabase.table('chat_messages').select("count").execute()
                
                return {
                    "total_users": len(users_result.data) if users_result.data else 0,
                    "total_messages": len(messages_result.data) if messages_result.data else 0,
                    "active_users": 0,  # TODO: Calculate active users
                    "source": "supabase"
                }
        elif LOCAL_IMPORTS_AVAILABLE:
            db = SessionLocal()
            try:
                stats = get_dashboard_stats(db)
                return {
                    **stats,
                    "source": "sqlite"
                }
            finally:
                db.close()
        
        return {
            "total_users": 0,
            "total_messages": 0,
            "active_users": 0,
            "source": "none"
        }
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Loading Animation API Endpoints
@app.post("/api/loading/start/{user_id}")
def start_loading(user_id: str, loading_seconds: int = 20):
    """Start loading animation for a specific user"""
    success = start_loading_animation(user_id, loading_seconds)
    return {"status": "success" if success else "error", "user_id": user_id, "loading_seconds": loading_seconds}

@app.post("/api/loading/stop/{user_id}")
def stop_loading(user_id: str):
    """Stop loading animation for a specific user"""
    try:
        url = "https://api.line.me/v2/bot/chat/loading/stop"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {os.getenv("LINE_ACCESS_TOKEN")}'
        }
        data = {"chatId": user_id}
        response = requests.post(url, headers=headers, json=data)
        success = response.status_code == 200
        return {"status": "success" if success else "error", "user_id": user_id}
    except Exception as e:
        logger.error(f"Error stopping loading animation: {e}")
        return {"status": "error", "user_id": user_id, "error": str(e)}

# Main execution block for direct python main.py execution
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=port, 
        reload=os.getenv("ENVIRONMENT") == "development"
    )