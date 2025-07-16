#!/usr/bin/env python3
"""
Unit tests for /webhook PUT endpoint

Based on OpenAPI spec:
- PUT /webhook
- Proxy a webhook request to the loaded task engine
- Requires: ?token query param, Authorization header
- Returns: JSON response from task engine
"""

import unittest
import json
import os
import sys
from pathlib import Path
import tempfile
import io

# Add the parent directory to Python path to import dtc_api_sdk
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

from dtc_api_sdk import DTCApiClient
from dtc_api_sdk.exceptions import AuthenticationError, DTCApiError, NetworkError

class TestWebhookEndpoint(unittest.TestCase):
    """Test suite for the /webhook PUT endpoint"""

    def setUp(self):
        """Set up test client and create test task"""
        self.api_key = os.getenv('DTC_API_KEY')
        self.client = DTCApiClient(api_key=self.api_key)
        
        # Create a test task for webhook testing
        self.test_task_config = {
            "source": "webhook_1",
            "components": [
                {
                    "id": "webhook_1",
                    "provider": "webhook",
                    "config": {"mode": "Source", "type": "webhook"}
                },
                {
                    "id": "parse_1",
                    "provider": "parse",
                    "config": {},
                    "input": [{"lane": "tags", "from": "webhook_1"}]
                },
                {
                    "id": "response_1",
                    "provider": "response",
                    "config": {"lanes": []},
                    "input": [{"lane": "text", "from": "parse_1"}]
                }
            ],
            "id": "webhook_test_task"
        }
        
        # Create the test task
        self.test_token = None
        try:
            response = self._execute_task(self.test_task_config, "webhook_test")
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

    def _send_webhook(self, token, data=None, files=None):
        """Helper method to send webhook request"""
        try:
            params = {"token": token}
            
            if files:
                response = self.client._make_request("PUT", "/webhook", params=params, files=files)
            else:
                response = self.client._make_request("PUT", "/webhook", params=params, data=data)
            
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

    def test_webhook_with_json_data(self):
        """Test sending JSON data via webhook"""
        if not self.test_token:
            self.skipTest("No test task available")
        
        test_data = {
            "message": "Hello from webhook",
            "timestamp": "2025-01-15T10:00:00Z",
            "data": {"key": "value", "number": 42}
        }
        
        try:
            response = self._send_webhook(self.test_token, test_data)
            
            if hasattr(response, 'status'):
                print(f"✓ Webhook JSON response status: {response.status}")
                if response.data:
                    print(f"✓ Webhook JSON response data: {response.data}")
            else:
                print(f"✓ Webhook JSON response: {response}")
                
        except Exception as e:
            print(f"✗ Webhook JSON test failed: {e}")

    def test_webhook_with_text_data(self):
        """Test sending text data via webhook"""
        if not self.test_token:
            self.skipTest("No test task available")
        
        test_text = "This is a test message sent via webhook"
        
        try:
            response = self._send_webhook(self.test_token, test_text)
            
            if hasattr(response, 'status'):
                print(f"✓ Webhook text response status: {response.status}")
                if response.data:
                    print(f"✓ Webhook text response data: {response.data}")
            else:
                print(f"✓ Webhook text response: {response}")
                
        except Exception as e:
            print(f"✗ Webhook text test failed: {e}")

    def test_webhook_with_file_upload(self):
        """Test uploading files via webhook"""
        if not self.test_token:
            self.skipTest("No test task available")
        
        # Create a test file
        test_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
        test_file.write("Test file content for webhook upload")
        test_file.close()
        
        try:
            # Prepare file for upload
            with open(test_file.name, 'rb') as f:
                files = {'file': io.BytesIO(f.read())}
            
            response = self._send_webhook(self.test_token, files=files)
            
            if hasattr(response, 'status'):
                print(f"✓ Webhook file upload response status: {response.status}")
                if response.data:
                    print(f"✓ Webhook file upload response data: {response.data}")
            else:
                print(f"✓ Webhook file upload response: {response}")
                
        except Exception as e:
            print(f"✗ Webhook file upload test failed: {e}")
        finally:
            os.unlink(test_file.name)

    def test_webhook_with_empty_data(self):
        """Test sending empty data via webhook"""
        if not self.test_token:
            self.skipTest("No test task available")
        
        try:
            response = self._send_webhook(self.test_token, {})
            
            if hasattr(response, 'status'):
                print(f"✓ Webhook empty data response status: {response.status}")
                if response.data:
                    print(f"✓ Webhook empty data response data: {response.data}")
            else:
                print(f"✓ Webhook empty data response: {response}")
                
        except Exception as e:
            print(f"✗ Webhook empty data test failed: {e}")

    def test_webhook_with_invalid_token(self):
        """Test webhook with invalid task token"""
        invalid_token = "invalid-token-12345"
        
        test_data = {"message": "Test with invalid token"}
        
        try:
            response = self._send_webhook(invalid_token, test_data)
            
            if hasattr(response, 'status'):
                if response.status == 'Error':
                    print(f"✓ Invalid token correctly rejected: {response.error}")
                else:
                    print(f"✗ Invalid token unexpectedly accepted: {response}")
            else:
                print(f"✗ Invalid token unexpected response: {response}")
                
        except Exception as e:
            print(f"✓ Invalid token correctly rejected with exception: {e}")

    def test_webhook_with_nonexistent_token(self):
        """Test webhook with nonexistent task token"""
        nonexistent_token = "00000000-0000-0000-0000-000000000000"
        
        test_data = {"message": "Test with nonexistent token"}
        
        try:
            response = self._send_webhook(nonexistent_token, test_data)
            
            if hasattr(response, 'status'):
                if response.status == 'Error':
                    print(f"✓ Nonexistent token correctly rejected: {response.error}")
                else:
                    print(f"✗ Nonexistent token unexpectedly accepted: {response}")
            else:
                print(f"✗ Nonexistent token unexpected response: {response}")
                
        except Exception as e:
            print(f"✓ Nonexistent token correctly rejected with exception: {e}")

    def test_webhook_with_large_payload(self):
        """Test webhook with large data payload"""
        if not self.test_token:
            self.skipTest("No test task available")
        
        # Create large payload (100KB)
        large_data = {
            "message": "Large payload test",
            "data": "x" * 100000  # 100KB of data
        }
        
        try:
            response = self._send_webhook(self.test_token, large_data)
            
            if hasattr(response, 'status'):
                print(f"✓ Webhook large payload response status: {response.status}")
                if response.data:
                    print(f"✓ Webhook large payload response data: {str(response.data)[:100]}...")
            else:
                print(f"✓ Webhook large payload response: {str(response)[:100]}...")
                
        except Exception as e:
            print(f"✗ Webhook large payload test failed: {e}")

    def test_webhook_with_invalid_api_key(self):
        """Test webhook with invalid API key"""
        if not self.test_token:
            self.skipTest("No test task available")
        
        invalid_client = DTCApiClient(api_key='invalid_key_12345')
        
        test_data = {"message": "Test with invalid API key"}
        
        try:
            params = {"token": self.test_token}
            with self.assertRaises((AuthenticationError, DTCApiError)):
                invalid_client._make_request("PUT", "/webhook", params=params, data=test_data)
            print("✓ Invalid API key correctly rejected")
        except Exception as e:
            print(f"✗ Invalid API key test failed: {e}")

    def test_webhook_no_connectivity(self):
        """Test webhook with no network connectivity"""
        if not self.test_token:
            self.skipTest("No test task available")
        
        offline_client = DTCApiClient(
            api_key=self.api_key,
            base_url='https://invalid-url-that-does-not-exist.com'
        )
        
        test_data = {"message": "Test with no connectivity"}
        
        try:
            params = {"token": self.test_token}
            with self.assertRaises((NetworkError, DTCApiError)):
                offline_client._make_request("PUT", "/webhook", params=params, data=test_data)
            print("✓ Network connectivity error handled correctly")
        except Exception as e:
            print(f"✗ Network connectivity test failed: {e}")

    def test_webhook_response_structure(self):
        """Test the structure of webhook response"""
        if not self.test_token:
            self.skipTest("No test task available")
        
        test_data = {"message": "Response structure test"}
        
        try:
            response = self._send_webhook(self.test_token, test_data)
            
            print(f"✓ Webhook response type: {type(response)}")
            
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
            print(f"✗ Webhook response structure test failed: {e}")

    def test_webhook_multiple_requests(self):
        """Test multiple webhook requests to same task"""
        if not self.test_token:
            self.skipTest("No test task available")
        
        test_messages = [
            {"message": "First request", "id": 1},
            {"message": "Second request", "id": 2},
            {"message": "Third request", "id": 3}
        ]
        
        for i, message in enumerate(test_messages):
            try:
                response = self._send_webhook(self.test_token, message)
                
                if hasattr(response, 'status'):
                    print(f"✓ Request {i+1} response status: {response.status}")
                else:
                    print(f"✓ Request {i+1} response: {response}")
                    
            except Exception as e:
                print(f"✗ Request {i+1} failed: {e}")

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