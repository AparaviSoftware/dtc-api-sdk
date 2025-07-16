# DTC API SDK Examples

This directory contains comprehensive examples demonstrating different ways to use the DTC API SDK for document processing and data extraction.

## 🌟 Recommended Approach: Webhook Processing

The **webhook processing method** is the recommended approach for production applications. It provides direct API access to extracted data without requiring web interfaces.

### [webhook_processing.py](webhook_processing.py) ⭐ **START HERE**

A complete, production-ready example showing:
- **Robust webhook-based document processing**
- **Automatic retry logic with progressive timeouts** 
- **Comprehensive error handling**
- **Support for multiple file formats** (PDF, DOC, TXT, images)
- **Batch processing capabilities**
- **Structured data extraction**

```bash
# Process a single document
python webhook_processing.py document.pdf

# Process multiple documents
python webhook_processing.py doc1.pdf doc2.docx doc3.txt
```

**Key Benefits:**
- ✅ Direct programmatic access to results
- ✅ No web interfaces required
- ✅ Production-ready error handling
- ✅ Smart timeout management (60-120s based on file size)
- ✅ Automatic retry with progressive backoff

## Other Examples

### [basic_usage.py](basic_usage.py)
Simple introduction to the SDK covering:
- Client initialization
- Basic API calls
- Status checking
- Error handling fundamentals

### [async_processing.py](async_processing.py)
Asynchronous processing patterns:
- Non-blocking task execution
- Status monitoring
- Concurrent processing

### [file_processing.py](file_processing.py)
File handling utilities:
- File upload methods
- MIME type detection
- Batch file processing

### [cli_example.py](cli_example.py)
Command-line interface example:
- Argument parsing
- Interactive processing
- Progress reporting

## Quick Start Guide

1. **Set up your environment**:
   ```bash
   export DTC_API_KEY="your-api-key-here"
   ```

2. **Install the SDK**:
   ```bash
   pip install dtc-api-sdk
   ```

3. **Run the webhook processing example**:
   ```bash
   python webhook_processing.py path/to/your/document.pdf
   ```

## Architecture Overview

The examples demonstrate the **webhook → parse → response** pipeline pattern:

```
📄 Document → 🪝 Webhook → 🔄 Parse → 📤 Response → 📊 Structured Data
```

### Webhook Processing Flow

1. **Pipeline Creation**: Create webhook processing pipeline
2. **File Preparation**: Convert file to base64 format  
3. **Webhook Submission**: Send data with retry logic
4. **Result Processing**: Extract structured data
5. **Output**: Get text, metadata, and statistics

## Error Handling Best Practices

All examples include comprehensive error handling:

- **Connection Issues**: Automatic retry with progressive backoff
- **Timeout Management**: Smart timeout calculation based on file size
- **Authentication Errors**: Clear error messages and guidance
- **File Errors**: Validation and helpful error reporting

## Configuration Examples

### Environment Variables
```bash
export DTC_API_KEY="your-api-key"
export DTC_BASE_URL="https://eaas-dev.aparavi.com"  # Optional
```

### Programmatic Configuration
```python
from dtc_api_sdk import DTCApiClient

client = DTCApiClient(
    api_key="your-api-key",
    base_url="https://eaas-dev.aparavi.com",
    timeout=90
)
```

## Expected Output Format

The webhook processing examples return structured data:

```json
{
  "extracted_text": "Full document text content...",
  "metadata": {
    "Content-Type": "application/pdf",
    "Content-Encoding": "UTF-8"
  },
  "processing_stats": {
    "objects_requested": 1,
    "objects_completed": 1,
    "types": {}
  }
}
```

## Performance Guidelines

- **Small files (< 1MB)**: 60 second timeout
- **Medium files (1-10MB)**: 90 second timeout  
- **Large files (> 10MB)**: 120 second timeout
- **Retry attempts**: 3 with progressive backoff (5s, 8s, 11s)

## Troubleshooting

### Common Issues

1. **Authentication errors**:
   - Verify your API key is set correctly
   - Check the API key has necessary permissions

2. **Timeout errors**:
   - Large files may need longer timeouts
   - Check network connectivity
   - The retry logic will automatically increase timeouts

3. **File format issues**:
   - Ensure file format is supported (PDF, DOC, TXT, images)
   - Check file is not corrupted

### Debug Mode

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Advanced Usage

For advanced use cases, see the [Architecture Documentation](../docs/ARCHITECTURE.md) which covers:
- Custom pipeline configurations
- Advanced error handling patterns
- Performance optimization techniques
- Production deployment considerations

---

💡 **Start with `webhook_processing.py` for the best experience!** This example demonstrates all the key concepts and best practices for using the DTC API SDK in production applications. 