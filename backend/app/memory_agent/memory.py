# Import from parent app directory
try:
    from ..database import SessionLocal
    from ..models import ChatMessage
    from ..crud import get_chat_history
except ImportError:
    from database import SessionLocal
    from models import ChatMessage
    from crud import get_chat_history

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class MemoryManager:
    def get_conversation_context(self, user_id: str, max_messages: int = 10) -> list:
        db = next(get_db())
        messages = get_chat_history(db, user_id)[-max_messages:]
        return [{"role": "user" if msg.is_from_user else "assistant", "content": msg.message} for msg in messages]

    def summarize_context(self, user_id: str) -> str:
        context = self.get_conversation_context(user_id)
        if not context:
            return "No conversation history available."
        summary = "Conversation summary:\n"
        for msg in context:
            role = msg["role"].capitalize()
            summary += f"{role}: {msg['content']}\n"
        return summary