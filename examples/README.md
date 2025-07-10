# DTC API SDK Examples

This directory contains practical examples demonstrating how to use the Aparavi Data Toolchain API SDK.

## Prerequisites

1. **Install the SDK**:
   ```bash
   pip install -e ..  # From the root directory
   # or
   pip install dtc-api-sdk
   ```

2. **Set up your API key**:
   ```bash
   export DTC_API_KEY="your_api_key_here"
   ```

## Examples Overview

### 1. Basic Usage (`basic_usage.py`)

**Purpose**: Introduction to the SDK with fundamental operations.

**What it demonstrates**:
- Client initialization
- Connectivity testing
- Pipeline configuration and validation
- Task execution and monitoring
- Pipeline management

**How to run**:
```bash
python basic_usage.py
```

**Key concepts**:
- `DTCApiClient()` - Main client class
- `PipelineConfig` - Configuration object
- `validate_pipeline()` - Validate before execution
- `execute_task()` - Run one-off tasks
- `wait_for_task()` - Monitor completion

### 2. File Processing (`file_processing.py`)

**Purpose**: Comprehensive file upload and processing workflows.

**What it demonstrates**:
- Creating sample files
- Pipeline vs task workflows
- File upload handling
- Different processing configurations
- File type-specific settings

**How to run**:
```bash
python file_processing.py
```

**Key concepts**:
- `create_pipeline()` - Persistent pipelines
- `upload_files()` - File upload
- `delete_pipeline()` - Cleanup
- File type configurations (images, spreadsheets, emails)

### 3. Async Processing (`async_processing.py`)

**Purpose**: Concurrent task management and batch processing.

**What it demonstrates**:
- Multiple concurrent tasks
- Batch processing patterns
- Progress monitoring
- Performance scaling
- Webhook integration

**How to run**:
```bash
python async_processing.py
```

**Key concepts**:
- `BatchProcessor` - Custom batch management
- Thread scaling (1-16 threads)
- Webhook data handling
- Chat/Dropper UI integration

### 4. CLI Example (`cli_example.py`)

**Purpose**: Command-line interface for the SDK.

**What it demonstrates**:
- CLI argument parsing
- Configuration file loading
- Token management
- Interactive workflows

**How to run**:
```bash
# Check API status
python cli_example.py status

# Create sample configuration
python cli_example.py sample-config

# Submit a task
python cli_example.py submit --config sample_config.json --name "my_task"

# Monitor task
python cli_example.py monitor --token abc123 --wait

# Create pipeline
python cli_example.py pipeline --config sample_config.json --name "my_pipeline"

# Upload files
python cli_example.py upload --token abc123 --files file1.pdf file2.docx

# List saved tokens
python cli_example.py tokens

# Cancel task
python cli_example.py cancel --token abc123
```

**Key concepts**:
- Configuration file format
- Token persistence
- Command-line workflows
- Error handling

## Common Configuration Format

All examples use a consistent JSON configuration format:

```json
{
  "source": "s3://bucket/input",
  "transformations": [
    "extract_text",
    "analyze_content",
    "classify_documents"
  ],
  "destination": "s3://bucket/output",
  "settings": {
    "text_extraction": {
      "ocr_enabled": true,
      "language": "auto"
    },
    "content_analysis": {
      "extract_entities": true,
      "sentiment_analysis": true
    },
    "classification": {
      "categories": ["invoice", "contract", "report"],
      "confidence_threshold": 0.8
    },
    "output_format": "json"
  }
}
```

## Running Examples

### Environment Setup

1. **Development environment**:
   ```bash
   cd examples
   export DTC_API_KEY="your_dev_key"
   python basic_usage.py
   ```

2. **Production environment**:
   ```bash
   export DTC_API_KEY="your_prod_key"
   export DTC_BASE_URL="https://api.aparavi.com"
   python basic_usage.py
   ```

### Common Issues and Solutions

1. **Authentication Error**:
   ```
   ✗ Authentication failed: API key is required
   ```
   **Solution**: Set the `DTC_API_KEY` environment variable.

2. **Connection Error**:
   ```
   ✗ Connection test failed: Connection error
   ```
   **Solution**: Check your network connection and API endpoint.

3. **Validation Error**:
   ```
   ✗ Pipeline validation failed: Invalid configuration
   ```
   **Solution**: Review your configuration format and required fields.

### Example Workflows

#### 1. Quick Start Workflow
```bash
# 1. Check connectivity
python basic_usage.py

# 2. Create sample config
python cli_example.py sample-config

# 3. Submit task
python cli_example.py submit --config sample_config.json --name "quick_start"

# 4. Monitor completion
python cli_example.py monitor --token <returned_token> --wait
```

#### 2. File Processing Workflow
```bash
# 1. Run file processing example
python file_processing.py

# 2. Create pipeline for persistent processing
python cli_example.py pipeline --config sample_config.json --name "file_processor"

# 3. Upload your files
python cli_example.py upload --token <pipeline_token> --files document1.pdf document2.docx
```

#### 3. Batch Processing Workflow
```bash
# 1. Run concurrent processing
python async_processing.py

# 2. Monitor multiple tasks
python cli_example.py tokens  # List all tokens
python cli_example.py monitor --token <token1>
python cli_example.py monitor --token <token2>
```

## Configuration Examples

### Document Processing
```json
{
  "source": "s3://documents/input",
  "transformations": ["extract_text", "analyze_content", "classify_documents"],
  "destination": "s3://documents/output",
  "settings": {
    "text_extraction": {"ocr_enabled": true, "language": "auto"},
    "content_analysis": {"extract_entities": true, "sentiment_analysis": true},
    "classification": {"categories": ["invoice", "contract", "report"], "confidence_threshold": 0.8}
  }
}
```

### Image Processing
```json
{
  "source": "s3://images/input",
  "transformations": ["ocr", "image_analysis", "text_extraction"],
  "destination": "s3://images/output",
  "settings": {
    "ocr": {"language": ["eng", "fra"], "dpi": 300},
    "image_analysis": {"detect_objects": true, "extract_text": true}
  }
}
```

### Data Analysis
```json
{
  "source": "s3://data/csv",
  "transformations": ["data_validation", "statistical_analysis", "visualization"],
  "destination": "s3://data/output",
  "settings": {
    "validation": {"check_nulls": true, "outlier_detection": true},
    "analysis": {"correlation_matrix": true, "regression": true}
  }
}
```

## Best Practices

1. **Always validate configurations** before submitting tasks
2. **Use meaningful names** for tasks and pipelines
3. **Monitor task progress** regularly
4. **Handle errors gracefully** with try-catch blocks
5. **Clean up resources** (delete pipelines when done)
6. **Use appropriate thread counts** based on your data size
7. **Save tokens** for later reference

## Getting Help

- Check the main SDK documentation
- Review the OpenAPI specification
- Look at error messages and response data
- Use the `status` command to check API health

## Contributing

To add new examples:
1. Follow the existing code style
2. Include comprehensive error handling
3. Add documentation and comments
4. Update this README with your example 