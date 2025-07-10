# DTC API SDK - User Guide

Complete guide for getting started with the Aparavi Data Toolchain API SDK.

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Authentication](#authentication)
4. [Core Concepts](#core-concepts)
5. [Common Workflows](#common-workflows)
6. [Configuration Guide](#configuration-guide)
7. [Error Handling](#error-handling)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)

---

## Installation

### Requirements

- Python 3.8 or higher
- Active internet connection
- Valid DTC API key

### Install from PyPI

```bash
pip install dtc-api-sdk
```

### Install from Source

```bash
git clone https://github.com/aparavi/dtc-api-sdk.git
cd dtc-api-sdk
pip install -e .
```

### Development Installation

```bash
git clone https://github.com/aparavi/dtc-api-sdk.git
cd dtc-api-sdk
pip install -e ".[dev]"
```

---

## Quick Start

### 1. Get Your API Key

Contact your DTC administrator or visit the developer portal to obtain your API key.

### 2. Set Up Environment

```bash
export DTC_API_KEY="your_api_key_here"
```

### 3. Basic Usage

```python
from dtc_api_sdk import DTCApiClient, PipelineConfig

# Initialize client
client = DTCApiClient()

# Test connection
version = client.get_version()
print(f"Connected to DTC API v{version}")

# Create a simple configuration
config = PipelineConfig(
    source="s3://my-bucket/input",
    transformations=["extract_text", "analyze_content"],
    destination="s3://my-bucket/output"
)

# Execute a task
token = client.execute_task(config, name="my_first_task")
print(f"Task started: {token}")

# Monitor progress
task_info = client.get_task_status(token)
print(f"Status: {task_info.status}")
```

---

## Authentication

### Environment Variable (Recommended)

```bash
export DTC_API_KEY="your_api_key_here"
```

```python
client = DTCApiClient()  # Automatically uses environment variable
```

### Direct API Key

```python
client = DTCApiClient(api_key="your_api_key_here")
```

### Multiple Environments

```python
# Development
dev_client = DTCApiClient(
    api_key="dev_key",
    base_url="https://eaas-dev.aparavi.com"
)

# Production
prod_client = DTCApiClient(
    api_key="prod_key",
    base_url="https://api.aparavi.com"
)
```

---

## Core Concepts

### Pipelines vs Tasks

#### **Tasks** (Recommended for most use cases)
- One-off execution
- Simpler to manage
- Automatic cleanup
- Good for batch processing

```python
# Execute a task
token = client.execute_task(config, name="document_analysis")
```

#### **Pipelines** (For repeated operations)
- Persistent and reusable
- Multiple file uploads
- Manual cleanup required
- Good for continuous processing

```python
# Create pipeline
token = client.create_pipeline(config, name="document_processor")

# Upload files multiple times
client.upload_files(token, ["file1.pdf", "file2.docx"])
client.upload_files(token, ["file3.pdf", "file4.docx"])

# Clean up when done
client.delete_pipeline(token)
```

### Configuration Structure

All processing operations use a consistent configuration structure:

```python
config = PipelineConfig(
    source="data_source",           # Where data comes from
    transformations=["step1", "step2"],  # Processing steps
    destination="output_location",  # Where results go
    settings={"key": "value"}      # Additional settings
)
```

### Task States

Tasks progress through several states:

- **pending**: Submitted but not started
- **running**: Currently processing
- **completed**: Successfully finished
- **failed**: Error occurred
- **cancelled**: Manually stopped

---

## Common Workflows

### 1. Simple Document Processing

```python
from dtc_api_sdk import DTCApiClient, PipelineConfig

client = DTCApiClient()

config = PipelineConfig(
    source="s3://documents/input",
    transformations=["extract_text", "classify_documents"],
    destination="s3://documents/output",
    settings={
        "text_extraction": {"ocr_enabled": True},
        "classification": {"categories": ["invoice", "contract", "report"]}
    }
)

# Execute and wait for completion
token = client.execute_task(config, name="document_classification")
result = client.wait_for_task(token, timeout=300)
print(f"Processing complete: {result.result}")
```

### 2. Batch File Processing

```python
import os
from pathlib import Path

client = DTCApiClient()

# Create pipeline for multiple uploads
config = PipelineConfig(
    source="file_upload",
    transformations=["extract_text", "analyze_content"],
    destination="s3://processed/output"
)

pipeline_token = client.create_pipeline(config, name="batch_processor")

# Process files in batches
input_dir = Path("documents")
for batch in [list(input_dir.glob("*.pdf"))[i:i+10] for i in range(0, len(list(input_dir.glob("*.pdf"))), 10)]:
    client.upload_files(pipeline_token, [str(f) for f in batch])
    print(f"Uploaded batch of {len(batch)} files")

# Clean up
client.delete_pipeline(pipeline_token)
```

### 3. Concurrent Processing

```python
import time
from concurrent.futures import ThreadPoolExecutor

client = DTCApiClient()

def process_dataset(dataset_name):
    config = PipelineConfig(
        source=f"s3://data/{dataset_name}",
        transformations=["analyze", "summarize"],
        destination=f"s3://results/{dataset_name}"
    )
    
    token = client.execute_task(config, name=f"process_{dataset_name}")
    result = client.wait_for_task(token)
    return result

# Process multiple datasets concurrently
datasets = ["dataset1", "dataset2", "dataset3"]
with ThreadPoolExecutor(max_workers=3) as executor:
    results = list(executor.map(process_dataset, datasets))

print(f"Processed {len(results)} datasets")
```

### 4. Progress Monitoring

```python
import time

client = DTCApiClient()
token = client.execute_task(config, name="long_running_task")

# Monitor with progress updates
while True:
    task_info = client.get_task_status(token)
    print(f"Status: {task_info.status}, Progress: {task_info.progress}")
    
    if task_info.status.value in ["completed", "failed", "cancelled"]:
        break
    
    time.sleep(10)

print(f"Final result: {task_info.result}")
```

---

## Configuration Guide

### Source Types

#### S3 Sources
```python
config = PipelineConfig(
    source="s3://bucket/path",
    # ... other settings
)
```

#### File Upload Sources
```python
config = PipelineConfig(
    source="file_upload",  # Special source for direct uploads
    # ... other settings
)
```

#### Database Sources
```python
config = PipelineConfig(
    source="database://connection_string",
    # ... other settings
)
```

### Common Transformations

#### Text Processing
```python
transformations = [
    "extract_text",      # Extract text from documents
    "clean_text",        # Clean and normalize text
    "analyze_content",   # Content analysis
    "extract_entities",  # Named entity recognition
    "sentiment_analysis" # Sentiment analysis
]
```

#### Document Processing
```python
transformations = [
    "classify_documents",  # Document classification
    "extract_metadata",    # Metadata extraction
    "split_documents",     # Document splitting
    "merge_documents",     # Document merging
    "convert_format"       # Format conversion
]
```

#### Image Processing
```python
transformations = [
    "ocr",                # Optical character recognition
    "image_enhancement",  # Image quality improvement
    "object_detection",   # Object detection
    "face_recognition",   # Face recognition
    "image_classification" # Image classification
]
```

### Settings Examples

#### Text Extraction Settings
```python
settings = {
    "text_extraction": {
        "ocr_enabled": True,
        "language": "auto",  # or specific language codes
        "confidence_threshold": 0.8,
        "preserve_formatting": True
    }
}
```

#### Classification Settings
```python
settings = {
    "classification": {
        "categories": ["invoice", "contract", "report", "email"],
        "confidence_threshold": 0.7,
        "multi_label": False
    }
}
```

#### Output Settings
```python
settings = {
    "output_format": "json",  # json, xml, csv
    "include_metadata": True,
    "compress_output": True,
    "batch_size": 100
}
```

---

## Error Handling

### Exception Types

```python
from dtc_api_sdk.exceptions import (
    DTCApiError,
    AuthenticationError,
    ValidationError,
    PipelineError,
    TaskError,
    NetworkError
)
```

### Basic Error Handling

```python
try:
    client = DTCApiClient()
    token = client.execute_task(config)
except AuthenticationError:
    print("Check your API key")
except ValidationError as e:
    print(f"Configuration error: {e}")
except NetworkError:
    print("Network connection issue")
except DTCApiError as e:
    print(f"API error: {e}")
```

### Detailed Error Information

```python
try:
    client.execute_task(config)
except DTCApiError as e:
    print(f"Error: {e.message}")
    print(f"Status Code: {e.status_code}")
    print(f"Response Data: {e.response_data}")
```

### Retry Logic

```python
import time
from dtc_api_sdk.exceptions import NetworkError

def execute_with_retry(client, config, max_retries=3):
    for attempt in range(max_retries):
        try:
            return client.execute_task(config)
        except NetworkError as e:
            if attempt == max_retries - 1:
                raise
            print(f"Attempt {attempt + 1} failed, retrying...")
            time.sleep(2 ** attempt)  # Exponential backoff
```

---

## Best Practices

### 1. Resource Management

```python
# Always clean up pipelines
pipeline_token = client.create_pipeline(config)
try:
    # Use pipeline
    client.upload_files(pipeline_token, files)
finally:
    client.delete_pipeline(pipeline_token)
```

### 2. Configuration Validation

```python
# Validate before execution
if client.validate_pipeline(config):
    token = client.execute_task(config)
else:
    print("Configuration is invalid")
```

### 3. Monitoring and Logging

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def monitored_task(config):
    token = client.execute_task(config)
    logger.info(f"Task started: {token}")
    
    result = client.wait_for_task(token)
    logger.info(f"Task completed: {result.status}")
    
    return result
```

### 4. Environment-Specific Settings

```python
import os

# Use environment variables for configuration
CLIENT_CONFIG = {
    "api_key": os.getenv("DTC_API_KEY"),
    "base_url": os.getenv("DTC_BASE_URL", "https://eaas-dev.aparavi.com"),
    "timeout": int(os.getenv("DTC_TIMEOUT", "30")),
    "max_retries": int(os.getenv("DTC_MAX_RETRIES", "3"))
}

client = DTCApiClient(**CLIENT_CONFIG)
```

### 5. Batch Processing Optimization

```python
# Process files in optimal batch sizes
def process_files_in_batches(files, batch_size=10):
    for i in range(0, len(files), batch_size):
        batch = files[i:i + batch_size]
        client.upload_files(token, batch)
        print(f"Processed batch {i//batch_size + 1}")
```

---

## Troubleshooting

### Common Issues

#### 1. Authentication Errors
```
Error: API key is required
```
**Solution**: Set the `DTC_API_KEY` environment variable or pass it directly.

#### 2. Connection Timeouts
```
Error: Request timed out after 30 seconds
```
**Solution**: Increase timeout or check network connection.
```python
client = DTCApiClient(timeout=60)
```

#### 3. Configuration Validation Errors
```
Error: Missing required field in config: source
```
**Solution**: Ensure all required fields are present in your configuration.

#### 4. Task Failures
```
Task failed: Processing error occurred
```
**Solution**: Check task error details and input data format.
```python
task_info = client.get_task_status(token)
if task_info.error_message:
    print(f"Error details: {task_info.error_message}")
```

### Debug Mode

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Or for just the SDK
logging.getLogger("dtc_api_sdk").setLevel(logging.DEBUG)
```

### Health Checks

```python
def health_check():
    try:
        version = client.get_version()
        status = client.get_status()
        print(f"✓ API reachable, version: {version}")
        return True
    except Exception as e:
        print(f"✗ Health check failed: {e}")
        return False

if health_check():
    # Proceed with operations
    pass
```

### Network Diagnostics

```python
import requests

# Test direct connection
try:
    response = requests.get("https://eaas-dev.aparavi.com/version", timeout=10)
    print(f"Direct connection: {response.status_code}")
except requests.exceptions.RequestException as e:
    print(f"Network issue: {e}")
```

---

## Next Steps

1. **Explore Examples**: Check the `examples/` directory for practical use cases
2. **API Reference**: Review the complete API documentation
3. **Advanced Features**: Learn about webhooks, UI integration, and batch processing
4. **Performance Tuning**: Optimize for your specific use case
5. **Integration**: Integrate with your existing systems

---

## Getting Help

- **Documentation**: Full API reference and examples
- **Support**: Contact your DTC administrator
- **Issues**: Report bugs on GitHub
- **Community**: Join the developer community

Happy processing with the DTC API SDK! 