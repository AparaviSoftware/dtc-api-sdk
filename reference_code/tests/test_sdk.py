#!/usr/bin/env python3
"""
Quick test script for the DTC API SDK
"""

import os
from dtc_api_sdk import DTCApiClient, PipelineConfig
from dtc_api_sdk.exceptions import DTCApiError, AuthenticationError

def test_sdk():
    print("🧪 Testing DTC API SDK...")
    
    # Test 1: Import check
    print("✅ SDK imported successfully")
    
    # Test 2: Check if API key is available
    api_key = os.getenv("DTC_API_KEY")
    if not api_key:
        print("⚠️  No DTC_API_KEY environment variable found")
        print("   You can still test the SDK structure, but won't be able to make real API calls")
        
        # Test creating client without API key (should raise AuthenticationError)
        try:
            client = DTCApiClient()
            print("❌ Expected AuthenticationError but didn't get one")
        except AuthenticationError as e:
            print(f"✅ Correctly caught AuthenticationError: {e}")
        
        # Test with a fake API key for structure testing
        try:
            client = DTCApiClient(api_key="fake_key_for_testing")
            print("✅ Client created with fake API key (structure test)")
            
            # Test creating configuration
            config = PipelineConfig(
                source="s3://test-bucket/input",
                transformations=["extract_text", "analyze_content"],
                destination="s3://test-bucket/output",
                settings={"test": "value"}
            )
            print("✅ PipelineConfig created successfully")
            print(f"   Source: {config.source}")
            print(f"   Transformations: {config.transformations}")
            print(f"   Destination: {config.destination}")
            print(f"   Settings: {config.settings}")
            
            # Test config to dict conversion
            config_dict = config.to_dict()
            print("✅ Configuration converted to dict:")
            for key, value in config_dict.items():
                print(f"   {key}: {value}")
                
        except Exception as e:
            print(f"❌ Error creating client or config: {e}")
    
    else:
        print(f"✅ Found API key: {api_key[:8]}...")
        
        # Test with real API key
        try:
            client = DTCApiClient()
            print("✅ Client created with real API key")
            
            # Test connectivity
            print("🔗 Testing API connectivity...")
            try:
                version = client.get_version()
                print(f"✅ Connected! API Version: {version}")
                
                # Test status
                status = client.get_status()
                print(f"✅ Server Status: {status}")
                
                # Test services
                services = client.get_services()
                print(f"✅ Found {len(services)} services:")
                for service in services[:3]:  # Show first 3
                    print(f"   - {service.name}: {service.status}")
                
            except DTCApiError as e:
                print(f"⚠️  API Error (might be expected): {e}")
                if e.status_code:
                    print(f"   Status Code: {e.status_code}")
            
        except AuthenticationError as e:
            print(f"❌ Authentication failed: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
    
    print("\n🎉 SDK test completed!")

if __name__ == "__main__":
    test_sdk() 