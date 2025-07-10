# DTC API SDK - API Reference

Complete reference documentation for the Aparavi Data Toolchain API SDK.

## Table of Contents

- [Client](#client)
- [Models](#models)
- [Exceptions](#exceptions)
- [Methods](#methods)
  - [Health Check](#health-check)
  - [Pipeline Management](#pipeline-management)
  - [Task Management](#task-management)
  - [File Operations](#file-operations)
  - [Webhook & UI](#webhook--ui)
  - [Services](#services)

---

## Client

### `DTCApiClient`

The main client class for interacting with the DTC API.

#### Constructor

```python
DTCApiClient(
    api_key: str = None,
    base_url: str = "https://eaas-dev.aparavi.com",
    timeout: int = 30,
    max_retries: int = 3
)
```

**Parameters:**
- `api_key` (str, optional): API key for authentication. If not provided, looks for `DTC_API_KEY` environment variable.
- `base_url` (str): Base URL for the API. Defaults to dev environment.
- `timeout` (int): Request timeout in seconds. Default: 30.
- `max_retries` (int): Maximum retry attempts for failed requests. Default: 3.

**Raises:**
- `AuthenticationError`: If no API key is provided.

**Example:**
```python
from dtc_api_sdk import DTCApiClient

# Using environment variable
client = DTCApiClient()

# Using explicit API key
client = DTCApiClient(api_key="your_api_key_here")

# Using production environment
client = DTCApiClient(
    api_key="your_prod_key",
    base_url="https://api.aparavi.com"
)
```

---

## Models

### `PipelineConfig`

Configuration object for pipelines and tasks.

```python
@dataclass
class PipelineConfig:
    source: str
    transformations: List[str] = field(default_factory=list)
    destination: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None
```

**Attributes:**
- `source` (str): Data source location or type
- `transformations` (List[str]): List of transformation steps
- `destination` (str, optional): Output destination
- `settings` (Dict, optional): Additional configuration settings

**Methods:**
- `to_dict()`: Convert to dictionary for API requests

**Example:**
```python
from dtc_api_sdk import PipelineConfig

config = PipelineConfig(
    source="s3://bucket/input",
    transformations=["extract_text", "analyze_content"],
    destination="s3://bucket/output",
    settings={
        "text_extraction": {"ocr_enabled": True},
        "output_format": "json"
    }
)
```

### `APIResponse`

Base response object for all API calls.

```python
@dataclass
class APIResponse:
    status: ResponseStatus
    data: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    metrics: Optional[Dict[str, Any]] = None
```

**Properties:**
- `is_success`: Boolean indicating if response was successful
- `error_message`: Extract error message if available

### `TaskInfo`

Task information and status.

```python
@dataclass
class TaskInfo:
    token: str
    status: TaskStatus
    name: Optional[str] = None
    progress: Optional[float] = None
    created_at: Optional[str] = None
    completed_at: Optional[str] = None
    error_message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
```

### `ServiceInfo`

Service information.

```python
@dataclass
class ServiceInfo:
    name: str
    status: str
    version: Optional[str] = None
    description: Optional[str] = None
    endpoints: Optional[List[str]] = None
```

---

## Exceptions

### `DTCApiError`

Base exception for all API errors.

```python
class DTCApiError(Exception):
    def __init__(self, message: str, status_code: int = None, response_data: dict = None)
```

**Attributes:**
- `message` (str): Error message
- `status_code` (int, optional): HTTP status code
- `response_data` (dict, optional): Full response data

### `AuthenticationError`

Raised when authentication fails.

### `ValidationError`

Raised when request validation fails.

### `PipelineError`

Raised when pipeline operations fail.

### `TaskError`

Raised when task operations fail.

### `NetworkError`

Raised when network operations fail.

---

## Methods

### Health Check

#### `get_version() -> str`

Get the API version.

**Returns:** Version string

**Example:**
```python
version = client.get_version()
print(f"API Version: {version}")
```

#### `get_status() -> Dict[str, Any]`

Get server status information.

**Returns:** Dictionary containing status information

**Example:**
```python
status = client.get_status()
print(f"Server Status: {status}")
```

---

### Pipeline Management

#### `create_pipeline(config, name=None) -> str`

Create a new processing pipeline.

**Parameters:**
- `config` (PipelineConfig | Dict): Pipeline configuration
- `name` (str, optional): Pipeline name

**Returns:** Pipeline token for subsequent operations

**Raises:** `PipelineError` if creation fails

**Example:**
```python
config = PipelineConfig(source="s3://bucket/data")
token = client.create_pipeline(config, name="my_pipeline")
```

#### `delete_pipeline(token) -> bool`

Delete an existing pipeline.

**Parameters:**
- `token` (str): Pipeline token

**Returns:** True if deletion was successful

**Example:**
```python
success = client.delete_pipeline(token)
```

#### `validate_pipeline(config) -> bool`

Validate a pipeline configuration without creating it.

**Parameters:**
- `config` (PipelineConfig | Dict): Pipeline configuration

**Returns:** True if configuration is valid

**Example:**
```python
is_valid = client.validate_pipeline(config)
if is_valid:
    print("Configuration is valid")
```

---

### Task Management

#### `execute_task(config, name=None, threads=None) -> str`

Execute a one-off task.

**Parameters:**
- `config` (PipelineConfig | Dict): Task configuration
- `name` (str, optional): Task name
- `threads` (int, optional): Number of threads (1-16)

**Returns:** Task token

**Raises:** `TaskError` if execution fails

**Example:**
```python
token = client.execute_task(
    config=config,
    name="data_processing",
    threads=4
)
```

#### `get_task_status(token) -> TaskInfo`

Get the status of a task.

**Parameters:**
- `token` (str): Task token

**Returns:** TaskInfo object with current status

**Example:**
```python
task_info = client.get_task_status(token)
print(f"Status: {task_info.status}")
print(f"Progress: {task_info.progress}")
```

#### `cancel_task(token) -> bool`

Cancel a running task.

**Parameters:**
- `token` (str): Task token

**Returns:** True if cancellation was successful

**Example:**
```python
success = client.cancel_task(token)
```

#### `wait_for_task(token, poll_interval=5, timeout=300) -> TaskInfo`

Wait for a task to complete.

**Parameters:**
- `token` (str): Task token
- `poll_interval` (int): Seconds between status checks. Default: 5
- `timeout` (int): Maximum seconds to wait. Default: 300

**Returns:** Final TaskInfo when task completes

**Raises:** 
- `TimeoutError`: If task doesn't complete within timeout
- `TaskError`: If task fails

**Example:**
```python
try:
    final_info = client.wait_for_task(token, timeout=600)
    print(f"Task completed: {final_info.result}")
except TimeoutError:
    print("Task is still running")
```

---

### File Operations

#### `upload_files(token, files) -> bool`

Upload files to a pipeline for processing.

**Parameters:**
- `token` (str): Pipeline token
- `files` (List[str | Path]): List of file paths to upload

**Returns:** True if upload was successful

**Raises:** `FileNotFoundError` if any file doesn't exist

**Example:**
```python
files = ["document1.pdf", "document2.docx"]
success = client.upload_files(token, files)
```

---

### Webhook & UI

#### `send_webhook(token, webhook_data) -> Dict[str, Any]`

Send webhook data to a task.

**Parameters:**
- `token` (str): Task token
- `webhook_data` (Dict): Data to send via webhook

**Returns:** Webhook response data

**Example:**
```python
data = {
    "event": "data_received",
    "payload": {"id": 123, "content": "Sample data"}
}
response = client.send_webhook(token, data)
```

#### `get_chat_url(token, pipeline_type, api_key=None) -> str`

Get chat interface URL with session parameters.

**Parameters:**
- `token` (str): Task token
- `pipeline_type` (str): Type of pipeline
- `api_key` (str, optional): API key (uses client's key if not provided)

**Returns:** Chat URL with session parameters

**Example:**
```python
url = client.get_chat_url(token, "document_processing")
print(f"Chat URL: {url}")
```

#### `get_dropper_url(token, pipeline_type, api_key=None) -> str`

Get dropper interface URL with session parameters.

**Parameters:**
- `token` (str): Task token
- `pipeline_type` (str): Type of pipeline
- `api_key` (str, optional): API key (uses client's key if not provided)

**Returns:** Dropper URL with session parameters

**Example:**
```python
url = client.get_dropper_url(token, "file_upload")
print(f"Dropper URL: {url}")
```

---

### Services

#### `get_services(service_name=None) -> List[ServiceInfo]`

Get available services.

**Parameters:**
- `service_name` (str, optional): Specific service name to filter

**Returns:** List of ServiceInfo objects

**Example:**
```python
# Get all services
services = client.get_services()
for service in services:
    print(f"{service.name}: {service.status}")

# Get specific service
ocr_service = client.get_services("ocr")
```

---

## Common Patterns

### Error Handling

```python
from dtc_api_sdk.exceptions import DTCApiError, AuthenticationError

try:
    client = DTCApiClient()
    result = client.execute_task(config)
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
except DTCApiError as e:
    print(f"API error: {e}")
    if e.status_code:
        print(f"Status code: {e.status_code}")
```

### Configuration Management

```python
# Using dataclass
config = PipelineConfig(
    source="s3://bucket/data",
    transformations=["extract_text", "analyze"],
    settings={"format": "json"}
)

# Using dictionary
config_dict = {
    "source": "s3://bucket/data",
    "transformations": ["extract_text", "analyze"],
    "settings": {"format": "json"}
}

# Both work with API methods
token = client.execute_task(config)
token = client.execute_task(config_dict)
```

### Async Processing

```python
import time

# Submit multiple tasks
tokens = []
for i in range(5):
    token = client.execute_task(config, name=f"task_{i}")
    tokens.append(token)

# Monitor all tasks
while tokens:
    completed = []
    for token in tokens:
        task_info = client.get_task_status(token)
        if task_info.status.value in ["completed", "failed", "cancelled"]:
            completed.append(token)
            print(f"Task {token[:8]} completed with status: {task_info.status}")
    
    # Remove completed tasks
    for token in completed:
        tokens.remove(token)
    
    if tokens:
        time.sleep(10)  # Wait before next check
```

---

## Environment Variables

The SDK respects the following environment variables:

- `DTC_API_KEY`: API key for authentication
- `DTC_BASE_URL`: Base URL for the API (overrides default)
- `DTC_TIMEOUT`: Request timeout in seconds
- `DTC_MAX_RETRIES`: Maximum retry attempts

**Example:**
```bash
export DTC_API_KEY="your_api_key_here"
export DTC_BASE_URL="https://api.aparavi.com"
export DTC_TIMEOUT="60"
export DTC_MAX_RETRIES="5"
``` 