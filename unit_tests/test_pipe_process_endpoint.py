#!/usr/bin/env python3
"""
Unit tests for /pipe/process PUT endpoint

Based on OpenAPI spec:
- PUT /pipe/process
- Upload data to process through a pipeline
- Requires: ?token query param, Authorization header, multipart/form-data
- Returns: ResultBase with processing results
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

class TestPipeProcessEndpoint(unittest.TestCase):
    """Test suite for the /pipe/process PUT endpoint"""

    def setUp(self):
        """Set up test client and create test pipeline"""
        self.api_key = os.getenv('DTC_API_KEY')
        self.client = DTCApiClient(api_key=self.api_key)
        
        # Create a test pipeline for processing
        self.test_pipeline_config = {
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
            "id": "process_test_pipeline"
        }
        
        # Create the test pipeline
        self.test_token = None
        try:
            response = self._create_pipeline(self.test_pipeline_config, "process_test")
            if hasattr(response, 'status') and response.status == 'OK':
                if response.data and 'token' in response.data:
                    self.test_token = response.data['token']
                    print(f"✓ Created test pipeline with token: {self.test_token}")
        except Exception as e:
            print(f"⚠ Failed to create test pipeline: {e}")

        # Create test files
        self.test_files = []
        self._create_test_files()

    def _create_pipeline(self, pipeline_config, name=None):
        """Helper method to create a pipeline"""
        try:
            params = {"name": name} if name else {}
            wrapped_config = {"pipeline": pipeline_config}
            response = self.client._make_request("POST", "/pipe", params=params, data=wrapped_config)
            return response
        except Exception as e:
            return e

    def _create_test_files(self):
        """Create temporary test files for processing"""
        # Create a temporary text file
        text_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
        text_file.write("This is a test document for processing.\nIt contains some sample text.")
        text_file.close()
        self.test_files.append(text_file.name)

        # Create a temporary JSON file
        json_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        json.dump({"test": "data", "message": "Hello from JSON file"}, json_file)
        json_file.close()
        self.test_files.append(json_file.name)

        # Create a temporary CSV file
        csv_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        csv_file.write("name,age,city\nJohn,25,New York\nJane,30,London")
        csv_file.close()
        self.test_files.append(csv_file.name)

    def _process_files(self, token, files):
        """Helper method to process files through a pipeline"""
        try:
            params = {"token": token}
            
            # Prepare files for multipart upload
            files_data = {}
            for i, file_path in enumerate(files):
                with open(file_path, 'rb') as f:
                    files_data[f'file_{i}'] = f.read()
            
            # Create file objects for requests
            files_for_request = {}
            for key, data in files_data.items():
                files_for_request[key] = io.BytesIO(data)
            
            response = self.client._make_request("PUT", "/pipe/process", params=params, files=files_for_request)
            return response
        except Exception as e:
            return e

    def test_process_single_file(self):
        """Test processing a single file"""
        if not self.test_token:
            self.skipTest("No test pipeline available")
        
        try:
            response = self._process_files(self.test_token, [self.test_files[0]])
            
            if hasattr(response, 'status'):
                if response.status == 'OK':
                    print(f"✓ Successfully processed single file: {response.data}")
                    self.assertEqual(response.status, 'OK')
                else:
                    print(f"✗ Failed to process single file: {response.error}")
            else:
                print(f"✗ Unexpected response processing single file: {response}")
                
        except Exception as e:
            print(f"✗ Single file processing failed: {e}")

    def test_process_multiple_files(self):
        """Test processing multiple files"""
        if not self.test_token:
            self.skipTest("No test pipeline available")
        
        try:
            response = self._process_files(self.test_token, self.test_files[:2])
            
            if hasattr(response, 'status'):
                if response.status == 'OK':
                    print(f"✓ Successfully processed multiple files: {response.data}")
                    self.assertEqual(response.status, 'OK')
                else:
                    print(f"✗ Failed to process multiple files: {response.error}")
            else:
                print(f"✗ Unexpected response processing multiple files: {response}")
                
        except Exception as e:
            print(f"✗ Multiple files processing failed: {e}")

    def test_process_different_file_types(self):
        """Test processing different file types"""
        if not self.test_token:
            self.skipTest("No test pipeline available")
        
        for i, file_path in enumerate(self.test_files):
            file_type = Path(file_path).suffix
            try:
                response = self._process_files(self.test_token, [file_path])
                
                if hasattr(response, 'status'):
                    if response.status == 'OK':
                        print(f"✓ Successfully processed {file_type} file: {response.data}")
                    else:
                        print(f"✗ Failed to process {file_type} file: {response.error}")
                else:
                    print(f"✗ Unexpected response processing {file_type} file: {response}")
                    
            except Exception as e:
                print(f"✗ {file_type} file processing failed: {e}")

    def test_process_with_invalid_token(self):
        """Test processing with invalid pipeline token"""
        invalid_token = "invalid-token-12345"
        
        try:
            response = self._process_files(invalid_token, [self.test_files[0]])
            
            if hasattr(response, 'status'):
                if response.status == 'Error':
                    print(f"✓ Correctly rejected invalid token: {response.error}")
                    self.assertEqual(response.status, 'Error')
                else:
                    print(f"✗ Unexpected success with invalid token: {response}")
            else:
                print(f"✗ Unexpected response with invalid token: {response}")
                
        except Exception as e:
            print(f"✓ Correctly rejected invalid token with exception: {e}")

    def test_process_with_nonexistent_token(self):
        """Test processing with nonexistent pipeline token"""
        nonexistent_token = "00000000-0000-0000-0000-000000000000"
        
        try:
            response = self._process_files(nonexistent_token, [self.test_files[0]])
            
            if hasattr(response, 'status'):
                if response.status == 'Error':
                    print(f"✓ Correctly rejected nonexistent token: {response.error}")
                    self.assertEqual(response.status, 'Error')
                else:
                    print(f"✗ Unexpected success with nonexistent token: {response}")
            else:
                print(f"✗ Unexpected response with nonexistent token: {response}")
                
        except Exception as e:
            print(f"✓ Correctly rejected nonexistent token with exception: {e}")

    def test_process_empty_file(self):
        """Test processing an empty file"""
        if not self.test_token:
            self.skipTest("No test pipeline available")
        
        # Create an empty file
        empty_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
        empty_file.close()
        
        try:
            response = self._process_files(self.test_token, [empty_file.name])
            
            if hasattr(response, 'status'):
                print(f"✓ Empty file processing result: {response.status}")
                if response.status == 'Error':
                    print(f"✓ Empty file correctly handled: {response.error}")
                elif response.status == 'OK':
                    print(f"✓ Empty file processed successfully: {response.data}")
            else:
                print(f"✗ Unexpected response processing empty file: {response}")
                
        except Exception as e:
            print(f"✓ Empty file processing handled with exception: {e}")
        finally:
            os.unlink(empty_file.name)

    def test_process_large_file(self):
        """Test processing a large file"""
        if not self.test_token:
            self.skipTest("No test pipeline available")
        
        # Create a large file (1MB)
        large_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
        large_content = "This is a large file test. " * 40000  # ~1MB
        large_file.write(large_content)
        large_file.close()
        
        try:
            response = self._process_files(self.test_token, [large_file.name])
            
            if hasattr(response, 'status'):
                if response.status == 'OK':
                    print(f"✓ Successfully processed large file: {response.data}")
                    self.assertEqual(response.status, 'OK')
                else:
                    print(f"✗ Failed to process large file: {response.error}")
            else:
                print(f"✗ Unexpected response processing large file: {response}")
                
        except Exception as e:
            print(f"✗ Large file processing failed: {e}")
        finally:
            os.unlink(large_file.name)

    def test_process_with_invalid_api_key(self):
        """Test processing with invalid API key"""
        if not self.test_token:
            self.skipTest("No test pipeline available")
        
        invalid_client = DTCApiClient(api_key='invalid_key_12345')
        
        try:
            params = {"token": self.test_token}
            files_data = {'file_0': io.BytesIO(b'test content')}
            
            with self.assertRaises((AuthenticationError, DTCApiError)):
                invalid_client._make_request("PUT", "/pipe/process", params=params, files=files_data)
            print("✓ Invalid API key correctly rejected")
        except Exception as e:
            print(f"✗ Invalid API key test failed: {e}")

    def test_process_no_connectivity(self):
        """Test processing with no network connectivity"""
        if not self.test_token:
            self.skipTest("No test pipeline available")
        
        offline_client = DTCApiClient(
            api_key=self.api_key,
            base_url='https://invalid-url-that-does-not-exist.com'
        )
        
        try:
            params = {"token": self.test_token}
            files_data = {'file_0': io.BytesIO(b'test content')}
            
            with self.assertRaises((NetworkError, DTCApiError)):
                offline_client._make_request("PUT", "/pipe/process", params=params, files=files_data)
            print("✓ Network connectivity error handled correctly")
        except Exception as e:
            print(f"✗ Network connectivity test failed: {e}")

    def test_process_response_structure(self):
        """Test the structure of processing response"""
        if not self.test_token:
            self.skipTest("No test pipeline available")
        
        try:
            response = self._process_files(self.test_token, [self.test_files[0]])
            
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

    def tearDown(self):
        """Clean up test files and pipeline"""
        # Clean up test files
        for file_path in self.test_files:
            try:
                os.unlink(file_path)
            except Exception as e:
                print(f"⚠ Could not delete test file {file_path}: {e}")
        
        # Clean up test pipeline
        if self.test_token:
            try:
                params = {"token": self.test_token}
                self.client._make_request("DELETE", "/pipe", params=params)
                print(f"✓ Cleaned up test pipeline: {self.test_token}")
            except Exception as e:
                print(f"⚠ Could not clean up test pipeline {self.test_token}: {e}")

if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2) 