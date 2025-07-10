#!/usr/bin/env python3
"""
Test the sample pipeline with webhook -> parse -> text output
Based on the aparavi pipeline export
"""

import json
import time
import tempfile
from pathlib import Path
from dtc_api_sdk import DTCApiClient, PipelineConfig
from dtc_api_sdk.exceptions import DTCApiError

def create_test_file():
    """Create a simple test file for processing"""
    temp_dir = Path(tempfile.mkdtemp())
    test_file = temp_dir / "test_document.txt"
    test_file.write_text("Hello, this is a test document for the DTC API parsing pipeline. It contains some sample text to be processed.")
    return test_file

def test_parse_pipeline():
    print("🧪 Testing Webhook -> Parse Pipeline")
    print("=" * 50)
    
    client = DTCApiClient()
    
    # Create a simplified version of the sample pipeline
    # Focus on webhook -> parse -> text output
    pipeline_config = {
        "source": "webhook_input",  # Start with webhook
        "transformations": ["parse"],  # Use parse transformation
        "destination": "output",
        "settings": {
            "webhook": {
                "mode": "Source",
                "type": "webhook"
            },
            "parse": {
                "profile": "default"
            },
            "output_lanes": ["text"]  # We want text output
        }
    }
    
    print("📋 Pipeline Configuration:")
    print(json.dumps(pipeline_config, indent=2))
    
    # Test 1: Validate the configuration
    try:
        print("\n✅ Validating pipeline configuration...")
        is_valid = client.validate_pipeline(pipeline_config)
        print(f"Configuration is: {'✅ Valid' if is_valid else '❌ Invalid'}")
    except DTCApiError as e:
        print(f"⚠️  Validation error: {e}")
        print("Let's try a simpler configuration...")
        
        # Fallback to even simpler config
        simple_config = PipelineConfig(
            source="file_upload",
            transformations=["parse", "extract_text"],
            destination="text_output",
            settings={
                "parse": {"extract_text": True},
                "output_format": "text"
            }
        )
        
        try:
            is_valid = client.validate_pipeline(simple_config)
            print(f"Simple config is: {'✅ Valid' if is_valid else '❌ Invalid'}")
            pipeline_config = simple_config
        except DTCApiError as e2:
            print(f"❌ Simple config also failed: {e2}")
            return
    
    # Test 2: Create a pipeline
    try:
        print(f"\n🔧 Creating pipeline...")
        pipeline_token = client.create_pipeline(
            config=pipeline_config,
            name="parse_test_pipeline"
        )
        print(f"✅ Pipeline created! Token: {pipeline_token[:8]}...")
        
        # Test 3: Create and upload a test file
        print(f"\n📄 Creating test file...")
        test_file = create_test_file()
        print(f"✅ Created test file: {test_file}")
        print(f"   Content: '{test_file.read_text()[:50]}...'")
        
        # Upload the file
        print(f"\n⬆️  Uploading file to pipeline...")
        upload_success = client.upload_files(pipeline_token, [str(test_file)])
        
        if upload_success:
            print("✅ File uploaded successfully!")
            
            # Wait a moment for processing
            print("⏳ Waiting for processing...")
            time.sleep(5)
            
            print("✅ Processing should have started!")
            print("   In a real scenario, you would:")
            print("   - Monitor the pipeline for completion")
            print("   - Check the output destination for results")
            print("   - Look for text lane outputs")
        else:
            print("❌ File upload failed")
        
        # Clean up
        print(f"\n🧹 Cleaning up...")
        cleanup_success = client.delete_pipeline(pipeline_token)
        print(f"Pipeline deleted: {'✅' if cleanup_success else '❌'}")
        
        # Clean up test file
        test_file.unlink()
        test_file.parent.rmdir()
        print("✅ Test file cleaned up")
        
    except DTCApiError as e:
        print(f"❌ Pipeline operations failed: {e}")
        if e.status_code:
            print(f"   Status Code: {e.status_code}")
        if e.response_data:
            print(f"   Response: {e.response_data}")

def test_simple_parse_task():
    """Try a simple one-off task instead of a pipeline"""
    print(f"\n🚀 Testing Simple Parse Task (Alternative Approach)")
    print("=" * 50)
    
    client = DTCApiClient()
    
    # Very simple configuration for parsing
    config = PipelineConfig(
        source="s3://test/parse-sample",
        transformations=["parse", "extract_text"],
        destination="s3://test/parse-output",
        settings={
            "parse": {
                "extract_text": True,
                "extract_metadata": True
            },
            "output": {
                "format": "json",
                "include_lanes": ["text"]
            }
        }
    )
    
    try:
        print("🧪 Submitting parse task...")
        token = client.execute_task(
            config=config,
            name="simple_parse_test",
            threads=1
        )
        print(f"✅ Task submitted! Token: {token[:8]}...")
        
        # Check status
        task_info = client.get_task_status(token)
        print(f"📊 Status: {task_info.status.value}")
        print(f"   Name: {task_info.name}")
        
        # Cancel immediately to avoid resource usage
        print("🛑 Cancelling task (test purposes)...")
        cancelled = client.cancel_task(token)
        print(f"Task cancelled: {'✅' if cancelled else '❌'}")
        
    except DTCApiError as e:
        print(f"⚠️  Task submission failed: {e}")
        print("This might indicate the parse transformation needs specific configuration")

if __name__ == "__main__":
    print("🎯 DTC API Parse Pipeline Test")
    print("Testing webhook -> parse flow with file ingestion")
    print("Looking for text lane output\n")
    
    test_parse_pipeline()
    test_simple_parse_task()
    
    print(f"\n🎉 Parse pipeline test completed!")
    print("=" * 50) 