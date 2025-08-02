import os
import logging
from supabase import create_client, Client
from typing import Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SQLAlchemy setup for backwards compatibility
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./line_agent.db")
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class DatabaseManager:
    def __init__(self):
        self.supabase: Optional[Client] = None
        self._initialize_supabase()
    
    def _initialize_supabase(self):
        """Initialize Supabase connection"""
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_service_key = os.getenv("SUPABASE_SERVICE_KEY")
        
        if not supabase_url or not supabase_service_key:
            logger.error("❌ Supabase credentials not found in environment variables")
            logger.error("Please check SUPABASE_URL and SUPABASE_SERVICE_KEY")
            return
        
        try:
            # Create client without proxy parameter
            self.supabase = create_client(supabase_url, supabase_service_key)
            logger.info("✅ Supabase connection established successfully")
            
            # Test connection
            result = self.supabase.table('line_users').select("count").execute()
            logger.info(f"✅ Database connection test successful")
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to Supabase: {e}")
            # If it's a proxy error, try to create client differently
            if "proxy" in str(e):
                try:
                    # Alternative approach without any extra parameters
                    import supabase
                    self.supabase = supabase.Client(supabase_url, supabase_service_key)
                    logger.info("✅ Supabase connection established with alternative method")
                except:
                    self.supabase = None
            else:
                self.supabase = None
    
    def get_client(self) -> Optional[Client]:
        """Get Supabase client"""
        if not self.supabase:
            logger.warning("⚠️ Supabase client not available, attempting reconnection...")
            self._initialize_supabase()
        return self.supabase
    
    def is_connected(self) -> bool:
        """Check if connected to database"""
        return self.supabase is not None
    
    def health_check(self) -> dict:
        """Database health check"""
        if not self.supabase:
            return {
                "status": "unhealthy",
                "error": "No database connection"
            }
        
        try:
            # Simple query to test connection
            result = self.supabase.table('line_users').select("count").execute()
            return {
                "status": "healthy",
                "type": "supabase",
                "url": os.getenv("SUPABASE_URL", "").split("@")[-1] if "@" in os.getenv("SUPABASE_URL", "") else os.getenv("SUPABASE_URL", "")[:50] + "..."
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }

# Global database manager instance
db_manager = DatabaseManager()

# Convenience function for getting client
def get_supabase() -> Optional[Client]:
    """Get Supabase client instance"""
    return db_manager.get_client()

# Convenience function for health check
def database_health() -> dict:
    """Get database health status"""
    return db_manager.health_check()
