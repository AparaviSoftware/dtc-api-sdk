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

class TestPipeValidateEndpoint(unittest.TestCase):
    """Test suite for the /pipe/validate POST endpoint"""

    def setUp(self):
        """Set up test client and load example pipeline data"""
        self.api_key = os.getenv('DTC_API_KEY')
        self.client = DTCApiClient(api_key=self.api_key)
        
        # Load all example pipeline files
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

    def _get_validation_response(self, pipeline_config):
        """Helper method to get full validation response for debugging"""
        try:
            # Make direct request to get full response
            response = self.client._make_request("POST", "/pipe/validate", data=pipeline_config)
            return response
        except Exception as e:
            # If direct request fails, just return the exception
            return e

    def test_validate_example_pipelines(self):
        """Test validation of all example pipeline configurations"""
        for file_path, pipeline_config in self.pipeline_data.items():
            with self.subTest(pipeline=file_path):
                try:
                    is_valid = self.client.validate_pipeline(pipeline_config)
                    self.assertTrue(is_valid, f"Pipeline validation failed for {file_path}")
                    print(f"✓ {file_path} validation: {'VALID' if is_valid else 'INVALID'}")
                except Exception as e:
                    # For debugging, get the full response
                    full_response = self._get_validation_response(pipeline_config)
                    if hasattr(full_response, 'error'):
                        print(f"✗ {file_path} validation error: {full_response.error}")
                    self.fail(f"Pipeline validation failed for {file_path}: {str(e)}")

    def test_validate_simple_pipeline(self):
        """Test validation of a simple pipeline configuration"""
        simple_pipeline = {
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
            "id": "simple_test"
        }
        
        is_valid = self.client.validate_pipeline(simple_pipeline)
        self.assertTrue(is_valid)
        print(f"✓ Simple pipeline validation: {'VALID' if is_valid else 'INVALID'}")

    def test_validate_empty_pipeline(self):
        """Test validation of an empty pipeline configuration"""
        empty_pipeline = {
            "components": [],
            "id": "empty_test"
        }
        
        try:
            is_valid = self.client.validate_pipeline(empty_pipeline)
            print(f"✓ Empty pipeline validation: {'VALID' if is_valid else 'INVALID'}")
        except Exception as e:
            print(f"✓ Empty pipeline validation error: {str(e)}")

    def test_validate_invalid_pipeline(self):
        """Test validation of an invalid pipeline configuration"""
        invalid_pipeline = {
            "invalid_key": "invalid_value",
            "components": [
                {
                    "id": "invalid_component",
                    "provider": "nonexistent_provider",
                    "config": {}
                }
            ]
        }
        
        try:
            is_valid = self.client.validate_pipeline(invalid_pipeline)
            print(f"✓ Invalid pipeline validation: {'VALID' if is_valid else 'INVALID'}")
        except Exception as e:
            print(f"✓ Invalid pipeline validation error: {str(e)}")

    def test_validate_malformed_json(self):
        """Test validation with malformed pipeline data"""
        malformed_pipeline = {
            "components": "this should be an array",
            "id": 123  # should be string
        }
        
        try:
            is_valid = self.client.validate_pipeline(malformed_pipeline)
            print(f"✓ Malformed pipeline validation: {'VALID' if is_valid else 'INVALID'}")
        except Exception as e:
            print(f"✓ Malformed pipeline validation error: {str(e)}")

    def test_validate_pipeline_with_invalid_api_key(self):
        """Test validation with invalid API key"""
        invalid_client = DTCApiClient(api_key='invalid_key_12345')
        
        # Use first available pipeline
        if self.pipeline_data:
            pipeline_config = next(iter(self.pipeline_data.values()))
            
            with self.assertRaises((AuthenticationError, DTCApiError)):
                invalid_client.validate_pipeline(pipeline_config)
            print("✓ Invalid API key correctly rejected")

    def test_validate_pipeline_no_connectivity(self):
        """Test validation with no network connectivity simulation"""
        # Create client with invalid base URL to simulate connectivity issues
        offline_client = DTCApiClient(
            api_key=self.api_key,
            base_url='https://invalid-url-that-does-not-exist.com'
        )
        
        if self.pipeline_data:
            pipeline_config = next(iter(self.pipeline_data.values()))
            
            with self.assertRaises(Exception):  # Could be APIError or NetworkError
                offline_client.validate_pipeline(pipeline_config)
            print("✓ Network connectivity error handled correctly")

    def test_validate_pipeline_response_structure(self):
        """Test the structure of successful validation response"""
        if self.pipeline_data:
            pipeline_config = next(iter(self.pipeline_data.values()))
            
            # Test the boolean return value
            is_valid = self.client.validate_pipeline(pipeline_config)
            self.assertIsInstance(is_valid, bool)
            
            # Get full response for debugging
            full_response = self._get_validation_response(pipeline_config)
            if hasattr(full_response, 'status'):
                print(f"✓ Full response status: {full_response.status}")
            if hasattr(full_response, 'data'):
                print(f"✓ Full response data: {full_response.data}")
            if hasattr(full_response, 'error'):
                print(f"✓ Full response error: {full_response.error}")
                
            print(f"✓ Validation result: {'VALID' if is_valid else 'INVALID'}")

    def assertHasAttribute(self, obj, attr):
        """Helper method to check if object has attribute"""
        self.assertTrue(hasattr(obj, attr), f"Object does not have attribute '{attr}'")

if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2) 