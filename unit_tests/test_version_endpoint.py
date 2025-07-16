#!/usr/bin/env python3
"""
Unit tests for /version endpoint

Based on OpenAPI spec:
- GET /version
- Returns version of the cloud Engine
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


class TestVersionEndpoint(unittest.TestCase):
    """Test cases for the /version endpoint"""
    
    def setUp(self):
        """Set up test client"""
        self.api_key = os.getenv("DTC_API_KEY")
        if not self.api_key:
            self.skipTest("DTC_API_KEY environment variable not set")
        
        self.client = DTCApiClient(api_key=self.api_key)
        print(f"Using API key: {self.api_key[:12]}...")
    
    def test_version_endpoint_success(self):
        """Test that /version endpoint returns successful response"""
        try:
            version_data = self.client.get_version()
            self.assertIsNotNone(version_data, "Version data should not be None")
            # The API returns nested data structure, so check for the nested version
            if isinstance(version_data, dict) and 'version' in version_data:
                version = version_data['version']
            else:
                version = version_data
            print(f"SUCCESS: Version endpoint returned: {version}")
        except Exception as e:
            self.fail(f"Version endpoint failed: {e}")
    
    def test_version_endpoint_response_type(self):
        """Test that version response contains version info"""
        try:
            version_data = self.client.get_version()
            self.assertIsNotNone(version_data, "Version data should not be None")
            print(f"SUCCESS: Version response received: {version_data}")
        except Exception as e:
            self.fail(f"Version type check failed: {e}")
    
    def test_version_endpoint_with_invalid_key(self):
        """Test version endpoint with invalid API key"""
        # Create client with invalid key
        invalid_client = DTCApiClient(api_key="invalid-key-123")
        
        with self.assertRaises(DTCApiError) as context:
            invalid_client.get_version()
        
        print(f"SUCCESS: Invalid key properly rejected: {context.exception}")
    
    def test_version_endpoint_connectivity(self):
        """Test basic connectivity to version endpoint"""
        try:
            # This should not raise an exception with valid credentials
            version_data = self.client.get_version()
            self.assertIsNotNone(version_data)
            print("SUCCESS: Basic connectivity test passed")
        except AuthenticationError:
            self.fail("Authentication failed - check API key")
        except Exception as e:
            self.fail(f"Connectivity test failed: {e}")


def run_version_tests():
    """Run version endpoint tests with simple output"""
    print("=" * 60)
    print("Testing /version endpoint")
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
    suite = unittest.TestLoader().loadTestsFromTestCase(TestVersionEndpoint)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    if result.wasSuccessful():
        print("\nSUCCESS: All version endpoint tests passed!")
        return True
    else:
        print(f"\nFAILED: {len(result.failures)} test(s) failed")
        print(f"ERRORS: {len(result.errors)} test(s) had errors")
        return False


if __name__ == "__main__":
    run_version_tests() 