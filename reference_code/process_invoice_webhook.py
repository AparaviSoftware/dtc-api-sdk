#!/usr/bin/env python3
"""
Invoice Processing Script using DTC API SDK
===========================================

This script demonstrates comprehensive usage of the DTC API SDK to process
the Invoice-E6CD52F5-0002.pdf through a webhook → parse → response pipeline.

Features:
- Pipeline creation and validation
- Webhook-based document processing
- Comprehensive error handling
- Full API endpoint usage
- Detailed logging and results extraction
"""

import os
import sys
import json
import base64
import time
import mimetypes
from pathlib import Path
from typing import Dict, Any, Optional

from dtc_api_sdk import DTCApiClient
from dtc_api_sdk.exceptions import (
    DTCApiError, 
    AuthenticationError, 
    NetworkError, 
    TimeoutError,
    TaskError,
    PipelineError
)


class InvoiceProcessor:
    """Invoice processing class using DTC API SDK"""
    
    def __init__(self, api_key: str = None):
        """Initialize the invoice processor"""
        self.api_key = api_key or os.getenv("DTC_API_KEY")
        if not self.api_key:
            raise AuthenticationError("API key required. Set DTC_API_KEY environment variable.")
        
        self.client = DTCApiClient(api_key=self.api_key)
        self.pipeline_token = None
        self.task_token = None
        
    def get_pipeline_config(self) -> Dict[str, Any]:
        """Get the webhook → parse → response pipeline configuration"""
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
                            },
                            {
                                "lane": "text",
                                "from": "webhook_1"
                            }
                        ]
                    }
                ],
                "id": "invoice-processor"
            }
        }
    
    def check_api_health(self) -> Dict[str, Any]:
        """Check API health and get version information"""
        print("🔍 Checking API Health...")
        try:
            version = self.client.get_version()
            status = self.client.get_status()
            
            print(f"   ✅ API Version: {version}")
            print(f"   ✅ Server Status: {status}")
            
            return {"version": version, "status": status}
        except DTCApiError as e:
            print(f"   ❌ Health check failed: {e}")
            raise
    
    def get_available_services(self) -> None:
        """Get and display available services"""
        print("\n🔌 Available Services:")
        try:
            services = self.client.get_services()
            for service in services:
                print(f"   - {service.name}: {service.status}")
                if service.version:
                    print(f"     Version: {service.version}")
                if service.description:
                    print(f"     Description: {service.description}")
        except DTCApiError as e:
            print(f"   ⚠️  Could not retrieve services: {e}")
    
    def validate_pipeline(self, config: Dict[str, Any]) -> bool:
        """Validate the pipeline configuration"""
        print("\n🔍 Validating Pipeline Configuration...")
        try:
            is_valid = self.client.validate_pipeline(config)
            if is_valid:
                print("   ✅ Pipeline configuration is valid")
            else:
                print("   ❌ Pipeline configuration is invalid")
            return is_valid
        except DTCApiError as e:
            print(f"   ❌ Pipeline validation failed: {e}")
            return False
    
    def create_pipeline(self, config: Dict[str, Any]) -> str:
        """Create a pipeline and return its token"""
        print("\n🔧 Creating Pipeline...")
        try:
            self.pipeline_token = self.client.create_pipeline(
                config=config,
                name="invoice_processing_pipeline"
            )
            print(f"   ✅ Pipeline created successfully!")
            print(f"   📝 Pipeline Token: {self.pipeline_token[:12]}...")
            return self.pipeline_token
        except DTCApiError as e:
            print(f"   ❌ Pipeline creation failed: {e}")
            raise
    
    def create_task(self, config: Dict[str, Any]) -> str:
        """Create a task and return its token"""
        print("\n🎯 Creating Task...")
        try:
            self.task_token = self.client.execute_task(
                config=config,
                name="invoice_processing_task",
                threads=2
            )
            print(f"   ✅ Task created successfully!")
            print(f"   📝 Task Token: {self.task_token[:12]}...")
            return self.task_token
        except DTCApiError as e:
            print(f"   ❌ Task creation failed: {e}")
            raise
    
    def get_interface_urls(self, token: str) -> Dict[str, str]:
        """Get interface URLs for the pipeline/task"""
        print("\n🌐 Getting Interface URLs...")
        urls = {}
        
        try:
            dropper_url = self.client.get_dropper_url(token, "parse")
            urls["dropper"] = dropper_url
            print(f"   ✅ Dropper URL: {dropper_url}")
        except DTCApiError as e:
            print(f"   ⚠️  Dropper URL error: {e}")
        
        try:
            chat_url = self.client.get_chat_url(token, "parse")
            urls["chat"] = chat_url
            print(f"   ✅ Chat URL: {chat_url}")
        except DTCApiError as e:
            print(f"   ⚠️  Chat URL error: {e}")
        
        return urls
    
    def prepare_file_data(self, file_path: str) -> Dict[str, Any]:
        """Prepare file data for webhook submission"""
        print(f"\n📄 Preparing File Data...")
        
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Get file info
        file_size = file_path.stat().st_size
        mime_type, _ = mimetypes.guess_type(str(file_path))
        mime_type = mime_type or "application/octet-stream"
        
        print(f"   📁 File: {file_path.name}")
        print(f"   📊 Size: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")
        print(f"   📋 MIME Type: {mime_type}")
        
        # Read and encode file
        with open(file_path, 'rb') as f:
            file_content = f.read()
        
        base64_content = base64.b64encode(file_content).decode('utf-8')
        
        webhook_data = {
            "filename": file_path.name,
            "content_type": mime_type,
            "size": file_size,
            "data": base64_content
        }
        
        print(f"   ✅ File prepared for webhook submission")
        return webhook_data
    
    def send_webhook_with_retry(self, token: str, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send webhook data with retry logic"""
        print(f"\n🪝 Sending Webhook Data...")
        
        max_attempts = 3
        base_timeout = 60
        
        for attempt in range(max_attempts):
            try:
                print(f"   🔄 Attempt {attempt + 1}/{max_attempts}")
                
                # Calculate timeout based on file size
                file_size_mb = webhook_data["size"] / 1024 / 1024
                timeout = base_timeout + (attempt * 30)  # Progressive timeout
                if file_size_mb > 10:
                    timeout += 60
                
                print(f"   ⏱️  Timeout: {timeout} seconds")
                
                # Update client timeout
                self.client.timeout = timeout
                
                response = self.client.send_webhook(token, webhook_data)
                
                print(f"   ✅ Webhook sent successfully!")
                return response
                
            except (NetworkError, TimeoutError) as e:
                print(f"   ⚠️  Attempt {attempt + 1} failed: {e}")
                if attempt < max_attempts - 1:
                    wait_time = (attempt + 1) * 5
                    print(f"   ⏳ Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                else:
                    raise
            except DTCApiError as e:
                print(f"   ❌ Webhook failed: {e}")
                raise
    
    def monitor_task_status(self, token: str, max_wait: int = 300) -> Dict[str, Any]:
        """Monitor task status until completion"""
        print(f"\n📊 Monitoring Task Status...")
        
        start_time = time.time()
        poll_interval = 10
        
        while time.time() - start_time < max_wait:
            try:
                task_info = self.client.get_task_status(token)
                
                print(f"   📈 Status: {task_info.status}")
                if task_info.progress:
                    print(f"   📊 Progress: {task_info.progress}%")
                
                if task_info.status.value == "completed":
                    print(f"   ✅ Task completed successfully!")
                    return task_info
                elif task_info.status.value == "failed":
                    print(f"   ❌ Task failed: {task_info.error_message}")
                    raise TaskError(f"Task failed: {task_info.error_message}")
                elif task_info.status.value == "cancelled":
                    print(f"   ⏹️  Task was cancelled")
                    raise TaskError("Task was cancelled")
                
                print(f"   ⏳ Waiting {poll_interval} seconds...")
                time.sleep(poll_interval)
                
            except DTCApiError as e:
                print(f"   ⚠️  Status check failed: {e}")
                time.sleep(poll_interval)
        
        raise TimeoutError(f"Task did not complete within {max_wait} seconds")
    
    def extract_results(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and format results from webhook response"""
        print(f"\n📊 Extracting Results...")
        
        results = {
            "extracted_text": "",
            "metadata": {},
            "processing_stats": {},
            "objects": {}
        }
        
        if isinstance(response, dict):
            # Check for objects with extracted content
            if "objects" in response:
                results["objects"] = response["objects"]
                
                # Extract text from objects
                for obj_id, obj_data in response["objects"].items():
                    if "text" in obj_data:
                        results["extracted_text"] += obj_data["text"] + "\n"
                    
                    if "metadata" in obj_data:
                        results["metadata"].update(obj_data["metadata"])
            
            # Check for direct text response
            if "text" in response:
                results["extracted_text"] = response["text"]
            
            # Check for metadata
            if "metadata" in response:
                results["metadata"].update(response["metadata"])
            
            # Check for processing statistics
            if "processing_stats" in response:
                results["processing_stats"] = response["processing_stats"]
            
            # Check for metrics
            if "metrics" in response:
                results["processing_stats"].update(response["metrics"])
        
        # Log results summary
        if results["extracted_text"]:
            text_length = len(results["extracted_text"])
            print(f"   📄 Extracted {text_length:,} characters of text")
        
        if results["metadata"]:
            print(f"   📋 Found {len(results['metadata'])} metadata fields")
        
        if results["objects"]:
            print(f"   📦 Found {len(results['objects'])} processed objects")
        
        return results
    
    def save_results(self, results: Dict[str, Any], output_file: str) -> None:
        """Save results to file"""
        print(f"\n💾 Saving Results to {output_file}...")
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            print(f"   ✅ Results saved successfully!")
            
        except Exception as e:
            print(f"   ⚠️  Could not save results: {e}")
    
    def cleanup(self) -> None:
        """Clean up resources"""
        print(f"\n🧹 Cleaning Up...")
        
        if self.pipeline_token:
            try:
                success = self.client.delete_pipeline(self.pipeline_token)
                if success:
                    print(f"   ✅ Pipeline deleted successfully")
                else:
                    print(f"   ⚠️  Pipeline deletion may have failed")
            except DTCApiError as e:
                print(f"   ⚠️  Pipeline cleanup error: {e}")
        
        if self.task_token:
            try:
                success = self.client.cancel_task(self.task_token)
                if success:
                    print(f"   ✅ Task cancelled successfully")
            except DTCApiError as e:
                print(f"   ⚠️  Task cleanup error: {e}")
    
    def process_invoice(self, file_path: str) -> Dict[str, Any]:
        """Main method to process the invoice"""
        print("🚀 DTC Invoice Processing Pipeline")
        print("=" * 60)
        
        try:
            # Step 1: Check API health
            health_info = self.check_api_health()
            
            # Step 2: Get available services
            self.get_available_services()
            
            # Step 3: Get pipeline configuration
            config = self.get_pipeline_config()
            
            # Step 4: Validate pipeline
            if not self.validate_pipeline(config):
                raise PipelineError("Pipeline configuration is invalid")
            
            # Step 5: Create task (recommended for webhook processing)
            task_token = self.create_task(config)
            
            # Step 6: Get interface URLs
            urls = self.get_interface_urls(task_token)
            
            # Step 7: Prepare file data
            webhook_data = self.prepare_file_data(file_path)
            
            # Step 8: Send webhook with retry
            response = self.send_webhook_with_retry(task_token, webhook_data)
            
            # Step 9: Extract results
            results = self.extract_results(response)
            
            # Step 10: Save results
            output_file = f"invoice_results_{Path(file_path).stem}.json"
            self.save_results(results, output_file)
            
            print(f"\n🎉 Processing Completed Successfully!")
            print("=" * 60)
            
            return results
            
        except Exception as e:
            print(f"\n❌ Processing Failed: {e}")
            raise
        finally:
            # Cleanup
            self.cleanup()


def main():
    """Main function"""
    # File path to the invoice
    invoice_file = "test_data/Invoice-E6CD52F5-0002.pdf"
    
    # Check if file exists
    if not Path(invoice_file).exists():
        print(f"❌ Invoice file not found: {invoice_file}")
        print("Please ensure the file is in the correct location.")
        sys.exit(1)
    
    # Check API key
    api_key = os.getenv('DTC_API_KEY')
    if not api_key:
        print("❌ Error: DTC_API_KEY environment variable not set")
        print("Please set your API key:")
        print("  export DTC_API_KEY='your-api-key-here'")
        sys.exit(1)
    
    try:
        # Initialize processor
        processor = InvoiceProcessor(api_key)
        
        # Process the invoice
        results = processor.process_invoice(invoice_file)
        
        # Display results summary
        print(f"\n📊 RESULTS SUMMARY:")
        print("=" * 30)
        
        if results["extracted_text"]:
            print(f"📄 Extracted Text Preview:")
            preview = results["extracted_text"][:500]
            print(f"{preview}{'...' if len(results['extracted_text']) > 500 else ''}")
        
        if results["metadata"]:
            print(f"\n📋 Metadata:")
            for key, value in results["metadata"].items():
                print(f"   {key}: {value}")
        
        if results["processing_stats"]:
            print(f"\n📈 Processing Statistics:")
            for key, value in results["processing_stats"].items():
                print(f"   {key}: {value}")
        
        print(f"\n✅ Invoice processing completed successfully!")
        
    except Exception as e:
        print(f"❌ Error processing invoice: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 