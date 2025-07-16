# DTC API SDK Unit Tests

Comprehensive test suite for the Aparavi Data Toolchain API SDK covering all endpoints and functionality.

## 🚀 Quick Start

### Prerequisites
1. **API Key**: Set your DTC API key in `.env` file:
   ```bash
   DTC_API_KEY=your-api-key-here
   ```

2. **Dependencies**: Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

### Running Tests

#### Run All Tests (Recommended)
```bash
python run_unit_tests.py
```
- Executes all 11 test modules sequentially
- Provides comprehensive reporting with statistics
- Shows performance metrics and detailed results
- Exit code 0 = success, 1 = failure

#### Run Individual Test Files
```bash
python unit_tests/test_version_endpoint.py
python unit_tests/test_status_endpoint.py
# ... etc
```

## 📋 Test Coverage

### System Health (13 tests)
- **`test_version_endpoint.py`** - GET `/version`
  - API version retrieval and format validation
  - Authentication and connectivity testing
- **`test_status_endpoint.py`** - GET `/status`  
  - Server status checks and uptime monitoring
  - Response structure validation
- **`test_services_endpoint.py`** - GET `/services`
  - Service enumeration and filtering
  - Service info validation (name, status, version)

### Pipeline Management (34 tests)
- **`test_pipe_validate_endpoint.py`** - POST `/pipe/validate`
  - Pipeline configuration validation using example data
  - Error handling for invalid configurations
- **`test_pipe_create_endpoint.py`** - POST `/pipe`
  - Pipeline creation with various configurations
  - Duplicate handling and resource management
- **`test_pipe_delete_endpoint.py`** - DELETE `/pipe`
  - Pipeline deletion and cleanup
  - Error handling for non-existent pipelines
- **`test_pipe_process_endpoint.py`** - PUT `/pipe/process`
  - File upload and processing (text, JSON, CSV)
  - Multi-file processing and large file handling

### Task Management (11 tests)
- **`test_task_execute_endpoint.py`** - PUT `/task`
  - Task execution with threading options
  - Status monitoring and cancellation
  - Configuration validation and error handling

### User Interface Endpoints (32 tests)
- **`test_webhook_endpoint.py`** - PUT `/webhook`
  - Webhook data processing (JSON, text, files)
  - Large payload handling and multiple requests
- **`test_chat_endpoint.py`** - GET `/chat`
  - Chat session initialization and cookie management
  - Parameter validation and redirect handling
- **`test_dropper_endpoint.py`** - GET `/dropper`
  - File dropper interface setup
  - Session management and UI redirects

## 🎯 Test Categories

Each test file includes:

### ✅ **Success Cases**
- Valid inputs and expected responses
- Proper data formats and structures
- Successful API interactions

### ❌ **Error Handling**
- Invalid API keys and authentication failures
- Malformed requests and data validation
- Non-existent resources and edge cases

### 🌐 **Network & Connectivity**
- Timeout handling and retry logic
- Connection failures and offline scenarios
- Response structure validation

### 🔧 **Resource Management**
- Proper setup and teardown procedures
- Token-based resource cleanup
- Memory and file management

## 📊 Test Statistics

- **Total Tests**: 90
- **Test Modules**: 11
- **API Endpoints Covered**: 11/11 (100%)
- **Success Rate**: 100% (when API is healthy)
- **Average Execution Time**: ~2.7 minutes

## 🛠️ Test Architecture

### Test Structure
```
unit_tests/
├── test_version_endpoint.py      # GET /version
├── test_status_endpoint.py       # GET /status  
├── test_services_endpoint.py     # GET /services
├── test_pipe_validate_endpoint.py # POST /pipe/validate
├── test_pipe_create_endpoint.py  # POST /pipe
├── test_pipe_delete_endpoint.py  # DELETE /pipe
├── test_pipe_process_endpoint.py # PUT /pipe/process
├── test_task_execute_endpoint.py # PUT /task
├── test_webhook_endpoint.py      # PUT /webhook
├── test_chat_endpoint.py         # GET /chat
├── test_dropper_endpoint.py      # GET /dropper
└── README.md                     # This file
```

### Common Test Patterns
- **Environment Setup**: Loads API key from `.env`
- **Resource Creation**: Creates test pipelines/tasks as needed
- **Test Execution**: Runs multiple scenarios per endpoint
- **Cleanup**: Automatically cleans up created resources
- **Error Reporting**: Detailed failure information

## 🔍 Example Test Output

```
🚀 Starting DTC API SDK Unit Test Suite
📋 Running 11 test modules
✅ API Key loaded: qFz-sHpQd3...

================================================================================
Running: unit_tests.test_version_endpoint
================================================================================
✅ PASSED - 4 tests, 0 failures, 0 errors, 0 skipped
Duration: 2.64s

📊 COMPREHENSIVE TEST REPORT
================================================================================
⏱️  Total Duration: 161.85 seconds
📁 Test Modules: 11
✅ Successful Modules: 11
🧪 Total Tests: 90
✅ Passed: 90
📈 Success Rate: 100.0%

🎉 ALL TESTS PASSED! The DTC API SDK is working correctly.
```

## 🚨 Troubleshooting

### Common Issues
1. **Missing API Key**: Ensure `DTC_API_KEY` is set in `.env`
2. **Network Issues**: Check internet connection and API endpoint availability
3. **Import Errors**: Verify all dependencies are installed
4. **Permission Issues**: Ensure write permissions for temporary files

### Debug Individual Tests
```bash
# Run with verbose output
python unit_tests/test_version_endpoint.py -v

# Run specific test method
python -m unittest unit_tests.test_version_endpoint.TestVersionEndpoint.test_version_success
```

## 🎯 CI/CD Integration

The test runner returns appropriate exit codes:
- **Exit 0**: All tests passed
- **Exit 1**: Some tests failed

Perfect for automated testing pipelines and quality assurance checks. 