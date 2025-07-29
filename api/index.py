"""
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