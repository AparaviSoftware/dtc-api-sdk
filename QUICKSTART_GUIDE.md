# DTC API SDK - Quick Start Guide

Get up and running with document processing in 5 minutes! 🚀

## 📋 Prerequisites

- Python 3.7+
- DTC API Key
- Internet connection

## 🏃‍♂️ 5-Minute Setup

### 1. Install Dependencies

```bash
git clone https://github.com/AparaviSoftware/dtc-api-sdk.git
cd dtc-api-sdk
pip install -r requirements.txt
```

### 2. Set Your API Key

```bash
# Option A: Environment variable
export DTC_API_KEY="your-api-key-here"

# Option B: Create .env file
echo "DTC_API_KEY=your-api-key-here" > .env
```

### 3. Test Your Setup

```bash
python run_unit_tests.py
```

**Expected Output:**
```
🚀 Starting DTC API SDK Unit Test Suite
✅ API Key loaded: qFz-sHpQd3...
✅ PASSED - 90 tests, 0 failures
🎉 ALL TESTS PASSED! The DTC API SDK is working correctly.
```

## 🎯 Your First Document Processing

### Basic Processing (3 lines of code!)

```python
from dtc_api_sdk.client import DTCApiClient
import json

# Initialize client
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

# Process document
task_token = client.execute_task(pipeline_config, name="Quick Start Demo")
result = client.upload_file_to_webhook(
    token=task_token,
    file_path="test_data/Challenge_LeadAiDev.docx"
)

print(f"✅ Document processed successfully!")
print(f"Result: {result}")
```

## 📓 Interactive Learning

### Try the Notebooks

1. **Start Jupyter:**
   ```bash
   jupyter notebook
   ```

2. **Open these notebooks:**
   - `notebooks/SDK_Method_Flow_Guide.ipynb` - Complete walkthrough
   - `notebooks/Sample_Doc_Processing_Guide.ipynb` - Real examples
   - `process_invoice_simple.ipynb` - Invoice processing tutorial

3. **Run the cells step by step**

## 🔧 Common Use Cases

### 1. Process PDF Invoice

```python
# Process invoice and extract data
task_token = client.execute_task(pipeline_config, name="Invoice Processing")
result = client.upload_file_to_webhook(
    token=task_token,
    file_path="invoices/invoice.pdf",
    timeout=90
)

# Extract text content
if result.get('status') == 'OK':
    extracted_text = result['data']['objects']['text']
    print(f"Invoice text: {extracted_text}")
```

### 2. Batch Process Multiple Files

```python
import os

files_to_process = [
    "documents/contract.pdf",
    "documents/report.docx",
    "documents/receipt.jpg"
]

results = {}
for file_path in files_to_process:
    if os.path.exists(file_path):
        try:
            task_token = client.execute_task(pipeline_config, name=f"Process {os.path.basename(file_path)}")
            result = client.upload_file_to_webhook(token=task_token, file_path=file_path)
            results[file_path] = result
            print(f"✅ Processed: {file_path}")
        except Exception as e:
            print(f"❌ Failed: {file_path} - {e}")
            results[file_path] = {"error": str(e)}

print(f"Processed {len(results)} files")
```

### 3. Health Check & System Info

```python
# Check API health
version = client.get_version()
status = client.get_status()
services = client.get_services()

print(f"API Version: {version}")
print(f"System Status: {status}")
print(f"Available Services: {len(services)}")
```

## 📁 File Types Supported

- **PDFs**: `.pdf`
- **Word Documents**: `.docx`, `.doc`
- **Text Files**: `.txt`
- **Images**: `.jpg`, `.png`, `.tiff`
- **Spreadsheets**: `.xlsx`, `.csv`
- **And more!**

## 🎯 Processing Approaches

### Task Endpoint (Recommended for APIs)

```python
# Simple one-time processing
task_token = client.execute_task(pipeline_config, name="API Processing")
result = client.upload_file_to_webhook(token=task_token, file_path="document.pdf")
# ✅ Automatic cleanup
```

**Use for:** APIs, webhooks, one-time processing

### Pipeline Endpoint (For Web UIs)

```python
# Reusable pipeline for multiple files
pipeline_token = client.create_pipeline(pipeline_config, name="Batch Pipeline")
result1 = client.process_pipeline(pipeline_token, "file1.pdf")
result2 = client.process_pipeline(pipeline_token, "file2.pdf")
client.delete_pipeline(pipeline_token)  # Manual cleanup
```

**Use for:** Web applications, batch processing

## 🚨 Troubleshooting

### Common Issues

| Problem | Solution |
|---------|----------|
| `AuthenticationError` | Check your API key is set correctly |
| `Connection timeout` | Increase timeout: `timeout=120` |
| `File not found` | Verify file path exists |
| `Import errors` | Run `pip install -r requirements.txt` |

### Debug Mode

```python
# Enable verbose logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Test with smaller file first
result = client.upload_file_to_webhook(
    token=task_token,
    file_path="test_data/Challenge_LeadAiDev.docx",  # Small test file
    timeout=60
)
```

### Test Your Setup

```bash
# Run specific test
python unit_tests/test_version_endpoint.py

# Run webhook tests
python unit_tests/test_webhook_endpoint.py

# Run all tests with verbose output
python run_unit_tests.py -v
```

## 🎉 Next Steps

### 1. Explore Examples
```bash
ls examples/
# Try: python examples/basic_usage.py
```

### 2. Read Documentation
- [Document Processing Flow](docs/PDF_PROCESSING_PIPELINE_GUIDE.md)
- [Pipeline vs Task Workflows](docs/PIPE_VS_TASK_WORKFLOWS.md)
- [API Documentation](open_api_docs/API_DOCUMENTATION.md)

### 3. Advanced Features
- Custom pipeline configurations
- Async processing patterns
- Error handling strategies
- Performance optimization

### 4. Integration
- Build REST API endpoints
- Create web interfaces
- Integrate with databases
- Set up batch processing

## 📞 Need Help?

- **📓 Interactive Notebooks**: Start with `notebooks/`
- **🧪 Run Tests**: `python run_unit_tests.py`
- **📖 Documentation**: Check the `docs/` folder
- **🔍 Examples**: Browse the `examples/` directory
- **🐛 Issues**: Use GitHub issues for bugs

## 🎯 Quick Commands Reference

```bash
# Setup
export DTC_API_KEY="your-key"
pip install -r requirements.txt

# Test
python run_unit_tests.py

# Run examples
python examples/basic_usage.py

# Start notebooks
jupyter notebook
```

---

**🚀 Ready to go?** Your SDK is now configured and ready to process documents! Start with the [interactive notebooks](notebooks/) or dive into the [examples](examples/).

*Processing your first document is just 3 lines of code away!* 
