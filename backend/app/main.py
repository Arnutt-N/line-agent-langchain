import json
from fastapi import FastAPI, WebSocket, Depends, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, FollowEvent, UnfollowEvent
from dotenv import load_dotenv
import os
from contextlib import asynccontextmanager
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, StateGraph
from langgraph.graph.message import MessagesState
from langchain_core.messages import HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import AgentExecutor
# Handle both direct execution and module imports
try:
    from .database import SessionLocal
    from .models import LineUser
    from .crud import get_all_users, get_chat_history, update_line_user_mode, create_line_user, create_chat_message, create_event_log, renew_line_user, block_line_user, get_dashboard_stats
    from .schemas import LineUserSchema, ChatMessageSchema, DashboardStats
    from .telegram import send_telegram_notify
    from .tools import switch_to_manual_mode, query_conversation_history, summarize_conversation
except ImportError:
    from database import SessionLocal
    from models import LineUser
    from crud import get_all_users, get_chat_history, update_line_user_mode, create_line_user, create_chat_message, create_event_log, renew_line_user, block_line_user, get_dashboard_stats
    from schemas import LineUserSchema, ChatMessageSchema, DashboardStats
    from telegram import send_telegram_notify
    from tools import switch_to_manual_mode, query_conversation_history, summarize_conversation
from sqlalchemy.orm import Session
from typing import List
import asyncio
from datetime import datetime

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

# LangChain LLM (Gemini)
llm = ChatGoogleGenerativeAI(
    model=os.getenv("GEMINI_MODEL", "gemini-1.5-flash"), 
    api_key=os.getenv("GEMINI_API_KEY"),
    temperature=float(os.getenv("GEMINI_TEMPERATURE", "0.7")),
    max_tokens=int(os.getenv("GEMINI_MAX_TOKENS", "1000"))
)

# Tools
tools = [switch_to_manual_mode, query_conversation_history, summarize_conversation]

# Prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a friendly chat bot. In bot mode, echo messages or use tools if needed. If 'human' is mentioned, use switch_to_manual_mode. In manual mode, do not respond."),
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
                line_bot_api.push_message(user_id, TextSendMessage(text=message))
                db = SessionLocal()
                create_chat_message(db, user_id, message, is_from_user=False)
                await manager.broadcast({"type": "message", "user_id": user_id, "text": message, "from": "admin"})
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
    else:
        create_line_user(db, user_id, profile.display_name, profile.picture_url)
        create_event_log(db, user_id, 'add')
    # Remove asyncio.create_task for now to avoid sync/async issues
    # asyncio.create_task(manager.broadcast({"type": "user_update", "user_id": user_id, "action": "add/renew"}))

@handler.add(UnfollowEvent)
def handle_unfollow(event):
    db = SessionLocal()
    user_id = event.source.user_id
    block_line_user(db, user_id)
    create_event_log(db, user_id, 'block')
    # Remove asyncio.create_task for now to avoid sync/async issues
    # asyncio.create_task(manager.broadcast({"type": "user_update", "user_id": user_id, "action": "block"}))

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
        config = {"configurable": {"thread_id": user_id}}
        input_msg = {"messages": [HumanMessage(content=text)]}
        # Use agent_executor directly for now
        try:
            output = agent_executor.invoke({"input": text, "chat_history": []})
            reply_text = output.get("output", "No response")
        except Exception as e:
            reply_text = f"Error: {str(e)}"
            print(f"Agent error for user {user_id}: {e}")
        
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
        create_chat_message(db, user_id, reply_text, is_from_user=False)
        
        # Check for tool call (mode switch)
        if "switch_to_manual_mode" in str(output).lower():  # Simple check; improve with output parsing
            update_line_user_mode(db, user_id, 'manual')
            send_telegram_notify(user_id)
            # Remove asyncio.create_task for now to avoid sync/async issues
            # asyncio.create_task(manager.broadcast({"type": "mode_switch", "user_id": user_id, "mode": "manual"}))
    else:
        # Manual mode - don't auto-reply
        print(f"User {user_id} in manual mode, not replying automatically")
    
    # Remove asyncio.create_task for now to avoid sync/async issues  
    # asyncio.create_task(manager.broadcast({"type": "message", "user_id": user_id, "text": text, "from": "user"}))

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
def set_mode(user_id: str, mode: str, db: Session = Depends(get_db)):
    user = update_line_user_mode(db, user_id, mode)
    return {"status": "ok", "mode": user.mode}

@app.get("/api/dashboard", response_model=DashboardStats)
def dashboard(db: Session = Depends(get_db)):
    stats = get_dashboard_stats(db)
    response = JSONResponse(content=stats)
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response

# Main execution block for direct python main.py execution
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)