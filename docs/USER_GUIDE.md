# DTC API SDK - User Guide

This guide shows you how to use the Aparavi Data Toolchain (DTC) API SDK for programmatic document processing and data extraction.

## 🚀 Quick Start - Webhook Processing

The **webhook approach is the recommended method** for production applications. It provides direct API access to extracted data without requiring web interfaces.

### 1. Installation & Setup

```bash
# Install the SDK
pip install dtc-api-sdk

# Set your API key
export DTC_API_KEY="your-api-key-here"
```

### 2. Basic Webhook Processing

```python
import os
import base64
from dtc_api_sdk import DTCApiClient

# Initialize client
client = DTCApiClient()

# Create webhook processing pipeline
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
            "id": "document-processor"
        }
    }

# Process any document
def process_document(file_path):
    # Create processing task
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
    
    # Send for processing
    response = client.send_webhook(task_token, webhook_data)
    
    # Extract results
    if 'objects' in response:
        for obj_id, obj_data in response['objects'].items():
            if 'text' in obj_data:
                extracted_content = obj_data['text']
                print(f"Extracted: {extracted_content}")
            
            if 'metadata' in obj_data:
                metadata = obj_data['metadata']
                print(f"Metadata: {metadata}")
    
    return response

# Process your document
results = process_document("path/to/document.pdf")
```

## 🏗️ Architecture: Webhook Processing Flow

The SDK uses a **webhook → parse → response** pipeline pattern:

```
📄 Document → 🪝 Webhook → 🔄 Parse → 📤 Response → 📊 Structured Data
```

### Why Webhook Processing?

✅ **Direct API Access** - Get results programmatically in your code  
✅ **No Web Interfaces** - Pure API workflow  
✅ **Automatic Retry** - Built-in retry logic with progressive backoff  
✅ **Smart Timeouts** - Timeout management based on file size  
✅ **Structured Results** - JSON responses with extracted content and metadata  

## 📋 Supported File Formats

- **Documents**: PDF, DOC, DOCX, RTF, TXT
- **Images**: PNG, JPG, JPEG (with OCR)
- **Spreadsheets**: XLS, XLSX, CSV
- **Presentations**: PPT, PPTX
- **Other**: HTML, XML, JSON

## 🛡️ Production-Ready Error Handling

### Robust Processing with Retry Logic

```python
import time
from pathlib import Path

def robust_document_processing(file_path, max_retries=3):
    """Process document with comprehensive error handling."""
    client = DTCApiClient()
    
    for attempt in range(max_retries):
        try:
            # Progressive timeout based on file size
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
            return parse_response(response)
            
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = 5 + (attempt * 3)  # Progressive backoff
                print(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise Exception(f"All processing attempts failed: {e}")
```

### Error Types and Solutions

| Error Type | Description | Solution |
|------------|-------------|----------|
| `AuthenticationError` | Invalid API key | Check your API key is set correctly |
| `TimeoutError` | Processing timeout | Increase timeout or retry with larger timeout |
| `NetworkError` | Connection issues | Check network connectivity; automatic retry will handle temporary issues |
| `ValidationError` | Invalid data/config | Review file format and pipeline configuration |

## 📊 Understanding Response Data

### Response Structure

```json
{
  "objects": {
    "object-uuid": {
      "__types": {"text": "text"},
      "metadata": {
        "Content-Type": "application/pdf",
        "Content-Encoding": "UTF-8"
      },
      "name": "processed-file-name",
      "path": "file-path",
      "text": ["extracted content..."]
    }
  },
  "types": {},
  "objectsRequested": 1,
  "objectsCompleted": 1
}
```

### Extracting Data

```python
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
            # Extract text content
            if 'text' in obj_data and obj_data['text']:
                text_content = obj_data['text'][0] if isinstance(obj_data['text'], list) else obj_data['text']
                results["extracted_text"] = text_content
            
            # Extract metadata
            if 'metadata' in obj_data:
                results["metadata"] = obj_data['metadata']
    
    return results
```

## 🔧 Advanced Configuration

### Custom Client Configuration

```python
from dtc_api_sdk import DTCApiClient

# Development environment
client = DTCApiClient(
    api_key="your-dev-key",
    base_url="https://eaas-dev.aparavi.com",
    timeout=90
)

# Production environment
client = DTCApiClient(
    api_key="your-prod-key", 
    base_url="https://api.aparavi.com",
    timeout=120
)
```

### Performance Optimization

```python
def calculate_optimal_timeout(file_size):
    """Calculate optimal timeout based on file size."""
    if file_size < 1_000_000:  # < 1MB
        return 60
    elif file_size < 10_000_000:  # < 10MB
        return 90
    else:  # >= 10MB
        return 120

def get_mime_type(file_path):
    """Get appropriate MIME type for file."""
    import mimetypes
    mime_type, _ = mimetypes.guess_type(file_path)
    
    if not mime_type:
        ext = Path(file_path).suffix.lower()
        mime_mapping = {
            '.pdf': 'application/pdf',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.txt': 'text/plain',
            '.png': 'image/png',
            '.jpg': 'image/jpeg'
        }
        mime_type = mime_mapping.get(ext, 'application/octet-stream')
    
    return mime_type
```

