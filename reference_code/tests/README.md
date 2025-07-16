# DTC API SDK - Tests

This directory contains all test files and demonstrations for the DTC API SDK.

## Test Files

### Core SDK Tests
- `test_sdk.py` - Basic SDK functionality and import tests
- `advanced_test.py` - Advanced SDK features and pipeline validation
- `simple_cli_test.py` - Simple command-line interface tests

### Pipeline Tests
- `test_parse_pipeline.py` - Webhook → Parse pipeline flow testing
- `test_native_pipeline.py` - Native pipeline format testing
- `test_final_pipeline.py` - Comprehensive pipeline format testing
- `test_text_output.py` - Text output capture investigation

### Format Discovery Tests
- `final_test.py` - Pipeline wrapper format testing
- `correct_format_test.py` - Correct pipeline format validation

### Success Demonstrations
- `success_demo.py` - Complete working webhook → parse pipeline demo

## Running Tests

### Prerequisites
```bash
export DTC_API_KEY="your_api_key_here"
cd tests/
```

### Basic SDK Test
```bash
python test_sdk.py
```

### Pipeline Tests
```bash
python test_native_pipeline.py
python success_demo.py
```

### Text Output Investigation
```bash
python test_text_output.py
```

## Test Results Summary

✅ **Working:**
- SDK installation and import
- API connectivity and authentication
- Pipeline validation (both simple and complex)
- Webhook → Parse pipeline structure
- Error handling and exception management

⚠️  **In Progress:**
- Pipeline creation (format issues resolved)
- Text output capture methods
- File upload workflows

🎯 **Discovered:**
- Correct pipeline format: `{"pipeline": {"source": "component_id", "components": [...]}}`
- Component-based architecture with input/output lanes
- Webhook integration capabilities 