#!/usr/bin/env python3
"""
Production Webhook Processing Example
=====================================

This example demonstrates the recommended webhook approach for document processing
using the DTC API SDK. The webhook method provides direct API access to processed
results without requiring web interfaces.

Features:
- Robust error handling with automatic retry
- Progressive timeout management
- Support for multiple file formats
- Structured data extraction
- Comprehensive logging

Usage:
    python webhook_processing.py path/to/document.pdf
"""

import os
import sys
import json
import base64
import time
import mimetypes
from pathlib import Path
from typing import Dict, Any, Optional, List

from dtc_api_sdk import DTCApiClient
from dtc_api_sdk.exceptions import DTCApiError, AuthenticationError, NetworkError


def create_webhook_pipeline() -> Dict[str, Any]:
    """
    Create a webhook processing pipeline configuration.
    
    Pipeline flow: webhook → parse → response
    - webhook_1: Receives file data via webhook
    - parse_1: Extracts text and metadata from files
    - response_1: Returns structured results
    
    Returns:
        Pipeline configuration dictionary
    """
    return {
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
            "id": "production-webhook-processor"
        }
    }


def get_mime_type(file_path: str) -> str:
    """Get MIME type for file."""
    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type:
        # Default mappings for common document types
        ext = Path(file_path).suffix.lower()
        mime_mapping = {
            '.pdf': 'application/pdf',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.txt': 'text/plain',
            '.rtf': 'application/rtf',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg'
        }
        mime_type = mime_mapping.get(ext, 'application/octet-stream')
    
    return mime_type


def calculate_timeout(file_size: int) -> int:
    """Calculate appropriate timeout based on file size."""
    if file_size < 1_000_000:  # < 1MB
        return 60
    elif file_size < 10_000_000:  # < 10MB  
        return 90
    else:  # >= 10MB
        return 120


def robust_webhook_processing(
    client: DTCApiClient,
    file_path: str,
    max_retries: int = 3
) -> Dict[str, Any]:
    """
    Process document using webhook with comprehensive error handling.
    
    Args:
        client: DTCApiClient instance
        file_path: Path to document to process
        max_retries: Maximum number of retry attempts
    
    Returns:
        Dictionary containing extracted data and metadata
        
    Raises:
        Exception: If all retry attempts fail
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    file_size = file_path.stat().st_size
    print(f"📄 Processing: {file_path.name} ({file_size:,} bytes)")
    
    for attempt in range(max_retries):
        try:
            # Calculate timeout based on file size and attempt
            base_timeout = calculate_timeout(file_size)
            timeout = base_timeout + (attempt * 30)  # Progressive timeout increase
            
            print(f"🔄 Attempt {attempt + 1}/{max_retries} (timeout: {timeout}s)")
            
            # Set client timeout
            original_timeout = client.timeout
            client.timeout = timeout
            
            # Create pipeline
            pipeline = create_webhook_pipeline()
            task_token = client.execute_task(
                pipeline, 
                name=f"process_{file_path.stem}_{int(time.time())}"
            )
            print(f"✅ Task created: {task_token}")
            
            # Prepare file data
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            webhook_data = {
                "filename": file_path.name,
                "content_type": get_mime_type(str(file_path)),
                "size": len(file_content),
                "data": base64.b64encode(file_content).decode('utf-8')
            }
            
            print(f"📤 Sending webhook data...")
            response = client.send_webhook(task_token, webhook_data)
            
            # Restore original timeout
            client.timeout = original_timeout
            
            print(f"✅ Processing completed successfully!")
            return parse_webhook_response(response)
            
        except (NetworkError, ConnectionError, TimeoutError) as e:
            print(f"❌ Attempt {attempt + 1} failed: {e}")
            
            if attempt < max_retries - 1:
                wait_time = 5 + (attempt * 3)  # Progressive backoff: 5s, 8s, 11s
                print(f"⏳ Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
            
        except AuthenticationError:
            print(f"🔐 Authentication failed - check your API key")
            raise
            
        except Exception as e:
            print(f"💥 Unexpected error: {e}")
            if attempt < max_retries - 1:
                wait_time = 5 + (attempt * 3)
                print(f"⏳ Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
            else:
                raise
        
        finally:
            # Always restore original timeout
            if 'original_timeout' in locals():
                client.timeout = original_timeout
    
    raise Exception(f"All {max_retries} processing attempts failed")


def parse_webhook_response(response: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse webhook response and extract structured data.
    
    Args:
        response: Raw webhook response
        
    Returns:
        Structured data dictionary with extracted content
    """
    results = {
        "extracted_text": "",
        "metadata": {},
        "processing_stats": {
            "objects_requested": response.get("objectsRequested", 0),
            "objects_completed": response.get("objectsCompleted", 0),
            "types": response.get("types", {})
        },
        "raw_response": response
    }
    
    print(f"📊 Processing completed:")
    print(f"   Objects requested: {results['processing_stats']['objects_requested']}")
    print(f"   Objects completed: {results['processing_stats']['objects_completed']}")
    
    if 'objects' in response and response['objects']:
        print(f"🔍 Analyzing {len(response['objects'])} processed objects...")
        
        for obj_id, obj_data in response['objects'].items():
            print(f"   📦 Object: {obj_id}")
            
            # Extract metadata
            if 'metadata' in obj_data:
                results['metadata'] = obj_data['metadata']
                print(f"   📋 Metadata: {obj_data['metadata']}")
            
            # Extract text content
            if 'text' in obj_data and obj_data['text']:
                text_content = obj_data['text']
                
                if isinstance(text_content, list) and text_content:
                    # Handle list format
                    content = text_content[0]
                    
                    # Check if content is JSON string (webhook data)
                    try:
                        parsed_content = json.loads(content)
                        if 'data' in parsed_content:
                            # This is the original file data - decode it
                            file_data = base64.b64decode(parsed_content['data'])
                            # Try to extract readable text from the decoded content
                            try:
                                decoded_text = file_data.decode('utf-8', errors='ignore')
                                # Extract readable portions
                                readable_lines = []
                                for line in decoded_text.split('\n'):
                                    if len(line.strip()) > 5 and any(c.isalnum() for c in line):
                                        if not line.startswith(('%', '<<', '>>')):
                                            readable_lines.append(line.strip())
                                
                                if readable_lines:
                                    results['extracted_text'] = '\n'.join(readable_lines[:50])  # First 50 lines
                                    print(f"   📄 Extracted {len(readable_lines)} text lines")
                                
                            except Exception:
                                # If decoding fails, use the JSON content as text
                                results['extracted_text'] = str(parsed_content)
                        else:
                            results['extracted_text'] = content
                    
                    except json.JSONDecodeError:
                        # Not JSON, use as-is
                        results['extracted_text'] = content
                
                elif isinstance(text_content, str):
                    results['extracted_text'] = text_content
                
                print(f"   📄 Text content: {len(results['extracted_text'])} characters")
    
    return results


