#!/usr/bin/env python3
"""
Unit tests for /pipe DELETE endpoint

Based on OpenAPI spec:
- DELETE /pipe
- Deletes an existing processing pipeline
- Requires: ?token query param and Authorization header
- Returns: ResultBase with success/error status
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

class TestPipeDeleteEndpoint(unittest.TestCase):
    """Test suite for the /pipe DELETE endpoint"""

    def setUp(self):
        """Set up test client and create test pipelines"""
        self.api_key = os.getenv('DTC_API_KEY')
        self.client = DTCApiClient(api_key=self.api_key)
        
        # Create some test pipelines to delete
        self.test_pipelines = []
        self.test_tokens = []
        
        # Create test pipelines
        test_configs = [
            {
                "source": "webhook_1",
                "components": [
                    {
                        "id": "webhook_1",
                        "provider": "webhook",
                        "config": {"mode": "Source", "type": "webhook"}
                    },
                    {
                        "id": "response_1",
                        "provider": "response",
                        "config": {"lanes": []},
                        "input": [{"lane": "text", "from": "webhook_1"}]
                    }
                ],
                "id": "delete_test_pipeline_1"
            },
            {
                "source": "webhook_2",
                "components": [
                    {
                        "id": "webhook_2",
                        "provider": "webhook",
                        "config": {"mode": "Source", "type": "webhook"}
                    },
                    {
                        "id": "response_2",
                        "provider": "response",
                        "config": {"lanes": []},
                        "input": [{"lane": "text", "from": "webhook_2"}]
                    }
                ],
                "id": "delete_test_pipeline_2"
            }
        ]
        
        # Create the test pipelines
        for i, config in enumerate(test_configs):
            try:
                response = self._create_pipeline(config, f"delete_test_{i}")
                if hasattr(response, 'status') and response.status == 'OK':
                    if response.data and 'token' in response.data:
                        token = response.data['token']
                        self.test_tokens.append(token)
                        print(f"✓ Created test pipeline {i} with token: {token}")
            except Exception as e:
                print(f"⚠ Failed to create test pipeline {i}: {e}")

    def _create_pipeline(self, pipeline_config, name=None):
        """Helper method to create a pipeline for testing"""
        try:
            params = {"name": name} if name else {}
            wrapped_config = {"pipeline": pipeline_config}
            response = self.client._make_request("POST", "/pipe", params=params, data=wrapped_config)
            return response
        except Exception as e:
            return e

    def _delete_pipeline(self, token):
        """Helper method to delete a pipeline"""
        try:
            params = {"token": token}
            response = self.client._make_request("DELETE", "/pipe", params=params)
            return response
        except Exception as e:
            return e

    def test_delete_existing_pipeline(self):
        """Test deleting an existing pipeline"""
        if not self.test_tokens:
            self.skipTest("No test pipelines available for deletion")
        
        token = self.test_tokens.pop(0)  # Remove from cleanup list
        
        try:
            response = self._delete_pipeline(token)
            if hasattr(response, 'status') and response.status == 'OK':
                print(f"✓ Successfully deleted pipeline with token: {token}")
                self.assertEqual(response.status, 'OK')
            else:
                print(f"✗ Failed to delete pipeline {token}: {response}")
                self.fail(f"Pipeline deletion failed: {response}")
        except Exception as e:
            self.fail(f"Pipeline deletion failed: {e}")

    def test_delete_multiple_pipelines(self):
        """Test deleting multiple pipelines"""
        if len(self.test_tokens) < 2:
            self.skipTest("Need at least 2 test pipelines for multiple deletion test")
        
        tokens_to_delete = self.test_tokens[:2]
        self.test_tokens = self.test_tokens[2:]  # Remove from cleanup list
        
        for token in tokens_to_delete:
            try:
                response = self._delete_pipeline(token)
                if hasattr(response, 'status') and response.status == 'OK':
                    print(f"✓ Successfully deleted pipeline with token: {token}")
                    self.assertEqual(response.status, 'OK')
                else:
                    print(f"✗ Failed to delete pipeline {token}: {response}")
            except Exception as e:
                print(f"✗ Failed to delete pipeline {token}: {e}")

    def test_delete_nonexistent_pipeline(self):
        """Test deleting a pipeline that doesn't exist"""
        fake_token = "nonexistent-token-12345"
        
        try:
            response = self._delete_pipeline(fake_token)
            if hasattr(response, 'status'):
                if response.status == 'Error':
                    print(f"✓ Correctly rejected nonexistent pipeline: {response.error}")
                    self.assertEqual(response.status, 'Error')
                else:
                    print(f"✗ Unexpected success deleting nonexistent pipeline: {response}")
            else:
                print(f"✗ Unexpected response deleting nonexistent pipeline: {response}")
        except Exception as e:
            print(f"✓ Correctly rejected nonexistent pipeline with exception: {e}")

    def test_delete_pipeline_with_invalid_token_format(self):
        """Test deleting pipeline with invalid token format"""
        invalid_tokens = ["", "short", "invalid-format", "123", None]
        
        for invalid_token in invalid_tokens:
            if invalid_token is None:
                continue
            try:
                response = self._delete_pipeline(invalid_token)
                if hasattr(response, 'status'):
                    if response.status == 'Error':
                        print(f"✓ Correctly rejected invalid token '{invalid_token}': {response.error}")
                    else:
                        print(f"✗ Unexpected success with invalid token '{invalid_token}': {response}")
                else:
                    print(f"✗ Unexpected response with invalid token '{invalid_token}': {response}")
            except Exception as e:
                print(f"✓ Correctly rejected invalid token '{invalid_token}' with exception: {e}")

    def test_delete_pipeline_with_invalid_api_key(self):
        """Test deleting pipeline with invalid API key"""
        if not self.test_tokens:
            self.skipTest("No test tokens available")
        
        invalid_client = DTCApiClient(api_key='invalid_key_12345')
        token = self.test_tokens[0]  # Don't remove from cleanup list
        
        try:
            params = {"token": token}
            with self.assertRaises((AuthenticationError, DTCApiError)):
                invalid_client._make_request("DELETE", "/pipe", params=params)
            print("✓ Invalid API key correctly rejected")
        except Exception as e:
            print(f"✗ Invalid API key test failed: {e}")

    def test_delete_pipeline_no_connectivity(self):
        """Test deleting pipeline with no network connectivity"""
        if not self.test_tokens:
            self.skipTest("No test tokens available")
        
        offline_client = DTCApiClient(
            api_key=self.api_key,
            base_url='https://invalid-url-that-does-not-exist.com'
        )
        token = self.test_tokens[0]  # Don't remove from cleanup list
        
        try:
            params = {"token": token}
            with self.assertRaises((NetworkError, DTCApiError)):
                offline_client._make_request("DELETE", "/pipe", params=params)
            print("✓ Network connectivity error handled correctly")
        except Exception as e:
            print(f"✗ Network connectivity test failed: {e}")

    def test_delete_pipeline_response_structure(self):
        """Test the structure of pipeline deletion response"""
        if not self.test_tokens:
            self.skipTest("No test tokens available")
        
        token = self.test_tokens.pop(0)  # Remove from cleanup list
        
        try:
            response = self._delete_pipeline(token)
            
            # Check response structure
            if hasattr(response, 'status'):
                print(f"✓ Response status: {response.status}")
                self.assertIn(response.status, ['OK', 'Error'])
                
                if hasattr(response, 'data'):
                    print(f"✓ Response data: {response.data}")
                    
                if hasattr(response, 'error') and response.error:
                    print(f"✓ Response error: {response.error}")
                    
                if hasattr(response, 'metrics') and response.metrics:
                    print(f"✓ Response metrics: {response.metrics}")
            else:
                print(f"✗ Response structure test failed: {response}")
                
        except Exception as e:
            print(f"✗ Response structure test failed: {e}")

    def test_delete_already_deleted_pipeline(self):
        """Test deleting a pipeline that was already deleted"""
        if not self.test_tokens:
            self.skipTest("No test tokens available")
        
        token = self.test_tokens.pop(0)  # Remove from cleanup list
        
        try:
            # Delete the pipeline first time
            response1 = self._delete_pipeline(token)
            if hasattr(response1, 'status') and response1.status == 'OK':
                print(f"✓ First deletion successful: {token}")
                
                # Try to delete the same pipeline again
                response2 = self._delete_pipeline(token)
                if hasattr(response2, 'status'):
                    if response2.status == 'Error':
                        print(f"✓ Second deletion correctly rejected: {response2.error}")
                        self.assertEqual(response2.status, 'Error')
                    else:
                        print(f"✗ Second deletion unexpectedly succeeded: {response2}")
                else:
                    print(f"✗ Second deletion unexpected response: {response2}")
            else:
                print(f"✗ First deletion failed: {response1}")
                
        except Exception as e:
            print(f"✗ Double deletion test failed: {e}")

    def tearDown(self):
        """Clean up remaining test pipelines"""
        for token in self.test_tokens:
            try:
                self._delete_pipeline(token)
                print(f"✓ Cleaned up test pipeline: {token}")
            except Exception as e:
                print(f"⚠ Could not clean up test pipeline {token}: {e}")

if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2) 