## 📦 Batch Processing

### Process Multiple Documents

```python
def process_multiple_documents(file_paths):
    """Process multiple documents efficiently."""
    client = DTCApiClient()
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

### Concurrent Processing

```python
import concurrent.futures
from typing import List, Dict

def process_documents_concurrently(file_paths: List[str], max_workers: int = 3) -> Dict:
    """Process multiple documents concurrently."""
    results = {}
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_file = {
            executor.submit(robust_document_processing, file_path): file_path 
            for file_path in file_paths
        }
        
        # Collect results as they complete
        for future in concurrent.futures.as_completed(future_to_file):
            file_path = future_to_file[future]
            try:
                result = future.result()
                results[file_path] = result
                print(f"✅ Completed: {file_path}")
            except Exception as e:
                results[file_path] = {"error": str(e)}
                print(f"❌ Failed: {file_path} - {e}")
    
    return results
```

## 🔍 Monitoring and Debugging

### Enable Debug Logging

```python
import logging

# Enable detailed logging
logging.basicConfig(level=logging.DEBUG)

# Or just for the SDK
logger = logging.getLogger('dtc_api_sdk')
logger.setLevel(logging.DEBUG)
```

### Task Status Monitoring

```python
def monitor_task_status(client, task_token, max_wait_time=300):
    """Monitor task processing status."""
    start_time = time.time()
    
    while time.time() - start_time < max_wait_time:
        try:
            status = client.get_task_status(task_token)
            print(f"Task status: {status}")
            
            if status.get('completed'):
                return status
            
            time.sleep(5)  # Check every 5 seconds
            
        except Exception as e:
            print(f"Status check failed: {e}")
            time.sleep(10)
    
    raise TimeoutError(f"Task did not complete within {max_wait_time} seconds")
```

## 📈 Performance Guidelines

### Timeout Recommendations

| File Size | Recommended Timeout | Retry Strategy |
|-----------|-------------------|----------------|
| < 1MB | 60 seconds | 3 attempts with 5s, 8s, 11s backoff |
| 1-10MB | 90 seconds | 3 attempts with progressive timeout increase |
| > 10MB | 120 seconds | 3 attempts with extended timeouts |

### Memory Considerations

- **Large Files**: Process files > 100MB in chunks if possible
- **Batch Processing**: Limit concurrent operations to 3-5 for optimal performance
- **Memory Usage**: Base64 encoding increases file size by ~33%

## 🏭 Production Deployment

### Environment Configuration

```bash
# Production environment variables
export DTC_API_KEY="your-production-key"
export DTC_BASE_URL="https://api.aparavi.com"
export DTC_TIMEOUT="120"
export DTC_MAX_RETRIES="3"
```

### Production-Ready Implementation

```python
import os
from dtc_api_sdk import DTCApiClient

class ProductionDocumentProcessor:
    def __init__(self):
        self.client = DTCApiClient(
            api_key=os.getenv('DTC_API_KEY'),
            base_url=os.getenv('DTC_BASE_URL', 'https://api.aparavi.com'),
            timeout=int(os.getenv('DTC_TIMEOUT', '120'))
        )
        self.max_retries = int(os.getenv('DTC_MAX_RETRIES', '3'))
    
    def process(self, file_path):
        """Production document processing."""
        return robust_document_processing(file_path, self.max_retries)
    
    def health_check(self):
        """Check API health."""
        try:
            status = self.client.get_status()
            return status.get('status') == 'healthy'
        except Exception:
            return False

# Usage
processor = ProductionDocumentProcessor()
if processor.health_check():
    results = processor.process("document.pdf")
```

## 🆘 Troubleshooting

### Common Issues

1. **"All connection attempts failed"**
   - Check network connectivity
   - Verify API endpoint is accessible
   - Try increasing timeout values

2. **"Authentication failed"**
   - Verify API key is correct
   - Check API key has necessary permissions
   - Ensure environment variable is set

3. **"Processing timeout"**
   - Large files may need longer timeouts
   - Check file format is supported
   - Try processing smaller files first

### Getting Help

- 📚 **Documentation**: Review the [Architecture Guide](ARCHITECTURE.md) and [API Reference](API_REFERENCE.md)
- 🔧 **Examples**: Check the `examples/` directory for working code samples
- 🐛 **Issues**: Report bugs via GitHub Issues
- 💬 **Support**: Contact support with specific error messages and request details

---

## 🎉 You're Ready!

Start with the [webhook processing example](../examples/webhook_processing.py) to see all these concepts in action. The example includes:

- ✅ Complete error handling
- ✅ Automatic retry logic
- ✅ Batch processing
- ✅ Progress reporting
- ✅ Result parsing

**Next Steps:**
1. Run the webhook processing example with your documents
2. Integrate the patterns into your application
3. Customize the pipeline configuration for your specific needs
4. Deploy with production-ready error handling and monitoring 