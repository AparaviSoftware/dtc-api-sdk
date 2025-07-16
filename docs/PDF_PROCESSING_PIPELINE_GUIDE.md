# Document Processing Flow

## Overview

This document outlines the sequence of API endpoints and SDK calls used to process documents through the DTC API using the task-based workflow with webhook processing.

## Processing Objective

Process documents through a configured pipeline (e.g., `simpleparser.json`) using the task endpoint approach for one-time document processing with automatic cleanup.

## Processing Flow Sequence

### Step 1: Task Creation
**Endpoint**: `PUT /task`
**SDK Method**: `client.execute_task()`

```python
# Initialize client
client = DTCApiClient()

# Load pipeline configuration
with open('example_pipelines/simpleparser.json', 'r') as f:
    pipeline_config = json.load(f)

# Create task
task_token = client.execute_task(
    pipeline_config, 
    name="Document Processing Task"
)
```

**API Call Details**:
- **URL**: `https://eaas-dev.aparavi.com/task`
- **Method**: PUT
- **Headers**: `Authorization: Bearer <api_key>`
- **Body**: Pipeline configuration JSON
- **Response**: Returns task token for subsequent webhook calls

### Step 2: Document Processing via Webhook
**Endpoint**: `PUT /webhook`
**SDK Method**: `client.upload_file_to_webhook()` (Recommended)

#### Option A: Using SDK Method (Recommended)
```python
# Upload file using the SDK method
result = client.upload_file_to_webhook(
    token=task_token,
    file_path="test_data/document.pdf",
    timeout=60
)
```

#### Option B: Direct HTTP Request
```python
# Construct webhook URL with parameters
webhook_url = f"{client.base_url}/webhook"
params = {
    'type': 'cpu',
    'apikey': client.api_key,
    'token': task_token
}

# Upload file directly
with open(file_path, 'rb') as file:
    headers = {
        'Authorization': client.api_key,  # No Bearer prefix
        'Content-Type': 'application/pdf'
    }
    
    response = requests.put(
        webhook_url,
        params=params,
        headers=headers,
        data=file,  # Direct file upload
        timeout=60
    )
```

**API Call Details**:
- **URL**: `https://eaas-dev.aparavi.com/webhook?type=cpu&apikey=<key>&token=<token>`
- **Method**: PUT
- **Headers**: 
  - `Authorization: <api_key>` (no Bearer prefix)
  - `Content-Type: application/pdf`
- **Body**: Raw file data (binary)
- **Response**: Processed document data

### Step 3: Automatic Cleanup
**Behavior**: Task automatically cleans up after processing completion
**No manual intervention required**

## Pipeline Configuration

Example `simpleparser.json` configuration:

```json
{
  "pipeline": {
    "source": "webhook_1",
    "components": [
      {
        "id": "webhook_1",
        "provider": "webhook",
        "config": {
          "hideForm": true,
          "mode": "Source"
        }
      },
      {
        "id": "parse_1",
        "provider": "parse",
        "input": [
          {
            "lane": "tags",
            "from": "webhook_1"
          }
        ]
      },
      {
        "id": "response_1",
        "provider": "response",
        "input": [
          {
            "lane": "text",
            "from": "parse_1"
          }
        ]
      }
    ]
  }
}
```

## API Endpoints Reference

Based on the OpenAPI specification, the following endpoints are used in the processing flow:

### 1. Task Creation Endpoint
- **Endpoint**: `PUT /task`
- **Purpose**: Create a new task with the pipeline configuration
- **Headers**: `Authorization: Bearer <api_key>`
- **Body**: Pipeline configuration JSON
- **Response**: Returns task token

### 2. Webhook Processing Endpoint
- **Endpoint**: `PUT /webhook`
- **Purpose**: Process file through the created task
- **Parameters**: `type=cpu&apikey=<key>&token=<task_token>`
- **Headers**: 
  - `Authorization: <api_key>` (no Bearer prefix)
  - `Content-Type: application/pdf`
- **Body**: Raw file data (binary)
- **Response**: Processed document data

## SDK Methods Used

### DTCApiClient.execute_task()
```python
task_token = client.execute_task(
    pipeline_config, 
    name="Document Processing Task"
)
```
- **Purpose**: Creates a task with the pipeline configuration
- **Parameters**: 
  - `pipeline_config`: Dictionary containing pipeline configuration
  - `name`: Optional name for the task
- **Returns**: Task token string

### DTCApiClient.upload_file_to_webhook()
```python
result = client.upload_file_to_webhook(
    token=task_token,
    file_path="test_data/document.pdf",
    content_type="application/pdf",  # Optional, auto-detected
    timeout=60
)
```
- **Purpose**: Uploads file for processing via webhook endpoint
- **Parameters**:
  - `token`: Task token from execute_task()
  - `file_path`: Path to the file to upload
  - `content_type`: MIME type (optional, auto-detected)
  - `timeout`: Request timeout in seconds (default: 60)
- **Returns**: Processed document data
- **Note**: This method handles direct file upload with proper headers and error handling

## Request/Response Flow

### Task Creation Request
```http
PUT /task HTTP/1.1
Host: eaas-dev.aparavi.com
Authorization: Bearer <api_key>
Content-Type: application/json

{
  "pipeline": {
    "source": "webhook_1",
    "components": [...]
  }
}
```

### Task Creation Response
```json
{
  "status": "OK",
  "data": {
    "token": "<task_token>"
  }
}
```

### Webhook Processing Request
```http
PUT /webhook?type=cpu&apikey=<key>&token=<task_token> HTTP/1.1
Host: eaas-dev.aparavi.com
Authorization: <api_key>
Content-Type: application/pdf

<binary file data>
```

### Webhook Processing Response
```json
{
  "status": "OK",
  "data": {
    "text": "Extracted document content...",
    "metadata": {...}
  }
}
```

## Technical Implementation Notes

### File Upload Method
- Use direct file upload as request body (binary data)
- Similar to curl's `-T` flag behavior
- Do not use multipart form data or JSON with base64 encoding

### Header Requirements
- Task creation: `Authorization: Bearer <api_key>`
- Webhook processing: `Authorization: <api_key>` (no Bearer prefix)
- Content-Type must match the actual file type

### URL Parameters
- `type=cpu`: Processing type
- `apikey=<key>`: API key parameter
- `token=<task_token>`: Task token from step 1

### Automatic Cleanup
- Tasks automatically clean up after processing completion
- No manual deletion required (unlike pipeline approach)

## Complete Example Using SDK

```python
import json
from dtc_api_sdk.client import DTCApiClient

def process_document_complete_example():
    """Complete example using the new SDK method."""
    
    # Initialize client
    client = DTCApiClient()
    
    # Load pipeline configuration
    with open('example_pipelines/simpleparser.json', 'r') as f:
        pipeline_data = json.load(f)
    
    # Wrap configuration with required "pipeline" key
    pipeline_config = {
        "pipeline": {
            "source": "webhook_1",
            "components": pipeline_data.get("components", [])
        }
    }
    
    # Step 1: Create task
    task_token = client.execute_task(
        pipeline_config, 
        name="Document Processing Task"
    )
    
    # Step 2: Process document using new SDK method
    result = client.upload_file_to_webhook(
        token=task_token,
        file_path="test_data/document.pdf",
        timeout=60
    )
    
    # Step 3: Automatic cleanup (no action needed)
    return result

# Usage
result = process_document_complete_example()
print(f"Processing result: {result}")
``` 