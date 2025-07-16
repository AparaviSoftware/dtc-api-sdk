# DTC API SDK

A Python SDK for the Aparavi Data Toolchain (DTC) API that provides programmatic access to document processing and data extraction capabilities.

## 🚀 Quick Start - Webhook Processing (Recommended)

The **webhook approach** is the recommended method for programmatic data extraction, providing direct API access to processed results without web interfaces.

```python
import os
import base64
from dtc_api_sdk import DTCApiClient

# Initialize client
os.environ["DTC_API_KEY"] = "your-api-key-here"
client = DTCApiClient()

# Create webhook pipeline for document processing
def create_webhook_pipeline():
    return {
        "pipeline": {
            "source": "webhook_1",
            "components": [
                {
                    "id": "webhook_1",
                    "provider": "webhook",
                    "config": {"hideForm": True, "mode": "Source", "type": "webhook"}
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
            "id": "webhook-processor"
        }
    }

# Process any document and get structured results
def process_document(file_path):
    # Create processing pipeline
    pipeline = create_webhook_pipeline()
    task_token = client.execute_task(pipeline, name="document-processor")
    
    # Prepare file data
    with open(file_path, 'rb') as f:
        file_content = f.read()
    
    webhook_data = {
        "filename": os.path.basename(file_path),
        "content_type": "application/pdf",  # or appropriate MIME type
        "size": len(file_content),
        "data": base64.b64encode(file_content).decode('utf-8')
    }
    
    # Send for processing with retry logic
    response = client.send_webhook(task_token, webhook_data)
    
    # Extract structured data
    if 'objects' in response:
        for obj_id, obj_data in response['objects'].items():
            if 'text' in obj_data:
                # Access extracted text content
                extracted_content = obj_data['text']
                print(f"Extracted content: {extracted_content}")
            
            if 'metadata' in obj_data:
                # Access file metadata
                metadata = obj_data['metadata']
                print(f"File metadata: {metadata}")
    
    return response

# Process your document
results = process_document("path/to/your/document.pdf")
```

## ✨ Key Features

- **🪝 Webhook Processing**: Direct API integration with structured JSON responses
- **📄 Multi-Format Support**: PDF, DOC, TXT, images, and more
- **🔄 Robust Error Handling**: Automatic retry with progressive timeouts
- **📊 Structured Output**: Extracted text, metadata, and processing statistics
- **🛡️ Production Ready**: Built-in timeout management and connection recovery
- **💻 Pure API Workflow**: No web interfaces required

## 🏗️ Architecture Overview

The SDK uses a **webhook → parse → response** pipeline pattern for optimal performance:

```
📄 Document → 🪝 Webhook → 🔄 Parse → 📤 Response → 📊 Structured Data
```

### Webhook Processing Benefits

- **Direct API Access**: Get results programmatically in your code
- **Automatic Retry**: Built-in retry logic with progressive backoff
- **Timeout Management**: Smart timeout handling (60-120s based on file size)
- **Error Recovery**: Robust connection handling and error recovery
- **Structured Results**: JSON responses with extracted content and metadata

## 📦 Installation

```bash
pip install dtc-api-sdk
```

Or for development:

```bash
git clone https://github.com/your-org/dtc-api-sdk.git
cd dtc-api-sdk
pip install -e .
```

## 🔧 Configuration

### Environment Variables (Recommended)

```bash
export DTC_API_KEY="your-api-key-here"
export DTC_BASE_URL="https://eaas-dev.aparavi.com"  # Optional, defaults to dev
```

### Direct Configuration

```python
from dtc_api_sdk import DTCApiClient

client = DTCApiClient(
    api_key="your-api-key-here",
    base_url="https://eaas-dev.aparavi.com",
    timeout=90  # seconds
)
```

## 🔍 Advanced Usage

### Processing with Custom Configuration

