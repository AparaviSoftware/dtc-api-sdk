#!/usr/bin/env python3
"""
Curl Format Test - Exact Match to Working Curl Command
======================================================

This test exactly matches the successful curl command format.
"""

import os
import json
import time
from pathlib import Path
import requests

def curl_format_test():
    """Test that exactly matches the successful curl command."""
    print("🚀 Curl Format Test - Exact Match")
    print("=" * 32)
    
    # Use the API key from the curl command
    api_key = "itUuVlf1cNHmYIRENUG7c51wdx4sH4veHmX24LQsTAje9sY_-u8V76CrTn4INwPT"
    base_url = "https://eaas-dev.aparavi.com"
    
    # Pipeline configuration
    pipeline_config = {
        "pipeline": {
            "source": "webhook_1",
            "components": [
                {
                    "id": "webhook_1",
                    "provider": "webhook",
                    "config": {
                        "hideForm": True,
                        "mode": "Source",
                        "type": "webhook"
                    }
                },
                {
                    "id": "parse_1",
                    "provider": "parse",
                    "config": {},
                    "input": [{"lane": "tags", "from": "webhook_1"}]
                },
                {
                    "id": "response_1",
                    "provider": "response",
                    "config": {"lanes": []},
                    "input": [
                        {"lane": "text", "from": "parse_1"},
                        {"lane": "text", "from": "webhook_1"}
                    ]
                }
            ]
        }
    }
    
    # Create task
    print("1️⃣ Creating task...")
    task_response = requests.put(
        f"{base_url}/task",
        params={"name": "curl_format_test"},
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json=pipeline_config,
        timeout=30
    )
    
    if task_response.status_code != 200:
        print(f"❌ Task creation failed: {task_response.text}")
        return False
    
    task_token = task_response.json()["data"]["token"]
    print(f"✅ Task created: {task_token}")
    
    # Wait for task to be ready
    print("⏳ Waiting for task to be ready...")
    time.sleep(5)
    
    # Send Word document via webhook - EXACT curl format
    print("\n2️⃣ Sending Word document via webhook (curl format)...")
    word_file = "test_data/10-MB-Test.docx"
    
    print(f"📄 File: {Path(word_file).name}")
    print(f"📏 Size: {Path(word_file).stat().st_size:,} bytes")
    
    # Read file as binary data (like curl -T)
    with open(word_file, 'rb') as f:
        file_data = f.read()
    
    # Webhook URL with exact parameters from curl command
    webhook_url = f"{base_url}/webhook"
    webhook_params = {
        "type": "cpu",
        "apikey": api_key,
        "token": task_token
    }
    
    # Headers exactly like curl command
    webhook_headers = {
        "Authorization": api_key,  # Note: no "Bearer" prefix in curl
        "Content-Type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    }
    
    print(f"🔗 URL: {webhook_url}")
    print(f"📋 Params: {webhook_params}")
    print(f"📋 Headers: {webhook_headers}")
    
    start_time = time.time()
    webhook_response = requests.put(
        webhook_url,
        params=webhook_params,
        headers=webhook_headers,
        data=file_data,  # Upload file as request body (not multipart)
        timeout=120
    )
    upload_time = time.time() - start_time
    
    if webhook_response.status_code != 200:
        print(f"❌ Webhook failed: {webhook_response.text}")
        return False
    
    print(f"✅ File uploaded in {upload_time:.1f} seconds")
    
    # Check webhook response
    print("\n3️⃣ Checking webhook response...")
    webhook_result = webhook_response.json()
    
    print(f"📊 Response Summary:")
    print(f"   Status: {webhook_result.get('status', 'N/A')}")
    
    if 'data' in webhook_result:
        data = webhook_result["data"]
        print(f"   Objects Requested: {data.get('objectsRequested', 0)}")
        print(f"   Objects Completed: {data.get('objectsCompleted', 0)}")
        print(f"   Processing Time: {webhook_result.get('metrics', {}).get('total_time', 0)/1000:.1f} seconds")
        
        objects = data.get("objects", {})
        if objects:
            print(f"\n📄 Extracted Objects: {len(objects)}")
            for obj_id, obj_data in objects.items():
                print(f"\n   Object ID: {obj_id}")
                
                if "text" in obj_data:
                    if isinstance(obj_data["text"], list):
                        text = "\n".join(obj_data["text"])
                    else:
                        text = obj_data["text"]
                    
                    print(f"   Text Length: {len(text)} characters")
                    print(f"   Text Preview: {text[:200]}...")
                
                if "metadata" in obj_data:
                    metadata = obj_data["metadata"]
                    print(f"   Content-Type: {metadata.get('Content-Type', 'N/A')}")
                    print(f"   Creator: {metadata.get('dc:creator', 'N/A')}")
                
                if "__types" in obj_data:
                    print(f"   Data Types: {obj_data['__types']}")
        else:
            print("⚠️ No objects found - might still be processing")
    
    # Save results
    with open("curl_format_results.json", 'w') as f:
        json.dump(webhook_result, f, indent=2)
    print(f"\n💾 Results saved to: curl_format_results.json")
    
    return True

if __name__ == "__main__":
    success = curl_format_test()
    if success:
        print("\n🎉 Curl format test successful!")
    else:
        print("\n❌ Curl format test failed.") 