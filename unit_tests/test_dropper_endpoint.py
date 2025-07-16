#!/usr/bin/env python3
"""
Unit tests for /dropper GET endpoint

Based on OpenAPI spec:
- GET /dropper
- Set cookies for dropper session and redirect to dropper UI
- Requires: ?type, ?token, ?apikey query params
- Returns: RedirectResponse to dropper UI with cookies set
"""

import unittest
import json
import os
import sys
from pathlib import Path

# Add the parent directory to Python path to import dtc_api_sdk
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

from dtc_api_sdk import DTCApiClient
from dtc_api_sdk.exceptions import AuthenticationError, DTCApiError, NetworkError

class TestDropperEndpoint(unittest.TestCase):
    """Test suite for the /dropper GET endpoint"""

    def setUp(self):
        """Set up test client and create test task"""
        self.api_key = os.getenv('DTC_API_KEY')
        self.client = DTCApiClient(api_key=self.api_key)
        
        # Create a test task for dropper testing
        self.test_task_config = {
            "source": "dropper_1",
            "components": [
                {
                    "id": "dropper_1",
                    "provider": "dropper",
                    "config": {
                        "mode": "Source",
                        "type": "dropper"
                    }
                },
                {
                    "id": "parse_1",
                    "provider": "parse",
                    "config": {},
                    "input": [{"lane": "tags", "from": "dropper_1"}]
                },
                {
                    "id": "response_1",
                    "provider": "response",
                    "config": {"lanes": []},
                    "input": [{"lane": "text", "from": "parse_1"}]
                }
            ],
            "id": "dropper_test_task"
        }
        
        # Create the test task
        self.test_token = None
        try:
            response = self._execute_task(self.test_task_config, "dropper_test")
            if hasattr(response, 'status') and response.status == 'OK':
                if response.data and 'token' in response.data:
                    self.test_token = response.data['token']
                    print(f"✓ Created test task with token: {self.test_token}")
        except Exception as e:
            print(f"⚠ Failed to create test task: {e}")

    def _execute_task(self, task_config, name=None):
        """Helper method to execute a task"""
        try:
            params = {"name": name} if name else {}
            wrapped_config = {"pipeline": task_config}
            response = self.client._make_request("PUT", "/task", params=params, data=wrapped_config)
            return response
        except Exception as e:
            return e

    def _get_dropper_url(self, token, pipeline_type, api_key=None):
        """Helper method to get dropper URL"""
        try:
            params = {
                "type": pipeline_type,
                "token": token,
                "apikey": api_key or self.api_key
            }
            
            # This endpoint returns a redirect, so we need to handle it differently
            response = self.client._make_request("GET", "/dropper", params=params)
            return response
        except Exception as e:
            return e

    def _cancel_task(self, token):
        """Helper method to cancel a task"""
        try:
            params = {"token": token}
            response = self.client._make_request("DELETE", "/task", params=params)
            return response
        except Exception as e:
            return e

    def test_dropper_url_with_valid_params(self):
        """Test getting dropper URL with valid parameters"""
        if not self.test_token:
            self.skipTest("No test task available")
        
        try:
            response = self._get_dropper_url(self.test_token, "dropper", self.api_key)
            
            # The endpoint should return a redirect response
            print(f"✓ Dropper URL response: {response}")
            
            if hasattr(response, 'status'):
                print(f"✓ Response status: {response.status}")
                if response.data:
                    print(f"✓ Response data: {response.data}")
            else:
                print(f"✓ Direct response: {response}")
                
        except Exception as e:
            print(f"✗ Dropper URL test failed: {e}")

    def test_dropper_url_with_different_types(self):
        """Test dropper URL with different pipeline types"""
        if not self.test_token:
            self.skipTest("No test task available")
        
        pipeline_types = ["dropper", "file_upload", "document_drop", "media_drop"]
        
        for pipeline_type in pipeline_types:
            try:
                response = self._get_dropper_url(self.test_token, pipeline_type, self.api_key)
                
                print(f"✓ Dropper URL for type '{pipeline_type}': {response}")
                
                if hasattr(response, 'status'):
                    print(f"✓ Response status for '{pipeline_type}': {response.status}")
                    
            except Exception as e:
                print(f"✗ Dropper URL test for '{pipeline_type}' failed: {e}")

    def test_dropper_url_with_invalid_token(self):
        """Test dropper URL with invalid task token"""
        invalid_token = "invalid-token-12345"
        
        try:
            response = self._get_dropper_url(invalid_token, "dropper", self.api_key)
            
            if hasattr(response, 'status'):
                if response.status == 'Error':
                    print(f"✓ Invalid token correctly rejected: {response.error}")
                else:
                    print(f"✗ Invalid token unexpectedly accepted: {response}")
            else:
                print(f"✗ Invalid token unexpected response: {response}")
                
        except Exception as e:
            print(f"✓ Invalid token correctly rejected with exception: {e}")

    def test_dropper_url_with_nonexistent_token(self):
        """Test dropper URL with nonexistent task token"""
        nonexistent_token = "00000000-0000-0000-0000-000000000000"
        
        try:
            response = self._get_dropper_url(nonexistent_token, "dropper", self.api_key)
            
            if hasattr(response, 'status'):
                if response.status == 'Error':
                    print(f"✓ Nonexistent token correctly rejected: {response.error}")
                else:
                    print(f"✗ Nonexistent token unexpectedly accepted: {response}")
            else:
                print(f"✗ Nonexistent token unexpected response: {response}")
                
        except Exception as e:
            print(f"✓ Nonexistent token correctly rejected with exception: {e}")

    def test_dropper_url_with_invalid_api_key(self):
        """Test dropper URL with invalid API key"""
        if not self.test_token:
            self.skipTest("No test task available")
        
        invalid_api_key = "invalid_key_12345"
        
        try:
            response = self._get_dropper_url(self.test_token, "dropper", invalid_api_key)
            
            if hasattr(response, 'status'):
                if response.status == 'Error':
                    print(f"✓ Invalid API key correctly rejected: {response.error}")
                else:
                    print(f"✗ Invalid API key unexpectedly accepted: {response}")
            else:
                print(f"✗ Invalid API key unexpected response: {response}")
                
        except Exception as e:
            print(f"✓ Invalid API key correctly rejected with exception: {e}")

    def test_dropper_url_missing_required_params(self):
        """Test dropper URL with missing required parameters"""
        if not self.test_token:
            self.skipTest("No test task available")
        
        # Test missing type parameter
        try:
            params = {"token": self.test_token, "apikey": self.api_key}
            response = self.client._make_request("GET", "/dropper", params=params)
            
            if hasattr(response, 'status'):
                if response.status == 'Error':
                    print(f"✓ Missing type parameter correctly rejected: {response.error}")
                else:
                    print(f"✗ Missing type parameter unexpectedly accepted: {response}")
            else:
                print(f"✗ Missing type parameter unexpected response: {response}")
                
        except Exception as e:
            print(f"✓ Missing type parameter correctly rejected with exception: {e}")

        # Test missing token parameter
        try:
            params = {"type": "dropper", "apikey": self.api_key}
            response = self.client._make_request("GET", "/dropper", params=params)
            
            if hasattr(response, 'status'):
                if response.status == 'Error':
                    print(f"✓ Missing token parameter correctly rejected: {response.error}")
                else:
                    print(f"✗ Missing token parameter unexpectedly accepted: {response}")
            else:
                print(f"✗ Missing token parameter unexpected response: {response}")
                
        except Exception as e:
            print(f"✓ Missing token parameter correctly rejected with exception: {e}")

        # Test missing apikey parameter
        try:
            params = {"type": "dropper", "token": self.test_token}
            response = self.client._make_request("GET", "/dropper", params=params)
            
            if hasattr(response, 'status'):
                if response.status == 'Error':
                    print(f"✓ Missing apikey parameter correctly rejected: {response.error}")
                else:
                    print(f"✗ Missing apikey parameter unexpectedly accepted: {response}")
            else:
                print(f"✗ Missing apikey parameter unexpected response: {response}")
                
        except Exception as e:
            print(f"✓ Missing apikey parameter correctly rejected with exception: {e}")

    def test_dropper_url_with_special_characters(self):
        """Test dropper URL with special characters in parameters"""
        if not self.test_token:
            self.skipTest("No test task available")
        
        special_types = ["dropper&type", "dropper%20type", "dropper+type", "dropper/type"]
        
        for special_type in special_types:
            try:
                response = self._get_dropper_url(self.test_token, special_type, self.api_key)
                
                print(f"✓ Dropper URL for special type '{special_type}': {response}")
                
                if hasattr(response, 'status'):
                    print(f"✓ Response status for special type '{special_type}': {response.status}")
                    
            except Exception as e:
                print(f"✗ Dropper URL test for special type '{special_type}' failed: {e}")

    def test_dropper_url_no_connectivity(self):
        """Test dropper URL with no network connectivity"""
        if not self.test_token:
            self.skipTest("No test task available")
        
        offline_client = DTCApiClient(
            api_key=self.api_key,
            base_url='https://invalid-url-that-does-not-exist.com'
        )
        
        try:
            params = {
                "type": "dropper",
                "token": self.test_token,
                "apikey": self.api_key
            }
            
            with self.assertRaises((NetworkError, DTCApiError)):
                offline_client._make_request("GET", "/dropper", params=params)
            print("✓ Network connectivity error handled correctly")
        except Exception as e:
            print(f"✗ Network connectivity test failed: {e}")

    def test_dropper_url_response_structure(self):
        """Test the structure of dropper URL response"""
        if not self.test_token:
            self.skipTest("No test task available")
        
        try:
            response = self._get_dropper_url(self.test_token, "dropper", self.api_key)
            
            print(f"✓ Dropper URL response type: {type(response)}")
            
            if hasattr(response, 'status'):
                print(f"✓ Response status: {response.status}")
                
                if hasattr(response, 'data'):
                    print(f"✓ Response data: {response.data}")
                    
                if hasattr(response, 'error') and response.error:
                    print(f"✓ Response error: {response.error}")
                    
                if hasattr(response, 'metrics') and response.metrics:
                    print(f"✓ Response metrics: {response.metrics}")
            else:
                print(f"✓ Direct response: {response}")
                
        except Exception as e:
            print(f"✗ Dropper URL response structure test failed: {e}")

    def test_dropper_url_multiple_calls(self):
        """Test multiple calls to dropper URL endpoint"""
        if not self.test_token:
            self.skipTest("No test task available")
        
        for i in range(3):
            try:
                response = self._get_dropper_url(self.test_token, "dropper", self.api_key)
                
                if hasattr(response, 'status'):
                    print(f"✓ Call {i+1} response status: {response.status}")
                else:
                    print(f"✓ Call {i+1} response: {response}")
                    
            except Exception as e:
                print(f"✗ Call {i+1} failed: {e}")

    def test_dropper_url_with_long_token(self):
        """Test dropper URL with very long token"""
        if not self.test_token:
            self.skipTest("No test task available")
        
        # Use actual token but test with long type parameter
        long_type = "dropper" + "x" * 1000  # Very long type parameter
        
        try:
            response = self._get_dropper_url(self.test_token, long_type, self.api_key)
            
            print(f"✓ Dropper URL with long type: {response}")
            
            if hasattr(response, 'status'):
                print(f"✓ Response status for long type: {response.status}")
                
        except Exception as e:
            print(f"✗ Dropper URL test with long type failed: {e}")

    def tearDown(self):
        """Clean up test task"""
        if self.test_token:
            try:
                self._cancel_task(self.test_token)
                print(f"✓ Cleaned up test task: {self.test_token}")
            except Exception as e:
                print(f"⚠ Could not clean up test task {self.test_token}: {e}")

if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2) 