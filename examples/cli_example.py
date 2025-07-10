#!/usr/bin/env python3
"""
Command-line interface example for the DTC API SDK.

This example demonstrates how to create a CLI tool using the SDK.
Usage examples:
    python cli_example.py status
    python cli_example.py submit --config config.json --name "my_task"
    python cli_example.py monitor --token abc123
    python cli_example.py upload --token abc123 --files file1.pdf file2.docx
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

from dtc_api_sdk import DTCApiClient, PipelineConfig
from dtc_api_sdk.exceptions import DTCApiError


class DTCCli:
    """Command-line interface for the DTC API SDK."""
    
    def __init__(self):
        self.client = DTCApiClient()
    
    def check_status(self) -> None:
        """Check API status and version."""
        try:
            version = self.client.get_version()
            status = self.client.get_status()
            
            print(f"✓ API Version: {version}")
            print(f"✓ Status: {status}")
            
            # List available services
            services = self.client.get_services()
            print(f"\nAvailable Services ({len(services)}):")
            for service in services:
                print(f"  - {service.name}: {service.status}")
                if service.version:
                    print(f"    Version: {service.version}")
        
        except DTCApiError as e:
            print(f"✗ Error: {e}")
            sys.exit(1)
    
    def submit_task(self, config_file: str, name: Optional[str] = None, threads: int = 2) -> None:
        """Submit a task from configuration file."""
        try:
            # Load configuration
            config_path = Path(config_file)
            if not config_path.exists():
                print(f"✗ Configuration file not found: {config_file}")
                sys.exit(1)
            
            with open(config_path, 'r') as f:
                config_data = json.load(f)
            
            # Validate required fields
            required_fields = ['source']
            for field in required_fields:
                if field not in config_data:
                    print(f"✗ Missing required field in config: {field}")
                    sys.exit(1)
            
            # Create pipeline config
            pipeline_config = PipelineConfig(
                source=config_data['source'],
                transformations=config_data.get('transformations', []),
                destination=config_data.get('destination'),
                settings=config_data.get('settings', {})
            )
            
            # Validate configuration
            is_valid = self.client.validate_pipeline(pipeline_config)
            if not is_valid:
                print("✗ Pipeline configuration is invalid")
                sys.exit(1)
            
            print("✓ Configuration validated")
            
            # Submit task
            token = self.client.execute_task(
                config=pipeline_config,
                name=name,
                threads=threads
            )
            
            print(f"✓ Task submitted successfully!")
            print(f"  Token: {token}")
            print(f"  Name: {name or 'Unnamed'}")
            print(f"  Threads: {threads}")
            
            # Save token for later use
            self._save_token(token, name)
            
        except DTCApiError as e:
            print(f"✗ Error: {e}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"✗ Invalid JSON in config file: {e}")
            sys.exit(1)
    
    def monitor_task(self, token: str, wait: bool = False) -> None:
        """Monitor task status."""
        try:
            task_info = self.client.get_task_status(token)
            
            print(f"Task Status: {task_info.status.value}")
            print(f"Token: {token}")
            if task_info.name:
                print(f"Name: {task_info.name}")
            if task_info.progress is not None:
                print(f"Progress: {task_info.progress:.1%}")
            if task_info.created_at:
                print(f"Created: {task_info.created_at}")
            if task_info.completed_at:
                print(f"Completed: {task_info.completed_at}")
            if task_info.error_message:
                print(f"Error: {task_info.error_message}")
            
            if wait and task_info.status.value not in ["completed", "failed", "cancelled"]:
                print("\n⏳ Waiting for task completion...")
                try:
                    final_info = self.client.wait_for_task(token, timeout=300)
                    print(f"✓ Task completed with status: {final_info.status.value}")
                    if final_info.result:
                        print(f"Result: {final_info.result}")
                except TimeoutError:
                    print("⚠ Task is still running after timeout")
        
        except DTCApiError as e:
            print(f"✗ Error: {e}")
            sys.exit(1)
    
    def cancel_task(self, token: str) -> None:
        """Cancel a running task."""
        try:
            success = self.client.cancel_task(token)
            if success:
                print(f"✓ Task cancelled successfully: {token}")
            else:
                print(f"✗ Failed to cancel task: {token}")
        
        except DTCApiError as e:
            print(f"✗ Error: {e}")
            sys.exit(1)
    
    def create_pipeline(self, config_file: str, name: Optional[str] = None) -> None:
        """Create a persistent pipeline."""
        try:
            # Load and validate configuration
            config_path = Path(config_file)
            if not config_path.exists():
                print(f"✗ Configuration file not found: {config_file}")
                sys.exit(1)
            
            with open(config_path, 'r') as f:
                config_data = json.load(f)
            
            pipeline_config = PipelineConfig(
                source=config_data['source'],
                transformations=config_data.get('transformations', []),
                destination=config_data.get('destination'),
                settings=config_data.get('settings', {})
            )
            
            # Create pipeline
            token = self.client.create_pipeline(pipeline_config, name=name)
            
            print(f"✓ Pipeline created successfully!")
            print(f"  Token: {token}")
            print(f"  Name: {name or 'Unnamed'}")
            
            # Save token for later use
            self._save_token(token, name, pipeline=True)
            
        except DTCApiError as e:
            print(f"✗ Error: {e}")
            sys.exit(1)
    
    def upload_files(self, token: str, files: List[str]) -> None:
        """Upload files to a pipeline."""
        try:
            # Validate files exist
            file_paths = []
            for file_path in files:
                path = Path(file_path)
                if not path.exists():
                    print(f"✗ File not found: {file_path}")
                    sys.exit(1)
                file_paths.append(path)
            
            # Upload files
            success = self.client.upload_files(token, file_paths)
            
            if success:
                print(f"✓ Uploaded {len(files)} files successfully!")
                for file_path in file_paths:
                    print(f"  - {file_path.name} ({file_path.stat().st_size} bytes)")
            else:
                print("✗ File upload failed")
                sys.exit(1)
        
        except DTCApiError as e:
            print(f"✗ Error: {e}")
            sys.exit(1)
    
    def list_tokens(self) -> None:
        """List saved tokens."""
        token_file = Path.home() / ".dtc_tokens.json"
        if not token_file.exists():
            print("No saved tokens found")
            return
        
        try:
            with open(token_file, 'r') as f:
                tokens = json.load(f)
            
            print(f"Saved Tokens ({len(tokens)}):")
            for token_info in tokens:
                print(f"  - {token_info['token'][:8]}... "
                      f"({token_info.get('name', 'Unnamed')}) "
                      f"[{'Pipeline' if token_info.get('pipeline') else 'Task'}]")
        
        except (json.JSONDecodeError, KeyError):
            print("✗ Error reading saved tokens")
    
    def _save_token(self, token: str, name: Optional[str] = None, pipeline: bool = False) -> None:
        """Save token to file for later use."""
        token_file = Path.home() / ".dtc_tokens.json"
        
        # Load existing tokens
        tokens = []
        if token_file.exists():
            try:
                with open(token_file, 'r') as f:
                    tokens = json.load(f)
            except json.JSONDecodeError:
                tokens = []
        
        # Add new token
        tokens.append({
            "token": token,
            "name": name,
            "pipeline": pipeline,
            "created_at": str(Path.cwd())
        })
        
        # Keep only last 10 tokens
        tokens = tokens[-10:]
        
        # Save tokens
        with open(token_file, 'w') as f:
            json.dump(tokens, f, indent=2)


def create_sample_config(filename: str = "sample_config.json") -> None:
    """Create a sample configuration file."""
    sample_config = {
        "source": "s3://my-bucket/input",
        "transformations": [
            "extract_text",
            "analyze_content",
            "classify_documents"
        ],
        "destination": "s3://my-bucket/output",
        "settings": {
            "text_extraction": {
                "ocr_enabled": True,
                "language": "auto"
            },
            "content_analysis": {
                "extract_entities": True,
                "sentiment_analysis": True
            },
            "classification": {
                "categories": ["invoice", "contract", "report"],
                "confidence_threshold": 0.8
            },
            "output_format": "json"
        }
    }
    
    with open(filename, 'w') as f:
        json.dump(sample_config, f, indent=2)
    
    print(f"✓ Sample configuration created: {filename}")


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="DTC API SDK Command Line Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s status                           # Check API status
  %(prog)s submit --config config.json     # Submit a task
  %(prog)s monitor --token abc123          # Monitor task
  %(prog)s monitor --token abc123 --wait   # Monitor and wait
  %(prog)s cancel --token abc123           # Cancel task
  %(prog)s pipeline --config config.json  # Create pipeline
  %(prog)s upload --token abc123 file.pdf  # Upload files
  %(prog)s tokens                          # List saved tokens
  %(prog)s sample-config                   # Create sample config
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Status command
    subparsers.add_parser('status', help='Check API status and version')
    
    # Submit command
    submit_parser = subparsers.add_parser('submit', help='Submit a task')
    submit_parser.add_argument('--config', '-c', required=True, help='Configuration file path')
    submit_parser.add_argument('--name', '-n', help='Task name')
    submit_parser.add_argument('--threads', '-t', type=int, default=2, help='Number of threads (1-16)')
    
    # Monitor command
    monitor_parser = subparsers.add_parser('monitor', help='Monitor task status')
    monitor_parser.add_argument('--token', '-k', required=True, help='Task token')
    monitor_parser.add_argument('--wait', '-w', action='store_true', help='Wait for completion')
    
    # Cancel command
    cancel_parser = subparsers.add_parser('cancel', help='Cancel a task')
    cancel_parser.add_argument('--token', '-k', required=True, help='Task token')
    
    # Pipeline command
    pipeline_parser = subparsers.add_parser('pipeline', help='Create a pipeline')
    pipeline_parser.add_argument('--config', '-c', required=True, help='Configuration file path')
    pipeline_parser.add_argument('--name', '-n', help='Pipeline name')
    
    # Upload command
    upload_parser = subparsers.add_parser('upload', help='Upload files to pipeline')
    upload_parser.add_argument('--token', '-k', required=True, help='Pipeline token')
    upload_parser.add_argument('--files', '-f', nargs='+', required=True, help='Files to upload')
    
    # List tokens command
    subparsers.add_parser('tokens', help='List saved tokens')
    
    # Sample config command
    sample_parser = subparsers.add_parser('sample-config', help='Create sample configuration file')
    sample_parser.add_argument('--filename', '-f', default='sample_config.json', help='Output filename')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Handle sample-config command separately (doesn't need API client)
    if args.command == 'sample-config':
        create_sample_config(args.filename)
        return
    
    # Initialize CLI and execute command
    cli = DTCCli()
    
    try:
        if args.command == 'status':
            cli.check_status()
        elif args.command == 'submit':
            cli.submit_task(args.config, args.name, args.threads)
        elif args.command == 'monitor':
            cli.monitor_task(args.token, args.wait)
        elif args.command == 'cancel':
            cli.cancel_task(args.token)
        elif args.command == 'pipeline':
            cli.create_pipeline(args.config, args.name)
        elif args.command == 'upload':
            cli.upload_files(args.token, args.files)
        elif args.command == 'tokens':
            cli.list_tokens()
    
    except KeyboardInterrupt:
        print("\n✗ Operation cancelled by user")
        sys.exit(1)


if __name__ == "__main__":
    main() 