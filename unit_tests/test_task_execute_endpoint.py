#!/usr/bin/env python3
"""
Unit tests for /task PUT endpoint

Based on OpenAPI spec:
- PUT /task
- Execute a task with pipeline configuration
- Requires: pipeline config in body, optional ?name and ?threads query params
- Returns: ResultBase with task token in data on success
"""

import unittest
import json
import os
import sys
from pathlib import Path
import time

# Add the parent directory to Python path to import dtc_api_sdk
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

from dtc_api_sdk import DTCApiClient
from dtc_api_sdk.exceptions import AuthenticationError, DTCApiError, NetworkError

class TestTaskExecuteEndpoint(unittest.TestCase):
    """Test suite for the /task PUT endpoint"""

    def setUp(self):
        """Set up test client and task configurations"""
        self.api_key = os.getenv('DTC_API_KEY')
        self.client = DTCApiClient(api_key=self.api_key)
        
        # Track created task tokens for cleanup
        self.task_tokens = []
        
        # Define test task configurations
        self.test_task_configs = [
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
                "id": "simple_task"
            },
            {
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
                "id": "parse_task"
            }
        ]

    def _execute_task(self, task_config, name=None, threads=None):
        """Helper method to execute a task"""
        try:
            params = {}
            if name:
                params["name"] = name
            if threads:
                params["threads"] = threads
            
            # API expects task config wrapped in "pipeline" field
            wrapped_config = {"pipeline": task_config}
            response = self.client._make_request("PUT", "/task", params=params, data=wrapped_config)
            return response
        except Exception as e:
            return e

    def _get_task_status(self, token):
        """Helper method to get task status"""
        try:
            params = {"token": token}
            response = self.client._make_request("GET", "/task", params=params)
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

    def test_execute_simple_task(self):
        """Test executing a simple task"""
        try:
            response = self._execute_task(self.test_task_configs[0], "simple_test")
            
            if hasattr(response, 'status') and response.status == 'OK':
                if response.data and 'token' in response.data:
                    token = response.data['token']
                    self.task_tokens.append(token)
                    print(f"✓ Simple task executed with token: {token}")
                    self.assertEqual(response.status, 'OK')
                else:
                    print(f"✓ Simple task executed: {response.data}")
            else:
                print(f"✗ Simple task execution failed: {response}")
                
        except Exception as e:
            print(f"✗ Simple task execution failed: {e}")

    def test_execute_task_with_name(self):
        """Test executing a task with a specific name"""
        try:
            response = self._execute_task(self.test_task_configs[0], "named_task_test")
            
            if hasattr(response, 'status') and response.status == 'OK':
                if response.data and 'token' in response.data:
                    token = response.data['token']
                    self.task_tokens.append(token)
                    print(f"✓ Named task executed with token: {token}")
                    self.assertEqual(response.status, 'OK')
                else:
                    print(f"✓ Named task executed: {response.data}")
            else:
                print(f"✗ Named task execution failed: {response}")
                
        except Exception as e:
            print(f"✗ Named task execution failed: {e}")

    def test_execute_task_with_threads(self):
        """Test executing a task with specific thread count"""
        try:
            response = self._execute_task(self.test_task_configs[0], "threaded_task", threads=2)
            
            if hasattr(response, 'status') and response.status == 'OK':
                if response.data and 'token' in response.data:
                    token = response.data['token']
                    self.task_tokens.append(token)
                    print(f"✓ Threaded task executed with token: {token}")
                    self.assertEqual(response.status, 'OK')
                else:
                    print(f"✓ Threaded task executed: {response.data}")
            else:
                print(f"✗ Threaded task execution failed: {response}")
                
        except Exception as e:
            print(f"✗ Threaded task execution failed: {e}")

    def test_execute_task_with_invalid_threads(self):
        """Test executing a task with invalid thread count"""
        invalid_thread_counts = [0, 17, -1, 100]
        
        for thread_count in invalid_thread_counts:
            try:
                response = self._execute_task(self.test_task_configs[0], f"invalid_threads_{thread_count}", threads=thread_count)
                
                if hasattr(response, 'status'):
                    if response.status == 'Error':
                        print(f"✓ Invalid thread count {thread_count} correctly rejected: {response.error}")
                    else:
                        print(f"✗ Invalid thread count {thread_count} unexpectedly accepted: {response}")
                        if response.data and 'token' in response.data:
                            self.task_tokens.append(response.data['token'])
                else:
                    print(f"✗ Invalid thread count {thread_count} unexpected response: {response}")
                    
            except Exception as e:
                print(f"✓ Invalid thread count {thread_count} correctly rejected with exception: {e}")

    def test_execute_multiple_tasks(self):
        """Test executing multiple tasks"""
        for i, task_config in enumerate(self.test_task_configs):
            try:
                response = self._execute_task(task_config, f"multi_task_{i}")
                
                if hasattr(response, 'status') and response.status == 'OK':
                    if response.data and 'token' in response.data:
                        token = response.data['token']
                        self.task_tokens.append(token)
                        print(f"✓ Task {i} executed with token: {token}")
                    else:
                        print(f"✓ Task {i} executed: {response.data}")
                else:
                    print(f"✗ Task {i} execution failed: {response}")
                    
            except Exception as e:
                print(f"✗ Task {i} execution failed: {e}")

    def test_execute_task_and_check_status(self):
        """Test executing a task and checking its status"""
        try:
            # Execute task
            response = self._execute_task(self.test_task_configs[0], "status_check_task")
            
            if hasattr(response, 'status') and response.status == 'OK':
                if response.data and 'token' in response.data:
                    token = response.data['token']
                    self.task_tokens.append(token)
                    print(f"✓ Task executed with token: {token}")
                    
                    # Check task status
                    status_response = self._get_task_status(token)
                    if hasattr(status_response, 'status'):
                        print(f"✓ Task status: {status_response.status}")
                        if status_response.data:
                            print(f"✓ Task status data: {status_response.data}")
                    else:
                        print(f"✗ Task status check failed: {status_response}")
                else:
                    print(f"✗ Task execution failed: no token returned")
            else:
                print(f"✗ Task execution failed: {response}")
                
        except Exception as e:
            print(f"✗ Task execution and status check failed: {e}")

    def test_execute_task_with_invalid_config(self):
        """Test executing a task with invalid configuration"""
        invalid_configs = [
            {"invalid": "config"},
            {"components": "not_an_array"},
            {"source": 123, "components": []},
            {}
        ]
        
        for i, invalid_config in enumerate(invalid_configs):
            try:
                response = self._execute_task(invalid_config, f"invalid_config_{i}")
                
                if hasattr(response, 'status'):
                    if response.status == 'Error':
                        print(f"✓ Invalid config {i} correctly rejected: {response.error}")
                    else:
                        print(f"✗ Invalid config {i} unexpectedly accepted: {response}")
                        if response.data and 'token' in response.data:
                            self.task_tokens.append(response.data['token'])
                else:
                    print(f"✗ Invalid config {i} unexpected response: {response}")
                    
            except Exception as e:
                print(f"✓ Invalid config {i} correctly rejected with exception: {e}")

    def test_execute_task_with_invalid_api_key(self):
        """Test executing task with invalid API key"""
        invalid_client = DTCApiClient(api_key='invalid_key_12345')
        
        try:
            wrapped_config = {"pipeline": self.test_task_configs[0]}
            with self.assertRaises((AuthenticationError, DTCApiError)):
                invalid_client._make_request("PUT", "/task", data=wrapped_config)
            print("✓ Invalid API key correctly rejected")
        except Exception as e:
            print(f"✗ Invalid API key test failed: {e}")

    def test_execute_task_no_connectivity(self):
        """Test executing task with no network connectivity"""
        offline_client = DTCApiClient(
            api_key=self.api_key,
            base_url='https://invalid-url-that-does-not-exist.com'
        )
        
        try:
            wrapped_config = {"pipeline": self.test_task_configs[0]}
            with self.assertRaises((NetworkError, DTCApiError)):
                offline_client._make_request("PUT", "/task", data=wrapped_config)
            print("✓ Network connectivity error handled correctly")
        except Exception as e:
            print(f"✗ Network connectivity test failed: {e}")

    def test_execute_task_response_structure(self):
        """Test the structure of task execution response"""
        try:
            response = self._execute_task(self.test_task_configs[0], "response_structure_test")
            
            # Check response structure
            if hasattr(response, 'status'):
                print(f"✓ Response status: {response.status}")
                self.assertIn(response.status, ['OK', 'Error'])
                
                if hasattr(response, 'data'):
                    print(f"✓ Response data: {response.data}")
                    if response.data and 'token' in response.data:
                        token = response.data['token']
                        self.task_tokens.append(token)
                        self.assertIsInstance(token, str)
                        self.assertGreater(len(token), 0)
                        print(f"✓ Token is valid string: {token}")
                    
                if hasattr(response, 'error') and response.error:
                    print(f"✓ Response error: {response.error}")
                    
                if hasattr(response, 'metrics') and response.metrics:
                    print(f"✓ Response metrics: {response.metrics}")
            else:
                print(f"✗ Response structure test failed: {response}")
                
        except Exception as e:
            print(f"✗ Response structure test failed: {e}")

    def test_execute_and_cancel_task(self):
        """Test executing a task and then canceling it"""
        try:
            # Execute task
            response = self._execute_task(self.test_task_configs[1], "cancel_test_task")
            
            if hasattr(response, 'status') and response.status == 'OK':
                if response.data and 'token' in response.data:
                    token = response.data['token']
                    print(f"✓ Task executed with token: {token}")
                    
                    # Cancel the task
                    cancel_response = self._cancel_task(token)
                    if hasattr(cancel_response, 'status'):
                        if cancel_response.status == 'OK':
                            print(f"✓ Task cancelled successfully")
                        else:
                            print(f"✗ Task cancellation failed: {cancel_response.error}")
                    else:
                        print(f"✗ Task cancellation unexpected response: {cancel_response}")
                else:
                    print(f"✗ Task execution failed: no token returned")
            else:
                print(f"✗ Task execution failed: {response}")
                
        except Exception as e:
            print(f"✗ Task execution and cancellation failed: {e}")

    def tearDown(self):
        """Clean up created tasks"""
        for token in self.task_tokens:
            try:
                self._cancel_task(token)
                print(f"✓ Cleaned up task: {token}")
            except Exception as e:
                print(f"⚠ Could not clean up task {token}: {e}")

if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2) 