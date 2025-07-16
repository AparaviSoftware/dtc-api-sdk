#!/usr/bin/env python3
"""
Test using the native pipeline format from the sample
"""

import json
import tempfile
from pathlib import Path
from dtc_api_sdk import DTCApiClient
from dtc_api_sdk.exceptions import DTCApiError

def test_native_pipeline_format():
    print("🔬 Testing Native Pipeline Format")
    print("=" * 50)
    
    client = DTCApiClient()
    
    # Use the actual format from the sample pipeline
    # Simplified version focusing on webhook -> parse -> response
    native_pipeline = {
        "components": [
            {
                "id": "webhook_1",
                "provider": "webhook",
                "config": {
                    "mode": "Source",
                    "type": "webhook"
                }
            },
            {
                "id": "parse_1", 
                "provider": "parse",
                "config": {},
                "input": [
                    {
                        "lane": "tags",
                        "from": "webhook_1"
                    }
                ]
            },
            {
                "id": "response_1",
                "provider": "response", 
                "config": {
                    "lanes": []
                },
                "input": [
                    {
                        "lane": "text",
                        "from": "parse_1"
                    }
                ]
            }
        ],
        "id": "test-webhook-parse-pipeline"
    }
    
    print("📋 Native Pipeline Configuration:")
    print(json.dumps(native_pipeline, indent=2))
    
    # Test 1: Validate this format
    try:
        print("\n✅ Validating native pipeline format...")
        is_valid = client.validate_pipeline(native_pipeline)
        print(f"Native format is: {'✅ Valid' if is_valid else '❌ Invalid'}")
        
        if is_valid:
            # Test 2: Try to create pipeline
            print(f"\n🔧 Creating native format pipeline...")
            pipeline_token = client.create_pipeline(
                config=native_pipeline,
                name="native_parse_test"
            )
            print(f"✅ Pipeline created! Token: {pipeline_token[:8]}...")
            
            # Test 3: Try webhook approach
            print(f"\n🪝 Getting webhook URL...")
            webhook_url = client.get_dropper_url(pipeline_token, "parse")
            print(f"✅ Webhook URL: {webhook_url}")
            
            # Clean up
            print(f"\n🧹 Cleaning up...")
            cleanup_success = client.delete_pipeline(pipeline_token)
            print(f"Pipeline deleted: {'✅' if cleanup_success else '❌'}")
            
    except DTCApiError as e:
        print(f"❌ Native format failed: {e}")
        if e.status_code:
            print(f"   Status Code: {e.status_code}")
        if e.response_data:
            print(f"   Response: {e.response_data}")

def test_task_with_native_format():
    print(f"\n🚀 Testing Task with Native Format")
    print("=" * 50)
    
    client = DTCApiClient()
    
    # Try the native format as a task
    native_config = {
        "components": [
            {
                "id": "parse_1",
                "provider": "parse", 
                "config": {
                    "profile": "default"
                }
            },
            {
                "id": "response_1",
                "provider": "response",
                "config": {
                    "lanes": ["text"]
                },
                "input": [
                    {
                        "lane": "text", 
                        "from": "parse_1"
                    }
                ]
            }
        ]
    }
    
    try:
        print("🧪 Submitting task with native format...")
        token = client.execute_task(
            config=native_config,
            name="native_parse_task",
            threads=1
        )
        print(f"✅ Task submitted! Token: {token[:8]}...")
        
        # Check status
        task_info = client.get_task_status(token)
        print(f"📊 Status: {task_info.status.value}")
        print(f"   Name: {task_info.name}")
        
        # Cancel task
        print("🛑 Cancelling task...")
        cancelled = client.cancel_task(token)
        print(f"Task cancelled: {'✅' if cancelled else '❌'}")
        
    except DTCApiError as e:
        print(f"⚠️  Native task failed: {e}")
        if e.status_code:
            print(f"   Status Code: {e.status_code}")

def test_load_actual_sample():
    """Load and test the actual sample pipeline file"""
    print(f"\n📄 Testing Actual Sample Pipeline File")
    print("=" * 50)
    
    client = DTCApiClient()
    
    try:
        # Load the actual sample file
        with open("examle_pipelines/aparavi-project-export-new-project-2025-07-09T19-18.json", "r") as f:
            sample_pipeline = json.load(f)
        
        print(f"✅ Loaded sample pipeline with {len(sample_pipeline['components'])} components")
        
        # Print component summary
        print("📋 Pipeline Components:")
        for comp in sample_pipeline['components']:
            provider = comp.get('provider', 'unknown')
            comp_id = comp.get('id', 'unknown')
            print(f"   - {comp_id}: {provider}")
        
        # Test validation
        print(f"\n✅ Validating actual sample pipeline...")
        is_valid = client.validate_pipeline(sample_pipeline)
        print(f"Sample pipeline is: {'✅ Valid' if is_valid else '❌ Invalid'}")
        
        if is_valid:
            print("🎉 Sample pipeline validates successfully!")
            print("   You could use this for actual processing")
        
    except FileNotFoundError:
        print("❌ Sample pipeline file not found")
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {e}")
    except DTCApiError as e:
        print(f"❌ Validation failed: {e}")

if __name__ == "__main__":
    print("🧬 DTC API Native Pipeline Format Test")
    print("Testing the native component-based pipeline format\n")
    
    test_native_pipeline_format()
    test_task_with_native_format() 
    test_load_actual_sample()
    
    print(f"\n🎉 Native pipeline test completed!")
    print("=" * 50) 