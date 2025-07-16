# DTC API SDK

A comprehensive Python SDK for the Aparavi Data Toolchain (DTC) API that provides programmatic access to document processing, data extraction, and pipeline management capabilities.

## 🎯 **Start Here **

**Quickstart Guide**: Get started with the DTC API SDK by following our [Quickstart Guide](QUICKSTART_GUIDE.md) for a step-by-step setup.

**NEW**: Try our interactive Jupyter notebooks to learn the SDK quickly:

- **📓 [SDK Doc Processing Guide](notebooks/Sample_Doc_Processing_Guide.ipynb)** - Complete walkthrough of the new `upload_file_to_webhook()` method
- **📓 [Sample Document Processing](notebooks/Sample_Doc_Processing_Guide.ipynb)** - Real examples with different file types

*Run these notebooks locally or in your favorite Jupyter environment!*

## 🏗️ Python SDK Structure

The DTC API SDK provides a simple, unified interface to the document processing API:

```python
from dtc_api_sdk.client import DTCApiClient

# One client handles everything
client = DTCApiClient()

# System health & info
client.get_version()
client.get_status()
client.get_services()

# Task-based processing (recommended)
task_token = client.execute_task(pipeline_config)
result = client.upload_file_to_webhook(task_token, "document.pdf")

# Pipeline management (for web apps)
pipeline_token = client.create_pipeline(pipeline_config)
result = client.process_pipeline(pipeline_token, "document.pdf")
client.delete_pipeline(pipeline_token)
```

## 🚀 Quick Start

### Installation

```bash
git clone https://github.com/your-org/dtc-api-sdk.git
cd dtc-api-sdk
pip install -r requirements.txt
```

### Environment Setup

```bash
# Set your API key
export DTC_API_KEY="your-api-key-here"

# Or create a .env file
echo "DTC_API_KEY=your-api-key-here" > .env
```

### Simple Document Processing

```python
from dtc_api_sdk.client import DTCApiClient
import json

# Initialize client (automatically uses DTC_API_KEY environment variable)
client = DTCApiClient()

# Load pipeline configuration
with open('example_pipelines/simpleparser.json', 'r') as f:
    pipeline_data = json.load(f)

pipeline_config = {
    "pipeline": {
        "source": "webhook_1",
        "components": pipeline_data.get("components", [])
    }
}

# Step 1: Create task
task_token = client.execute_task(pipeline_config, name="Document Processing")

# Step 2: Process document (NEW SDK METHOD!)
result = client.upload_file_to_webhook(
    token=task_token,
    file_path="path/to/your/document.pdf",
    timeout=60
)

# Step 3: Automatic cleanup (no manual action needed)
print(f"Processing result: {result}")
```

## 📚 Documentation

### Core Guides
- **[📖 Document Processing Flow](docs/PDF_PROCESSING_PIPELINE_GUIDE.md)** - Complete API flow sequence and SDK methods
- **[📖 Pipeline vs Task Workflows](docs/PIPE_VS_TASK_WORKFLOWS.md)** - When to use each processing approach
- **[🏗️ SDK Architecture](docs/SDK_ARCHITECTURE.md)** - Technical architecture with detailed Mermaid diagrams
- **[📖 API Documentation](open_api_docs/API_DOCUMENTATION.md)** - Complete endpoint reference
- **[📖 OpenAPI Specification](open_api_docs/openapi.json)** - Machine-readable API spec

### Testing & Quality
- **[🧪 Unit Tests Guide](unit_tests/UNIT_TESTS.md)** - Comprehensive test suite (90 tests across 11 modules)
- **[🔧 Test Runner](run_unit_tests.py)** - Automated test execution with detailed reporting

### Examples & Usage
- **[📁 Examples Directory](examples/)** - Working code examples for common use cases
- **[📁 Reference Code](reference_code/)** - Advanced implementations and patterns
- **[📁 Notebooks](notebooks/)** - Interactive learning materials

## 🎯 New Features

### ✨ `upload_file_to_webhook()` Method

**NEW**: Simplified file upload method that handles all the complexity automatically:

```python
# Before (complex HTTP requests)
webhook_url = f"{client.base_url}/webhook"
params = {'type': 'cpu', 'apikey': client.api_key, 'token': task_token}
headers = {'Authorization': client.api_key, 'Content-Type': 'application/pdf'}
with open(file_path, 'rb') as file:
    response = requests.put(webhook_url, params=params, headers=headers, data=file)

# After (simple SDK method)
result = client.upload_file_to_webhook(token=task_token, file_path=file_path)
```

