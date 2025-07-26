from langchain_core.tools import tool

# Handle both package and direct imports
try:
    from .database import SessionLocal
    from .crud import update_line_user_mode
    from .memory_agent.memory import MemoryManager
except ImportError:
    from database import SessionLocal
    from crud import update_line_user_mode
    from memory_agent.memory import MemoryManager

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@tool
def switch_to_manual_mode(user_id: str):
    """Switches the user to manual mode."""
    db = next(get_db())
    update_line_user_mode(db, user_id, 'manual')
    return {"status": "success", "message": "Switched to manual mode"}

@tool
def query_conversation_history(user_id: str):
    """Queries the conversation history for the user."""
    memory_manager = MemoryManager()
    history = memory_manager.get_conversation_context(user_id)
    return {"history": history}

@tool
def summarize_conversation(user_id: str):
    """Summarizes the conversation for the user."""
    memory_manager = MemoryManager()
    summary = memory_manager.summarize_context(user_id)
    return {"summary": summary}