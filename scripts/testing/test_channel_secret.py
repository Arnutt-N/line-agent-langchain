#!/usr/bin/env python3
"""
Test script เพื่อตรวจสอบ Channel Secret ของ LINE Bot
"""
import os
from dotenv import load_dotenv
import hashlib
import hmac
import base64

load_dotenv()

def test_channel_secret():
    channel_secret = os.getenv('LINE_CHANNEL_SECRET')
    
    print("=== LINE Bot Channel Secret Test ===")
    print(f"Channel Secret Length: {len(channel_secret) if channel_secret else 'None'}")
    print(f"Channel Secret (first 10 chars): {channel_secret[:10] if channel_secret else 'None'}")
    print(f"Channel Secret (last 5 chars): {channel_secret[-5:] if channel_secret else 'None'}")
    
    # Test signature calculation
    test_body = '{"destination":"U05386e034c9e9951fab88bd214a6d724","events":[]}'
    test_body_bytes = test_body.encode('utf-8')
    
    try:
        hash = hmac.new(channel_secret.encode('utf-8'), test_body_bytes, hashlib.sha256).digest()
        calculated_signature = base64.b64encode(hash).decode()
        print(f"Calculated signature for test body: {calculated_signature}")
        
        # The signature from your log
        received_signature = "Sg6T0ofegAWB9u/QYtGcbdFtVP2XzUwefJKaV7NY8p0="
        print(f"Received signature from LINE: {received_signature}")
        print(f"Signatures match: {calculated_signature == received_signature}")
        
    except Exception as e:
        print(f"Error calculating signature: {e}")
        print("This usually means the Channel Secret is invalid")

if __name__ == "__main__":
    test_channel_secret()
