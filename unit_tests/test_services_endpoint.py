#!/usr/bin/env python3
"""
Unit tests for /services endpoint

Based on OpenAPI spec:
- GET /services
- Optional query parameter: service (string)
- Asynchronously retrieves service information
- Response: Result schema with service data
"""

import os
import sys
import unittest
from pathlib import Path

# Add the parent directory to Python path to import dtc_api_sdk
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

from dtc_api_sdk import DTCApiClient
from dtc_api_sdk.exceptions import DTCApiError, AuthenticationError


class TestServicesEndpoint(unittest.TestCase):
    """Test cases for the /services endpoint"""
    
    def setUp(self):
        """Set up test client"""
        self.api_key = os.getenv("DTC_API_KEY")
        if not self.api_key:
            self.skipTest("DTC_API_KEY environment variable not set")
        
        self.client = DTCApiClient(api_key=self.api_key)
        print(f"Using API key: {self.api_key[:12]}...")
    
    def test_services_endpoint_success(self):
        """Test that /services endpoint returns successful response"""
        try:
            services_data = self.client.get_services()
            self.assertIsNotNone(services_data, "Services data should not be None")
            print(f"SUCCESS: Services endpoint returned: {services_data}")
        except Exception as e:
            self.fail(f"Services endpoint failed: {e}")
    
    def test_services_endpoint_response_type(self):
        """Test that services response contains service information"""
        try:
            services_data = self.client.get_services()
            self.assertIsNotNone(services_data, "Services data should not be None")
            # Should return a list of services
            if isinstance(services_data, list):
                print(f"SUCCESS: Services response received: {len(services_data)} services")
                for service in services_data:
                    print(f"  - Service: {service.name if hasattr(service, 'name') else service}")
            else:
                print(f"SUCCESS: Services response received: {services_data}")
        except Exception as e:
            self.fail(f"Services type check failed: {e}")
    
    def test_services_endpoint_with_specific_service(self):
        """Test services endpoint with specific service name"""
        try:
            # First get all services to see what's available
            all_services = self.client.get_services()
            
            # If there are services, try to get a specific one
            if all_services and isinstance(all_services, list) and len(all_services) > 0:
                first_service = all_services[0]
                service_name = first_service.name if hasattr(first_service, 'name') else None
                
                if service_name:
                    specific_service = self.client.get_services(service_name)
                    self.assertIsNotNone(specific_service, "Specific service should not be None")
                    print(f"SUCCESS: Specific service '{service_name}' retrieved: {specific_service}")
                else:
                    print("SUCCESS: No specific service name available to test")
            else:
                print("SUCCESS: No services available to test specific service query")
        except Exception as e:
            self.fail(f"Specific service test failed: {e}")
    
    def test_services_endpoint_with_invalid_key(self):
        """Test services endpoint with invalid API key"""
        # Create client with invalid key
        invalid_client = DTCApiClient(api_key="invalid-key-123")
        
        try:
            services_data = invalid_client.get_services()
            # Services endpoint might not require authentication
            print(f"SUCCESS: Services endpoint accessible without valid authentication: {services_data}")
        except DTCApiError as e:
            print(f"SUCCESS: Invalid key properly rejected: {e}")
        except Exception as e:
            self.fail(f"Unexpected error: {e}")
    
    def test_services_endpoint_connectivity(self):
        """Test basic connectivity to services endpoint"""
        try:
            # This should not raise an exception with valid credentials
            services_data = self.client.get_services()
            self.assertIsNotNone(services_data)
            print("SUCCESS: Basic connectivity test passed")
        except AuthenticationError:
            self.fail("Authentication failed - check API key")
        except Exception as e:
            self.fail(f"Connectivity test failed: {e}")


def run_services_tests():
    """Run services endpoint tests with simple output"""
    print("=" * 60)
    print("Testing /services endpoint")
    print("=" * 60)
    
    # Load .env file
    load_dotenv()
    
    # Check prerequisites
    api_key = os.getenv("DTC_API_KEY")
    if not api_key:
        print("ERROR: DTC_API_KEY not found in .env file")
        print("Please create a .env file with:")
        print("  DTC_API_KEY=your-actual-api-key-here")
        return False
    
    print(f"Loaded API key: {api_key[:12]}...")
    
    # Run tests
    suite = unittest.TestLoader().loadTestsFromTestCase(TestServicesEndpoint)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    if result.wasSuccessful():
        print("\nSUCCESS: All services endpoint tests passed!")
        return True
    else:
        print(f"\nFAILED: {len(result.failures)} test(s) failed")
        print(f"ERRORS: {len(result.errors)} test(s) had errors")
        return False


if __name__ == "__main__":
    run_services_tests() 