```python
import time
from pathlib import Path

def robust_document_processing(file_path, max_retries=3):
    """Process document with comprehensive error handling."""
    client = DTCApiClient()
    
    for attempt in range(max_retries):
        try:
            # Progressive timeout increase for larger files
            file_size = Path(file_path).stat().st_size
            timeout = 60 if file_size < 1_000_000 else 90 if file_size < 10_000_000 else 120
            client.timeout = timeout
            
            # Create and execute pipeline
            pipeline = create_webhook_pipeline()
            task_token = client.execute_task(pipeline, name=f"process_{Path(file_path).stem}")
            
            # Prepare and send data
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            webhook_data = {
                "filename": Path(file_path).name,
                "content_type": get_mime_type(file_path),
                "size": len(file_content),
                "data": base64.b64encode(file_content).decode('utf-8')
            }
            
            response = client.send_webhook(task_token, webhook_data)
            
            # Parse and return results
            return parse_webhook_response(response)
            
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = 5 + (attempt * 3)  # Progressive backoff
                print(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise Exception(f"All processing attempts failed: {e}")

def parse_webhook_response(response):
    """Extract structured data from webhook response."""
    results = {
        "extracted_text": "",
        "metadata": {},
        "processing_stats": {
            "objects_requested": response.get("objectsRequested", 0),
            "objects_completed": response.get("objectsCompleted", 0)
        }
    }
    
    if 'objects' in response:
        for obj_id, obj_data in response['objects'].items():
            if 'text' in obj_data and obj_data['text']:
                # Extract text content
                text_content = obj_data['text'][0] if isinstance(obj_data['text'], list) else obj_data['text']
                results["extracted_text"] = text_content
            
            if 'metadata' in obj_data:
                results["metadata"] = obj_data['metadata']
    
    return results
```

### Batch Processing

```python
def process_multiple_documents(file_paths):
    """Process multiple documents efficiently."""
    results = {}
    
    for file_path in file_paths:
        try:
            print(f"Processing: {file_path}")
            result = robust_document_processing(file_path)
            results[file_path] = result
            print(f"✅ Completed: {file_path}")
        except Exception as e:
            print(f"❌ Failed: {file_path} - {e}")
            results[file_path] = {"error": str(e)}
    
    return results

# Process multiple files
file_list = ["doc1.pdf", "doc2.docx", "doc3.txt"]
batch_results = process_multiple_documents(file_list)
```

## 📚 API Reference

### Core Methods

#### `DTCApiClient`

- `get_version()` - Get API version information
- `get_status()` - Check API health status
- `execute_task(pipeline, name=None)` - Create processing pipeline and get task token
- `send_webhook(task_token, data)` - Send data for processing via webhook
- `get_task_status(task_token)` - Check processing status
- `cancel_task(task_token)` - Cancel running task

#### Pipeline Management

- `create_pipeline(config)` - Create custom pipeline
- `validate_pipeline(config)` - Validate pipeline configuration
- `delete_pipeline(pipeline_id)` - Remove pipeline

### Error Handling

The SDK provides comprehensive error handling:

```python
from dtc_api_sdk.exceptions import (
    DTCApiError,
    AuthenticationError,
    ValidationError,
    NetworkError,
    TimeoutError
)

try:
    response = client.send_webhook(task_token, data)
except AuthenticationError:
    print("Invalid API key or authentication failed")
except TimeoutError:
    print("Processing timeout - try increasing timeout value")
except NetworkError:
    print("Network connectivity issue")
except ValidationError as e:
    print(f"Invalid data or configuration: {e}")
except DTCApiError as e:
    print(f"General API error: {e}")
```

## 🧪 Examples

Comprehensive examples are available in the `examples/` directory:

- `examples/basic_usage.py` - Simple document processing
- `examples/async_processing.py` - Asynchronous processing patterns
- `examples/file_processing.py` - File handling utilities
- `examples/cli_example.py` - Command-line interface

## 🔗 Related Documentation

- [Architecture Guide](docs/ARCHITECTURE.md) - Detailed technical architecture
- [API Reference](docs/API_REFERENCE.md) - Complete API documentation
- [User Guide](docs/USER_GUIDE.md) - Step-by-step usage guide

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check the `docs/` directory for detailed guides
- **Issues**: Report bugs and request features via GitHub Issues
- **Examples**: See `examples/` directory for working code samples

## 🏷️ Version History

- **v1.2.0** - Enhanced webhook processing with robust error handling and timeout management
- **v1.1.0** - Added comprehensive pipeline support and improved error handling
- **v1.0.0** - Initial release with basic API functionality

---

**Ready to extract data from your documents?** Start with the webhook processing example above! 🚀