def save_results(results: Dict[str, Any], output_file: str) -> None:
    """Save processing results to JSON file."""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"💾 Results saved to: {output_file}")


def process_multiple_files(file_paths: List[str]) -> Dict[str, Any]:
    """Process multiple documents in batch."""
    client = DTCApiClient()
    results = {}
    
    print(f"📦 Batch processing {len(file_paths)} files...")
    
    for i, file_path in enumerate(file_paths, 1):
        print(f"\n[{i}/{len(file_paths)}] Processing: {file_path}")
        
        try:
            result = robust_webhook_processing(client, file_path)
            results[file_path] = result
            print(f"✅ Completed: {file_path}")
            
        except Exception as e:
            print(f"❌ Failed: {file_path} - {e}")
            results[file_path] = {"error": str(e)}
    
    return results


def main():
    """Main entry point for the webhook processing example."""
    if len(sys.argv) < 2:
        print("Usage: python webhook_processing.py <file_path> [file_path2] ...")
        print("\nExample:")
        print("  python webhook_processing.py document.pdf")
        print("  python webhook_processing.py doc1.pdf doc2.docx doc3.txt")
        sys.exit(1)
    
    # Check API key
    api_key = os.getenv('DTC_API_KEY')
    if not api_key:
        print("❌ Error: DTC_API_KEY environment variable not set")
        print("Please set your API key:")
        print("  export DTC_API_KEY='your-api-key-here'")
        sys.exit(1)
    
    file_paths = sys.argv[1:]
    
    try:
        if len(file_paths) == 1:
            # Single file processing
            client = DTCApiClient()
            print(f"🚀 DTC Webhook Document Processor")
            print(f"API Base URL: {client.base_url}")
            print("=" * 50)
            
            results = robust_webhook_processing(client, file_paths[0])
            
            # Display results
            print(f"\n📊 PROCESSING RESULTS:")
            print("=" * 30)
            
            if results['extracted_text']:
                print(f"📄 Extracted Text Preview:")
                preview = results['extracted_text'][:500]
                print(f"{preview}{'...' if len(results['extracted_text']) > 500 else ''}")
            
            if results['metadata']:
                print(f"\n📋 File Metadata:")
                for key, value in results['metadata'].items():
                    print(f"   {key}: {value}")
            
            print(f"\n📈 Processing Statistics:")
            stats = results['processing_stats']
            for key, value in stats.items():
                print(f"   {key}: {value}")
            
            # Save results
            output_file = f"results_{Path(file_paths[0]).stem}.json"
            save_results(results, output_file)
            
        else:
            # Batch processing
            print(f"🚀 DTC Batch Document Processor")
            print("=" * 50)
            
            batch_results = process_multiple_files(file_paths)
            
            # Save batch results
            save_results(batch_results, "batch_results.json")
            
            # Summary
            successful = sum(1 for r in batch_results.values() if 'error' not in r)
            failed = len(batch_results) - successful
            
            print(f"\n📊 BATCH PROCESSING SUMMARY:")
            print("=" * 30)
            print(f"✅ Successful: {successful}")
            print(f"❌ Failed: {failed}")
            print(f"📁 Total: {len(batch_results)}")
    
    except KeyboardInterrupt:
        print(f"\n⚠️ Processing interrupted by user")
        sys.exit(1)
    
    except Exception as e:
        print(f"\n💥 Processing failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 