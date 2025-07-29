"""
Database configuration optimized for Vercel serverless deployment.
Uses connection pooling and environment-based configuration.
"""

from sqlalchemy import create_engine, pool
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

# If no DATABASE_URL is provided, fall back to SQLite for development
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./line_agent.db"

# Configure engine for serverless environment
if DATABASE_URL.startswith("postgresql"):
    # PostgreSQL configuration for production
    engine = create_engine(
        DATABASE_URL,
        poolclass=pool.NullPool,  # No connection pooling for serverless
        pool_pre_ping=True,       # Verify connections before use
        echo=False,               # Disable SQL logging in production
        connect_args={
            "sslmode": "require" if "localhost" not in DATABASE_URL else "disable",
            "connect_timeout": 30
        }
    )
else:
    # SQLite configuration for development/testing
    engine = create_engine(
        DATABASE_URL,
        poolclass=pool.StaticPool,
        connect_args={"check_same_thread": False},
        echo=False
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """
    Database session dependency for FastAPI.
    Ensures proper session cleanup in serverless environment.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_database():
    """
    Initialize database tables.
    Safe to call multiple times.
    """
    Base.metadata.create_all(bind=engine)