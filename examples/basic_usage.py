#!/usr/bin/env python3
"""
Basic usage example for the DTC API SDK.

This example demonstrates the fundamental operations:
1. Initialize the client
2. Check connectivity
3. Create a simple pipeline
4. Execute a task
"""

import os
from dtc_api_sdk import DTCApiClient, PipelineConfig
from dtc_api_sdk.exceptions import DTCApiError, AuthenticationError


def main():
    """Main example function."""
    # Initialize the client
    # API key can be set via environment variable DTC_API_KEY
    # or passed directly to the constructor
    try:
        client = DTCApiClient(
            api_key=os.getenv("DTC_API_KEY"),  # Replace with your API key
            base_url="https://eaas-dev.aparavi.com"  # Use dev environment
        )
        print("✓ Client initialized successfully")
    except AuthenticationError as e:
        print(f"✗ Authentication failed: {e}")
        print("Please set your API key in the DTC_API_KEY environment variable")
        return
    
    # Test connectivity
    try:
        version = client.get_version()
        print(f"✓ Connected to DTC API version: {version}")
        
        status = client.get_status()
        print(f"✓ Server status: {status}")
    except DTCApiError as e:
        print(f"✗ Connection test failed: {e}")
        return
    
    # Create a simple pipeline configuration
    pipeline_config = PipelineConfig(
        source="s3://example-bucket/data",
        transformations=["filter", "aggregate", "transform"],
        destination="s3://example-bucket/output",
        settings={
            "filter_criteria": {"type": "document"},
            "output_format": "json"
        }
    )
    
    # Validate the pipeline configuration
    try:
        is_valid = client.validate_pipeline(pipeline_config)
        print(f"✓ Pipeline configuration is valid: {is_valid}")
    except DTCApiError as e:
        print(f"✗ Pipeline validation failed: {e}")
        return
    
    # Execute a one-off task (recommended for simple operations)
    try:
        print("\n--- Executing Task ---")
        task_token = client.execute_task(
            config=pipeline_config,
            name="basic_example_task",
            threads=2
        )
        print(f"✓ Task started with token: {task_token}")
        
        # Check task status
        task_info = client.get_task_status(task_token)
        print(f"✓ Task status: {task_info.status}")
        print(f"  - Name: {task_info.name}")
        print(f"  - Progress: {task_info.progress}")
        
        # Wait for task completion (optional)
        print("⏳ Waiting for task to complete...")
        try:
            final_task_info = client.wait_for_task(task_token, timeout=60)
            print(f"✓ Task completed successfully!")
            print(f"  - Final status: {final_task_info.status}")
            print(f"  - Result: {final_task_info.result}")
        except TimeoutError:
            print("⚠ Task is still running after timeout")
            # You can cancel the task if needed
            # client.cancel_task(task_token)
        
    except DTCApiError as e:
        print(f"✗ Task execution failed: {e}")
    
    # Alternative: Create a persistent pipeline for multiple file uploads
    try:
        print("\n--- Creating Persistent Pipeline ---")
        pipeline_token = client.create_pipeline(
            config=pipeline_config,
            name="persistent_example_pipeline"
        )
        print(f"✓ Pipeline created with token: {pipeline_token}")
        
        # Note: For file uploads, you would use:
        # client.upload_files(pipeline_token, ["file1.pdf", "file2.docx"])
        
        # Clean up - delete the pipeline
        success = client.delete_pipeline(pipeline_token)
        print(f"✓ Pipeline deleted: {success}")
        
    except DTCApiError as e:
        print(f"✗ Pipeline operations failed: {e}")
    
    # Get available services
    try:
        print("\n--- Available Services ---")
        services = client.get_services()
        for service in services:
            print(f"  - {service.name}: {service.status}")
            if service.version:
                print(f"    Version: {service.version}")
    except DTCApiError as e:
        print(f"✗ Failed to get services: {e}")


if __name__ == "__main__":
    main() 