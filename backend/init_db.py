#!/usr/bin/env python3
"""
Database initialization script for LINE Agent
"""
import os
import sys

# Add app directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.database import engine, Base
from app.models import LineUser, ChatMessage, EventLog

def init_database():
    """Initialize database with all tables"""
    print("Initializing database...")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    print("Database tables created successfully!")
    print("Tables created:")
    for table in Base.metadata.tables.keys():
        print(f"  - {table}")

if __name__ == "__main__":
    init_database()