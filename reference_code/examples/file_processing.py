#!/usr/bin/env python3
"""
File processing example for the DTC API SDK.

This example demonstrates:
1. Creating a pipeline for file processing
2. Uploading multiple files
3. Monitoring processing progress
4. Handling different file types
"""

import os
import tempfile
from pathlib import Path
from dtc_api_sdk import DTCApiClient, PipelineConfig
from dtc_api_sdk.exceptions import DTCApiError


def create_sample_files() -> list[Path]:
    """Create sample files for testing."""
    temp_dir = Path(tempfile.mkdtemp())
    files = []
    
    # Create sample text file
    text_file = temp_dir / "sample.txt"
    text_file.write_text("This is a sample text file for processing.")
    files.append(text_file)
    
    # Create sample CSV file
    csv_file = temp_dir / "data.csv"
    csv_file.write_text("name,age,city\nJohn,30,New York\nJane,25,London\nBob,35,Paris")
    files.append(csv_file)
    
    # Create sample JSON file
    json_file = temp_dir / "config.json"
    json_file.write_text('{"version": "1.0", "settings": {"debug": true}}')
    files.append(json_file)
    
    return files


def main():
    """Main file processing example."""
    # Initialize client
    client = DTCApiClient()
    
    try:
        # Test connectivity
        version = client.get_version()
        print(f"✓ Connected to DTC API version: {version}")
        
        # Create sample files
        print("\n--- Creating Sample Files ---")
        sample_files = create_sample_files()
        print(f"✓ Created {len(sample_files)} sample files:")
        for file_path in sample_files:
            print(f"  - {file_path.name} ({file_path.stat().st_size} bytes)")
        
        # Configure pipeline for document processing
        pipeline_config = PipelineConfig(
            source="file_upload",  # Special source for file uploads
            transformations=[
                "extract_text",
                "analyze_content", 
                "classify_documents",
                "extract_metadata"
            ],
            destination="s3://processed-documents/output",
            settings={
                "text_extraction": {
                    "ocr_enabled": True,
                    "language": "auto"
                },
                "content_analysis": {
                    "extract_entities": True,
                    "sentiment_analysis": True,
                    "key_phrases": True
                },
                "classification": {
                    "categories": ["invoice", "contract", "report", "other"],
                    "confidence_threshold": 0.8
                },
                "output_format": "json"
            }
        )
        
        # Validate pipeline configuration
        is_valid = client.validate_pipeline(pipeline_config)
        print(f"✓ Pipeline configuration validated: {is_valid}")
        
        # Method 1: Using persistent pipeline for multiple file uploads
        print("\n--- Method 1: Persistent Pipeline ---")
        pipeline_token = client.create_pipeline(
            config=pipeline_config,
            name="file_processing_pipeline"
        )
        print(f"✓ Pipeline created with token: {pipeline_token[:8]}...")
        
        # Upload files to the pipeline
        print("⏳ Uploading files...")
        upload_success = client.upload_files(
            token=pipeline_token,
            files=[str(f) for f in sample_files]
        )
        print(f"✓ Files uploaded successfully: {upload_success}")
        
        # Monitor processing (in a real scenario, you might want to implement polling)
        print("⏳ Files are being processed...")
        print("   (In a real implementation, you would poll for completion)")
        
        # Clean up pipeline
        client.delete_pipeline(pipeline_token)
        print("✓ Pipeline cleaned up")
        
        # Method 2: Using one-off task (alternative approach)
        print("\n--- Method 2: One-off Task ---")
        
        # For tasks, you might need to specify file locations differently
        task_config = PipelineConfig(
            source="s3://input-bucket/documents",  # Pre-uploaded files
            transformations=["extract_text", "analyze_content"],
            destination="s3://output-bucket/results",
            settings={
                "batch_size": 10,
                "parallel_processing": True
            }
        )
        
        task_token = client.execute_task(
            config=task_config,
            name="document_processing_task",
            threads=4
        )
        print(f"✓ Task started with token: {task_token[:8]}...")
        
        # Monitor task progress
        print("⏳ Monitoring task progress...")
        for i in range(5):  # Check 5 times
            task_info = client.get_task_status(task_token)
            print(f"  Status: {task_info.status}, Progress: {task_info.progress}")
            
            if task_info.status.value in ["completed", "failed", "cancelled"]:
                break
                
            # In a real scenario, you might want to wait between checks
            # time.sleep(10)
        
        # Example of different file type configurations
        print("\n--- Different File Type Configurations ---")
        
        # Configuration for image processing
        image_config = PipelineConfig(
            source="file_upload",
            transformations=["ocr", "image_analysis", "text_extraction"],
            settings={
                "ocr": {
                    "language": ["eng", "fra", "deu"],
                    "dpi": 300
                },
                "image_analysis": {
                    "detect_objects": True,
                    "extract_text": True,
                    "analyze_layout": True
                }
            }
        )
        
        # Configuration for spreadsheet processing
        spreadsheet_config = PipelineConfig(
            source="file_upload",
            transformations=["parse_spreadsheet", "data_validation", "analysis"],
            settings={
                "spreadsheet": {
                    "sheet_selection": "all",
                    "header_row": 1,
                    "data_types": "auto_detect"
                },
                "validation": {
                    "check_duplicates": True,
                    "validate_formats": True
                }
            }
        )
        
        # Configuration for email processing
        email_config = PipelineConfig(
            source="file_upload",
            transformations=["parse_email", "extract_attachments", "content_analysis"],
            settings={
                "email": {
                    "extract_headers": True,
                    "process_attachments": True,
                    "thread_detection": True
                },
                "content_analysis": {
                    "detect_pii": True,
                    "classify_content": True
                }
            }
        )
        
        configs = [
            ("Image Processing", image_config),
            ("Spreadsheet Processing", spreadsheet_config),
            ("Email Processing", email_config)
        ]
        
        for name, config in configs:
            try:
                is_valid = client.validate_pipeline(config)
                print(f"✓ {name} configuration: {'Valid' if is_valid else 'Invalid'}")
            except DTCApiError as e:
                print(f"✗ {name} configuration failed: {e}")
        
        # Cancel the task if it's still running
        try:
            client.cancel_task(task_token)
            print("✓ Task cancelled")
        except DTCApiError:
            pass  # Task might have already completed
        
    except DTCApiError as e:
        print(f"✗ Error: {e}")
    
    finally:
        # Clean up sample files
        for file_path in sample_files:
            try:
                file_path.unlink()
                file_path.parent.rmdir()
            except:
                pass


if __name__ == "__main__":
    main() 