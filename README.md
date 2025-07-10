# Aparavi Data Toolchain API SDK

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![PyPI Version](https://img.shields.io/pypi/v/dtc-api-sdk.svg)](https://pypi.org/project/dtc-api-sdk/)

Python SDK for the Aparavi Data Toolchain API - a powerful platform for automated data processing, document analysis, and intelligent content extraction.

## 🚀 Features

- **Simple & Intuitive**: Easy-to-use Python interface for complex data processing workflows
- **Comprehensive**: Full coverage of all DTC API endpoints and features
- **Robust**: Built-in error handling, retries, and connection management
- **Flexible**: Support for both one-off tasks and persistent pipelines
- **Concurrent**: Batch processing and concurrent task execution
- **Well-Documented**: Extensive documentation and practical examples

## 📦 Installation

### Requirements

- Python 3.8 or higher
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

## 🏃 Quick Start

### 1. Set up your API key

```bash
export DTC_API_KEY="your_api_key_here"
```

### 2. Basic Usage

```python
from dtc_api_sdk import DTCApiClient, PipelineConfig

# Initialize client
client = DTCApiClient()

# Test connection
version = client.get_version()
print(f"Connected to DTC API v{version}")

# Create a simple configuration
config = PipelineConfig(
    source="s3://my-bucket/documents",
    transformations=["extract_text", "analyze_content", "classify_documents"],
    destination="s3://my-bucket/processed",
    settings={
        "text_extraction": {"ocr_enabled": True},
        "classification": {"categories": ["invoice", "contract", "report"]}
    }
)

# Execute a task
token = client.execute_task(config, name="document_processing")
print(f"Task started: {token}")

# Wait for completion
result = client.wait_for_task(token)
print(f"Task completed: {result.status}")
```

## 🎯 Core Concepts

### Tasks vs Pipelines

**Tasks** (Recommended for most use cases):
- One-off execution
- Automatic cleanup
- Perfect for batch processing

**Pipelines** (For continuous processing):
- Persistent and reusable
- Multiple file uploads
- Manual lifecycle management

### Configuration Structure

```python
config = PipelineConfig(
    source="data_source",              # Where data comes from
    transformations=["step1", "step2"], # Processing steps
    destination="output_location",     # Where results go
    settings={"key": "value"}         # Additional settings
)
```

## 📚 Documentation

### Core Documentation

- [**User Guide**](docs/USER_GUIDE.md) - Complete getting started guide
- [**API Reference**](docs/API_REFERENCE.md) - Full API documentation
- [**Examples**](examples/README.md) - Practical usage examples

### Key Classes

- **`DTCApiClient`** - Main client for API interaction
- **`PipelineConfig`** - Configuration for processing pipelines
- **`TaskInfo`** - Task status and progress information
- **`APIResponse`** - Standardized API response format

## 🔧 Examples

### Document Processing

```python
from dtc_api_sdk import DTCApiClient, PipelineConfig

client = DTCApiClient()

config = PipelineConfig(
    source="s3://documents/legal",
    transformations=["extract_text", "legal_analysis", "compliance_check"],
    destination="s3://processed/legal",
    settings={
        "legal_analysis": {"extract_clauses": True},
        "compliance": {"regulations": ["GDPR", "CCPA"]}
    }
)

token = client.execute_task(config, name="legal_document_analysis")
result = client.wait_for_task(token)
```

### File Upload Processing

```python
# Create pipeline for file uploads
config = PipelineConfig(
    source="file_upload",
    transformations=["extract_text", "analyze_content"],
    destination="s3://processed/output"
)

pipeline_token = client.create_pipeline(config)

# Upload files
files = ["document1.pdf", "document2.docx", "image.png"]
client.upload_files(pipeline_token, files)

# Clean up
client.delete_pipeline(pipeline_token)
```

### Batch Processing

```python
# Process multiple datasets concurrently
datasets = ["dataset1", "dataset2", "dataset3"]
tokens = []

for dataset in datasets:
    config = PipelineConfig(
        source=f"s3://data/{dataset}",
        transformations=["analyze", "summarize"],
        destination=f"s3://results/{dataset}"
    )
    token = client.execute_task(config, name=f"process_{dataset}")
    tokens.append(token)

# Wait for all to complete
results = []
for token in tokens:
    result = client.wait_for_task(token)
    results.append(result)
```

### Command Line Interface

```bash
# Check API status
python -m dtc_api_sdk.examples.cli_example status

# Submit a task
python -m dtc_api_sdk.examples.cli_example submit --config config.json

# Monitor progress
python -m dtc_api_sdk.examples.cli_example monitor --token abc123 --wait
```

## 🛠️ Advanced Features

### Error Handling

```python
from dtc_api_sdk.exceptions import DTCApiError, AuthenticationError

try:
    client = DTCApiClient()
    token = client.execute_task(config)
except AuthenticationError:
    print("Check your API key")
except DTCApiError as e:
    print(f"API error: {e}")
    print(f"Status code: {e.status_code}")
```

### Webhook Integration

```python
# Configure webhook-enabled task
config = PipelineConfig(
    source="webhook_input",
    transformations=["real_time_processing"],
    settings={
        "webhook": {
            "callback_url": "https://your-app.com/webhook",
            "events": ["processing_complete", "error_occurred"]
        }
    }
)

token = client.execute_task(config)

# Send webhook data
webhook_data = {"event": "data_received", "data": {...}}
client.send_webhook(token, webhook_data)
```

### UI Integration

```python
# Get URLs for integrated UI components
chat_url = client.get_chat_url(token, "document_processing")
dropper_url = client.get_dropper_url(token, "file_upload")
```

## 🎨 Configuration Examples

### Image Processing

```python
config = PipelineConfig(
    source="s3://images/input",
    transformations=["ocr", "image_analysis", "text_extraction"],
    settings={
        "ocr": {"languages": ["eng", "fra"], "dpi": 300},
        "image_analysis": {"detect_objects": True}
    }
)
```

### Data Analysis

```python
config = PipelineConfig(
    source="s3://data/csv",
    transformations=["data_validation", "statistical_analysis"],
    settings={
        "validation": {"check_nulls": True, "outlier_detection": True},
        "analysis": {"correlation_matrix": True}
    }
)
```

### Email Processing

```python
config = PipelineConfig(
    source="s3://email/archives",
    transformations=["parse_email", "thread_analysis", "pii_detection"],
    settings={
        "parsing": {"extract_attachments": True},
        "pii": {"mask_sensitive_data": True}
    }
)
```

## 🚀 Available Transformations

### Text Processing
- `extract_text` - Extract text from documents
- `clean_text` - Clean and normalize text
- `analyze_content` - Content analysis and insights
- `sentiment_analysis` - Sentiment detection
- `extract_entities` - Named entity recognition

### Document Processing
- `classify_documents` - Document classification
- `extract_metadata` - Metadata extraction
- `split_documents` - Document splitting
- `merge_documents` - Document merging
- `convert_format` - Format conversion

### Image Processing
- `ocr` - Optical character recognition
- `image_enhancement` - Image quality improvement
- `object_detection` - Object detection
- `face_recognition` - Face recognition
- `image_classification` - Image classification

### Data Processing
- `data_validation` - Data quality checks
- `statistical_analysis` - Statistical analysis
- `data_transformation` - Data transformation
- `deduplication` - Remove duplicates
- `data_enrichment` - Data enrichment

## 🔒 Security & Best Practices

### Environment Variables

```bash
export DTC_API_KEY="your_api_key_here"
export DTC_BASE_URL="https://api.aparavi.com"  # Production
export DTC_TIMEOUT="60"
export DTC_MAX_RETRIES="3"
```

### Resource Management

```python
# Always clean up pipelines
pipeline_token = client.create_pipeline(config)
try:
    client.upload_files(pipeline_token, files)
finally:
    client.delete_pipeline(pipeline_token)
```

### Configuration Validation

```python
# Validate before execution
if client.validate_pipeline(config):
    token = client.execute_task(config)
else:
    print("Configuration is invalid")
```

## 🧪 Testing

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=dtc_api_sdk

# Run specific test file
pytest tests/test_client.py
```

## 📈 Performance Tips

1. **Use appropriate thread counts** (1-16) based on your data size
2. **Batch file uploads** for better performance
3. **Monitor task progress** to avoid timeouts
4. **Validate configurations** before submitting
5. **Use tasks for one-off operations**, pipelines for continuous processing

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **API Documentation**: [docs/API_REFERENCE.md](docs/API_REFERENCE.md)
- **User Guide**: [docs/USER_GUIDE.md](docs/USER_GUIDE.md)
- **Examples**: [examples/](examples/)
- **PyPI Package**: [https://pypi.org/project/dtc-api-sdk/](https://pypi.org/project/dtc-api-sdk/)
- **Issues**: [GitHub Issues](https://github.com/aparavi/dtc-api-sdk/issues)

## 🆘 Support

- **Documentation**: Complete API reference and user guide
- **Examples**: Practical usage examples in the `examples/` directory
- **Issues**: Report bugs and request features via GitHub Issues
- **Community**: Join our developer community for support and discussions

---

**Happy processing with the Aparavi Data Toolchain API SDK!** 🎉
