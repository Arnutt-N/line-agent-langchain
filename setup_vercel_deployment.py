#!/usr/bin/env python3
"""
Setup script for Vercel deployment configuration.
This script creates all necessary files for deploying the LINE Bot to Vercel.
"""

import os
import json
import shutil
from pathlib import Path

def create_vercel_config():
    """Create vercel.json configuration file"""
    config = {
        "version": 2,
        "builds": [
            {
                "src": "backend/app/main.py",
                "use": "@vercel/python",
                "config": {
                    "maxLambdaSize": "50mb"
                }
            },
            {
                "src": "frontend/package.json",
                "use": "@vercel/static-build",
                "config": {
                    "buildCommand": "npm run build",
                    "outputDirectory": "dist"
                }
            }
        ],
        "routes": [
            {
                "src": "/api/(.*)",
                "dest": "/backend/app/main.py"
            },
            {
                "src": "/webhook",
                "dest": "/backend/app/main.py"
            },
            {
                "src": "/ws/(.*)",
                "dest": "/backend/app/main.py"
            },
            {
                "src": "/(.*)",
                "dest": "/frontend/$1"
            }
        ],
        "env": {
            "PYTHON_VERSION": "3.11"
        },
        "functions": {
            "backend/app/main.py": {
                "runtime": "python3.11",
                "maxDuration": 30
            }
        }
    }
    
    with open("vercel.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
    print("✅ Created vercel.json")

def create_api_handler():
    """Create API handler for Vercel"""
    os.makedirs("api", exist_ok=True)
    
    api_content = '''"""
Vercel serverless function entry point for the LINE Bot backend.
This file serves as the handler for all API requests in Vercel's serverless environment.
"""

import sys
import os
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

# Import the FastAPI app
from backend.app.main import app

# Vercel expects a handler function
def handler(request, response):
    """
    Vercel serverless function handler
    """
    return app(request, response)

# For compatibility with different Vercel Python runtimes
application = app
'''
    
    with open("api/index.py", "w", encoding="utf-8") as f:
        f.write(api_content)
    print("✅ Created api/index.py")

def create_requirements():
    """Create requirements.txt for Vercel"""
    requirements = """# FastAPI and server dependencies
fastapi==0.104.1
uvicorn[standard]==0.24.0

# LINE Bot SDK
line-bot-sdk==3.5.0

# Database - using PostgreSQL for production
sqlalchemy==2.0.23
psycopg[binary]==3.1.12

# Environment and configuration
python-dotenv==1.0.0
pydantic==2.5.0

# HTTP requests
requests==2.31.0

# AI/ML dependencies
langchain==0.0.350
langchain-google-genai==1.0.1
langgraph==0.0.62
langgraph-checkpoint-postgres==1.0.1

# WebSocket support
websockets==12.0

# Additional utilities
python-multipart==0.0.6
"""
    
    with open("requirements.txt", "w", encoding="utf-8") as f:
        f.write(requirements)
    print("✅ Created requirements.txt")

def create_runtime():
    """Create runtime.txt"""
    with open("runtime.txt", "w", encoding="utf-8") as f:
        f.write("python-3.11")
    print("✅ Created runtime.txt")

def update_vite_config():
    """Update Vite configuration for production"""
    vite_config = """import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [],
  css: {
    postcss: './postcss.config.js',
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false,
    minify: 'esbuild',
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['lucide']
        }
      }
    }
  },
  server: {
    port: 5173,
    host: true,
    strictPort: true,
    proxy: {
      '/api': {
        target: process.env.NODE_ENV === 'production' 
          ? 'https://your-vercel-app.vercel.app' 
          : 'http://localhost:8000',
        changeOrigin: true
      },
      '/webhook': {
        target: process.env.NODE_ENV === 'production' 
          ? 'https://your-vercel-app.vercel.app' 
          : 'http://localhost:8000',
        changeOrigin: true
      },
      '/ws': {
        target: process.env.NODE_ENV === 'production' 
          ? 'wss://your-vercel-app.vercel.app' 
          : 'ws://localhost:8000',
        ws: true,
        changeOrigin: true
      }
    }
  },
  preview: {
    port: 4173,
    host: true
  }
})"""
    
    with open("frontend/vite.config.js", "w", encoding="utf-8") as f:
        f.write(vite_config)
    print("✅ Updated frontend/vite.config.js")

def create_database_vercel():
    """Create database configuration for Vercel"""
    db_config = '''"""
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
'''
    
    with open("backend/app/database_vercel.py", "w", encoding="utf-8") as f:
        f.write(db_config)
    print("✅ Created backend/app/database_vercel.py")

def create_env_example():
    """Create .env.example for Vercel"""
    env_example = """# LINE Bot Configuration
LINE_ACCESS_TOKEN=your_line_access_token_here
LINE_CHANNEL_SECRET=your_32_character_channel_secret_here

# Google AI Configuration  
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
GEMINI_TEMPERATURE=0.7
GEMINI_MAX_TOKENS=1000
GEMINI_ENABLE_SAFETY=false

# Database Configuration (Production - PostgreSQL)
DATABASE_URL=postgresql://username:password@host:port/database_name

# Telegram Configuration (Optional)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here
"""
    
    with open(".env.vercel.example", "w", encoding="utf-8") as f:
        f.write(env_example)
    print("✅ Created .env.vercel.example")

def create_deployment_guide():
    """Create deployment guide markdown file"""
    guide_content = """# 🚀 Vercel Deployment Guide

## Quick Start

1. **Set Environment Variables in Vercel Dashboard:**
   - LINE_ACCESS_TOKEN
   - LINE_CHANNEL_SECRET
   - GEMINI_API_KEY
   - DATABASE_URL (PostgreSQL)

2. **Deploy to Vercel:**
   ```bash
   npm i -g vercel
   vercel login
   vercel --prod
   ```

3. **Update LINE Webhook URL:**
   - Go to LINE Developers Console
   - Update webhook URL to: https://your-app.vercel.app/webhook

## Testing

- Health Check: https://your-app.vercel.app/health
- Frontend: https://your-app.vercel.app/
- API: https://your-app.vercel.app/api/users

## Database Options

### Option 1: Vercel Postgres (Recommended)
1. Vercel Dashboard → Storage → Create Postgres
2. Copy connection string to DATABASE_URL

### Option 2: External Database (Neon/Supabase)
1. Create PostgreSQL database
2. Copy connection string to DATABASE_URL

## Support
- Check Vercel logs: `vercel logs --follow`
- Test locally: `vercel dev`
"""
    
    with open("VERCEL_DEPLOYMENT.md", "w", encoding="utf-8") as f:
        f.write(guide_content)
    print("✅ Created VERCEL_DEPLOYMENT.md")

def main():
    """Main setup function"""
    print("🚀 Setting up Vercel deployment configuration...\n")
    
    # Check if we're in the right directory
    if not os.path.exists("backend") or not os.path.exists("frontend"):
        print("❌ Error: Please run this script from the project root directory")
        print("   Expected structure: backend/ and frontend/ folders")
        return
    
    try:
        # Create all necessary files
        create_vercel_config()
        create_api_handler()
        create_requirements()
        create_runtime()
        update_vite_config()
        create_database_vercel()
        create_env_example()
        create_deployment_guide()
        
        print("\n🎉 Vercel deployment setup completed successfully!")
        print("\n📋 Next Steps:")
        print("1. Set environment variables in Vercel Dashboard")
        print("2. Commit and push to GitHub:")
        print("   git add .")
        print("   git commit -m 'Add Vercel deployment configuration'")
        print("   git push origin main")
        print("3. Deploy to Vercel:")
        print("   vercel --prod")
        print("4. Update LINE Bot webhook URL")
        print("\n📖 See VERCEL_DEPLOYMENT.md for detailed instructions")
        
    except Exception as e:
        print(f"❌ Error during setup: {e}")
        return

if __name__ == "__main__":
    main()
