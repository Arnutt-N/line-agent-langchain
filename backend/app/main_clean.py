"""
LINE Agent LangChain Backend
A FastAPI-based LINE Bot with LangChain integration for intelligent conversations.
"""
import os
import json
import asyncio
from contextlib import asynccontextmanager
from typing import List
from datetime import datetime

from fastapi import FastAPI, WebSocket, Depends, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, FollowEvent, UnfollowEvent
from dotenv import load_dotenv
from sqlalchemy.orm import Session

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
    from .crud import (get_all_users, get_chat_history, update_line_user_mode, 
                      create_line_user, create_chat_message, create_event_log,
                      renew_line_user, block_line_user, get_dashboard_stats)
    from .schemas import LineUserSchema, ChatMessageSchema, DashboardStats
    from .telegram import send_telegram_notify
    from .tools import switch_to_manual_mode, query_conversation_history, summarize_conversation
except ImportError:
    from database import SessionLocal
    from models import LineUser
    from crud import (get_all_users, get_chat_history, update_line_user_mode,
                     create_line_user, create_chat_message, create_event_log,
                     renew_line_user, block_line_user, get_dashboard_stats)
    from schemas import LineUserSchema, ChatMessageSchema, DashboardStats
    from telegram import send_telegram_notify
    from tools import switch_to_manual_mode, query_conversation_history, summarize_conversation

load_dotenv()

# Initialize checkpointer on first use
CHECKPOINTER = None


def get_checkpointer():
    """Get or create the checkpointer for LangGraph."""
    global CHECKPOINTER
    if CHECKPOINTER is None:
        CHECKPOINTER = MemorySaver()
    return CHECKPOINTER

# LINE Bot API initialization
line_bot_api = LineBotApi(os.getenv('LINE_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))

# LangChain LLM (Gemini)
llm = ChatGoogleGenerativeAI(
    model=os.getenv("GEMINI_MODEL", "gemini-1.5-flash"),
    api_key=os.getenv("GEMINI_API_KEY"),
    temperature=float(os.getenv("GEMINI_TEMPERATURE", "0.7")),
    max_tokens=int(os.getenv("GEMINI_MAX_TOKENS", "1000"))
)

# Tools and Agent setup
tools = [switch_to_manual_mode, query_conversation_history, summarize_conversation]

prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a friendly chat bot. In bot mode, echo messages or use tools if needed.
     If 'human' is mentioned, use switch_to_manual_mode. In manual mode, do not respond."""),
    ("placeholder", "{chat_history}"),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)


async def create_graph():
    """Create LangGraph for stateful conversation with checkpointer."""
    checkpointer = get_checkpointer()
    graph = StateGraph(state_schema=MessagesState)
    graph.add_node("agent", agent_executor)
    graph.add_edge(START, "agent")
    return graph.compile(checkpointer=checkpointer)


class ConnectionManager:
    """Manages WebSocket connections for real-time communication."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Accept and store new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection."""
        self.active_connections.remove(websocket)

    async def broadcast(self, data: dict):
        """Broadcast message to all connected WebSockets."""
        message = json.dumps(data)
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()

# FastAPI app initialization
app = FastAPI(title="LINE Agent API", description="LINE Bot with LangChain integration")
