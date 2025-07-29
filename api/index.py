"""
Simplified LINE Bot webhook for Vercel
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import json
import os

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "LINE Bot API is running on Vercel!"}

@app.post("/")
async def webhook(request: Request):
    """Handle LINE webhook"""
    try:
        body = await request.body()
        return {"status": "ok", "message": "Webhook received"}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )