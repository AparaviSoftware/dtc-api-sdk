#!/usr/bin/env python3
"""
Async and batch processing example for the DTC API SDK.

This example demonstrates:
1. Running multiple tasks concurrently
2. Batch processing workflows
3. Progress monitoring for multiple tasks
4. Error handling in concurrent scenarios
"""

import asyncio
import concurrent.futures
import time
from typing import List, Dict, Any
from dtc_api_sdk import DTCApiClient, PipelineConfig, TaskInfo
from dtc_api_sdk.exceptions import DTCApiError


class BatchProcessor:
    """Helper class for batch processing with the DTC API."""
    
    def __init__(self, client: DTCApiClient):
        self.client = client
        self.active_tasks: Dict[str, str] = {}  # token -> task_name
    
    def submit_task(self, config: PipelineConfig, name: str, threads: int = 2) -> str:
        """Submit a task and track it."""
        try:
            token = self.client.execute_task(config, name=name, threads=threads)
            self.active_tasks[token] = name
            return token
        except DTCApiError as e:
            print(f"✗ Failed to submit task {name}: {e}")
            raise
    
    def get_all_task_status(self) -> Dict[str, TaskInfo]:
        """Get status of all active tasks."""
        status_map = {}
        for token, name in self.active_tasks.items():
            try:
                task_info = self.client.get_task_status(token)
                status_map[token] = task_info
            except DTCApiError as e:
                print(f"✗ Failed to get status for task {name}: {e}")
        return status_map
    
    def wait_for_completion(self, timeout: int = 300) -> Dict[str, TaskInfo]:
        """Wait for all tasks to complete."""
        start_time = time.time()
        completed_tasks = {}
        
        while self.active_tasks and (time.time() - start_time) < timeout:
            print(f"⏳ Monitoring {len(self.active_tasks)} active tasks...")
            
            # Get current status of all tasks
            status_map = self.get_all_task_status()
            
            # Check for completed tasks
            completed_tokens = []
            for token, task_info in status_map.items():
                task_name = self.active_tasks[token]
                print(f"  {task_name}: {task_info.status.value}")
                
                if task_info.status.value in ["completed", "failed", "cancelled"]:
                    completed_tasks[token] = task_info
                    completed_tokens.append(token)
            
            # Remove completed tasks from active list
            for token in completed_tokens:
                del self.active_tasks[token]
            
            if self.active_tasks:
                time.sleep(10)  # Wait before next check
        
        # Handle remaining tasks (timeout or incomplete)
        if self.active_tasks:
            print(f"⚠ {len(self.active_tasks)} tasks still running after timeout")
            for token, name in self.active_tasks.items():
                try:
                    task_info = self.client.get_task_status(token)
                    completed_tasks[token] = task_info
                except DTCApiError:
                    pass
        
        return completed_tasks


def create_sample_configs() -> List[PipelineConfig]:
    """Create sample pipeline configurations for testing."""
    configs = []
    
    # Document processing pipeline
    configs.append(PipelineConfig(
        source="s3://documents/legal",
        transformations=["extract_text", "legal_analysis", "compliance_check"],
        destination="s3://processed/legal",
        settings={
            "legal_analysis": {"extract_clauses": True, "risk_assessment": True},
            "compliance": {"regulations": ["GDPR", "CCPA", "SOX"]}
        }
    ))
    
    # Image processing pipeline
    configs.append(PipelineConfig(
        source="s3://images/raw",
        transformations=["ocr", "image_enhancement", "metadata_extraction"],
        destination="s3://processed/images",
        settings={
            "ocr": {"languages": ["eng", "fra"], "confidence_threshold": 0.85},
            "enhancement": {"denoise": True, "sharpen": True}
        }
    ))
    
    # Data analysis pipeline
    configs.append(PipelineConfig(
        source="s3://data/csv",
        transformations=["data_validation", "statistical_analysis", "visualization"],
        destination="s3://processed/analytics",
        settings={
            "validation": {"check_nulls": True, "outlier_detection": True},
            "analysis": {"correlation_matrix": True, "regression": True}
        }
    ))
    
    # Email processing pipeline
    configs.append(PipelineConfig(
        source="s3://email/archives",
        transformations=["parse_email", "thread_analysis", "pii_detection"],
        destination="s3://processed/email",
        settings={
            "parsing": {"extract_attachments": True, "decode_headers": True},
            "pii": {"mask_sensitive_data": True, "compliance_report": True}
        }
    ))
    
    return configs


