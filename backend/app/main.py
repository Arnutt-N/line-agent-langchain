import json
import os
import asyncio
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, WebSocket, Depends, Request, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
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

# Local imports - use relative imports for package structure
from .database import SessionLocal
from .models import LineUser, MessageCategory, MessageTemplate, TemplateUsageLog
from .crud import (get_all_users, get_chat_history, update_line_user_mode, create_line_user, 
                   create_chat_message, create_event_log, renew_line_user, block_line_user, get_dashboard_stats)
from .schemas import (LineUserSchema, ChatMessageSchema, DashboardStats, MessageCategoryCreate, 
                      MessageCategoryUpdate, MessageCategorySchema, MessageTemplateCreate, 
                      MessageTemplateUpdate, MessageTemplateSchema, TemplateSelectionRequest)
from .telegram import send_telegram_notify
from .tools import switch_to_manual_mode, query_conversation_history, summarize_conversation
from .hr_tools import search_hr_faq, search_hr_policies, check_leave_balance
from .template_crud import (create_message_category, get_message_categories, get_message_category, 
                           update_message_category, delete_message_category, create_message_template, 
                           get_message_templates, get_message_template, update_message_template, delete_message_template)
from .template_selector import TemplateSelector
from .message_builder import LineMessageBuilder

load_dotenv()


# FastAPI app without lifespan for now (debugging)
app = FastAPI()

# Add CORS middleware - must be after app creation but before routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add manual CORS headers as backup
@app.middleware("http")
async def add_cors_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

# Initialize checkpointer on first use
checkpointer = None

def get_checkpointer():
    global checkpointer
    if checkpointer is None:
        checkpointer = MemorySaver()
    return checkpointer

