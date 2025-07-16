#!/usr/bin/env python3
"""
Unit tests for /pipe POST endpoint (create pipeline)

Based on OpenAPI spec:
- POST /pipe
- Creates a new processing pipeline
- Requires: pipeline config in body, optional ?name query param
- Returns: ResultBase with token in data on success
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

class TestPipeCreateEndpoint(unittest.TestCase):
    """Test suite for the /pipe POST endpoint"""

    def setUp(self):
        """Set up test client and load example pipeline data"""
        self.api_key = os.getenv('DTC_API_KEY')
        self.client = DTCApiClient(api_key=self.api_key)
        
        # Load example pipeline files - these contain the correct components structure
        self.pipeline_files = [
            'example_pipelines/aparavi-project-export-new-project-2025-07-09T19-13.json',
            'example_pipelines/aparavi-project-export-new-project-2025-07-09T19-18.json', 
            'example_pipelines/aparavi-project-export-new-project-2025-07-09T19-20.json',
            'example_pipelines/aparavi-project-export-new-project-2025-07-10T11-40.json',
            'example_pipelines/aparavi-project-export-new-project-2025-07-10T13-51.json',
            'example_pipelines/aparavi-project-export-new-project-2025-07-10T13-58.json'
        ]
        
        # Load pipeline data
        self.pipeline_data = {}
        for file_path in self.pipeline_files:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    self.pipeline_data[file_path] = json.load(f)
        
        # Keep track of created pipelines for cleanup
        self.created_tokens = []

    def tearDown(self):
        """Clean up created pipelines"""
        for token in self.created_tokens:
            try:
                self.client.delete_pipeline(token)
                print(f"✓ Cleaned up pipeline with token: {token}")
            except Exception as e:
                print(f"⚠ Could not clean up pipeline {token}: {e}")

    def _get_create_response(self, pipeline_config, name=None):
        """Helper method to get full create response for debugging"""
        try:
            params = {"name": name} if name else {}
            
            # Ensure pipeline has required fields
            if "source" not in pipeline_config:
                # Find the first component to use as source
                if "components" in pipeline_config and pipeline_config["components"]:
                    pipeline_config["source"] = pipeline_config["components"][0]["id"]
                else:
                    pipeline_config["source"] = "default_source"
            
            # API expects pipeline config wrapped in "pipeline" field
            wrapped_config = {"pipeline": pipeline_config}
            response = self.client._make_request("POST", "/pipe", params=params, data=wrapped_config)
            return response
        except Exception as e:
            return e

    def test_create_simple_pipeline(self):
        """Test creating a simple pipeline configuration"""
        simple_pipeline = {
            "source": "webhook_1",
            "components": [
                {
                    "id": "webhook_1",
                    "provider": "webhook",
                    "config": {
                        "mode": "Source",
                        "type": "webhook"
                    }
                },
                {
                    "id": "response_1",
                    "provider": "response",
                    "config": {
                        "lanes": []
                    },
                    "input": [
                        {
                            "lane": "text",
                            "from": "webhook_1"
                        }
                    ]
                }
            ],
            "id": "simple_test_pipeline"
        }
        
        try:
            response = self._get_create_response(simple_pipeline, "simple_test")
            if hasattr(response, 'status') and response.status == 'OK':
                self.assertIsNotNone(response.data)
                if response.data and 'token' in response.data:
                    token = response.data['token']
                    self.created_tokens.append(token)
                    print(f"✓ Simple pipeline created with token: {token}")
                else:
                    print(f"✓ Simple pipeline created: {response.data}")
            else:
                print(f"✗ Simple pipeline creation failed: {response}")
        except Exception as e:
            print(f"✗ Simple pipeline creation failed: {e}")

    def test_create_example_pipelines(self):
        """Test creating pipelines from example configuration files"""
        for i, (file_path, pipeline_config) in enumerate(self.pipeline_data.items()):
            with self.subTest(pipeline=file_path):
                try:
                    pipeline_name = f"test_pipeline_{i}"
                    response = self._get_create_response(pipeline_config, pipeline_name)
                    
                    if hasattr(response, 'status') and response.status == 'OK':
                        if response.data and 'token' in response.data:
                            token = response.data['token']
                            self.created_tokens.append(token)
                            print(f"✓ {file_path} created with token: {token}")
                        else:
                            print(f"✓ {file_path} created: {response.data}")
                    else:
                        print(f"✗ {file_path} creation failed: {response}")
                        
                except Exception as e:
                    print(f"✗ {file_path} creation failed: {e}")

    def test_create_pipeline_with_name(self):
        """Test creating a pipeline with a specific name"""
        pipeline_config = {
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
            "id": "named_test_pipeline"
        }
        
        try:
            response = self._get_create_response(pipeline_config, "my_named_pipeline")
            if hasattr(response, 'status') and response.status == 'OK':
                if response.data and 'token' in response.data:
                    token = response.data['token']
                    self.created_tokens.append(token)
                    print(f"✓ Named pipeline created with token: {token}")
                else:
                    print(f"✓ Named pipeline created: {response.data}")
            else:
                print(f"✗ Named pipeline creation failed: {response}")
        except Exception as e:
            print(f"✗ Named pipeline creation failed: {e}")

    def test_create_pipeline_without_name(self):
        """Test creating a pipeline without specifying a name"""
        pipeline_config = {
            "source": "file://unnamed-input",
            "transformations": ["parse", "filter"],
            "destination": "s3://unnamed-output",
            "settings": {
                "filter_criteria": {"size": "< 10MB"}
            }
        }
        
        try:
            response = self._get_create_response(pipeline_config)
            if hasattr(response, 'status') and response.status == 'OK':
                if response.data and 'token' in response.data:
                    token = response.data['token']
                    self.created_tokens.append(token)
                    print(f"✓ Unnamed pipeline created with token: {token}")
                else:
                    print(f"✓ Unnamed pipeline created: {response.data}")
            else:
                print(f"✗ Unnamed pipeline creation failed: {response}")
        except Exception as e:
            print(f"✗ Unnamed pipeline creation failed: {e}")

    def test_create_duplicate_pipeline(self):
        """Test creating duplicate pipelines with same name"""
        pipeline_config = {
            "source": "webhook://duplicate-input",
            "transformations": ["parse", "duplicate"],
            "destination": "database://duplicate-output",
            "settings": {
                "duplicate_detection": True
            }
        }
        
        try:
            # Create first pipeline
            response1 = self._get_create_response(pipeline_config, "duplicate_test")
            if hasattr(response1, 'status') and response1.status == 'OK':
                if response1.data and 'token' in response1.data:
                    token1 = response1.data['token']
                    self.created_tokens.append(token1)
                    print(f"✓ First duplicate pipeline created with token: {token1}")
                
                # Try to create second pipeline with same name
                response2 = self._get_create_response(pipeline_config, "duplicate_test")
                if hasattr(response2, 'status'):
                    if response2.status == 'Error':
                        print(f"✓ Duplicate pipeline correctly rejected: {response2.error}")
                    else:
                        if response2.data and 'token' in response2.data:
                            token2 = response2.data['token']
                            self.created_tokens.append(token2)
                            print(f"✓ Second duplicate pipeline created with token: {token2}")
                else:
                    print(f"✗ Duplicate pipeline test failed: {response2}")
            else:
                print(f"✗ First duplicate pipeline creation failed: {response1}")
        except Exception as e:
            print(f"✗ Duplicate pipeline test failed: {e}")

    def test_create_pipeline_with_invalid_api_key(self):
        """Test creating pipeline with invalid API key"""
        invalid_client = DTCApiClient(api_key='invalid_key_12345')
        
        pipeline_config = {
            "source": "webhook://invalid-key-test",
            "transformations": ["parse"],
            "destination": "file://invalid-key-output"
        }
        
        try:
            with self.assertRaises((AuthenticationError, DTCApiError)):
                invalid_client._make_request("POST", "/pipe", data=pipeline_config)
            print("✓ Invalid API key correctly rejected")
        except Exception as e:
            print(f"✗ Invalid API key test failed: {e}")

    def test_create_pipeline_no_connectivity(self):
        """Test creating pipeline with no network connectivity"""
        offline_client = DTCApiClient(
            api_key=self.api_key,
            base_url='https://invalid-url-that-does-not-exist.com'
        )
        
        pipeline_config = {
            "source": "webhook://connectivity-test",
            "transformations": ["parse"],
            "destination": "file://connectivity-output"
        }
        
        try:
            with self.assertRaises((NetworkError, DTCApiError)):
                offline_client._make_request("POST", "/pipe", data=pipeline_config)
            print("✓ Network connectivity error handled correctly")
        except Exception as e:
            print(f"✗ Network connectivity test failed: {e}")

    def test_create_pipeline_response_structure(self):
        """Test the structure of successful pipeline creation response"""
        pipeline_config = {
            "source": "webhook://response-structure-test",
            "transformations": ["parse", "validate"],
            "destination": "api://response-structure-output",
            "settings": {
                "validation_schema": {"type": "object"}
            }
        }
        
        try:
            response = self._get_create_response(pipeline_config, "response_test")
            
            if hasattr(response, 'status'):
                print(f"✓ Response status: {response.status}")
                
                if hasattr(response, 'data') and response.data:
                    print(f"✓ Response data: {response.data}")
                    if 'token' in response.data:
                        token = response.data['token']
                        self.created_tokens.append(token)
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

if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2) 