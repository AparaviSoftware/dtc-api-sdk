#!/usr/bin/env python3
"""
Final test - try different ways to submit the pipeline
"""

import json
from dtc_api_sdk import DTCApiClient
from dtc_api_sdk.exceptions import DTCApiError

def test_pipeline_wrapper_formats():
    print("🔧 Testing Different Pipeline Wrapper Formats")
    print("=" * 60)
    
    client = DTCApiClient()
    
    # Load the actual sample that validates successfully
    with open("examle_pipelines/aparavi-project-export-new-project-2025-07-09T19-18.json", "r") as f:
        sample_pipeline = json.load(f)
    
    print(f"✅ Loaded sample pipeline: {sample_pipeline['id']}")
    
    # Try different wrapper formats
    test_formats = [
        {
            "name": "Direct Pipeline",
            "config": sample_pipeline
        },
        {
            "name": "Pipeline in pipeline key",
            "config": {"pipeline": sample_pipeline}
        },
        {
            "name": "Pipeline in config key", 
            "config": {"config": sample_pipeline}
        },
        {
            "name": "Minimal parse-only pipeline",
            "config": {
                "components": [
                    {
                        "id": "parse_1",
                        "provider": "parse",
                        "config": {"profile": "default"}
                    }
                ],
                "id": "minimal-parse-test"
            }
        }
    ]
    
    for test_format in test_formats:
        print(f"\n🧪 Testing: {test_format['name']}")
        try:
            # First validate
            is_valid = client.validate_pipeline(test_format['config'])
            print(f"   Validation: {'✅ Valid' if is_valid else '❌ Invalid'}")
            
            if is_valid:
                # Try to create pipeline
                print("   🔧 Attempting pipeline creation...")
                pipeline_token = client.create_pipeline(
                    config=test_format['config'],
                    name=f"test_{test_format['name'].lower().replace(' ', '_')}"
                )
                print(f"   ✅ SUCCESS! Token: {pipeline_token[:8]}...")
                
                # Immediately clean up
                client.delete_pipeline(pipeline_token)
                print("   🧹 Cleaned up")
                break  # If one works, we found the format!
                
        except DTCApiError as e:
            print(f"   ❌ Failed: {e.message}")
            if "Missing or invalid 'pipeline' object" in str(e):
                print("   💡 Still the pipeline object issue")
            continue

def test_task_execution():
    """Try submitting as a task instead of pipeline"""
    print(f"\n🚀 Testing Task Execution with Sample Pipeline")
    print("=" * 60)
    
    client = DTCApiClient()
    
    # Create a very simple parse task
    simple_parse = {
        "components": [
            {
                "id": "parse_only",
                "provider": "parse",
                "config": {"profile": "default"}
            }
        ],
        "id": "simple-parse-task"
    }
    
    try:
        print("🧪 Validating simple parse task...")
        is_valid = client.validate_pipeline(simple_parse)
        print(f"✅ Validation: {'Valid' if is_valid else 'Invalid'}")
        
        if is_valid:
            print("🚀 Executing as task...")
            token = client.execute_task(
                config=simple_parse,
                name="simple_parse_execution",
                threads=1
            )
            print(f"✅ Task submitted! Token: {token[:8]}...")
            
            # Check status
            task_info = client.get_task_status(token)
            print(f"📊 Status: {task_info.status.value}")
            print(f"   Name: {task_info.name}")
            
            # Cancel
            client.cancel_task(token)
            print("🛑 Task cancelled")
            
    except DTCApiError as e:
        print(f"❌ Task execution failed: {e}")

def show_summary():
    """Show what we've learned"""
    print(f"\n📋 Summary of SDK Testing")
    print("=" * 60)
    print("✅ What works:")
    print("   - SDK installation and import")
    print("   - API connectivity and authentication") 
    print("   - Version and status checks")
    print("   - Service listing")
    print("   - Pipeline validation (both simple and complex)")
    print("   - Error handling and exception catching")
    
    print("\n⚠️  What needs work:")
    print("   - Pipeline creation (Missing or invalid 'pipeline' object)")
    print("   - Task execution with pipeline configs")
    print("   - File upload to pipelines")
    
    print("\n🎯 Next Steps:")
    print("   - Check API documentation for exact pipeline format")
    print("   - Try different authentication scopes")
    print("   - Test with simpler pipeline configurations")
    print("   - Contact API support for pipeline object format")

if __name__ == "__main__":
    print("🏁 Final DTC API SDK Test")
    print("Testing pipeline wrapper formats and task execution\n")
    
    test_pipeline_wrapper_formats()
    test_task_execution()
    show_summary()
    
    print(f"\n🎉 SDK testing completed!")
    print("The SDK is working well - just need to resolve the pipeline format issue!") 