line_bot_api = LineBotApi(os.getenv('LINE_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))

def get_template_response(db: Session, user_id: str, user_message: str, context: str = "general"):
    """Get template-based response for the user"""
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
        print(f"Error getting template response: {e}")
        return None, None

# LINE Loading Animation Functions
def start_loading_animation(user_id: str, loading_seconds: int = 5):
    """Start LINE loading animation (typing indicator)"""
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
            print(f"Loading animation started for user {user_id} for {loading_seconds}s")
            return True
        else:
            print(f"Failed to start loading animation: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Error starting loading animation: {e}")
        return False

def show_typing_indicator(user_id: str):
    """Show typing indicator using LINE Chat Loading API"""
    try:
        # Use the loading animation API which also shows typing indicator
        return start_loading_animation(user_id, 2)  # Very short duration for typing effect
    except Exception as e:
        print(f"Error showing typing indicator: {e}")
        return False

def stop_loading_animation(user_id: str):
    """Stop LINE loading animation"""
    try:
        url = "https://api.line.me/v2/bot/chat/loading/stop"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {os.getenv("LINE_ACCESS_TOKEN")}'
        }
        data = {
            "chatId": user_id
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            print(f"Loading animation stopped for user {user_id}")
            return True
        else:
            print(f"Failed to stop loading animation: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Error stopping loading animation: {e}")
        return False

# LangChain LLM (Gemini)
llm = ChatGoogleGenerativeAI(
    model=os.getenv("GEMINI_MODEL", "gemini-1.5-flash"), 
    api_key=os.getenv("GEMINI_API_KEY"),
    temperature=float(os.getenv("GEMINI_TEMPERATURE", "0.7")),
    max_tokens=int(os.getenv("GEMINI_MAX_TOKENS", "1000"))
)

# Tools
tools = [
    switch_to_manual_mode, 
    query_conversation_history, 
    summarize_conversation,
    search_hr_faq,
    search_hr_policies,
    check_leave_balance
]

# Prompt
HR_SYSTEM_PROMPT = """คุณคือผู้ช่วย HR อัจฉริยะของกองบริหารทรัพยากรบุคคล สำนักงานปลัดกระทรวงยุติธรรม

## บทบาทและหน้าที่:
1. ให้บริการข้อมูลด้าน HR แก่บุคลากรในสังกัดกระทรวงยุติธรรม
2. ตอบคำถามเกี่ยวกับการลา สวัสดิการ เงินเดือน ระเบียบ และข้อมูล HR ทั่วไป
3. ช่วยค้นหาข้อมูลจากระเบียบ กฎหมาย คำสั่ง และประกาศที่เกี่ยวข้อง
4. แนะนำขั้นตอนการปฏิบัติงานด้าน HR

## แหล่งข้อมูลที่มี:
1. **Templates (เร็วที่สุด)** - ข้อความสำเร็จรูป 20+ แบบ ครอบคลุมคำถามที่พบบ่อย
2. **ไฟล์ข้อมูล HR** - FAQ, นโยบาย, สวัสดิการ ในโฟลเดอร์ data/text/
3. **ความรู้พื้นฐาน** - ข้อมูลทั่วไปเกี่ยวกับระบบราชการไทย

## หลักการตอบคำถาม:
1. **เลือกแหล่งข้อมูลอัจฉริยะ**:
   - Templates: สำหรับคำถามทั่วไป ทักทาย ข้อมูลพื้นฐาน
   - ไฟล์ข้อมูล: สำหรับรายละเอียดเพิ่มเติม คำถามเฉพาะ
   - ความรู้ทั่วไป: สำหรับข้อมูลที่ไม่มีในระบบ

2. **รูปแบบการตอบ**:
   - ใช้ภาษาราชการที่สุภาพ เป็นทางการ
   - ตอบตรงประเด็น กระชับ ชัดเจน
   - ใช้ emoji เพื่อให้อ่านง่าย (📋 📌 ✅ 💡)
   - แบ่งหัวข้อชัดเจนด้วย bullet points
   - อ้างอิงระเบียบ/กฎหมายเมื่อตอบเรื่องสิทธิ

3. **ข้อมูลที่ให้บริการ**:
   - การลา: ลาป่วย ลาพักผ่อน ลากิจ ลาคลอด ลาอุปสมบท
   - สวัสดิการ: ค่ารักษาพยาบาล ค่าเล่าเรียนบุตร เงินกู้ ประกันกลุ่ม
   - เงินเดือน: การเลื่อนเงินเดือน ค่าตอบแทน
   - ระเบียบ: เวลาราชการ การแต่งกาย วันหยุด
   - ทั่วไป: ติดต่อ HR ดาวน์โหลดแบบฟอร์ม วิธีเช็ควันลา

## ตัวอย่างการตอบ:
คำถาม: "ขอทราบสิทธิการลาป่วย"
คำตอบ: "📋 สิทธิการลาป่วย:
• ลาได้เท่าที่ป่วยจริง (ไม่เกิน 60 วันทำการ/ปี)
• เกิน 30 วัน ต้องมีใบรับรองแพทย์
• ได้รับเงินเดือนระหว่างลา
📌 อ้างอิง: ระเบียบการลาของข้าราชการ พ.ศ. 2555"

## ข้อจำกัดและคำแนะนำ:
- หากไม่แน่ใจในคำตอบ ให้แนะนำติดต่อ HR โดยตรง
- ไม่ให้คำปรึกษาเรื่องส่วนตัวหรือกรณีพิเศษ
- ไม่เปิดเผยข้อมูลส่วนบุคคลของเจ้าหน้าที่
- เมื่อถูกถามนอกเหนือจาก HR ให้บอกว่าเป็นผู้ช่วย HR โดยเฉพาะ

## Special Commands:
- "เช็ควันลา [รหัสพนักงาน]" - ดูวันลาคงเหลือ
- "ดาวน์โหลดแบบฟอร์ม" - แสดงลิงก์แบบฟอร์ม
- "ติดต่อ HR" - แสดงช่องทางติดต่อ"""

prompt = ChatPromptTemplate.from_messages([
    ("system", HR_SYSTEM_PROMPT),
    ("placeholder", "{chat_history}"),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

# Agent
agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# LangGraph for stateful conversation with checkpointer
async def create_graph():
    checkpointer = get_checkpointer()
    graph = StateGraph(state_schema=MessagesState)
    graph.add_node("agent", agent_executor)
    graph.add_edge(START, "agent")
    return graph.compile(checkpointer=checkpointer)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, data: dict):
        message = json.dumps(data)
        for connection in self.active_connections:
            await connection.send_text(message)

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
                    line_bot_api.push_message(user_id, TextSendMessage(text=message))
                    db = SessionLocal()
                    create_chat_message(db, user_id, message, is_from_user=False)
                    await manager.broadcast({"type": "message", "user_id": user_id, "text": message, "from": "admin"})
                except Exception as e:
                    print(f"Error sending admin message: {e}")
    except Exception as e:
        print(e)
        manager.disconnect(websocket)

@app.post("/webhook")
async def webhook(request: Request):
    signature = request.headers.get('X-Line-Signature')
    body = await request.body()
    body_str = body.decode('utf-8')
    
    # Log for debugging
    print(f"Received webhook: {body_str[:100]}...")
    print(f"Received signature: {signature}")
    print(f"Channel Secret: {os.getenv('LINE_CHANNEL_SECRET')[:10]}...") # Show first 10 chars only
    
    try:
        handler.handle(body_str, signature)
        return JSONResponse(content={"status": "OK"}, status_code=200)
    except InvalidSignatureError as e:
        print(f"Invalid signature error: {e}")
        # Additional debug info
        import hashlib
        import hmac
        import base64
        channel_secret = os.getenv('LINE_CHANNEL_SECRET')
        hash = hmac.new(channel_secret.encode('utf-8'), body, hashlib.sha256).digest()
        expected_signature = base64.b64encode(hash).decode()
        print(f"Expected signature: {expected_signature}")
        raise HTTPException(status_code=400, detail="Invalid signature")
    except Exception as e:
        print(f"Webhook error: {e}")
        return JSONResponse(content={"status": "Error", "detail": str(e)}, status_code=500)

@handler.add(FollowEvent)
def handle_follow(event):
    db = SessionLocal()
    user_id = event.source.user_id
    profile = line_bot_api.get_profile(user_id)
    user = db.query(LineUser).filter(LineUser.line_id == user_id).first()
    if user and user.blocked_at:
        renew_line_user(db, user_id)
        create_event_log(db, user_id, 'renew')
        action = "renew"
    else:
        create_line_user(db, user_id, profile.display_name, profile.picture_url)
        create_event_log(db, user_id, 'add')
        action = "add"
    
    # Broadcast user update
    asyncio.create_task(manager.broadcast({
        "type": "user_update", 
        "user_id": user_id, 
        "action": action
    }))

@handler.add(UnfollowEvent)
def handle_unfollow(event):
    db = SessionLocal()
    user_id = event.source.user_id
    block_line_user(db, user_id)
    create_event_log(db, user_id, 'block')
    
    # Broadcast user update
    asyncio.create_task(manager.broadcast({
        "type": "user_update", 
        "user_id": user_id, 
        "action": "block"
    }))

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    db = SessionLocal()
    user_id = event.source.user_id
    text = event.message.text
    
    # Create chat message first
    create_chat_message(db, user_id, text, is_from_user=True)
    
    # Check if user exists, if not create them
    user = db.query(LineUser).filter(LineUser.line_id == user_id).first()
    if user is None:
        # User doesn't exist, create them first
        try:
            profile = line_bot_api.get_profile(user_id)
            user = create_line_user(db, user_id, profile.display_name, profile.picture_url)
            create_event_log(db, user_id, 'add')
            print(f"Created new user: {user_id}")
        except Exception as e:
            print(f"Error creating user {user_id}: {e}")
            # Create with default values
            user = create_line_user(db, user_id, "Unknown User", "")
            create_event_log(db, user_id, 'add')
    
    # Check if user is blocked
    if user.blocked_at is not None:
        print(f"User {user_id} is blocked, ignoring message")
        return
    
    # Process message based on mode
    if user.mode == 'bot':
        # Show typing indicator immediately
        show_typing_indicator(user_id)
        
        # Also try loading animation
        start_loading_animation(user_id, 5)  # Show loading for up to 5 seconds
        
        try:
            # First, try to get template-based response
            template_message, template = get_template_response(db, user_id, text, "conversation")
            
            if template_message and template:
                # Use template response
                line_bot_api.reply_message(event.reply_token, template_message)
                reply_text = f"[Template: {template.name}] " + str(template.content.get('text', 'Template response'))
                print(f"Used template '{template.name}' for user {user_id}")
            else:
                # Fallback to AI response
                config = {"configurable": {"thread_id": user_id}}
                input_msg = {"messages": [HumanMessage(content=text)]}
                output = agent_executor.invoke({"input": text, "chat_history": []})
                reply_text = output.get("output", "No response")
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
                print(f"Used AI response for user {user_id}")
                
        except Exception as e:
            # Final fallback to simple text
            reply_text = f"Error: {str(e)}"
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
            print(f"Error processing message for user {user_id}: {e}")
        
        create_chat_message(db, user_id, reply_text, is_from_user=False)
        
        # Broadcast bot reply to admin panel
        try:
            asyncio.create_task(manager.broadcast({
                "type": "message", 
                "user_id": user_id, 
                "text": reply_text, 
                "from": "bot"
            }))
        except Exception as e:
            print(f"Error broadcasting bot reply: {e}")
        
        # Check for tool call (mode switch)
        if "switch_to_manual_mode" in reply_text.lower():
            update_line_user_mode(db, user_id, 'manual')
            send_telegram_notify(user_id)
            # Broadcast mode switch
            try:
                asyncio.create_task(manager.broadcast({
                    "type": "mode_switch", 
                    "user_id": user_id, 
                    "mode": "manual"
                }))
            except Exception as e:
                print(f"Error broadcasting mode switch: {e}")
    else:
        # Manual mode - don't auto-reply
        print(f"User {user_id} in manual mode, not replying automatically")
    
    # Broadcast user message to admin panel
    try:
        asyncio.create_task(manager.broadcast({
            "type": "message", 
            "user_id": user_id, 
            "text": text, 
            "from": "user"
        }))
    except Exception as e:
        print(f"Error broadcasting user message: {e}")

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Root endpoint
@app.get("/")
def root():
    return {"message": "LINE Agent API is running", "docs": "/docs"}

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Simple webhook test endpoint
@app.post("/webhook-test")
async def webhook_test(request: Request):
    body = await request.body()
    return {"status": "OK", "received": len(body), "timestamp": datetime.now().isoformat()}

@app.get("/api/users", response_model=List[LineUserSchema])
def get_users(db: Session = Depends(get_db)):
    users = get_all_users(db)
    response = JSONResponse(content=[
        {
            "line_id": user.line_id,
            "name": user.name, 
            "picture": user.picture,
            "mode": user.mode,
            "added_at": user.added_at.isoformat(),
            "blocked_at": user.blocked_at.isoformat() if user.blocked_at else None
        } for user in users
    ])
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response

@app.get("/api/users/{user_id}/chat", response_model=List[ChatMessageSchema])
def get_messages(user_id: str, db: Session = Depends(get_db)):
    return get_chat_history(db, user_id)

@app.post("/api/mode/{user_id}")
def set_mode(user_id: str, mode: str = Query(..., description="Mode to set: 'bot' or 'manual'"), db: Session = Depends(get_db)):
    user = update_line_user_mode(db, user_id, mode)
    if user:
        # Broadcast mode change to connected clients
        try:
            asyncio.create_task(manager.broadcast({
                "type": "mode_switch", 
                "user_id": user_id, 
                "mode": mode
            }))
        except Exception as e:
            print(f"Error broadcasting mode change: {e}")
        
        return {"status": "ok", "mode": user.mode, "user_id": user_id}
    else:
        raise HTTPException(status_code=404, detail="User not found")

@app.get("/api/dashboard", response_model=DashboardStats)
def dashboard(db: Session = Depends(get_db)):
    stats = get_dashboard_stats(db)
    response = JSONResponse(content=stats)
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response

# Loading Animation API Endpoints
@app.post("/api/loading/start/{user_id}")
def start_loading(user_id: str, loading_seconds: int = 20):
    """Start loading animation for a specific user"""
    success = start_loading_animation(user_id, loading_seconds)
    return {"status": "success" if success else "error", "user_id": user_id, "loading_seconds": loading_seconds}

@app.post("/api/loading/stop/{user_id}")
def stop_loading(user_id: str):
    """Stop loading animation for a specific user"""
    success = stop_loading_animation(user_id)
    return {"status": "success" if success else "error", "user_id": user_id}

# Message Templates API Endpoints

# Categories
@app.post("/api/categories", response_model=MessageCategorySchema)
def create_category(category: MessageCategoryCreate, db: Session = Depends(get_db)):
    return create_message_category(db, category)

@app.get("/api/categories", response_model=List[MessageCategorySchema])
def list_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_message_categories(db, skip, limit)

@app.get("/api/categories/{category_id}", response_model=MessageCategorySchema)
def get_category(category_id: int, db: Session = Depends(get_db)):
    category = get_message_category(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@app.put("/api/categories/{category_id}", response_model=MessageCategorySchema)
def update_category(category_id: int, category_update: MessageCategoryUpdate, db: Session = Depends(get_db)):
    category = update_message_category(db, category_id, category_update)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@app.delete("/api/categories/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db)):
    category = delete_message_category(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"message": "Category deleted successfully"}

# Templates
@app.post("/api/templates", response_model=MessageTemplateSchema)
def create_template(template: MessageTemplateCreate, db: Session = Depends(get_db)):
    return create_message_template(db, template)

@app.get("/api/templates", response_model=List[MessageTemplateSchema])
def list_templates(
    skip: int = 0, 
    limit: int = 100,
    category_id: Optional[int] = None,
    message_type: Optional[str] = None,
    is_active: Optional[bool] = True,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    return get_message_templates(db, skip, limit, category_id, message_type, is_active, search)

@app.get("/api/templates/{template_id}", response_model=MessageTemplateSchema)
def get_template(template_id: int, db: Session = Depends(get_db)):
    template = get_message_template(db, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template

@app.put("/api/templates/{template_id}", response_model=MessageTemplateSchema)
def update_template(template_id: int, template_update: MessageTemplateUpdate, db: Session = Depends(get_db)):
    template = update_message_template(db, template_id, template_update)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template

@app.delete("/api/templates/{template_id}")
def delete_template(template_id: int, db: Session = Depends(get_db)):
    template = delete_message_template(db, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return {"message": "Template deleted successfully"}

# Template Selection for Bot
@app.post("/api/templates/select")
def select_template(request: TemplateSelectionRequest, db: Session = Depends(get_db)):
    """Select appropriate template based on context"""
    selector = TemplateSelector(db)
    template = selector.select_template(request)
    
    if template:
        return {
            "template_id": template.id,
            "template": template,
            "message": "Template selected successfully"
        }
    else:
        return {
            "template_id": None,
            "template": None,
            "message": "No suitable template found"
        }

# Main execution block for direct python main.py execution
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)