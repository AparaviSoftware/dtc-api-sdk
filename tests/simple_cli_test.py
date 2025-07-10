#!/usr/bin/env python3
"""
Simple CLI test for DTC API SDK
"""

import sys
from dtc_api_sdk import DTCApiClient, PipelineConfig
from dtc_api_sdk.exceptions import DTCApiError

def cli_test():
    print("🖥️  CLI Test for DTC API SDK")
    print("=" * 40)
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
    else:
        command = "status"
    
    client = DTCApiClient()
    
    if command == "status":
        print("📊 Checking API Status...")
        try:
            version = client.get_version()
            status = client.get_status()
            print(f"✅ API Version: {version}")
            print(f"✅ Server Status: Connected")
            print(f"✅ Active Tasks: {status.get('task', {}).get('active', 'Unknown')}")
        except DTCApiError as e:
            print(f"❌ Status check failed: {e}")
    
    elif command == "validate":
        print("✅ Validating Sample Configuration...")
        config = PipelineConfig(
            source="s3://test/input",
            transformations=["extract_text", "analyze"],
            destination="s3://test/output"
        )
        try:
            is_valid = client.validate_pipeline(config)
            print(f"Configuration is: {'✅ Valid' if is_valid else '❌ Invalid'}")
        except DTCApiError as e:
            print(f"❌ Validation failed: {e}")
    
    elif command == "services":
        print("🔌 Listing Services...")
        try:
            services = client.get_services()
            print(f"Found {len(services)} services:")
            for service in services:
                print(f"  - {service.name or 'Unknown'}: {service.status}")
        except DTCApiError as e:
            print(f"❌ Services check failed: {e}")
    
    elif command == "help":
        print("Available commands:")
        print("  status    - Check API status")
        print("  validate  - Validate a sample configuration") 
        print("  services  - List available services")
        print("  help      - Show this help")
    
    else:
        print(f"❌ Unknown command: {command}")
        print("Use 'help' to see available commands")

if __name__ == "__main__":
    cli_test() 