**Benefits:**
- ✅ **Auto-detection** - Automatically detects file MIME types
- ✅ **Error handling** - Proper exception handling built-in
- ✅ **Flexible** - Works with any file type supported by the pipeline
- ✅ **Simple API** - Just one method call instead of complex HTTP requests

## 🔧 SDK Methods

### Task Management
```python
# Execute task with pipeline configuration
task_token = client.execute_task(pipeline_config, name="My Task")

# Get task status
status = client.get_task_status(task_token)

# Cancel task
client.cancel_task(task_token)
```

### Pipeline Management
```python
# Validate pipeline configuration
is_valid = client.validate_pipeline(pipeline_config)

# Create persistent pipeline
pipeline_token = client.create_pipeline(pipeline_config, name="My Pipeline")

# Process files through pipeline
result = client.process_pipeline(pipeline_token, file_path)

# Delete pipeline
client.delete_pipeline(pipeline_token)
```

### File Processing
```python
# Upload file to webhook (NEW METHOD!)
result = client.upload_file_to_webhook(
    token=task_token,
    file_path="document.pdf",
    content_type="application/pdf",  # Optional, auto-detected
    timeout=60
)

# Send webhook data
result = client.send_webhook(task_token, webhook_data)
```

### System Information
```python
# Get API version
version = client.get_version()

# Get system status
status = client.get_status()

# Get available services
services = client.get_services()
```

## 🧪 Testing

### Run All Tests
```bash
python run_unit_tests.py
```

### Run Individual Tests
```bash
python unit_tests/test_version_endpoint.py
python unit_tests/test_webhook_endpoint.py
# ... etc
```

### Test Coverage
- **Total Tests**: 90 tests across 11 modules
- **Endpoints Covered**: 11/11 (100%)
- **Success Rate**: 100% (when API is healthy)
- **Average Execution Time**: ~2.7 minutes

## 📋 Processing Approaches

### Task Endpoint (Recommended for APIs)
- **Use for**: One-time processing, webhook endpoints, services
- **Benefits**: Simple, self-contained, automatic cleanup
- **Steps**: Create task → Upload file → Automatic cleanup

### Pipeline Endpoint (For Web UIs)
- **Use for**: Batch processing, web applications, repeated processing
- **Benefits**: Reusable, efficient for multiple files
- **Steps**: Create pipeline → Process files → Manual cleanup

See [Pipeline vs Task Workflows](docs/PIPE_VS_TASK_WORKFLOWS.md) for detailed comparison.

## 🛠️ Development

### Project Structure
```
dtc-api-sdk/
├── dtc_api_sdk/           # Main SDK package
├── docs/                  # Documentation
├── examples/              # Code examples
├── notebooks/             # Interactive tutorials
├── open_api_docs/         # API documentation
├── reference_code/        # Advanced examples
├── test_data/             # Test files
├── unit_tests/            # Test suite
├── example_pipelines/     # Pipeline configurations
└── run_unit_tests.py      # Test runner
```

### Environment Variables
```bash
DTC_API_KEY=your-api-key-here     # Required
DTC_BASE_URL=https://custom.url   # Optional, defaults to eaas-dev.aparavi.com
```

### Dependencies
- Python 3.7+
- requests
- pydantic
- python-dotenv

## 🔗 Related Resources

- **[Aparavi Data Toolchain](https://aparavi.com)** - Main platform
- **[API Documentation](open_api_docs/API_DOCUMENTATION.md)** - Complete endpoint reference
- **[OpenAPI Spec](open_api_docs/openapi.json)** - Machine-readable API specification

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass: `python run_unit_tests.py`
5. Submit a pull request

## 📞 Support

- **Documentation**: Start with the [notebooks](notebooks/) and [guides](docs/)
- **Issues**: Use GitHub issues for bugs and feature requests
- **Testing**: Run the full test suite to verify your setup

## 🎉 Getting Started

1. **🏃‍♂️ [Quick Start Guide](QUICKSTART_GUIDE.md)** - Get up and running in 5 minutes
2. **📓 [Try the Notebooks](notebooks/)** - Interactive learning experience
3. **🧪 [Run the Tests](unit_tests/UNIT_TESTS.md)** - Verify your setup
4. **📖 [Read the Docs](docs/)** - Deep dive into the SDK

---

*Ready to process documents? Start with the [Quick Start Guide](QUICKSTART_GUIDE.md) or jump into the [interactive notebooks](notebooks/)!*
