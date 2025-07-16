#!/usr/bin/env python3
"""
Advanced test of DTC API SDK features
"""

from dtc_api_sdk import DTCApiClient, PipelineConfig
from dtc_api_sdk.exceptions import DTCApiError

def advanced_test():
    print("🚀 Advanced DTC API SDK Test")
    print("=" * 50)
    
    # Initialize client
    client = DTCApiClient()
    print("✅ Client initialized")
    
    # Test 1: Create and validate different pipeline configurations
    print("\n📋 Testing Pipeline Configurations...")
    
    configs = [
        {
            "name": "Document Processing Pipeline",
            "config": PipelineConfig(
                source="s3://documents/input",
                transformations=["extract_text", "analyze_content", "classify_documents"],
                destination="s3://documents/processed",
                settings={
                    "text_extraction": {"ocr_enabled": True, "language": "auto"},
                    "classification": {"categories": ["invoice", "contract", "report"]},
                    "output_format": "json"
                }
            )
        },
        {
            "name": "Image Processing Pipeline", 
            "config": PipelineConfig(
                source="s3://images/raw",
                transformations=["ocr", "image_analysis", "metadata_extraction"],
                destination="s3://images/processed",
                settings={
                    "ocr": {"languages": ["eng", "fra"], "dpi": 300},
                    "image_analysis": {"detect_objects": True}
                }
            )
        },
        {
            "name": "Data Analysis Pipeline",
            "config": PipelineConfig(
                source="s3://data/csv", 
                transformations=["data_validation", "statistical_analysis"],
                destination="s3://data/results",
                settings={
                    "validation": {"check_nulls": True},
                    "analysis": {"correlation_matrix": True}
                }
            )
        }
    ]
    
    # Validate each configuration
    for item in configs:
        try:
            is_valid = client.validate_pipeline(item["config"])
            status = "✅ Valid" if is_valid else "❌ Invalid"
            print(f"{status} - {item['name']}")
            print(f"   Source: {item['config'].source}")
            print(f"   Transformations: {', '.join(item['config'].transformations)}")
        except DTCApiError as e:
            print(f"⚠️  Validation error for {item['name']}: {e}")
    
    # Test 2: Try to create a simple task (be careful not to use too many resources)
    print(f"\n🔧 Testing Task Creation...")
    
    simple_config = PipelineConfig(
        source="s3://test/small-sample",
        transformations=["extract_text"],
        destination="s3://test/output",
        settings={"batch_size": 1}  # Keep it small for testing
    )
    
    try:
        print("🧪 Testing task submission...")
        token = client.execute_task(
            config=simple_config,
            name="sdk_test_task",
            threads=1
        )
        print(f"✅ Task submitted! Token: {token[:8]}...")
        
        # Check initial status
        task_info = client.get_task_status(token)
        print(f"📊 Initial Status: {task_info.status.value}")
        print(f"   Name: {task_info.name}")
        print(f"   Progress: {task_info.progress}")
        
        # Cancel the task immediately (don't want to use resources)
        print("🛑 Cancelling test task...")
        cancelled = client.cancel_task(token)
        if cancelled:
            print("✅ Task cancelled successfully")
        
    except DTCApiError as e:
        print(f"⚠️  Task creation test failed (this might be expected): {e}")
        if e.status_code:
            print(f"   Status Code: {e.status_code}")
    
    # Test 3: Show available services in detail
    print(f"\n🔌 Services Information...")
    try:
        services = client.get_services()
        if services:
            for service in services:
                print(f"Service: {service.name or 'Unknown'}")
                print(f"  Status: {service.status}")
                if service.version:
                    print(f"  Version: {service.version}")
                if service.description:
                    print(f"  Description: {service.description}")
        else:
            print("No services returned")
    except DTCApiError as e:
        print(f"⚠️  Error getting services: {e}")
    
    # Test 4: Configuration conversion
    print(f"\n🔄 Configuration Conversion Test...")
    test_config = PipelineConfig(
        source="s3://demo/input",
        transformations=["transform1", "transform2"],
        destination="s3://demo/output", 
        settings={"key": "value", "nested": {"inner": "data"}}
    )
    
    config_dict = test_config.to_dict()
    print("✅ Configuration as dictionary:")
    import json
    print(json.dumps(config_dict, indent=2))
    
    print(f"\n🎉 Advanced test completed!")
    print("=" * 50)

if __name__ == "__main__":
    advanced_test() 