def simulate_concurrent_processing():
    """Simulate concurrent processing of multiple tasks."""
    client = DTCApiClient()
    
    try:
        # Test connectivity
        version = client.get_version()
        print(f"✓ Connected to DTC API version: {version}")
        
        # Create sample configurations
        configs = create_sample_configs()
        task_names = ["Legal Analysis", "Image Processing", "Data Analytics", "Email Processing"]
        
        print(f"\n--- Starting Batch Processing ({len(configs)} tasks) ---")
        
        # Initialize batch processor
        batch_processor = BatchProcessor(client)
        
        # Submit all tasks
        submitted_tokens = []
        for config, name in zip(configs, task_names):
            try:
                token = batch_processor.submit_task(config, name, threads=2)
                submitted_tokens.append(token)
                print(f"✓ Submitted task: {name} (token: {token[:8]}...)")
            except DTCApiError as e:
                print(f"✗ Failed to submit {name}: {e}")
        
        print(f"✓ {len(submitted_tokens)} tasks submitted successfully")
        
        # Monitor progress
        print("\n--- Monitoring Progress ---")
        completed_tasks = batch_processor.wait_for_completion(timeout=180)
        
        # Report results
        print(f"\n--- Results Summary ---")
        success_count = 0
        failed_count = 0
        
        for token, task_info in completed_tasks.items():
            task_name = task_names[list(completed_tasks.keys()).index(token)]
            
            if task_info.status.value == "completed":
                success_count += 1
                print(f"✓ {task_name}: Completed successfully")
                if task_info.result:
                    print(f"  Result: {task_info.result}")
            else:
                failed_count += 1
                print(f"✗ {task_name}: {task_info.status.value}")
                if task_info.error_message:
                    print(f"  Error: {task_info.error_message}")
        
        print(f"\nSummary: {success_count} successful, {failed_count} failed")
        
    except DTCApiError as e:
        print(f"✗ Batch processing failed: {e}")


def demonstrate_pipeline_scaling():
    """Demonstrate scaling pipelines with different thread counts."""
    client = DTCApiClient()
    
    try:
        print("\n--- Pipeline Scaling Demo ---")
        
        # Base configuration
        base_config = PipelineConfig(
            source="s3://large-dataset/documents",
            transformations=["extract_text", "analyze_content", "classify"],
            destination="s3://processed/output",
            settings={
                "batch_size": 100,
                "memory_limit": "4GB"
            }
        )
        
        # Test different thread counts
        thread_configs = [
            (1, "Single Thread"),
            (2, "Dual Thread"),
            (4, "Quad Thread"),
            (8, "Octo Thread"),
            (16, "Max Thread")
        ]
        
        scaling_results = []
        
        for threads, desc in thread_configs:
            print(f"\n--- Testing {desc} ({threads} threads) ---")
            
            try:
                # Submit task
                token = client.execute_task(
                    config=base_config,
                    name=f"scaling_test_{threads}",
                    threads=threads
                )
                
                # Monitor briefly
                start_time = time.time()
                initial_status = client.get_task_status(token)
                
                # In a real scenario, you would wait for completion
                # For demo, we'll just capture the initial response
                
                scaling_results.append({
                    "threads": threads,
                    "description": desc,
                    "token": token,
                    "initial_status": initial_status.status.value,
                    "submission_time": time.time() - start_time
                })
                
                print(f"✓ {desc} task submitted (token: {token[:8]}...)")
                
                # Cancel task to avoid resource usage
                client.cancel_task(token)
                
            except DTCApiError as e:
                print(f"✗ {desc} failed: {e}")
                scaling_results.append({
                    "threads": threads,
                    "description": desc,
                    "error": str(e)
                })
        
        # Print scaling results
        print("\n--- Scaling Results ---")
        for result in scaling_results:
            if "error" in result:
                print(f"✗ {result['description']}: {result['error']}")
            else:
                print(f"✓ {result['description']}: "
                      f"Status={result['initial_status']}, "
                      f"Time={result['submission_time']:.2f}s")
        
    except DTCApiError as e:
        print(f"✗ Scaling demo failed: {e}")


def demonstrate_webhook_integration():
    """Demonstrate webhook integration for real-time processing."""
    client = DTCApiClient()
    
    try:
        print("\n--- Webhook Integration Demo ---")
        
        # Configuration for webhook-enabled task
        webhook_config = PipelineConfig(
            source="webhook_input",
            transformations=["real_time_processing", "event_handling"],
            destination="webhook_output",
            settings={
                "webhook": {
                    "callback_url": "https://your-app.com/webhook",
                    "events": ["processing_complete", "error_occurred"],
                    "retry_attempts": 3
                },
                "real_time": {
                    "buffer_size": 10,
                    "flush_interval": 30
                }
            }
        )
        
        # Start webhook-enabled task
        token = client.execute_task(
            config=webhook_config,
            name="webhook_demo_task",
            threads=2
        )
        
        print(f"✓ Webhook task started (token: {token[:8]}...)")
        
        # Simulate sending webhook data
        webhook_data = {
            "event": "data_received",
            "timestamp": time.time(),
            "data": {
                "source": "external_system",
                "records": [
                    {"id": 1, "content": "Sample data 1"},
                    {"id": 2, "content": "Sample data 2"}
                ]
            }
        }
        
        # Send webhook data
        webhook_response = client.send_webhook(token, webhook_data)
        print(f"✓ Webhook data sent: {webhook_response}")
        
        # Get chat and dropper URLs for UI integration
        chat_url = client.get_chat_url(token, "document_processing")
        dropper_url = client.get_dropper_url(token, "document_processing")
        
        print(f"✓ Chat URL: {chat_url}")
        print(f"✓ Dropper URL: {dropper_url}")
        
        # Cancel the webhook task
        client.cancel_task(token)
        print("✓ Webhook task cancelled")
        
    except DTCApiError as e:
        print(f"✗ Webhook demo failed: {e}")


def main():
    """Main function to run all examples."""
    print("=== DTC API SDK - Async and Batch Processing Examples ===")
    
    # Run the examples
    simulate_concurrent_processing()
    demonstrate_pipeline_scaling()
    demonstrate_webhook_integration()
    
    print("\n=== All Examples Completed ===")


if __name__ == "__main__":
    main() 