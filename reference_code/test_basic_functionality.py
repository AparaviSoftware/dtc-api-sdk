#!/usr/bin/env python3
"""
Basic functionality test for DTC API SDK
"""

import os
import sys
from pathlib import Path
from dtc_api_sdk import DTCApiClient
from dtc_api_sdk.exceptions import DTCApiError

def test_basic_functionality():
    """Test basic API functionality"""
    
    print("🧪 Testing Basic DTC API Functionality")
    print("=" * 50)
    
    # Check API key
    api_key = os.getenv("DTC_API_KEY")
    if not api_key:
        print("❌ DTC_API_KEY environment variable not set")
        return False
    
    try:
        # Initialize client
        client = DTCApiClient(api_key=api_key)
        print("✅ Client initialized successfully")
        
        # Test version
        version = client.get_version()
        print(f"✅ API Version: {version}")
        
        # Test status
        status = client.get_status()
        print(f"✅ Server Status: {status}")
        
        # Test services
        services = client.get_services()
        print(f"✅ Found {len(services)} services")
        
        # Test pipeline validation
        test_config = {
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
                    }
                ],
                "id": "test-pipeline"
            }
        }
        
        is_valid = client.validate_pipeline(test_config)
        print(f"✅ Pipeline validation: {'Valid' if is_valid else 'Invalid'}")
        
        print("\n🎉 Basic functionality test completed successfully!")
        return True
        
    except DTCApiError as e:
        print(f"❌ API Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_basic_functionality()
    sys.exit(0 if success else 1) 