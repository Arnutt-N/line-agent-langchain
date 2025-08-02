# database_local.py - For local development with SessionLocal
import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from supabase import create_client, Client
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SQLAlchemy setup (for local development)
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./line_agent.db")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Supabase setup
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

supabase_client: Optional[Client] = None

if SUPABASE_URL and SUPABASE_SERVICE_KEY:
    try:
        supabase_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        logger.info("✅ Supabase connection established")
    except Exception as e:
        logger.error(f"❌ Failed to connect to Supabase: {e}")
else:
    logger.warning("⚠️ Supabase credentials not found, using SQLite")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_supabase() -> Optional[Client]:
    return supabase_client

# Re-export from original database.py
from .database import DatabaseManager, database_health

# Create database manager instance
db_manager = DatabaseManager()

# Helper functions
def is_using_supabase():
    return supabase_client is not None

def is_using_sqlite():
    return "sqlite" in SQLALCHEMY_DATABASE_URL
