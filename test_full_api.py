#!/usr/bin/env python3
"""
Test script to verify both Replicate (images) and OpenAI (backstories) are working.
"""
import requests
import json
import sys

API_URL = "http://localhost:8001/memory-sketch"
TEST_IMAGE = "test_selfie.jpg"

print("=" * 60)
print("Testing Memory Sketch API")
print("=" * 60)
print(f"\n1. Uploading image: {TEST_IMAGE}")
print(f"2. Calling API: {API_URL}\n")

try:
    with open(TEST_IMAGE, 'rb') as f:
        files = {'file': (TEST_IMAGE, f, 'image/jpeg')}
        response = requests.post(API_URL, files=files, timeout=120)
    
    print(f"Status Code: {response.status_code}\n")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ SUCCESS! Both services responded:\n")
        print("-" * 60)
        print("📸 SKETCH URL (from Replicate):")
        print(f"   {data.get('sketch_url', 'N/A')}")
        print("\n📝 BACKSTORY (from OpenAI/ChatGPT):")
        print(f"   {data.get('backstory', 'N/A')}")
        print("\n🔧 MODE:")
        print(f"   {data.get('mode', 'N/A')}")
        print("-" * 60)
        print("\n💡 You can open the sketch URL in your browser to see the image!")
    else:
        print("❌ ERROR:")
        error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
        print(json.dumps(error_data, indent=2))
        
except requests.exceptions.Timeout:
    print("❌ Request timed out. The image generation may take a while...")
except requests.exceptions.ConnectionError:
    print(f"❌ Could not connect to {API_URL}")
    print("   Make sure the server is running: uvicorn main:app --port 8001")
except Exception as e:
    print(f"❌ Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

