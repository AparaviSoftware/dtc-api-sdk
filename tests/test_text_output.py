#!/usr/bin/env python3
"""
Test to capture actual text output from webhook -> parse pipeline
"""

import json
import time
import tempfile
from pathlib import Path
from dtc_api_sdk import DTCApiClient

def test_text_output_capture():
    print("📄 Testing Text Output Capture from Parse Pipeline")
    print("=" * 60)
    
    client = DTCApiClient()
    
    # Create a pipeline that captures text output
    config = {
        'pipeline': {
            'source': 'webhook_1',
            'components': [
                {
                    'id': 'webhook_1',
                    'provider': 'webhook',
                    'config': {
                        'mode': 'Source',
                        'type': 'webhook'
                    }
                },
                {
                    'id': 'parse_1', 
                    'provider': 'parse',
                    'config': {
                        'profile': 'default'
                    },
                    'input': [
                        {
                            'lane': 'tags',  # Input from webhook
                            'from': 'webhook_1'
                        }
                    ]
                },
                {
                    'id': 'response_1',
                    'provider': 'response',
                    'config': {
                        'lanes': ['text']  # Capture text output
                    },
                    'input': [
                        {
                            'lane': 'text',   # Get text from parse
                            'from': 'parse_1'
                        }
                    ]
                }
            ],
            'id': 'text-capture-pipeline'
        }
    }
    
    try:
        print("🔧 Creating pipeline...")
        pipeline_token = client.create_pipeline(config, name="text_capture_test")
        print(f"✅ Pipeline created: {pipeline_token[:8]}...")
        
        # Create a test file with content to parse
        temp_dir = Path(tempfile.mkdtemp())
        test_file = temp_dir / "sample.txt"
        test_content = "This is a sample document with text content that should be extracted by the parse component."
        test_file.write_text(test_content)
        
        print(f"\n📁 Created test file: {test_file.name}")
        print(f"   Content: '{test_content}'")
        
        # Method 1: Try uploading file to pipeline
        try:
            print(f"\n⬆️  Method 1: Uploading file to pipeline...")
            upload_success = client.upload_files(pipeline_token, [str(test_file)])
            print(f"   Upload result: {upload_success}")
            
            if upload_success:
                print("   ⏳ Waiting for processing...")
                time.sleep(3)
                print("   📊 File should be processed through parse component")
        except Exception as e:
            print(f"   ⚠️  Upload method failed: {e}")
        
        # Method 2: Try sending webhook data
        try:
            print(f"\n🪝 Method 2: Sending webhook data...")
            webhook_data = {
                "file_content": test_content,
                "filename": "sample.txt",
                "content_type": "text/plain"
            }
            webhook_response = client.send_webhook(pipeline_token, webhook_data)
            print(f"   ✅ Webhook sent!")
            print(f"   📊 Response: {webhook_response}")
            
            print("   ⏳ Waiting for parse processing...")
            time.sleep(3)
            
        except Exception as e:
            print(f"   ⚠️  Webhook method failed: {e}")
        
        # Method 3: Check if there's a way to get pipeline output/results
        try:
            print(f"\n📋 Method 3: Checking pipeline status/results...")
            # Note: We'd need to check if there's an endpoint to get pipeline results
            # This might be task-specific or require different monitoring
            print("   💡 In a real scenario, you would:")
            print("   - Monitor the response component for output")
            print("   - Check destination storage for results")
            print("   - Use webhooks for result notifications")
            print("   - Poll for completion status")
            
        except Exception as e:
            print(f"   ⚠️  Status check failed: {e}")
        
        # Clean up
        print(f"\n🧹 Cleaning up...")
        client.delete_pipeline(pipeline_token)
        test_file.unlink()
        temp_dir.rmdir()
        print("✅ Cleanup complete")
        
    except Exception as e:
        print(f"❌ Pipeline test failed: {e}")

def show_expected_flow():
    print(f"\n🎯 Expected Text Output Flow")
    print("=" * 60)
    print("📋 How I Expected It To Work:")
    print("""
1. 📄 Input File/Data → Webhook Component
   └── File contains: "Sample text content"
   
2. 🔄 Webhook → Parse Component  
   └── Parse extracts: "Sample text content"
   
3. 📤 Parse → Response Component (text lane)
   └── Output: {"text": "Sample text content"}
   
4. 💾 Response Component → Storage/Output
   └── Accessible via: API endpoint, webhook callback, or storage location
    """)
    
    print("🔍 What We Need to Find:")
    print("   • How to retrieve response component output")
    print("   • Where parsed text is stored")
    print("   • How to monitor pipeline completion")
    print("   • How to access text lane results")
    
    print(f"\n🛠️  Potential Solutions:")
    print("   1. Check if tasks have result endpoints")
    print("   2. Use webhook callbacks for results")
    print("   3. Monitor destination storage")
    print("   4. Check pipeline execution logs")

def test_task_approach():
    """Try using task instead of pipeline to see if we get results back"""
    print(f"\n🚀 Testing Task Approach for Text Output")
    print("=" * 60)
    
    client = DTCApiClient()
    
    # Try as a task instead of pipeline
    task_config = {
        'pipeline': {
            'source': 'parse_1',
            'components': [
                {
                    'id': 'parse_1',
                    'provider': 'parse',
                    'config': {
                        'profile': 'default'
                    }
                }
            ],
            'id': 'simple-parse-task'
        }
    }
    
    try:
        print("🧪 Submitting parse task...")
        token = client.execute_task(config=task_config, name="parse_text_task", threads=1)
        print(f"✅ Task submitted: {token[:8]}...")
        
        # Check status
        task_info = client.get_task_status(token)
        print(f"📊 Status: {task_info.status.value}")
        print(f"   Name: {task_info.name}")
        print(f"   Progress: {task_info.progress}")
        print(f"   Result: {task_info.result}")
        
        # In a real scenario, task_info.result might contain the parsed text!
        if task_info.result:
            print("🎉 Found task result data!")
            print(f"   Result content: {task_info.result}")
        
        # Cancel task
        client.cancel_task(token)
        print("🛑 Task cancelled")
        
    except Exception as e:
        print(f"⚠️  Task approach failed: {e}")

if __name__ == "__main__":
    print("🔍 DTC API - Text Output Investigation")
    print("Testing how to capture parsed text from webhook → parse flow\n")
    
    test_text_output_capture()
    show_expected_flow()
    test_task_approach()
    
    print(f"\n💡 Summary: The pipeline structure works, but we need to find")
    print("   how to retrieve the actual text output from the parse component!") 