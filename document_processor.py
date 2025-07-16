#!/usr/bin/env python3
"""
Document Processor - Automated Pipeline Processing
==================================================

This processor automatically handles:
- Task creation with simpleparser.json pipeline
- Webhook setup and file processing
- Text extraction and result parsing
- All using just the API key - no manual UI setup required

Usage:
    from document_processor import DocumentProcessor
    
    processor = DocumentProcessor()
    results = processor.process_document("path/to/document.docx")
    print(results["extracted_text"])
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional
import requests


class DocumentProcessor:
    """Automated document processor using the DTC API."""
    
    def __init__(self, api_key: str = None, base_url: str = "https://eaas-dev.aparavi.com"):
        """Initialize the document processor."""
        self.api_key = api_key or os.getenv("DTC_API_KEY")
        if not self.api_key:
            raise ValueError("API key required. Set DTC_API_KEY environment variable or pass api_key parameter.")
        
        self.base_url = base_url
        self.pipeline_config = self._load_pipeline_config()
    
    def _load_pipeline_config(self) -> Dict[str, Any]:
        """Load the simpleparser.json pipeline configuration."""
        pipeline_file = Path("example_pipelines/simpleparser.json")
        
        if pipeline_file.exists():
            # Load from file
            with open(pipeline_file, 'r') as f:
                config = json.load(f)
            
            return {
                "pipeline": {
                    "source": "webhook_1",
                    "components": config["components"],
                    "id": config.get("id", "document-processor")
                }
            }
        else:
            # Use default configuration
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
    
    def _create_task(self, name: str = None) -> str:
        """Create a processing task and return the token."""
        task_name = name or f"doc_processor_{int(time.time())}"
        
        response = requests.put(
            f"{self.base_url}/task",
            params={"name": task_name},
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            json=self.pipeline_config,
            timeout=30
        )
        
        if response.status_code != 200:
            raise Exception(f"Task creation failed: {response.text}")
        
        return response.json()["data"]["token"]
    
    def _get_content_type(self, file_path: str) -> str:
        """Get the appropriate content type for the file."""
        file_path = Path(file_path)
        extension = file_path.suffix.lower()
        
        content_types = {
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.doc': 'application/msword',
            '.pdf': 'application/pdf',
            '.txt': 'text/plain',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.xls': 'application/vnd.ms-excel'
        }
        
        return content_types.get(extension, 'application/octet-stream')
    
    def _send_webhook(self, task_token: str, file_path: str) -> Dict[str, Any]:
        """Send file to webhook endpoint using the working curl format."""
        file_path = Path(file_path)
        
        # Read file as binary data
        with open(file_path, 'rb') as f:
            file_data = f.read()
        
        # Webhook parameters (exact format from working curl command)
        webhook_params = {
            "type": "cpu",
            "apikey": self.api_key,
            "token": task_token
        }
        
        # Headers (exact format from working curl command)
        webhook_headers = {
            "Authorization": self.api_key,  # No "Bearer" prefix
            "Content-Type": self._get_content_type(str(file_path))
        }
        
        # Send webhook request
        response = requests.put(
            f"{self.base_url}/webhook",
            params=webhook_params,
            headers=webhook_headers,
            data=file_data,  # Upload file as request body (like curl -T)
            timeout=120
        )
        
        if response.status_code != 200:
            raise Exception(f"Webhook failed: {response.text}")
        
        return response.json()
    
    def _parse_results(self, webhook_response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse webhook response and extract meaningful data."""
        results = {
            "status": webhook_response.get("status", "Unknown"),
            "processing_time": webhook_response.get("metrics", {}).get("total_time", 0) / 1000,
            "objects_processed": 0,
            "extracted_text": "",
            "metadata": {},
            "full_response": webhook_response
        }
        
        if "data" in webhook_response:
            data = webhook_response["data"]
            results["objects_processed"] = data.get("objectsCompleted", 0)
            
            # Extract text from all objects
            objects = data.get("objects", {})
            text_parts = []
            
            for obj_id, obj_data in objects.items():
                if "text" in obj_data:
                    if isinstance(obj_data["text"], list):
                        text_parts.extend(obj_data["text"])
                    else:
                        text_parts.append(obj_data["text"])
                
                # Extract metadata from first object
                if "metadata" in obj_data and not results["metadata"]:
                    results["metadata"] = obj_data["metadata"]
            
            results["extracted_text"] = "\n".join(text_parts) if text_parts else ""
        
        return results
    
    def process_document(self, file_path: str, task_name: str = None) -> Dict[str, Any]:
        """
        Process a document through the simpleparser.json pipeline.
        
        Args:
            file_path: Path to the document file
            task_name: Optional name for the processing task
            
        Returns:
            Dictionary containing:
            - status: Processing status
            - processing_time: Time taken in seconds
            - objects_processed: Number of objects processed
            - extracted_text: Extracted text content
            - metadata: File metadata
            - full_response: Complete API response
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        print(f"🚀 Processing document: {file_path.name}")
        print(f"📏 Size: {file_path.stat().st_size:,} bytes")
        
        # Step 1: Create task
        print("1️⃣ Creating processing task...")
        task_token = self._create_task(task_name)
        print(f"✅ Task created: {task_token}")
        
        # Step 2: Wait for task to be ready
        print("2️⃣ Waiting for task initialization...")
        time.sleep(5)
        
        # Step 3: Send file via webhook
        print("3️⃣ Sending file for processing...")
        start_time = time.time()
        webhook_response = self._send_webhook(task_token, file_path)
        processing_time = time.time() - start_time
        
        print(f"✅ Processing completed in {processing_time:.1f} seconds")
        
        # Step 4: Parse results
        print("4️⃣ Parsing results...")
        results = self._parse_results(webhook_response)
        
        print(f"📊 Results:")
        print(f"   Status: {results['status']}")
        print(f"   Objects Processed: {results['objects_processed']}")
        print(f"   Text Length: {len(results['extracted_text'])} characters")
        print(f"   Processing Time: {results['processing_time']:.1f} seconds")
        
        if results['extracted_text']:
            preview = results['extracted_text'][:200] + "..." if len(results['extracted_text']) > 200 else results['extracted_text']
            print(f"   Text Preview: {preview}")
        
        return results


def main():
    """Example usage of the document processor."""
    processor = DocumentProcessor()
    
    # Process a Word document
    try:
        results = processor.process_document("test_data/10-MB-Test.docx")
        
        # Save results
        with open("processing_results.json", 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n💾 Results saved to: processing_results.json")
        print(f"🎉 Document processing completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main() 