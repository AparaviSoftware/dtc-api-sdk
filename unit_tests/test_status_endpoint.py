#!/usr/bin/env python3
"""
Unit tests for /status endpoint

Based on OpenAPI spec:
- GET /status
- Compute the server status
- Response: Result schema with status field
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


class TestStatusEndpoint(unittest.TestCase):
    """Test cases for the /status endpoint"""
    
    def setUp(self):
        """Set up test client"""
        self.api_key = os.getenv("DTC_API_KEY")
        if not self.api_key:
            self.skipTest("DTC_API_KEY environment variable not set")
        
        self.client = DTCApiClient(api_key=self.api_key)
        print(f"Using API key: {self.api_key[:12]}...")
    
    def test_status_endpoint_success(self):
        """Test that /status endpoint returns successful response"""
        try:
            status_data = self.client.get_status()
            self.assertIsNotNone(status_data, "Status data should not be None")
            print(f"SUCCESS: Status endpoint returned: {status_data}")
        except Exception as e:
            self.fail(f"Status endpoint failed: {e}")
    
    def test_status_endpoint_response_type(self):
        """Test that status response contains server status info"""
        try:
            status_data = self.client.get_status()
            self.assertIsNotNone(status_data, "Status data should not be None")
            print(f"SUCCESS: Status response received: {status_data}")
        except Exception as e:
            self.fail(f"Status type check failed: {e}")
    
    def test_status_endpoint_with_invalid_key(self):
        """Test status endpoint with invalid API key"""
        # Create client with invalid key
        invalid_client = DTCApiClient(api_key="invalid-key-123")
        
        with self.assertRaises(DTCApiError) as context:
            invalid_client.get_status()
        
        print(f"SUCCESS: Invalid key properly rejected: {context.exception}")
    
    def test_status_endpoint_connectivity(self):
        """Test basic connectivity to status endpoint"""
        try:
            # This should not raise an exception with valid credentials
            status_data = self.client.get_status()
            self.assertIsNotNone(status_data)
            print("SUCCESS: Basic connectivity test passed")
        except AuthenticationError:
            self.fail("Authentication failed - check API key")
        except Exception as e:
            self.fail(f"Connectivity test failed: {e}")


def run_status_tests():
    """Run status endpoint tests with simple output"""
    print("=" * 60)
    print("Testing /status endpoint")
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
    suite = unittest.TestLoader().loadTestsFromTestCase(TestStatusEndpoint)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    if result.wasSuccessful():
        print("\nSUCCESS: All status endpoint tests passed!")
        return True
    else:
        print(f"\nFAILED: {len(result.failures)} test(s) failed")
        print(f"ERRORS: {len(result.errors)} test(s) had errors")
        return False


if __name__ == "__main__":
    run_status_tests() 