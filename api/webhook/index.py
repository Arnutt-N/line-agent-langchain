"""
LINE Bot webhook endpoint for Vercel serverless function
"""

import sys
import os
from pathlib import Path
import json

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from backend.app.main import app
    from fastapi import Request
    from starlette.responses import Response
    
    # Import Vercel adapter
    from mangum import Mangum
    handler = Mangum(app)
    
except ImportError as e:
    print(f"Import error: {e}")
    
    def handler(request, context):
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Import failed', 'detail': str(e)})
        }